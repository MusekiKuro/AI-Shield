"""Local Whisper server for the application's in-memory audio phrases."""

from __future__ import annotations

import hmac
import io
import logging
import os
import threading
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator

import soundfile as sf
import torch
from fastapi import FastAPI, HTTPException, Request
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import UploadFile
from starlette.formparsers import MultiPartException, MultiPartParser
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor


SAMPLE_RATE = 16_000
MAX_AUDIO_SECONDS = 30
MAX_REQUEST_BYTES = 16 * 1024 * 1024
logger = logging.getLogger("uvicorn.error")


@dataclass
class SpeechModel:
    model: Any
    processor: Any


@dataclass
class ServerState:
    api_key: bytes
    default: SpeechModel
    kazakh: SpeechModel | None
    gpu_lock: Any


def _load_model(name: str) -> SpeechModel:
    processor = AutoProcessor.from_pretrained(name)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        name,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
    )
    model.to("cuda")
    model.eval()
    return SpeechModel(model=model, processor=processor)


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    api_key = os.environ.get("STT_API_KEY", "")
    default_name = os.environ.get("STT_MODEL_DEFAULT", "").strip()
    kazakh_name = os.environ.get("STT_MODEL_KK", "").strip()

    if not api_key:
        raise RuntimeError("STT_API_KEY must be set")
    if not default_name:
        raise RuntimeError("STT_MODEL_DEFAULT must be set")
    if not torch.cuda.is_available():
        raise RuntimeError("A CUDA GPU is required for the STT server")

    default = _load_model(default_name)
    if kazakh_name == default_name:
        kazakh = default
    elif kazakh_name:
        kazakh = _load_model(kazakh_name)
    else:
        kazakh = None

    app.state.stt = ServerState(
        api_key=api_key.encode("utf-8"),
        default=default,
        kazakh=kazakh,
        gpu_lock=threading.Lock(),
    )
    yield


app = FastAPI(
    lifespan=_lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


class _RequestTooLarge(MultiPartException):
    pass


class _MemoryMultipartParser(MultiPartParser):
    # A zero spool limit disables automatic rollover to disk in Python.
    # Both names cover the Starlette versions used by FastAPI.
    spool_max_size = 0
    max_file_size = 0

    def __init__(self, request: Request) -> None:
        super().__init__(request.headers, _limited_stream(request), max_files=1, max_fields=3)
        self.complete = False

    def on_end(self) -> None:
        self.complete = True


async def _limited_stream(request: Request) -> AsyncIterator[bytes]:
    total = 0
    async for chunk in request.stream():
        total += len(chunk)
        if total > MAX_REQUEST_BYTES:
            raise _RequestTooLarge("Request is too large")
        yield chunk


def _authorize(request: Request, state: ServerState) -> None:
    scheme, separator, token = request.headers.get("Authorization", "").partition(" ")
    if (
        not separator
        or scheme.lower() != "bearer"
        or not token
        or not hmac.compare_digest(token.strip().encode("utf-8"), state.api_key)
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def _read_form(request: Request) -> tuple[bytes, str]:
    content_type = request.headers.get("content-type", "").partition(";")[0]
    if content_type.strip().lower() != "multipart/form-data":
        raise HTTPException(status_code=400, detail="Expected multipart/form-data")

    parser = _MemoryMultipartParser(request)
    try:
        form = await parser.parse()
    except _RequestTooLarge:
        raise HTTPException(status_code=413, detail="Request is too large") from None
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid multipart request") from None

    try:
        if not parser.complete:
            raise HTTPException(status_code=400, detail="Incomplete multipart request")

        files = form.getlist("file")
        languages = form.getlist("language")
        if len(files) != 1 or not isinstance(files[0], UploadFile):
            raise HTTPException(status_code=400, detail="One audio file is required")
        if len(languages) > 1 or (languages and not isinstance(languages[0], str)):
            raise HTTPException(status_code=400, detail="Invalid language field")

        language = (languages[0].strip().lower() if languages else "") or "auto"
        if language not in {"auto", "ru", "kk"}:
            raise HTTPException(status_code=400, detail="Language must be ru, kk, or auto")

        audio = await files[0].read()
        return audio, language
    finally:
        await form.close()


def _decode_wav(data: bytes) -> tuple[Any, int]:
    try:
        with sf.SoundFile(io.BytesIO(data)) as wav:
            if (
                wav.format not in {"WAV", "WAVEX"}
                or not wav.subtype.startswith("PCM_")
                or wav.samplerate != SAMPLE_RATE
                or wav.channels != 1
                or wav.frames <= 0
                or wav.frames > SAMPLE_RATE * MAX_AUDIO_SECONDS
            ):
                raise ValueError("Unsupported WAV")
            samples = wav.read(dtype="float32")
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Expected a non-empty mono PCM WAV at 16000 Hz, up to 30 seconds",
        ) from None

    if len(samples) == 0:
        raise HTTPException(status_code=400, detail="Audio is empty")
    duration_ms = round(len(samples) * 1000 / SAMPLE_RATE)
    return samples, duration_ms


def _features(model: SpeechModel, samples: Any) -> Any:
    inputs = model.processor.feature_extractor(
        samples,
        sampling_rate=SAMPLE_RATE,
        return_tensors="pt",
    )
    return inputs.input_features.to(device="cuda", dtype=torch.float16)


def _transcribe(state: ServerState, samples: Any, language: str) -> tuple[str, str]:
    # The lock lives in the worker thread, so a cancelled HTTP request cannot
    # release it while its GPU work is still running.
    with state.gpu_lock, torch.inference_mode():
        default_features = None
        if language == "auto":
            default_features = _features(state.default, samples)
            language_id = state.default.model.detect_language(
                input_features=default_features
            )[0].item()
            token = state.default.processor.tokenizer.convert_ids_to_tokens(language_id)
            if not isinstance(token, str) or not token.startswith("<|") or not token.endswith("|>"):
                raise RuntimeError("Whisper returned an invalid language token")
            language = token[2:-2]

        selected = state.kazakh if language == "kk" and state.kazakh else state.default
        if selected is state.default and default_features is not None:
            input_features = default_features
        else:
            input_features = _features(selected, samples)

        output = selected.model.generate(
            input_features=input_features,
            language=language,
            task="transcribe",
        )
        text = selected.processor.batch_decode(output, skip_special_tokens=True)[0].strip()
        return text, language


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/audio/transcriptions")
async def transcribe(request: Request) -> dict[str, str | int]:
    started = time.perf_counter()
    state: ServerState = request.app.state.stt
    _authorize(request, state)
    audio, requested_language = await _read_form(request)

    try:
        samples, duration_ms = await run_in_threadpool(_decode_wav, audio)
        text, language = await run_in_threadpool(
            _transcribe, state, samples, requested_language
        )
    except HTTPException:
        raise
    except Exception:
        logger.error("STT processing failed")
        raise HTTPException(status_code=500, detail="Speech recognition failed") from None

    processing_ms = round((time.perf_counter() - started) * 1000)
    logger.info(
        "STT duration_ms=%d language=%s processing_ms=%d",
        duration_ms,
        language,
        processing_ms,
    )
    return {"text": text, "language": language, "duration_ms": duration_ms}

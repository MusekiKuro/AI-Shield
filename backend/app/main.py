"""C01 scaffold. Business routes are introduced by C02–C06."""

from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.api.routes_health import router as health_router
from app.config import get_settings
from app.schemas import ErrorCode, ErrorResponse, HealthResponse, LlmHealth, SttHealth


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = get_settings()
    # Unknown/unprobed is never advertised as available. C03.9 owns probes.
    app.state.health = HealthResponse(
        llm=LlmHealth(available=False, model=None), stt=SttHealth(available=False),
    )
    yield


app = FastAPI(title="ИИ-щит · синтетическое демо", version="0.1.0", lifespan=lifespan)
app.include_router(health_router)


def error_response(request: Request, status: int, code: ErrorCode) -> JSONResponse:
    body = ErrorResponse(
        code=code, message="Request could not be completed.",
        request_id=getattr(request.state, "request_id", str(uuid4())),
    )
    return JSONResponse(status_code=status, content=body.model_dump(mode="json"),
                        headers={"X-Request-ID": body.request_id})


@app.middleware("http")
async def request_context(request: Request, call_next):
    request.state.request_id = str(uuid4())
    try:
        response = await call_next(request)
    except Exception:
        # Do not let validation inputs, model responses or PIN reach tracebacks/logs.
        return error_response(request, 500, "internal_error")
    response.headers["X-Request-ID"] = request.state.request_id
    return response


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, _error: RequestValidationError):
    return error_response(request, 422, "invalid_request")


@app.exception_handler(HTTPException)
async def http_error(request: Request, error: HTTPException):
    codes: dict[int, ErrorCode] = {
        401: "unauthorized", 403: "forbidden", 404: "not_found", 405: "method_not_allowed",
    }
    return error_response(request, error.status_code, codes.get(error.status_code, "invalid_request"))

"""Build grouped, stratified classifier training data from synthetic JSONL dialogs."""

import json
import random
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/training/raw"
OUTPUT = ROOT / "data/training"
PROMPT = ROOT / "backend/app/speech/classifier_prompt.txt"
SCHEMA = ROOT / "backend/app/speech/llm_schema.json"
SEED = 20261112
LANGUAGES = ("ru", "kk", "mixed")
KINDS = ("fraud", "normal", "hard_normal")


def normalize(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def stt(text):
    return "".join(c for c in text.lower() if not unicodedata.category(c).startswith("P"))


def window(segments):
    text = "\n".join("— " + s["text"] for s in segments[-40:])
    return text[-6000:]


def validate(record, schema):
    if not isinstance(record, dict):
        return "запись должна быть объектом"
    fields = {"id", "language", "synthetic", "kind", "segments", "request_seq", "target"}
    if set(record) != fields:
        return "неверный набор полей записи"
    language, kind = record["language"], record["kind"]
    if language not in LANGUAGES or kind not in KINDS:
        return "неверный language или kind"
    if not isinstance(record["id"], str) or not re.fullmatch(rf"{language}-\d{{2}}-\d{{3}}", record["id"]):
        return "неверный id"
    if record["synthetic"] is not True:
        return "synthetic должен быть true"
    segments = record["segments"]
    if not isinstance(segments, list) or not 4 <= len(segments) <= 14:
        return "число segments должно быть от 4 до 14"
    for segment in segments:
        if (not isinstance(segment, dict) or set(segment) != {"speaker", "text"}
                or segment["speaker"] not in ("caller", "customer")
                or not isinstance(segment["text"], str) or not segment["text"].strip()):
            return "невалидная реплика"
    seq = record["request_seq"]
    if kind == "fraud":
        if type(seq) is not int or not 1 <= seq <= len(segments):
            return "неверный request_seq для fraud"
    elif seq is not None:
        return "request_seq должен быть null для обычного диалога"
    target = record["target"]
    props = schema["properties"]
    if not isinstance(target, dict) or set(target) != set(schema["required"]):
        return "неверный набор полей target"
    if target["scheme"] not in props["scheme"]["enum"]:
        return "неверный scheme"
    for key in ("active_request", "urgency", "secrecy", "safe_account_request"):
        if type(target[key]) is not bool:
            return f"{key} должен быть boolean"
    evidence = target["evidence"]
    if not isinstance(evidence, list) or len(evidence) > props["evidence"]["maxItems"]:
        return "неверный evidence"
    for item in evidence:
        if (not isinstance(item, str) or not 1 <= len(item) <= 120
                or not any(item in segment["text"] for segment in segments)):
            return "evidence не является допустимым дословным фрагментом реплики"
        if item not in window(segments):
            return "evidence отсутствует в окне модели"
    if kind != "fraud" and (target["scheme"] != "none" or target["active_request"]
                            or target["safe_account_request"] or evidence):
        return "target обычного диалога противоречит формату"
    return None


def main():
    rng = random.Random(SEED)
    prompt = PROMPT.read_text(encoding="utf-8")
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    keys = list(schema["properties"])
    groups = defaultdict(list)
    seen = set()
    skipped = 0
    accepted = Counter()
    kinds = Counter()
    for path in sorted(RAW.glob("*.jsonl")):
        with path.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, 1):
                record = None
                try:
                    record = json.loads(line)
                    reason = validate(record, schema)
                except (json.JSONDecodeError, TypeError, ValueError) as exc:
                    reason = f"невалидный JSON или поле: {exc}"
                if reason is None:
                    fingerprint = normalize("\n".join(s["text"] for s in record["segments"]))
                    if fingerprint in seen:
                        reason = "дубликат нормализованного текста"
                    else:
                        seen.add(fingerprint)
                if reason is not None:
                    skipped += 1
                    identifier = record.get("id", "?") if isinstance(record, dict) else "?"
                    print(f"Пропущено: {path.relative_to(ROOT)}:{line_number}, id={identifier}, причина: {reason}")
                    continue
                accepted[record["language"]] += 1
                kinds[record["kind"]] += 1
                groups[(record["language"], record["kind"])].append(record)

    # Allocate the validation quota across language/kind strata by largest remainder.
    total = sum(map(len, groups.values()))
    quota = round(total * 0.1)
    counts = {key: len(rows) // 10 for key, rows in groups.items()}
    order = sorted(groups, key=lambda key: (-(len(groups[key]) % 10), key))
    for key in order[:quota - sum(counts.values())]:
        counts[key] += 1
    parts = {"train": [], "val": []}
    for key in sorted(groups):
        rows = groups[key]
        rng.shuffle(rows)
        for index, record in enumerate(rows):
            part = "val" if index < counts[key] else "train"
            parts[part].append((record["segments"], record["target"]))
            if record["kind"] == "fraud" and record["request_seq"] >= 3:
                parts[part].append((record["segments"][:record["request_seq"] - 1], {
                    "scheme": "none", "active_request": False, "urgency": False,
                    "secrecy": False, "safe_account_request": False, "evidence": [],
                }))

    all_examples = [(part, index) for part, rows in parts.items() for index in range(len(rows))]
    rng.shuffle(all_examples)
    stt_examples = set(all_examples[:round(len(all_examples) * 0.2)])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for part, rows in parts.items():
        with (OUTPUT / f"{part}.jsonl").open("w", encoding="utf-8") as output:
            for index, (segments, target) in enumerate(rows):
                answer = {key: target[key] for key in keys}
                if (part, index) in stt_examples:
                    segments = [{**segment, "text": stt(segment["text"])} for segment in segments]
                    answer["evidence"] = [stt(item) for item in answer["evidence"]]
                text = window(segments)
                example = {"messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text},
                    {"role": "assistant", "content": json.dumps(answer, ensure_ascii=False, separators=(",", ":"))},
                ]}
                output.write(json.dumps(example, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"Принято диалогов: {total}; пропущено: {skipped}")
    print("По языкам: " + ", ".join(f"{key}={accepted[key]}" for key in LANGUAGES))
    print("По видам: " + ", ".join(f"{key}={kinds[key]}" for key in KINDS))
    print(f"Размеры примеров: train={len(parts['train'])}, val={len(parts['val'])}; STT={len(stt_examples)}")


if __name__ == "__main__":
    main()

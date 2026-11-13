#!/usr/bin/env python3
"""Evaluate a local classifier against the annotated JSONL dialogue set."""

import argparse
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
FIELDS = ("scheme", "active_request", "urgency", "secrecy", "safe_account_request", "evidence")
LANGUAGES = ("ru", "kk", "mixed")
KINDS = ("fraud", "normal", "hard_normal")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="Model server URL, with or without /v1")
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--data", default="data/evaluation/test.jsonl")
    parser.add_argument("--label", required=True, help="Report filename without extension")
    args = parser.parse_args()
    if args.label in (".", "..") or not args.label or any(c in args.label for c in "/\\"):
        parser.error("--label must be a filename, not a path")
    return args


def read_data(path):
    rows = []
    with path.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                if (not isinstance(row, dict) or not isinstance(row.get("id"), str)
                        or row.get("language") not in LANGUAGES or row.get("kind") not in KINDS
                        or not isinstance(row.get("segments"), list)
                        or not all(isinstance(s, dict) and isinstance(s.get("text"), str) for s in row["segments"])
                        or not isinstance(row.get("target"), dict)):
                    raise ValueError("missing or invalid dialogue fields")
                rows.append(row)
            except (ValueError, json.JSONDecodeError) as exc:
                raise ValueError(f"{path}:{number}: {exc}") from exc
    if not rows:
        raise ValueError(f"{path}: no dialogues")
    return rows


def valid_result(value, schema):
    if not isinstance(value, dict) or set(value) != set(schema["required"]):
        return False
    if value["scheme"] not in schema["properties"]["scheme"]["enum"]:
        return False
    if any(type(value[field]) is not bool for field in FIELDS[1:5]):
        return False
    evidence = value["evidence"]
    return (isinstance(evidence, list) and len(evidence) <= 3
            and all(isinstance(item, str) and 1 <= len(item) <= 120 for item in evidence))


def window(segments):
    return "\n".join("— " + segment["text"] for segment in segments[-40:])[-6000:]


def normalized(text):
    return " ".join(text.split())


def classify(base_url, model, api_key, prompt, schema, text):
    base = base_url.rstrip("/")
    endpoint = base + ("/chat/completions" if base.endswith("/v1") else "/v1/chat/completions")
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": text}],
        "temperature": 0,
        "response_format": {"type": "json_schema", "json_schema": {"name": "ShieldClassifierResult", "strict": True, "schema": schema}},
        "chat_template_kwargs": {"enable_thinking": False},
    }
    request = Request(endpoint, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                      headers={"Content-Type": "application/json", "Authorization": "Bearer " + api_key}, method="POST")
    start = time.monotonic()
    try:
        with urlopen(request, timeout=120) as response:
            body = json.loads(response.read().decode("utf-8"))
        result = json.loads(body["choices"][0]["message"]["content"])
        if not valid_result(result, schema):
            result = None
    except (HTTPError, URLError, TimeoutError, OSError, UnicodeError, ValueError, KeyError, IndexError, TypeError):
        result = None
    return result, time.monotonic() - start


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def percentile(values, p):
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * p
    lower = math.floor(position)
    upper = math.ceil(position)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def metrics(records):
    size = len(records)
    tp = fp = fn = active_correct = 0
    correct = {field: 0 for field in FIELDS[0:1] + FIELDS[2:5]}
    false_alarms = {kind: 0 for kind in ("normal", "hard_normal")}
    kind_counts = {kind: 0 for kind in false_alarms}
    evidence_found = evidence_total = evidence_valid_responses = 0
    errors = []
    for record in records:
        target, result, kind = record["target"], record["result"], record["kind"]
        expected = target["active_request"]
        invalid = result is None
        predicted = not expected if invalid else result["active_request"]
        tp += bool(expected and predicted)
        fp += bool(not expected and predicted)
        fn += bool(expected and not predicted)
        active_correct += bool(not invalid and predicted == expected)
        if kind in kind_counts:
            kind_counts[kind] += 1
            false_alarms[kind] += bool(invalid or predicted)
        for field in correct:
            correct[field] += bool(not invalid and result[field] == target[field])
        bad_evidence = False
        if not invalid:
            for fragment in result["evidence"]:
                evidence_total += 1
                found = normalized(fragment) in normalized(record["window"])
                evidence_found += bool(found)
                bad_evidence |= not found
            evidence_valid_responses += not bad_evidence
        if invalid or predicted != expected or any(result[f] != target[f] for f in correct) or bad_evidence:
            errors.append(record["id"])
    precision = ratio(tp, tp + fp)
    recall = ratio(tp, tp + fn)
    f1 = ratio(2 * tp, 2 * tp + fp + fn)
    return {
        "size": size,
        "valid_rate": ratio(sum(r["result"] is not None for r in records), size),
        "active_request_accuracy": ratio(active_correct, size),
        "active_request_precision": precision,
        "active_request_recall": recall,
        "active_request_f1": f1,
        "normal_false_alarm_rate": ratio(false_alarms["normal"], kind_counts["normal"]),
        "hard_normal_false_alarm_rate": ratio(false_alarms["hard_normal"], kind_counts["hard_normal"]),
        **{field + "_accuracy": ratio(value, size) for field, value in correct.items()},
        "evidence_found_rate": ratio(evidence_found, evidence_total),
        "evidence_valid_response_rate": ratio(evidence_valid_responses, size),
        "evidence_found_count": evidence_found,
        "evidence_count": evidence_total,
        "latency_p50_seconds": percentile([r["latency"] for r in records], 0.50),
        "latency_p95_seconds": percentile([r["latency"] for r in records], 0.95),
        "error_ids": errors,
    }


def markdown(report):
    groups = report["groups"]
    names = ("all",) + LANGUAGES
    lines = [f"# Evaluation: {report['label']}", "", f"- Date (UTC): {report['date']}",
             f"- Model: {report['model']}", f"- Dataset size: {report['dataset_size']}", "",
             "| Metric | all | ru | kk | mixed |", "|---|---:|---:|---:|---:|"]
    for metric in groups["all"]:
        if metric == "error_ids":
            continue
        values = []
        for name in names:
            value = groups[name][metric]
            values.append("—" if value is None else f"{value:.4f}" if isinstance(value, float) else str(value))
        lines.append("| " + metric + " | " + " | ".join(values) + " |")
    lines.extend(["", "Invalid responses count as errors for every field; for active_request they count as the opposite of the target. "
                  "evidence_found_rate is the share of actual evidence fragments from valid responses found in the dialogue window; "
                  "evidence_count is the number of those fragments. "
                  "evidence_valid_response_rate is the share of all responses that are valid and whose evidence fragments all occur in the window "
                  "(an empty evidence list qualifies); invalid responses are errors. Empty denominators are shown as —.", "",
                  "## Error IDs", ""])
    for name in names:
        lines.append(f"- {name}: " + (", ".join(groups[name]["error_ids"]) or "—"))
    return "\n".join(lines) + "\n"


def main():
    args = parse_args()
    prompt = (ROOT / "backend/app/speech/classifier_prompt.txt").read_text(encoding="utf-8")
    schema = json.loads((ROOT / "backend/app/speech/llm_schema.json").read_text(encoding="utf-8"))
    data_path = Path(args.data)
    rows = read_data(data_path)
    for row in rows:
        if not valid_result(row["target"], schema):
            raise ValueError(f"{data_path}: invalid target for {row['id']}")
    records = []
    for row in rows:
        text = window(row["segments"])
        result, latency = classify(args.base_url, args.model, args.api_key, prompt, schema, text)
        records.append({"id": row["id"], "language": row["language"], "kind": row["kind"],
                        "target": row["target"], "window": text, "result": result, "latency": latency})
    groups = {"all": metrics(records)}
    groups.update({language: metrics([r for r in records if r["language"] == language]) for language in LANGUAGES})
    report = {"label": args.label, "date": datetime.now(timezone.utc).isoformat(), "model": args.model,
              "dataset_size": len(rows), "groups": groups}
    reports = ROOT / "ml/eval/reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / (args.label + ".json")).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (reports / (args.label + ".md")).write_text(markdown(report), encoding="utf-8")
    print(f"Reports written: {reports / (args.label + '.json')}, {reports / (args.label + '.md')}")


if __name__ == "__main__":
    main()

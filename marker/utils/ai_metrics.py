import threading
from copy import deepcopy


_LOCK = threading.Lock()
_STATE = {
    "totals": {
        "requests": 0,
        "success": 0,
        "errors": 0,
        "retries": 0,
        "elapsed_ms": 0,
        "prompt_chars": 0,
        "response_chars": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
    },
    "sources": {},
}


def _new_source_bucket():
    return {
        "requests": 0,
        "success": 0,
        "errors": 0,
        "retries": 0,
        "elapsed_ms": 0,
        "prompt_chars": 0,
        "response_chars": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "last_error": "",
        "last_model": "",
    }


def _coerce_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _usage_to_int(usage, key):
    if not isinstance(usage, dict):
        return 0
    return _coerce_int(usage.get(key, 0))


def record_ai_event(
    source,
    event_type,
    *,
    model="",
    elapsed_ms=0,
    prompt_chars=0,
    response_chars=0,
    usage=None,
    error="",
):
    source = (source or "unknown").strip() or "unknown"
    usage = usage or {}

    with _LOCK:
        bucket = _STATE["sources"].setdefault(source, _new_source_bucket())
        totals = _STATE["totals"]

        if event_type == "request":
            bucket["requests"] += 1
            totals["requests"] += 1
        elif event_type == "retry":
            bucket["retries"] += 1
            totals["retries"] += 1
        elif event_type == "success":
            bucket["success"] += 1
            totals["success"] += 1
            bucket["elapsed_ms"] += _coerce_int(elapsed_ms)
            totals["elapsed_ms"] += _coerce_int(elapsed_ms)
            bucket["prompt_chars"] += _coerce_int(prompt_chars)
            totals["prompt_chars"] += _coerce_int(prompt_chars)
            bucket["response_chars"] += _coerce_int(response_chars)
            totals["response_chars"] += _coerce_int(response_chars)

            in_tokens = _usage_to_int(usage, "input_tokens")
            out_tokens = _usage_to_int(usage, "output_tokens")
            total_tokens = _usage_to_int(usage, "total_tokens")

            bucket["input_tokens"] += in_tokens
            bucket["output_tokens"] += out_tokens
            bucket["total_tokens"] += total_tokens

            totals["input_tokens"] += in_tokens
            totals["output_tokens"] += out_tokens
            totals["total_tokens"] += total_tokens

            bucket["last_model"] = model or bucket["last_model"]
        elif event_type == "error":
            bucket["errors"] += 1
            totals["errors"] += 1
            bucket["last_error"] = str(error or "")[:300]
            bucket["last_model"] = model or bucket["last_model"]


def reset_ai_metrics():
    with _LOCK:
        _STATE["totals"] = _new_source_bucket() | {
            "last_error": None,
            "last_model": None,
        }
        _STATE["totals"].pop("last_error", None)
        _STATE["totals"].pop("last_model", None)
        _STATE["sources"] = {}


def get_ai_metrics_snapshot():
    with _LOCK:
        data = deepcopy(_STATE)

    for src_data in data["sources"].values():
        requests = src_data["requests"]
        src_data["error_rate_pct"] = (
            round((src_data["errors"] / requests) * 100, 2) if requests else 0.0
        )
        src_data["avg_latency_ms"] = (
            round(src_data["elapsed_ms"] / src_data["success"], 2)
            if src_data["success"]
            else 0.0
        )

    totals = data["totals"]
    total_requests = totals["requests"]
    totals["error_rate_pct"] = (
        round((totals["errors"] / total_requests) * 100, 2) if total_requests else 0.0
    )
    totals["avg_latency_ms"] = (
        round(totals["elapsed_ms"] / totals["success"], 2) if totals["success"] else 0.0
    )
    return data

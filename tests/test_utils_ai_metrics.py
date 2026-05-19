from marker.utils.ai_metrics import (
    get_ai_metrics_snapshot,
    record_ai_event,
    reset_ai_metrics,
)


def setup_function():
    reset_ai_metrics()


def test_ai_metrics_aggregates_success_and_retry():
    record_ai_event("report_sql", "request", model="gemini-a")
    record_ai_event("report_sql", "retry", model="gemini-a")
    record_ai_event(
        "report_sql",
        "success",
        model="gemini-a",
        elapsed_ms=120,
        prompt_chars=10,
        response_chars=20,
        usage={"input_tokens": 3, "output_tokens": 7, "total_tokens": 10},
    )

    snapshot = get_ai_metrics_snapshot()
    totals = snapshot["totals"]
    source = snapshot["sources"]["report_sql"]

    assert totals["requests"] == 1
    assert totals["retries"] == 1
    assert totals["success"] == 1
    assert totals["errors"] == 0
    assert totals["total_tokens"] == 10
    assert totals["avg_latency_ms"] == 120.0
    assert source["last_model"] == "gemini-a"


def test_ai_metrics_records_error_rate():
    record_ai_event("company_autofill", "request")
    record_ai_event("company_autofill", "error", error="timeout")

    snapshot = get_ai_metrics_snapshot()
    source = snapshot["sources"]["company_autofill"]

    assert source["errors"] == 1
    assert source["error_rate_pct"] == 100.0
    assert source["last_error"] == "timeout"

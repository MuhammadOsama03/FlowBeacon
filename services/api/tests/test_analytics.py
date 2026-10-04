from datetime import UTC, datetime, timedelta

from app.analytics import calculate_metrics, summarize_run
from app.models import EventType, TraceEvent, TraceStatus


def event(event_id, *, seconds=0, status=TraceStatus.OK, duration=10, attributes=None):
    return TraceEvent(event_id=event_id, run_id="run-1", span_id=event_id,
        timestamp=datetime(2026, 10, 4, tzinfo=UTC) + timedelta(seconds=seconds),
        event_type=EventType.MODEL, status=status, duration_ms=duration,
        attributes=attributes or {})


def test_summary_reports_timing_and_errors():
    result = summarize_run([event("a"), event("b", seconds=2, status=TraceStatus.ERROR)])
    assert result.duration_ms == 2000
    assert result.error_count == 1
    assert result.status == TraceStatus.ERROR


def test_metrics_aggregate_latency_tokens_and_cost():
    result = calculate_metrics([event("a", attributes={"input_tokens": 12, "output_tokens": 3,
        "cost_usd": .001}), event("b", duration=20, attributes={"input_tokens": 8})])
    assert result.latency_ms == 30
    assert result.input_tokens == 20
    assert result.output_tokens == 3
    assert result.estimated_cost_usd == .001

from datetime import UTC, datetime

from app.errors import ErrorCategory, classify_error
from app.models import EventType, TraceEvent, TraceStatus


def test_classifies_rate_limit_without_exposing_message():
    event = TraceEvent(event_id="e", run_id="r", span_id="s", timestamp=datetime.now(UTC),
        event_type=EventType.MODEL, status=TraceStatus.ERROR,
        attributes={"http.status_code": 429, "error.message": "rate limit reached"})
    assert classify_error(event) == ErrorCategory.RATE_LIMIT


def test_ignores_successful_events():
    event = TraceEvent(event_id="e", run_id="r", span_id="s", timestamp=datetime.now(UTC),
        event_type=EventType.TOOL, status=TraceStatus.OK)
    assert classify_error(event) is None

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models import EventType, TraceBatch, TraceEvent, TraceStatus


def event_payload() -> dict:
    return {
        "event_id": "evt-1",
        "run_id": "run-1",
        "span_id": "span-1",
        "timestamp": datetime(2026, 10, 3, 8, 0, tzinfo=UTC),
        "event_type": EventType.TOOL,
        "status": TraceStatus.OK,
        "duration_ms": 12.5,
        "attributes": {"tool.name": "search"},
    }


def test_accepts_versioned_trace_event():
    event = TraceEvent(**event_payload())

    assert event.schema_version == "1.0"
    assert event.attributes == {"tool.name": "search"}


@pytest.mark.parametrize(
    ("field", "value"),
    [("event_id", "spaces are unsafe"), ("duration_ms", -1)],
)
def test_rejects_invalid_event_fields(field, value):
    payload = event_payload()
    payload[field] = value

    with pytest.raises(ValidationError):
        TraceEvent(**payload)


def test_requires_timezone_aware_timestamp():
    payload = event_payload()
    payload["timestamp"] = datetime(2026, 10, 3, 8, 0)

    with pytest.raises(ValidationError, match="timezone"):
        TraceEvent(**payload)


def test_batch_has_bounded_size():
    with pytest.raises(ValidationError):
        TraceBatch(events=[])


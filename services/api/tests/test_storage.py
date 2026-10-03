from datetime import UTC, datetime, timedelta

from app.models import EventType, TraceEvent, TraceStatus
from app.storage import TraceStore


def make_event(event_id: str, seconds: int = 0) -> TraceEvent:
    return TraceEvent(
        event_id=event_id,
        run_id="run-1",
        span_id=event_id,
        timestamp=datetime(2026, 10, 3, 8, 0, tzinfo=UTC) + timedelta(seconds=seconds),
        event_type=EventType.CUSTOM,
        status=TraceStatus.OK,
    )


def test_inserts_and_orders_run_events(tmp_path):
    store = TraceStore(tmp_path / "traces.db")

    assert store.insert(make_event("second", seconds=2)) is True
    assert store.insert(make_event("first", seconds=1)) is True

    assert [event.event_id for event in store.get_run("run-1")] == ["first", "second"]


def test_duplicate_event_is_idempotent(tmp_path):
    store = TraceStore(tmp_path / "traces.db")
    event = make_event("same")

    assert store.insert(event) is True
    assert store.insert(event) is False
    assert len(store.get_run("run-1")) == 1


def test_unknown_run_returns_empty_list(tmp_path):
    assert TraceStore(tmp_path / "traces.db").get_run("missing") == []


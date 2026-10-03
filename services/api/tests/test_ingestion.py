from datetime import UTC, datetime

from app.ingestion import TraceIngestor
from app.models import EventType, TraceBatch, TraceEvent, TraceStatus
from app.storage import TraceStore


def make_event(event_id: str) -> TraceEvent:
    return TraceEvent(
        event_id=event_id,
        run_id="run-1",
        span_id="span-1",
        timestamp=datetime(2026, 10, 3, 8, 0, tzinfo=UTC),
        event_type=EventType.MODEL,
        status=TraceStatus.OK,
        attributes={"api_key": "hidden", "model": "example"},
    )


def test_ingestion_redacts_before_persistence(tmp_path):
    store = TraceStore(tmp_path / "ingestion.db")
    ingestor = TraceIngestor(store)

    result = ingestor.ingest(TraceBatch(events=[make_event("event-1")]))

    assert result.accepted == 1
    persisted = store.get_run("run-1")[0]
    assert persisted.attributes == {"api_key": "[REDACTED]", "model": "example"}


def test_ingestion_reports_duplicate_events(tmp_path):
    store = TraceStore(tmp_path / "ingestion.db")
    ingestor = TraceIngestor(store)
    batch = TraceBatch(events=[make_event("event-1")])

    assert ingestor.ingest(batch).model_dump() == {"accepted": 1, "duplicates": 0}
    assert ingestor.ingest(batch).model_dump() == {"accepted": 0, "duplicates": 1}


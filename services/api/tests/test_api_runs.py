from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.dependencies import get_store
from app.main import app
from app.models import EventType, TraceEvent, TraceStatus
from app.storage import TraceStore


def make_store(tmp_path) -> TraceStore:
    store = TraceStore(tmp_path / "runs.db")
    store.insert(
        TraceEvent(
            event_id="event-1",
            run_id="run-1",
            span_id="span-1",
            timestamp=datetime(2026, 10, 3, 8, 0, tzinfo=UTC),
            event_type=EventType.RUN,
            status=TraceStatus.OK,
        )
    )
    return store


def test_returns_ordered_run_trace(tmp_path):
    store = make_store(tmp_path)
    app.dependency_overrides[get_store] = lambda: store

    try:
        response = TestClient(app).get("/v1/runs/run-1")
        assert response.status_code == 200
        assert response.json()["events"][0]["event_id"] == "event-1"
    finally:
        app.dependency_overrides.clear()


def test_unknown_run_returns_404(tmp_path):
    store = TraceStore(tmp_path / "empty.db")
    app.dependency_overrides[get_store] = lambda: store

    try:
        response = TestClient(app).get("/v1/runs/missing")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_rejects_unsafe_run_identifier():
    assert TestClient(app).get("/v1/runs/unsafe%20id").status_code == 422


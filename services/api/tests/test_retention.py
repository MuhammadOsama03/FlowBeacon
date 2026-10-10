from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.dependencies import get_store
from app.main import app
from app.models import EventType, TraceEvent, TraceStatus
from app.storage import TraceStore


def add_event(store, event_id, run_id, year):
    store.insert(TraceEvent(event_id=event_id, run_id=run_id, span_id=event_id,
        timestamp=datetime(year, 1, 1, tzinfo=UTC), event_type=EventType.CUSTOM,
        status=TraceStatus.OK))


def test_retention_deletes_only_complete_expired_runs(tmp_path):
    store = TraceStore(tmp_path / "retention.db")
    add_event(store, "old-1", "old-run", 2024)
    add_event(store, "new-1", "new-run", 2026)
    assert store.delete_runs_before(datetime(2025, 1, 1, tzinfo=UTC)) == (1, 1)
    assert store.get_run("old-run") == []
    assert len(store.get_run("new-run")) == 1


def test_retention_endpoint_requires_admin_key(monkeypatch, tmp_path):
    store = TraceStore(tmp_path / "api-retention.db")
    add_event(store, "old-1", "old-run", 2024)
    monkeypatch.setenv("FLOWBEACON_ADMIN_API_KEY", "retention-admin-secret")
    app.dependency_overrides[get_store] = lambda: store
    try:
        client = TestClient(app)
        assert client.delete("/v1/admin/runs?before=2025-01-01T00:00:00Z").status_code == 401
        response = client.delete("/v1/admin/runs?before=2025-01-01T00:00:00Z",
            headers={"Authorization": "Bearer retention-admin-secret"})
        assert response.json() == {"deleted_runs": 1, "deleted_events": 1}
    finally:
        app.dependency_overrides.clear()


def test_storage_statistics_are_admin_only(monkeypatch, tmp_path):
    store = TraceStore(tmp_path / "stats.db")
    add_event(store, "event-1", "run-1", 2026)
    monkeypatch.setenv("FLOWBEACON_ADMIN_API_KEY", "storage-admin-secret")
    app.dependency_overrides[get_store] = lambda: store
    try:
        client = TestClient(app)
        assert client.get("/v1/admin/storage").status_code == 401
        response = client.get("/v1/admin/storage",
            headers={"Authorization": "Bearer storage-admin-secret"})
        assert response.status_code == 200
        assert response.json()["run_count"] == 1
        assert response.json()["event_count"] == 1
    finally:
        app.dependency_overrides.clear()

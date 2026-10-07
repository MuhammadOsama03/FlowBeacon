from fastapi.testclient import TestClient

from app.dependencies import get_store
from app.main import app
from app.storage import TraceStore


def test_readiness_checks_persistence(tmp_path):
    store = TraceStore(tmp_path / "ready.db")
    app.dependency_overrides[get_store] = lambda: store
    try:
        response = TestClient(app).get("/ready")
        assert response.status_code == 200
        assert response.json() == {"status": "ready", "persistence": "ok"}
    finally:
        app.dependency_overrides.clear()


def test_readiness_reports_storage_failure():
    class UnavailableStore:
        def ping(self): return False
    app.dependency_overrides[get_store] = UnavailableStore
    try:
        assert TestClient(app).get("/ready").status_code == 503
    finally:
        app.dependency_overrides.clear()

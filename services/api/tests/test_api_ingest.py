from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.dependencies import get_ingestor
from app.ingestion import TraceIngestor
from app.main import app
from app.storage import TraceStore


def event_payload() -> dict:
    return {
        "event_id": "event-1",
        "run_id": "run-1",
        "span_id": "span-1",
        "timestamp": datetime(2026, 10, 3, 8, 0, tzinfo=UTC).isoformat(),
        "event_type": "tool",
        "status": "ok",
        "attributes": {"tool.name": "search"},
    }


def test_health_endpoint():
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "flowbeacon-api",
        "version": "1.1.0",
    }
    assert len(response.headers["x-request-id"]) == 32


def test_preserves_valid_request_correlation_id():
    response = TestClient(app).get("/health", headers={"X-Request-ID": "deploy-12345"})
    assert response.headers["x-request-id"] == "deploy-12345"


def test_ingests_valid_event_batch(tmp_path):
    ingestor = TraceIngestor(TraceStore(tmp_path / "api.db"))
    app.dependency_overrides[get_ingestor] = lambda: ingestor
    client = TestClient(app)

    try:
        response = client.post("/v1/events", json={"events": [event_payload()]})
        assert response.status_code == 202
        assert response.json() == {"accepted": 1, "duplicates": 0}
    finally:
        app.dependency_overrides.clear()


def test_rejects_invalid_event_batch():
    response = TestClient(app).post("/v1/events", json={"events": []})

    assert response.status_code == 422

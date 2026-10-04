from fastapi.testclient import TestClient

from app.main import app


def test_configured_ingestion_key_is_required(monkeypatch):
    monkeypatch.setenv("FLOWBEACON_INGESTION_API_KEY", "expected-secret")
    response = TestClient(app).post("/v1/events", json={"events": []})
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_valid_key_reaches_payload_validation(monkeypatch):
    monkeypatch.setenv("FLOWBEACON_INGESTION_API_KEY", "expected-secret")
    response = TestClient(app).post("/v1/events", json={"events": []},
        headers={"Authorization": "Bearer expected-secret"})
    assert response.status_code == 422


def test_development_mode_remains_backwards_compatible(monkeypatch):
    monkeypatch.delenv("FLOWBEACON_INGESTION_API_KEY", raising=False)
    response = TestClient(app).post("/v1/events", json={"events": []})
    assert response.status_code == 422

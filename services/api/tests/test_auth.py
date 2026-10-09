from fastapi.testclient import TestClient

from app.main import app
from app.auth import require_admin_key
from fastapi import HTTPException
import pytest


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


def test_admin_key_fails_closed_when_unconfigured(monkeypatch):
    monkeypatch.delenv("FLOWBEACON_ADMIN_API_KEY", raising=False)
    with pytest.raises(HTTPException) as error:
        require_admin_key(None)
    assert error.value.status_code == 503


def test_admin_key_uses_constant_time_bearer_check(monkeypatch):
    monkeypatch.setenv("FLOWBEACON_ADMIN_API_KEY", "admin-secret-value")
    require_admin_key("Bearer admin-secret-value")
    with pytest.raises(HTTPException) as error:
        require_admin_key("Bearer wrong")
    assert error.value.status_code == 401

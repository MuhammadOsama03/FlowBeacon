import pytest

from app.config import Settings


def test_production_requires_strong_ingestion_key(monkeypatch):
    monkeypatch.setenv("FLOWBEACON_ENVIRONMENT", "production")
    monkeypatch.setenv("FLOWBEACON_INGESTION_API_KEY", "short")
    with pytest.raises(ValueError, match="at least 24"):
        Settings.from_environment()


def test_parses_explicit_allowed_hosts(monkeypatch):
    monkeypatch.setenv("FLOWBEACON_ENVIRONMENT", "test")
    monkeypatch.setenv("FLOWBEACON_ALLOWED_HOSTS", "traces.example.com, localhost")
    assert Settings.from_environment().allowed_hosts == ("traces.example.com", "localhost")

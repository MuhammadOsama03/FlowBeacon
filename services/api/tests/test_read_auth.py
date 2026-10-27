from fastapi import HTTPException
from app.auth import require_read_key
from app.config import Settings
import pytest


def test_local_read_is_open_by_default(monkeypatch):
    monkeypatch.setattr(Settings, "from_environment", classmethod(lambda cls: Settings()))
    assert require_read_key() is None


def test_production_read_rejects_missing_token(monkeypatch):
    monkeypatch.setattr(Settings, "from_environment", classmethod(
        lambda cls: Settings(environment="production", read_api_key="a" * 24)))
    with pytest.raises(HTTPException) as exc:
        require_read_key()
    assert exc.value.status_code == 401


def test_production_read_accepts_valid_token(monkeypatch):
    monkeypatch.setattr(Settings, "from_environment", classmethod(
        lambda cls: Settings(environment="production", read_api_key="a" * 24)))
    assert require_read_key("Bearer " + "a" * 24) is None

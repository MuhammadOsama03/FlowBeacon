import secrets
from typing import Annotated

from fastapi import Header, HTTPException, status

from .config import Settings


def require_ingestion_key(
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    expected = Settings.from_environment().ingestion_api_key
    if expected is None:
        return
    supplied = authorization.removeprefix("Bearer ") if authorization else ""
    if not secrets.compare_digest(supplied, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ingestion credentials", headers={"WWW-Authenticate": "Bearer"})


def require_admin_key(
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    expected = Settings.from_environment().admin_api_key
    if expected is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Administrative operations are not configured")
    supplied = authorization.removeprefix("Bearer ") if authorization else ""
    if not secrets.compare_digest(supplied, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid administrative credentials", headers={"WWW-Authenticate": "Bearer"})

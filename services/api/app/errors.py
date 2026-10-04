from enum import StrEnum

from .models import TraceEvent, TraceStatus


class ErrorCategory(StrEnum):
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    PROVIDER = "provider"
    UNKNOWN = "unknown"


def classify_error(event: TraceEvent) -> ErrorCategory | None:
    if event.status != TraceStatus.ERROR:
        return None
    text = " ".join(str(event.attributes.get(key, "")) for key in ("error.type", "error.message", "http.status_code")).lower()
    if any(value in text for value in ("401", "403", "unauthorized", "authentication")):
        return ErrorCategory.AUTHENTICATION
    if "429" in text or "rate limit" in text:
        return ErrorCategory.RATE_LIMIT
    if "timeout" in text or "timed out" in text:
        return ErrorCategory.TIMEOUT
    if any(value in text for value in ("500", "502", "503", "provider")):
        return ErrorCategory.PROVIDER
    return ErrorCategory.UNKNOWN

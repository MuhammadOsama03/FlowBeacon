import re
from typing import Any


REDACTED = "[REDACTED]"
SENSITIVE_KEY = re.compile(
    r"(?i)(authorization|cookie|api[_-]?key|access[_-]?token|password|secret)"
)
INLINE_SECRET = re.compile(
    r"(?i)\b(api[_-]?key|token|password|secret)\s*[:=]\s*([^\s,;]+)"
)
GITHUB_TOKEN = re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")
MAX_ATTRIBUTE_STRING = 4_096
MAX_NESTING_DEPTH = 8


def redact_attributes(value: Any, *, depth: int = 0) -> Any:
    if depth > MAX_NESTING_DEPTH:
        return "[TRUNCATED_DEPTH]"
    if isinstance(value, dict):
        return {
            str(key): REDACTED
            if SENSITIVE_KEY.search(str(key))
            else redact_attributes(item, depth=depth + 1)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_attributes(item, depth=depth + 1) for item in value]
    if isinstance(value, str):
        cleaned = GITHUB_TOKEN.sub(REDACTED, value)
        cleaned = INLINE_SECRET.sub(lambda match: f"{match.group(1)}={REDACTED}", cleaned)
        return cleaned[:MAX_ATTRIBUTE_STRING]
    return value


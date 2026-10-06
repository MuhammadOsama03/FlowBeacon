from enum import StrEnum

from pydantic import BaseModel

from .errors import classify_error
from .evaluation import EvaluationPolicy, evaluate_run
from .models import TraceEvent


class AlertSeverity(StrEnum):
    WARNING = "warning"
    CRITICAL = "critical"


class RunAlert(BaseModel):
    code: str
    severity: AlertSeverity
    message: str


def detect_alerts(events: list[TraceEvent], policy: EvaluationPolicy) -> list[RunAlert]:
    result = evaluate_run(events, policy)
    alerts: list[RunAlert] = []
    if not result.checks["latency"]:
        alerts.append(RunAlert(code="latency_threshold", severity=AlertSeverity.WARNING,
            message="Run latency exceeded the configured threshold"))
    categories = sorted({category.value for event in events if (category := classify_error(event))})
    if not result.checks["errors"]:
        suffix = f": {', '.join(categories)}" if categories else ""
        alerts.append(RunAlert(code="error_threshold", severity=AlertSeverity.CRITICAL,
            message="Run error count exceeded the configured threshold" + suffix))
    return alerts

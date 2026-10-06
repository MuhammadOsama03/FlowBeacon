from typing import Literal

from pydantic import BaseModel, Field

from .analytics import calculate_metrics
from .models import TraceEvent, TraceStatus


class EvaluationPolicy(BaseModel):
    max_latency_ms: float = Field(default=30_000, gt=0)
    max_errors: int = Field(default=0, ge=0)


class EvaluationResult(BaseModel):
    run_id: str
    verdict: Literal["pass", "fail"]
    score: float = Field(ge=0, le=1)
    checks: dict[str, bool]


def evaluate_run(events: list[TraceEvent], policy: EvaluationPolicy) -> EvaluationResult:
    if not events:
        raise ValueError("cannot evaluate an empty run")
    metrics = calculate_metrics(events)
    checks = {
        "latency": metrics.latency_ms <= policy.max_latency_ms,
        "errors": sum(event.status == TraceStatus.ERROR for event in events) <= policy.max_errors,
    }
    passed = sum(checks.values())
    return EvaluationResult(run_id=events[0].run_id,
        verdict="pass" if passed == len(checks) else "fail",
        score=passed / len(checks), checks=checks)

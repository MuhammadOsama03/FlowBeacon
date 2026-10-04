from .models import RunMetrics, RunSummary, TraceEvent, TraceStatus


def summarize_run(events: list[TraceEvent]) -> RunSummary:
    if not events:
        raise ValueError("cannot summarize an empty run")
    started, ended = events[0].timestamp, events[-1].timestamp
    errors = sum(event.status == TraceStatus.ERROR for event in events)
    return RunSummary(
        run_id=events[0].run_id,
        started_at=started,
        ended_at=ended,
        status=TraceStatus.ERROR if errors else events[-1].status,
        event_count=len(events),
        error_count=errors,
        duration_ms=max((ended - started).total_seconds() * 1000, 0),
    )


def calculate_metrics(events: list[TraceEvent]) -> RunMetrics:
    if not events:
        raise ValueError("cannot calculate metrics for an empty run")
    latency = sum(event.duration_ms or 0 for event in events)
    model_latency = sum(
        event.duration_ms or 0 for event in events if event.event_type == "model"
    )
    input_tokens = sum(_number(event.attributes.get("input_tokens")) for event in events)
    output_tokens = sum(_number(event.attributes.get("output_tokens")) for event in events)
    cost = sum(_number(event.attributes.get("cost_usd")) for event in events)
    return RunMetrics(
        run_id=events[0].run_id,
        latency_ms=latency,
        model_latency_ms=model_latency,
        input_tokens=int(input_tokens),
        output_tokens=int(output_tokens),
        estimated_cost_usd=round(cost, 8),
    )


def _number(value: object) -> float:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else 0

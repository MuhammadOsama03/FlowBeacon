from datetime import UTC, datetime
from typing import Any

from .models import EventType, TraceBatch, TraceEvent, TraceStatus
from .otlp_models import OtlpExportRequest, OtlpSpan


def translate_otlp(request: OtlpExportRequest) -> TraceBatch:
    events = [
        _translate_span(span)
        for resource in request.resource_spans
        for scope in resource.scope_spans
        for span in scope.spans
    ]
    return TraceBatch(events=events)


def _translate_span(span: OtlpSpan) -> TraceEvent:
    attributes = {item.key: _any_value(item.value) for item in span.attributes}
    attributes["span.name"] = span.name
    if span.status.message:
        attributes["error.message"] = span.status.message
    operation = str(attributes.get("gen_ai.operation.name", "")).lower()
    event_type = EventType.MODEL if operation in {"chat", "text_completion", "embeddings"} else EventType.CUSTOM
    return TraceEvent(
        event_id=span.span_id,
        run_id=span.trace_id,
        span_id=span.span_id,
        parent_span_id=span.parent_span_id or None,
        timestamp=datetime.fromtimestamp(span.start_time_unix_nano / 1_000_000_000, UTC),
        event_type=event_type,
        status=TraceStatus.ERROR if span.status.code == 2 else TraceStatus.OK,
        duration_ms=max(span.end_time_unix_nano - span.start_time_unix_nano, 0) / 1_000_000,
        attributes=attributes,
    )


def _any_value(value: dict[str, Any]) -> Any:
    for key in ("stringValue", "intValue", "doubleValue", "boolValue"):
        if key in value:
            return value[key]
    return str(value)

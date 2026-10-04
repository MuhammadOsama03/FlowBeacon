from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


Identifier = str


class EventType(StrEnum):
    RUN = "run"
    MODEL = "model"
    TOOL = "tool"
    RETRIEVAL = "retrieval"
    CUSTOM = "custom"


class TraceStatus(StrEnum):
    STARTED = "started"
    OK = "ok"
    ERROR = "error"


class TraceEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    event_id: Identifier = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$")
    run_id: Identifier = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$")
    span_id: Identifier = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$")
    parent_span_id: Identifier | None = Field(
        default=None, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$"
    )
    timestamp: datetime
    event_type: EventType
    status: TraceStatus
    duration_ms: float | None = Field(default=None, ge=0)
    attributes: dict[str, Any] = Field(default_factory=dict)

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_include_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include a timezone")
        return value


class TraceBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    events: list[TraceEvent] = Field(min_length=1, max_length=100)


class IngestResult(BaseModel):
    accepted: int = Field(ge=0)
    duplicates: int = Field(ge=0)


class RunTrace(BaseModel):
    run_id: str
    events: list[TraceEvent]


class RunSummary(BaseModel):
    run_id: str
    started_at: datetime
    ended_at: datetime
    status: TraceStatus
    event_count: int
    error_count: int
    duration_ms: float


class RunPage(BaseModel):
    items: list[RunSummary]
    total: int
    limit: int
    offset: int


class RunMetrics(BaseModel):
    run_id: str
    latency_ms: float
    model_latency_ms: float
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float

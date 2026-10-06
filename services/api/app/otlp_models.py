from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class OtlpKeyValue(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    key: str = Field(min_length=1, max_length=256)
    value: dict[str, Any]


class OtlpStatus(BaseModel):
    model_config = ConfigDict(extra="ignore")
    code: int = Field(default=0, ge=0, le=2)
    message: str = Field(default="", max_length=2048)


class OtlpSpan(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    trace_id: str = Field(alias="traceId", pattern=r"^[A-Fa-f0-9]{32}$")
    span_id: str = Field(alias="spanId", pattern=r"^[A-Fa-f0-9]{16}$")
    parent_span_id: str | None = Field(default=None, alias="parentSpanId")
    name: str = Field(min_length=1, max_length=256)
    start_time_unix_nano: int = Field(alias="startTimeUnixNano", ge=0)
    end_time_unix_nano: int = Field(alias="endTimeUnixNano", ge=0)
    attributes: list[OtlpKeyValue] = Field(default_factory=list, max_length=128)
    status: OtlpStatus = Field(default_factory=OtlpStatus)


class OtlpScopeSpans(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    spans: list[OtlpSpan] = Field(min_length=1, max_length=100)


class OtlpResourceSpans(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    scope_spans: list[OtlpScopeSpans] = Field(alias="scopeSpans", min_length=1, max_length=20)


class OtlpExportRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    resource_spans: list[OtlpResourceSpans] = Field(alias="resourceSpans", min_length=1, max_length=20)

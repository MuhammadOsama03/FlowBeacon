"""Minimal dependency-free OTLP/HTTP example for FlowBeacon."""

import json
import os
import time
import urllib.request
import uuid


def export_model_span(*, model: str, input_tokens: int, output_tokens: int) -> None:
    started = time.time_ns()
    # Wrap the real model call here.
    ended = time.time_ns()
    payload = {"resourceSpans": [{"scopeSpans": [{"spans": [{
        "traceId": uuid.uuid4().hex,
        "spanId": uuid.uuid4().hex[:16],
        "name": "agent.model.generate",
        "startTimeUnixNano": started,
        "endTimeUnixNano": ended,
        "status": {"code": 1},
        "attributes": [
            {"key": "gen_ai.operation.name", "value": {"stringValue": "chat"}},
            {"key": "gen_ai.request.model", "value": {"stringValue": model}},
            {"key": "input_tokens", "value": {"intValue": input_tokens}},
            {"key": "output_tokens", "value": {"intValue": output_tokens}},
        ],
    }]}]}]}
    request = urllib.request.Request(
        os.getenv("FLOWBEACON_URL", "http://localhost:8000") + "/v1/otlp/v1/traces",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + os.getenv("FLOWBEACON_API_KEY", "")},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        print(response.read().decode())


if __name__ == "__main__":
    export_model_span(model="example-model", input_tokens=24, output_tokens=12)

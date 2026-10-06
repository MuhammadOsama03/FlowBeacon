import json

from fastapi.testclient import TestClient

from app.dependencies import get_ingestor, get_store
from app.ingestion import TraceIngestor
from app.main import app
from app.storage import TraceStore


TRACE_ID = "0123456789abcdef0123456789abcdef"


def otlp_payload(status=1):
    return {"resourceSpans": [{"scopeSpans": [{"spans": [{
        "traceId": TRACE_ID, "spanId": "0123456789abcdef", "name": "chat",
        "startTimeUnixNano": 1_800_000_000_000_000_000,
        "endTimeUnixNano": 1_800_000_000_025_000_000,
        "status": {"code": status, "message": "provider timeout" if status == 2 else ""},
        "attributes": [
            {"key": "gen_ai.operation.name", "value": {"stringValue": "chat"}},
            {"key": "input_tokens", "value": {"intValue": 20}},
            {"key": "authorization", "value": {"stringValue": "secret"}},
        ],
    }]}]}]}


def test_otlp_ingest_evaluate_alert_and_export(tmp_path):
    store = TraceStore(tmp_path / "integration.db")
    app.dependency_overrides[get_store] = lambda: store
    app.dependency_overrides[get_ingestor] = lambda: TraceIngestor(store)
    client = TestClient(app)
    try:
        response = client.post("/v1/otlp/v1/traces", json=otlp_payload(status=2))
        assert response.status_code == 202
        assert response.json()["accepted"] == 1
        assert store.get_run(TRACE_ID)[0].attributes["authorization"] == "[REDACTED]"

        evaluation = client.post(f"/v1/runs/{TRACE_ID}/evaluate",
            json={"max_latency_ms": 10, "max_errors": 0})
        assert evaluation.json()["verdict"] == "fail"
        assert evaluation.json()["score"] == 0

        alerts = client.post(f"/v1/runs/{TRACE_ID}/alerts",
            json={"max_latency_ms": 10, "max_errors": 0})
        assert {alert["code"] for alert in alerts.json()} == {"latency_threshold", "error_threshold"}

        exported = client.get(f"/v1/runs/{TRACE_ID}/export")
        assert exported.headers["content-type"].startswith("application/x-ndjson")
        assert json.loads(exported.text)["run_id"] == TRACE_ID
    finally:
        app.dependency_overrides.clear()


def test_rejects_malformed_otlp_identifiers():
    payload = otlp_payload()
    payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0]["traceId"] = "unsafe"
    assert TestClient(app).post("/v1/otlp/v1/traces", json=payload).status_code == 422

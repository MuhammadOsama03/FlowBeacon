"""End-to-end smoke check against a running FlowBeacon instance."""

import json
import os
import time
import urllib.request
import uuid


BASE_URL = os.getenv("FLOWBEACON_URL", "http://localhost:8000").rstrip("/")
API_KEY = os.getenv("FLOWBEACON_API_KEY", "")


def request(path: str, *, payload: dict | None = None) -> tuple[int, dict]:
    headers = {"Accept": "application/json"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode()
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    with urllib.request.urlopen(urllib.request.Request(BASE_URL + path, data=data,
        headers=headers, method="POST" if data else "GET"), timeout=5) as response:
        return response.status, json.load(response)


def main() -> None:
    assert request("/ready")[0] == 200
    run_id, event_id = f"smoke-{uuid.uuid4().hex[:12]}", uuid.uuid4().hex
    payload = {"events": [{"event_id": event_id, "run_id": run_id,
        "span_id": uuid.uuid4().hex, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event_type": "custom", "status": "ok", "attributes": {"smoke": True}}]}
    assert request("/v1/events", payload=payload)[1]["accepted"] == 1
    status, trace = request(f"/v1/runs/{run_id}")
    assert status == 200 and trace["events"][0]["event_id"] == event_id
    print(f"FlowBeacon smoke test passed for {run_id}")


if __name__ == "__main__":
    main()

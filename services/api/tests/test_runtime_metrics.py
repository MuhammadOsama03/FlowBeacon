from fastapi.testclient import TestClient

from app.main import app
from app.runtime_metrics import RuntimeMetrics


def test_metrics_registry_uses_bounded_route_labels():
    metrics = RuntimeMetrics()
    metrics.observe("GET", "/v1/runs/{run_id}", 200, 12.25)
    output = metrics.prometheus()
    assert 'route="/v1/runs/{run_id}"' in output
    assert "flowbeacon_http_requests_total" in output
    assert output.endswith("\n")


def test_metrics_endpoint_is_protected(monkeypatch):
    monkeypatch.setenv("FLOWBEACON_ADMIN_API_KEY", "metrics-admin-secret")
    client = TestClient(app)
    client.get("/health")
    assert client.get("/metrics").status_code == 401
    response = client.get("/metrics",
        headers={"Authorization": "Bearer metrics-admin-secret"})
    assert response.status_code == 200
    assert 'route="/health"' in response.text
    assert response.headers["content-type"].startswith("text/plain")

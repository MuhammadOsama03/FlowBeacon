from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_serves_dashboard_shell():
    response = client.get("/")
    assert response.status_code == 200
    assert "Trace every decision" in response.text
    assert response.headers["content-type"].startswith("text/html")


def test_serves_versioned_dashboard_assets():
    assert client.get("/assets/styles.css").status_code == 200
    script = client.get("/assets/app.js")
    assert script.status_code == 200
    assert script.headers["content-type"].startswith("text/javascript")

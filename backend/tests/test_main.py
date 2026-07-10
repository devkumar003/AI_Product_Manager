from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """
    Test that the health check endpoint returns 200 and correct payload.
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "healthy"
    assert json_data["version"] == "1.0.0"


def test_root_health_endpoint():
    """
    Test that the root-level health endpoint also works.
    """
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "healthy"
    assert json_data["version"] == "1.0.0"


def test_root_welcome():
    """
    Test that the root route returns welcome message.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to AI ProductOS" in response.json()["message"]


def test_exception_handler_middleware():
    """
    Test that exceptions are caught and standard error structure is returned.
    """
    response = client.get("/api/v1/test-error")
    assert response.status_code == 500
    json_data = response.json()

    # Assert standard structure
    assert json_data["success"] is False
    assert "error" in json_data
    assert "traceId" in json_data
    assert "message" in json_data
    assert "simulated validation error" in json_data["error"]


def test_readiness_liveness_metrics():
    # Test readiness
    ready_res = client.get("/api/v1/ready")
    assert ready_res.status_code in [
        200,
        503,
    ]  # Depending on if DB is actually connected in mock test

    # Test liveness
    live_res = client.get("/api/v1/live")
    assert live_res.status_code == 200
    assert live_res.json()["status"] == "alive"

    # Test metrics
    metrics_res = client.get("/api/v1/metrics")
    assert metrics_res.status_code == 200
    assert "api_requests_total" in metrics_res.text


def test_security_headers():
    response = client.get("/api/v1/health")
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"

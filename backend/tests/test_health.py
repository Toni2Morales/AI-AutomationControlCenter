from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AI Automation Control Center"
    assert data["status"] == "ok"
    assert isinstance(data["message"], str)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_openapi():
    response = client.get("/openapi.json")
    assert response.status_code == 200


def test_cors_allows_angular_origin():
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:4200",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:4200"

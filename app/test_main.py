from .main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "System is alive"}

def test_background_task():
    response = client.post("/test-background")
    assert response.status_code == 200
    assert response.json() == {"message": "Task scheduled"}

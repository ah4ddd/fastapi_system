from .main import app
from fastapi.testclient import TestClient


"""
TestClient
      ↓
pretends to be browser
      ↓
talks directly to FastAPI
      ↓
inside memory
"""
client = TestClient(app)

"""
TestClient
      ↓
Creates fake HTTP request
      ↓
GET /health
      ↓
Sends into FastAPI
"""
def test_read_health():
    response = client.get("/health")
    # Expected: 200. Actual: 200. PASS
    assert response.status_code == 200
    # Expected JSON = Actual JSON. PASS
    assert response.json() == {"message": "System is alive"}


def test_background_task():
    response = client.post("/test-background")
    assert response.status_code == 200
    assert response.json() == {"message": "Task scheduled"}


def test_signup():
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@gmail.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201


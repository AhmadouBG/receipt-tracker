from fastapi.testclient import TestClient
try:
    from main import app
except ImportError:
    from backend.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

if __name__ == "__main__":
    test_read_root()
    test_health_check()
    print("✅ All backend tests passed successfully!")


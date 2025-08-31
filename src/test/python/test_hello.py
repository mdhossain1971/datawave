from fastapi.testclient import TestClient
from app.main import app
from app import Constants

client = TestClient(app)

def test_hello():
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": Constants.HELLO_MESSAGE}
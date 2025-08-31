import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.db import db
import asyncio

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    asyncio.run(db.connect())
    yield
    asyncio.run(clean_users())
    asyncio.run(db.disconnect())

async def clean_users():
    async with db.acquire() as conn:
        await conn.execute("DELETE FROM users")

def test_create_user():
    response = client.post("/users", json={
        "name": "Test User",
        "email": "test@example.com"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_get_user():
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(user["email"] == "test@example.com" for user in data)

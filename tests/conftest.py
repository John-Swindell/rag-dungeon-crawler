import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def session_id(client):
    """Create a game and return its session_id."""
    response = client.post("/game/new")
    return response.json()["session_id"]

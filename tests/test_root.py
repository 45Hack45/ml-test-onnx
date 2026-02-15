from fastapi.testclient import TestClient

from main import app
from FastEmbed.config import Config

client = TestClient(app)


def test_get_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Server is running"}

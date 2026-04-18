import pytest
from fastapi.testclient import TestClient
from main import app

class TestApp:
    def test_read_root(self, client):
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_chat_endpoint(self, client):
        response = client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Test message"}
                ]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "choices" in data
        assert len(data["choices"]) == 1
import pytest
from main import app
from fastapi.testclient import TestClient

class TestQuick:
    def test_basic_chat_completion(self, client):
        response = client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Hello!"}
                ]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["object"] == "chat.completion"
        assert data["choices"][0]["message"]["content"] == "This is a mock response."

    def test_root_endpoint(self, client):
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_check(self, client):
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
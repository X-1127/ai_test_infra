import pytest
from main import app
from fastapi.testclient import TestClient

class TestSimple:
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
        assert "model" in data
        assert data["choices"][0]["message"]["content"] == "This is a mock response."
        assert data["choices"][0]["finish_reason"] == "stop"

    def test_multiple_messages(self, client):
        response = client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "system", "content": "You are helpful."},
                    {"role": "user", "content": "Hi"},
                    {"role": "assistant", "content": "Hello!"},
                    {"role": "user", "content": "How are you?"}
                ]
            }
        )
        
        assert response.status_code == 200

    def test_custom_model(self, client):
        response = client.post(
            "/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": "Test"}],
                "model": "gpt-4"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "gpt-4"

    def test_empty_messages(self, client):
        response = client.post(
            "/v1/chat/completions",
            json={"messages": []}
        )
        
        assert response.status_code == 400

    def test_root_endpoint(self, client):
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_endpoint(self, client):
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
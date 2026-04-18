import pytest
from fastapi.testclient import TestClient
from main import app

def test_chat_completions_default(client):
    response = client.post(
        "/v1/chat/completions",
        json={
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "id" in data
    assert data["object"] == "chat.completion"
    assert "choices" in data
    assert len(data["choices"]) == 1
    assert data["choices"][0]["message"]["role"] == "assistant"
    assert data["choices"][0]["message"]["content"] == "This is a mock response."
    assert data["choices"][0]["finish_reason"] == "stop"

def test_chat_completions_with_model(client):
    response = client.post(
        "/v1/chat/completions",
        json={
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "model": "gpt-4"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "gpt-4"

def test_chat_completions_multiple_messages(client):
    response = client.post(
        "/v1/chat/completions",
        json={
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"}
            ]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "choices" in data
    assert len(data["choices"]) == 1

def test_chat_completions_empty_messages(client):
    response = client.post(
        "/v1/chat/completions",
        json={
            "messages": []
        }
    )
    
    assert response.status_code == 400
    assert "Messages list cannot be empty" in response.json()["detail"]

def test_root_endpoint(client):
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "endpoints" in data

def test_health_endpoint(client):
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
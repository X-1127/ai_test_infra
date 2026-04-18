import pytest
import os
from main import app
from fastapi.testclient import TestClient

class TestManual:
    def test_root_endpoint(self, client):
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_chat_completions_default_response(self, client):
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
        assert data["choices"][0]["message"]["content"] == "This is a mock response."

    def test_chat_completions_custom_mock_response(self):
        os.environ["MOCK_RESPONSE"] = "Custom mock response for testing!"
        
        import importlib
        import main
        importlib.reload(main)
        
        client = TestClient(main.app)
        response = client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "What is the weather?"}
                ]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["choices"][0]["message"]["content"] == "Custom mock response for testing!"
        
        del os.environ["MOCK_RESPONSE"]
        importlib.reload(main)

    def test_empty_messages(self, client):
        response = client.post(
            "/v1/chat/completions",
            json={
                "messages": []
            }
        )
        
        assert response.status_code == 400
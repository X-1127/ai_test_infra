import pytest
import time
from fastapi.testclient import TestClient
from app.main import app
from app.models import DelayConfig, FaultConfig


class TestAPIEndpoints:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "endpoints" in data
    
    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_chat_completions_basic(self, client):
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
        assert data["choices"][0]["finish_reason"] == "stop"
    
    def test_chat_completions_with_model(self, client):
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
    
    def test_chat_completions_multiple_messages(self, client):
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
        data = response.json()
        assert "choices" in data
        assert len(data["choices"]) == 1
    
    def test_chat_completions_empty_messages(self, client):
        response = client.post(
            "/v1/chat/completions",
            json={"messages": []}
        )
        assert response.status_code == 400
        assert "Messages list cannot be empty" in response.json()["detail"]


class TestInjectionAPIEndpoints:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_get_injection_config_default(self, client):
        response = client.get("/v1/config/injection")
        assert response.status_code == 200
        data = response.json()
        assert "delay" in data
        assert "fault" in data
        assert data["delay"]["enabled"] is False
        assert data["fault"]["enabled"] is False
    
    def test_update_delay_config(self, client):
        response = client.put(
            "/v1/config/injection",
            json={
                "delay": {
                    "enabled": True,
                    "min_delay_ms": 100,
                    "max_delay_ms": 500
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["delay"]["enabled"] is True
        assert data["delay"]["min_delay_ms"] == 100
        assert data["delay"]["max_delay_ms"] == 500
    
    def test_update_fault_config(self, client):
        response = client.put(
            "/v1/config/injection",
            json={
                "fault": {
                    "enabled": True,
                    "fault_type": "http_error",
                    "http_status_code": 503,
                    "error_message": "Service unavailable",
                    "probability": 0.5
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["fault"]["enabled"] is True
        assert data["fault"]["fault_type"] == "http_error"
        assert data["fault"]["http_status_code"] == 503
        assert data["fault"]["probability"] == 0.5
    
    def test_update_both_configs(self, client):
        response = client.put(
            "/v1/config/injection",
            json={
                "delay": {
                    "enabled": True,
                    "min_delay_ms": 200,
                    "max_delay_ms": 800
                },
                "fault": {
                    "enabled": True,
                    "fault_type": "timeout",
                    "probability": 0.3
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["delay"]["enabled"] is True
        assert data["fault"]["enabled"] is True
        assert data["fault"]["fault_type"] == "timeout"
    
    def test_reset_injection_config(self, client):
        client.put(
            "/v1/config/injection",
            json={
                "delay": {
                    "enabled": True,
                    "min_delay_ms": 100,
                    "max_delay_ms": 500
                },
                "fault": {
                    "enabled": True,
                    "fault_type": "http_error",
                    "probability": 0.5
                }
            }
        )
        
        response = client.post("/v1/config/injection/reset")
        assert response.status_code == 200
        data = response.json()
        assert data["delay"]["enabled"] is False
        assert data["fault"]["enabled"] is False
        assert data["fault"]["fault_type"] == "none"
    
    def test_delay_injection_effect(self, client):
        client.put(
            "/v1/config/injection",
            json={
                "delay": {
                    "enabled": True,
                    "min_delay_ms": 100,
                    "max_delay_ms": 200
                }
            }
        )
        
        start_time = time.time()
        response = client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            }
        )
        end_time = time.time()
        
        assert response.status_code == 200
        delay_ms = (end_time - start_time) * 1000
        assert 100 <= delay_ms <= 300
        
        client.post("/v1/config/injection/reset")
    
    def test_fault_injection_http_error(self, client):
        client.put(
            "/v1/config/injection",
            json={
                "fault": {
                    "enabled": True,
                    "fault_type": "http_error",
                    "http_status_code": 503,
                    "error_message": "Service unavailable",
                    "probability": 1.0
                }
            }
        )
        
        response = client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            }
        )
        
        assert response.status_code == 503
        assert "Service unavailable" in response.json()["detail"]
        
        client.post("/v1/config/injection/reset")
    
    def test_fault_injection_timeout(self, client):
        client.put(
            "/v1/config/injection",
            json={
                "fault": {
                    "enabled": True,
                    "fault_type": "timeout",
                    "probability": 1.0
                }
            }
        )
        
        response = client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            }
        )
        
        assert response.status_code == 504
        
        client.post("/v1/config/injection/reset")
    
    def test_fault_injection_invalid_response(self, client):
        client.put(
            "/v1/config/injection",
            json={
                "fault": {
                    "enabled": True,
                    "fault_type": "invalid_response",
                    "probability": 1.0
                }
            }
        )
        
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
        assert "invalid" in data
        
        client.post("/v1/config/injection/reset")
    
    def test_fault_injection_empty_response(self, client):
        client.put(
            "/v1/config/injection",
            json={
                "fault": {
                    "enabled": True,
                    "fault_type": "empty_response",
                    "probability": 1.0
                }
            }
        )
        
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
        assert "choices" in data
        assert len(data["choices"]) == 0
        
        client.post("/v1/config/injection/reset")
    
    def test_fault_injection_probability(self, client):
        client.put(
            "/v1/config/injection",
            json={
                "fault": {
                    "enabled": True,
                    "fault_type": "http_error",
                    "http_status_code": 500,
                    "error_message": "Internal error",
                    "probability": 0.0
                }
            }
        )
        
        response = client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            }
        )
        
        assert response.status_code == 200
        
        client.post("/v1/config/injection/reset")
    
    def test_combined_delay_and_fault(self, client):
        client.put(
            "/v1/config/injection",
            json={
                "delay": {
                    "enabled": True,
                    "min_delay_ms": 50,
                    "max_delay_ms": 100
                },
                "fault": {
                    "enabled": True,
                    "fault_type": "http_error",
                    "http_status_code": 503,
                    "error_message": "Service unavailable",
                    "probability": 1.0
                }
            }
        )
        
        start_time = time.time()
        response = client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            }
        )
        end_time = time.time()
        
        assert response.status_code == 503
        delay_ms = (end_time - start_time) * 1000
        assert 50 <= delay_ms <= 150
        
        client.post("/v1/config/injection/reset")
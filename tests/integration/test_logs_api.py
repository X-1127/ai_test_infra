import os

# 必须在导入app之前设置环境变量
os.environ['TESTING'] = '1'

import pytest
import time
from fastapi.testclient import TestClient
from app.main import app
from app.services.log_manager import get_log_manager


class TestLogAPIEndpoints:
    @pytest.fixture(autouse=True)
    def setup(self):
        log_manager = get_log_manager()
        log_manager.clear_logs()
        yield
        log_manager.clear_logs()
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_get_logs_empty(self, client):
        response = client.get("/v1/logs")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["logs"] == []
    
    def test_get_logs_after_request(self, client):
        client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            }
        )
        
        time.sleep(0.1)
        
        response = client.get("/v1/logs")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1
        assert len(data["logs"]) >= 1
    
    def test_get_logs_by_type(self, client):
        client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            }
        )
        
        time.sleep(0.1)
        
        response = client.get("/v1/logs?log_type=request")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1
        
        for log in data["logs"]:
            assert log["type"] == "request"
    
    def test_get_logs_with_limit(self, client):
        for i in range(5):
            client.post(
                "/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "user", "content": f"Hello {i}"}
                    ]
                }
            )
        
        time.sleep(0.1)
        
        response = client.get("/v1/logs?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3
        assert data["limit"] == 3
    
    def test_get_logs_with_offset(self, client):
        for i in range(5):
            client.post(
                "/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "user", "content": f"Hello {i}"}
                    ]
                }
            )
        
        time.sleep(0.1)
        
        response = client.get("/v1/logs?offset=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert data["offset"] == 2
        assert data["limit"] == 2
    
    def test_query_logs(self, client):
        client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            }
        )
        
        time.sleep(0.1)
        
        response = client.post(
            "/v1/logs/query",
            json={
                "log_type": "request",
                "limit": 10
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1
    
    def test_search_logs(self, client):
        client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            }
        )
        
        time.sleep(0.1)
        
        response = client.post(
            "/v1/logs/search",
            json={
                "keyword": "chat",
                "limit": 10
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1
    
    def test_search_logs_by_type(self, client):
        client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            }
        )
        
        time.sleep(0.1)
        
        response = client.post(
            "/v1/logs/search",
            json={
                "keyword": "chat",
                "log_type": "request",
                "limit": 10
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1
        
        for log in data["logs"]:
            assert log["type"] == "request"
    
    def test_get_log_stats(self, client):
        client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            }
        )
        
        time.sleep(0.1)
        
        response = client.get("/v1/logs/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_logs" in data
        assert "by_type" in data
        assert "recent_errors" in data
        assert "avg_response_time" in data
        assert data["total_logs"] >= 1
    
    def test_clear_logs(self, client):
        client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            }
        )
        
        time.sleep(0.1)
        
        response = client.delete("/v1/logs")
        assert response.status_code == 200
        
        response = client.get("/v1/logs")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
    
    def test_get_log_file_path(self, client):
        response = client.get("/v1/logs/file/request")
        assert response.status_code == 200
        data = response.json()
        assert "file_path" in data
        assert "request.log" in data["file_path"]
    
    def test_get_log_file_path_invalid_type(self, client):
        response = client.get("/v1/logs/file/invalid")
        assert response.status_code == 400
    
    def test_log_includes_request_details(self, client):
        client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            }
        )
        
        time.sleep(0.1)
        
        response = client.get("/v1/logs?log_type=request")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1
        
        log = data["logs"][0]
        assert "timestamp" in log
        assert "type" in log
        assert "method" in log
        assert "path" in log
        assert "status_code" in log
        assert "duration_ms" in log
    
    def test_multiple_requests_create_multiple_logs(self, client):
        for i in range(3):
            client.post(
                "/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "user", "content": f"Hello {i}"}
                    ]
                }
            )
        
        time.sleep(0.1)
        
        response = client.get("/v1/logs")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 3
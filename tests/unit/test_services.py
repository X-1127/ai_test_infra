import pytest
from app.services.mock_service import MockService
from app.config import settings


class TestMockService:
    def test_get_mock_response_default(self):
        service = MockService()
        response = service.get_mock_response()
        assert response == settings.mock_response
    
    def test_set_mock_response(self):
        service = MockService()
        custom_response = "Custom response"
        service.set_mock_response(custom_response)
        assert service.get_mock_response() == custom_response
    
    def test_reset_mock_response(self):
        service = MockService()
        service.set_mock_response("Custom response")
        service.reset_mock_response()
        assert service.get_mock_response() == settings.mock_response
import pytest
import asyncio
from app.services.mock_service import MockService
from app.config import settings
from app.models import DelayConfig, FaultConfig


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
    
    def test_delay_config_default(self):
        service = MockService()
        config = service.get_delay_config()
        assert config.enabled is False
        assert config.min_delay_ms == 0
        assert config.max_delay_ms == 1000
    
    def test_update_delay_config(self):
        service = MockService()
        new_config = DelayConfig(enabled=True, min_delay_ms=100, max_delay_ms=500)
        service.update_delay_config(new_config)
        config = service.get_delay_config()
        assert config.enabled is True
        assert config.min_delay_ms == 100
        assert config.max_delay_ms == 500
    
    @pytest.mark.asyncio
    async def test_apply_delay_disabled(self):
        service = MockService()
        config = DelayConfig(enabled=False)
        service.update_delay_config(config)
        
        start_time = asyncio.get_event_loop().time()
        await service.apply_delay()
        end_time = asyncio.get_event_loop().time()
        
        assert (end_time - start_time) < 0.1
    
    @pytest.mark.asyncio
    async def test_apply_delay_enabled(self):
        service = MockService()
        config = DelayConfig(enabled=True, min_delay_ms=100, max_delay_ms=200)
        service.update_delay_config(config)
        
        start_time = asyncio.get_event_loop().time()
        await service.apply_delay()
        end_time = asyncio.get_event_loop().time()
        
        delay_ms = (end_time - start_time) * 1000
        assert 100 <= delay_ms <= 300
    
    def test_fault_config_default(self):
        service = MockService()
        config = service.get_fault_config()
        assert config.enabled is False
        assert config.fault_type == "none"
        assert config.http_status_code == 500
        assert config.error_message == "Internal server error"
        assert config.probability == 1.0
    
    def test_update_fault_config(self):
        service = MockService()
        new_config = FaultConfig(
            enabled=True,
            fault_type="http_error",
            http_status_code=503,
            error_message="Service unavailable",
            probability=0.5
        )
        service.update_fault_config(new_config)
        config = service.get_fault_config()
        assert config.enabled is True
        assert config.fault_type == "http_error"
        assert config.http_status_code == 503
        assert config.error_message == "Service unavailable"
        assert config.probability == 0.5
    
    def test_should_inject_fault_disabled(self):
        service = MockService()
        config = FaultConfig(enabled=False)
        service.update_fault_config(config)
        assert service.should_inject_fault() is False
    
    def test_should_inject_fault_enabled_probability_1(self):
        service = MockService()
        config = FaultConfig(enabled=True, probability=1.0)
        service.update_fault_config(config)
        assert service.should_inject_fault() is True
    
    def test_should_inject_fault_enabled_probability_0(self):
        service = MockService()
        config = FaultConfig(enabled=True, probability=0.0)
        service.update_fault_config(config)
        assert service.should_inject_fault() is False
    
    def test_get_fault_details(self):
        service = MockService()
        config = FaultConfig(
            enabled=True,
            fault_type="http_error",
            http_status_code=503,
            error_message="Service unavailable"
        )
        service.update_fault_config(config)
        fault_type, status_code, error_message = service.get_fault_details()
        assert fault_type == "http_error"
        assert status_code == 503
        assert error_message == "Service unavailable"
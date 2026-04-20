import os
import random
import asyncio
from typing import Optional
from app.config import settings
from app.models import DelayConfig, FaultConfig
from app.services.response_config_manager import ResponseConfigManager


class MockService:
    def __init__(self):
        self.mock_response = settings.mock_response
        self.delay_config = DelayConfig()
        self.fault_config = FaultConfig()
        # 自动根据环境选择配置文件
        self.response_config_manager = ResponseConfigManager()
        self.use_yaml_config = False
    
    def get_mock_response(self, user_input: Optional[str] = None) -> str:
        if self.use_yaml_config and user_input:
            return self.response_config_manager.get_response(user_input)
        return self.mock_response
    
    def set_mock_response(self, response: str) -> None:
        self.mock_response = response
    
    def reset_mock_response(self) -> None:
        self.mock_response = settings.mock_response
    
    def set_use_yaml_config(self, use_yaml: bool) -> None:
        self.use_yaml_config = use_yaml
    
    def get_use_yaml_config(self) -> bool:
        return self.use_yaml_config
    
    def reload_yaml_config(self) -> None:
        self.response_config_manager.reload_config()
    
    def get_yaml_config(self):
        return self.response_config_manager.get_config()
    
    def update_delay_config(self, config: DelayConfig) -> None:
        self.delay_config = config
    
    def get_delay_config(self) -> DelayConfig:
        return self.delay_config
    
    def update_fault_config(self, config: FaultConfig) -> None:
        self.fault_config = config
    
    def get_fault_config(self) -> FaultConfig:
        return self.fault_config
    
    async def apply_delay(self) -> None:
        if self.delay_config.enabled:
            delay_ms = random.uniform(self.delay_config.min_delay_ms, self.delay_config.max_delay_ms)
            await asyncio.sleep(delay_ms / 1000)
    
    def should_inject_fault(self) -> bool:
        if not self.fault_config.enabled:
            return False
        return random.random() < self.fault_config.probability
    
    def get_fault_details(self) -> tuple:
        return (
            self.fault_config.fault_type,
            self.fault_config.http_status_code,
            self.fault_config.error_message
        )
    
    def reset_all(self) -> None:
        """重置所有配置到初始状态"""
        self.mock_response = settings.mock_response
        self.delay_config = DelayConfig()
        self.fault_config = FaultConfig()
        self.use_yaml_config = False
        # 重新加载配置（会自动根据环境选择配置文件）
        self.response_config_manager = ResponseConfigManager()
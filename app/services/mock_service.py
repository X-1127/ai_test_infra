import os
import random
import asyncio
from typing import Optional
from app.config import settings
from app.models import DelayConfig, FaultConfig


class MockService:
    def __init__(self):
        self.mock_response = settings.mock_response
        self.delay_config = DelayConfig()
        self.fault_config = FaultConfig()
    
    def get_mock_response(self) -> str:
        return self.mock_response
    
    def set_mock_response(self, response: str) -> None:
        self.mock_response = response
    
    def reset_mock_response(self) -> None:
        self.mock_response = settings.mock_response
    
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
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    app_name: str = "Mock LLM Server"
    app_version: str = "1.0.0"
    
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    mock_response: str = "This is a mock response."
    
    log_level: str = "INFO"
    log_format: str = "json"
    
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    testing: bool = False

    @field_validator('debug', 'rate_limit_enabled', 'testing', mode='before')
    @classmethod
    def parse_bool(cls, v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return bool(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
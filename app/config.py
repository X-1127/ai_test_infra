import os
import sys
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

# 检测是否在打包环境中运行
IS_FROZEN = getattr(sys, 'frozen', False)
if IS_FROZEN:
    # 打包环境
    APPLICATION_PATH = os.path.dirname(sys.executable)
else:
    # 开发环境
    APPLICATION_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
    
    # 添加应用路径
    application_path: str = APPLICATION_PATH
    
    def get_log_dir(self) -> str:
        """获取日志目录路径"""
        if self.testing:
            return os.path.join(self.application_path, "logs_test")
        else:
            return os.path.join(self.application_path, "logs")
    
    def get_config_dir(self) -> str:
        """获取配置目录路径"""
        return os.path.join(self.application_path, "config")

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
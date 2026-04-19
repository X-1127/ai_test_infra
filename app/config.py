import os
from typing import Optional


class Settings:
    def __init__(self):
        self.app_name = os.getenv("APP_NAME", "Mock LLM Server")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        self.mock_response = os.getenv("MOCK_RESPONSE", "This is a mock response.")
        
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = os.getenv("LOG_FORMAT", "json")
        
        self.rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "60"))


settings = Settings()
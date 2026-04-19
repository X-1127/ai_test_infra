import os
from typing import Optional
from app.config import settings


class MockService:
    def __init__(self):
        self.mock_response = settings.mock_response
    
    def get_mock_response(self) -> str:
        return self.mock_response
    
    def set_mock_response(self, response: str) -> None:
        self.mock_response = response
    
    def reset_mock_response(self) -> None:
        self.mock_response = settings.mock_response
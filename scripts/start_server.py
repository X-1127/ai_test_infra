import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from app.main import app
from app.config import settings


def start_server():
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Mock response: {settings.mock_response}")
    print(f"Server will be available at: http://{settings.host}:{settings.port}")
    print(f"API docs: http://{settings.host}:{settings.port}/docs")
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="debug" if settings.debug else "info",
        reload=settings.debug
    )


if __name__ == "__main__":
    start_server()
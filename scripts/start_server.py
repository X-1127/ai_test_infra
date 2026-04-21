import sys
import os
import argparse

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from app.main import app
from app.config import settings


def start_server(host=None, port=None):
    """启动服务器"""
    # 使用命令行参数覆盖配置
    server_host = host if host is not None else settings.host
    server_port = port if port is not None else settings.port
    
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Mock response: {settings.mock_response}")
    print(f"Server will be available at: http://{server_host}:{server_port}")
    print(f"API docs: http://{server_host}:{server_port}/docs")
    
    uvicorn.run(
        app,
        host=server_host,
        port=server_port,
        log_level="debug" if settings.debug else "info",
        reload=False
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start LLM Mock Server')
    parser.add_argument('--host', type=str, default=None, help='Host to bind to')
    parser.add_argument('--port', type=int, default=None, help='Port to bind to')
    
    args = parser.parse_args()
    
    start_server(host=args.host, port=args.port)
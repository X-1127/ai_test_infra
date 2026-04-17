@echo off
cd /d D:\X-1127\vibecoding\llm-mock-server\server
echo Starting Mock LLM Server...
echo.
set MOCK_RESPONSE=This is a mock response.
set PORT=8000
set HOST=0.0.0.0
..\venv\Scripts\python.exe main.py
pause
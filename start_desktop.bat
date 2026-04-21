@echo off
chcp 65001 >nul
echo ====================================
echo LLM Mock Server 桌面应用启动器
echo ====================================
echo.

python desktop\main.py

if errorlevel 1 (
    echo.
    echo 启动失败！请检查：
    echo 1. Python 是否已安装
    echo 2. PyQt6 是否已安装（运行: pip install -e .[desktop]）
    echo 3. 是否在正确的目录中
    echo.
    pause
)
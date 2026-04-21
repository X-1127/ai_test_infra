@echo off
chcp 65001 > nul
echo ========================================
echo LLM Mock Server Build Script
echo ========================================
echo.

REM Check Python environment
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found, please install Python 3.13+
    pause
    exit /b 1
)

echo [1/6] Checking Python environment... OK
echo.

REM Check virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo [2/6] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [2/6] Creating virtual environment... OK
) else (
    echo [2/6] Virtual environment exists... OK
)
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat
echo [3/6] Activating virtual environment... OK
echo.

REM Install dependencies
echo [4/6] Installing project dependencies...
pip install -e ".[desktop,build]" --upgrade
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo [4/6] Installing project dependencies... OK
echo.

REM Clean old build files
echo [5/6] Cleaning old build files...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
echo [5/6] Cleaning old build files... OK
echo.

REM Start building
echo [6/6] Starting build (this may take several minutes)...
echo.
pyinstaller --clean build.spec
if errorlevel 1 (
    echo.
    echo Error: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Executable location: dist\LLM_Mock_Server.exe
echo.
echo You can distribute dist\LLM_Mock_Server.exe to other users
echo Users can run it directly without installing Python
echo.
pause
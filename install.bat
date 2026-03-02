@echo off
echo ==========================================
echo 6-DOF Robotic Arm - Installation Script
echo ==========================================

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo.
    echo To install Python via command line (Windows 10/11), run:
    echo     winget install Python.Python.3
    echo.
    echo Or download it from: https://www.python.org/downloads/
    echo (Make sure to check "Add Python to PATH" during installation)
    echo.
    pause
    exit /b
)

echo [INFO] Python is installed.
echo [INFO] Installing required libraries...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install libraries.
    pause
    exit /b
)

echo.
echo [SUCCESS] All dependencies installed!
echo You can now run the software with: python software/gui_control.py
echo.
pause

@echo off
setlocal
title 6-DOF Robot Arm Controller

REM Change directory to the location of this script to ensure relative paths work
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found!
    echo Please run 'install.bat' first or install Python manually.
    pause
    exit /b 1
)

echo [INFO] Starting Robot Arm Controller...
echo [INFO] Script: software\gui_control.py
echo.

python "software\gui_control.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The application crashed or closed with an error.
    pause
)

endlocal

@echo off
setlocal

cd /d "%~dp0"
title Post Manager Web UI

set "PYTHON_CMD="
if exist "%~dp0.venv\Scripts\python.exe" set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"
if not defined PYTHON_CMD if exist "%~dp0venv\Scripts\python.exe" set "PYTHON_CMD=%~dp0venv\Scripts\python.exe"
if not defined PYTHON_CMD where python >nul 2>nul && set "PYTHON_CMD=python"
if not defined PYTHON_CMD py -3.10 -c "import sys" >nul 2>nul && set "PYTHON_CMD=py -3.10"
if not defined PYTHON_CMD where py >nul 2>nul && set "PYTHON_CMD=py -3"

if not defined PYTHON_CMD (
    echo Python was not found.
    echo Install Python or create a venv in this folder.
    pause
    exit /b 1
)

echo ========================================
echo   Post Manager - Web UI
echo ========================================
echo Starting server...
echo Open: http://127.0.0.1:8000/
echo Press Ctrl+C to stop.
echo.

call %PYTHON_CMD% src\api_server.py
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Server exited with error code %EXIT_CODE%.
    echo Run debug-start_webui.bat for more details.
    pause
)

exit /b %EXIT_CODE%

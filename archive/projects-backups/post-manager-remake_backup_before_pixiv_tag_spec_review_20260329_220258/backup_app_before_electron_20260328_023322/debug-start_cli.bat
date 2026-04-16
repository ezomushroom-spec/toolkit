@echo on
setlocal

cd /d "%~dp0"
title Post Manager CLI Debug

set "PYTHON_CMD="
if exist "%~dp0.venv\Scripts\python.exe" set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"
if not defined PYTHON_CMD if exist "%~dp0venv\Scripts\python.exe" set "PYTHON_CMD=%~dp0venv\Scripts\python.exe"
if not defined PYTHON_CMD where python >nul 2>nul && set "PYTHON_CMD=python"
if not defined PYTHON_CMD py -3.10 -c "import sys" >nul 2>nul && set "PYTHON_CMD=py -3.10"
if not defined PYTHON_CMD where py >nul 2>nul && set "PYTHON_CMD=py -3"

echo Working directory: %CD%
echo Python command: %PYTHON_CMD%

if not defined PYTHON_CMD (
    echo Python was not found.
    pause
    exit /b 1
)

call %PYTHON_CMD% --version
call %PYTHON_CMD% src\manager.py
echo Exit code: %ERRORLEVEL%
pause

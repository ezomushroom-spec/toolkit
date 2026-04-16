@echo off
cd /d "%~dp0"
setlocal

set "LOG_FILE=%~dp0startup_error.log"
set "PYTHON_EXE="

if exist "%~dp0.venv\Scripts\python.exe" set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not defined PYTHON_EXE if exist "%~dp0venv\Scripts\python.exe" set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"
if not defined PYTHON_EXE if exist "%LocalAppData%\Programs\Python\Python310\python.exe" set "PYTHON_EXE=%LocalAppData%\Programs\Python\Python310\python.exe"
if not defined PYTHON_EXE set "PYTHON_EXE=python"

echo debug start > "%LOG_FILE%"
echo python=%PYTHON_EXE% >> "%LOG_FILE%"
"%PYTHON_EXE%" "%~dp0main.py" >> "%LOG_FILE%" 2>&1

echo.
echo Log file: "%LOG_FILE%"
type "%LOG_FILE%"
pause

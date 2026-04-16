@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD="
set "CHECK_ONLY=0"

if /i "%~1"=="--check" set "CHECK_ONLY=1"

if exist ".venv\Scripts\python.exe" set "PYTHON_CMD=.venv\Scripts\python.exe"
if not defined PYTHON_CMD if exist "venv\Scripts\python.exe" set "PYTHON_CMD=venv\Scripts\python.exe"

if not defined PYTHON_CMD (
  py -3.10 -c "import sys" >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=py -3.10"
)

if not defined PYTHON_CMD (
  where python >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
  echo Python 3.10 was not found.
  pause
  exit /b 1
)

%PYTHON_CMD% -c "import PySide6, numpy, PIL, cv2" >nul 2>nul
if errorlevel 1 (
  echo Installing dependencies...
  %PYTHON_CMD% -m pip install -r requirements.txt
  if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
  )
)

if "%CHECK_ONLY%"=="1" (
  echo Launcher check passed.
  exit /b 0
)

%PYTHON_CMD% -m app.main
if errorlevel 1 (
  echo Failed to start the app.
  pause
  exit /b 1
)

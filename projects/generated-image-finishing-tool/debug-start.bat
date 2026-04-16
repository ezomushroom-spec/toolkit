@echo off
setlocal
cd /d "%~dp0"

set "LOG_FILE=%~dp0startup.log"
set "PYTHON_CMD="
set "CHECK_ONLY=0"

if /i "%~1"=="--check" set "CHECK_ONLY=1"

echo ==== debug start ==== > "%LOG_FILE%"
echo cwd=%cd% >> "%LOG_FILE%"

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

echo python_cmd=%PYTHON_CMD% >> "%LOG_FILE%"

if not defined PYTHON_CMD (
  echo Python 3.10 was not found. >> "%LOG_FILE%"
  type "%LOG_FILE%"
  pause
  exit /b 1
)

echo checking imports... >> "%LOG_FILE%"
%PYTHON_CMD% -c "import PySide6, numpy, PIL, cv2" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo installing requirements... >> "%LOG_FILE%"
  %PYTHON_CMD% -m pip install -r requirements.txt >> "%LOG_FILE%" 2>&1
  if errorlevel 1 (
    echo dependency install failed >> "%LOG_FILE%"
    type "%LOG_FILE%"
    pause
    exit /b 1
  )
)

if "%CHECK_ONLY%"=="1" (
  echo launcher_check=passed >> "%LOG_FILE%"
  type "%LOG_FILE%"
  pause
  exit /b 0
)

echo starting app... >> "%LOG_FILE%"
%PYTHON_CMD% -m app.main >> "%LOG_FILE%" 2>&1
set "EXIT_CODE=%ERRORLEVEL%"
echo exit_code=%EXIT_CODE% >> "%LOG_FILE%"
type "%LOG_FILE%"
pause
exit /b %EXIT_CODE%

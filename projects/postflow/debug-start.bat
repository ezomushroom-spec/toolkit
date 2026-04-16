@echo off
setlocal
cd /d "%~dp0"

set "LOG_FILE=%CD%\startup.log"
set "PYTHON_EXE="

break > "%LOG_FILE%"
echo [INFO] cwd=%CD%>> "%LOG_FILE%"

if exist ".venv\Scripts\python.exe" (
  set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"
  echo [INFO] using project .venv>> "%LOG_FILE%"
)

if not defined PYTHON_EXE if exist "venv\Scripts\python.exe" (
  set "PYTHON_EXE=%CD%\venv\Scripts\python.exe"
  echo [INFO] using project venv>> "%LOG_FILE%"
)

if not defined PYTHON_EXE if exist "C:\Users\ezomu\AppData\Local\Programs\Python\Python310\python.exe" (
  set "PYTHON_EXE=C:\Users\ezomu\AppData\Local\Programs\Python\Python310\python.exe"
  echo [INFO] using Python310>> "%LOG_FILE%"
)

if not defined PYTHON_EXE (
  where python >> "%LOG_FILE%" 2>&1
  if errorlevel 1 (
    echo [ERROR] python was not found.>> "%LOG_FILE%"
    type "%LOG_FILE%"
    pause
    exit /b 1
  )
  for /f "delims=" %%I in ('where python') do (
    set "PYTHON_EXE=%%I"
    goto :python_found
  )
)

:python_found
echo [INFO] python=%PYTHON_EXE%>> "%LOG_FILE%"

if not exist "%PYTHON_EXE%" (
  echo [ERROR] python executable does not exist.>> "%LOG_FILE%"
  type "%LOG_FILE%"
  pause
  exit /b 1
)

echo [INFO] checking PySide6>> "%LOG_FILE%"
call "%PYTHON_EXE%" -c "import PySide6; print('PySide6 OK')" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo [ERROR] PySide6 import failed.>> "%LOG_FILE%"
  type "%LOG_FILE%"
  pause
  exit /b 1
)

echo [INFO] starting app>> "%LOG_FILE%"
call "%PYTHON_EXE%" "app\app.py" >> "%LOG_FILE%" 2>&1
set "EXIT_CODE=%ERRORLEVEL%"
echo [INFO] exit_code=%EXIT_CODE%>> "%LOG_FILE%"

type "%LOG_FILE%"
pause
exit /b %EXIT_CODE%

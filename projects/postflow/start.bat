@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_EXE="
set "PYTHONW_EXE="

if exist ".venv\Scripts\python.exe" (
  set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"
  if exist ".venv\Scripts\pythonw.exe" set "PYTHONW_EXE=%CD%\.venv\Scripts\pythonw.exe"
)

if not defined PYTHON_EXE if exist "venv\Scripts\python.exe" (
  set "PYTHON_EXE=%CD%\venv\Scripts\python.exe"
  if exist "venv\Scripts\pythonw.exe" set "PYTHONW_EXE=%CD%\venv\Scripts\pythonw.exe"
)

if not defined PYTHON_EXE if exist "C:\Users\ezomu\AppData\Local\Programs\Python\Python310\python.exe" (
  set "PYTHON_EXE=C:\Users\ezomu\AppData\Local\Programs\Python\Python310\python.exe"
)

if not defined PYTHONW_EXE if exist "C:\Users\ezomu\AppData\Local\Programs\Python\Python310\pythonw.exe" (
  set "PYTHONW_EXE=C:\Users\ezomu\AppData\Local\Programs\Python\Python310\pythonw.exe"
)

if not defined PYTHON_EXE (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python was not found.
    echo Run debug-start.bat for details.
    pause
    exit /b 1
  )
  for /f "delims=" %%I in ('where python') do (
    set "PYTHON_EXE=%%I"
    goto :python_found
  )
)

:python_found
if not defined PYTHONW_EXE (
  set "PYTHONW_EXE=%PYTHON_EXE:python.exe=pythonw.exe%"
)

if not exist "%PYTHON_EXE%" (
  echo Python executable was not found.
  echo Run debug-start.bat for details.
  pause
  exit /b 1
)

if exist "%PYTHONW_EXE%" (
  start "" "%PYTHONW_EXE%" "app\app.py"
  exit /b 0
)

call "%PYTHON_EXE%" "app\app.py"
if errorlevel 1 (
  echo Failed to start PostFlow.
  echo Run debug-start.bat for details.
  pause
  exit /b 1
)

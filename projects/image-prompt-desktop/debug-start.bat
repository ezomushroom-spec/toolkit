@echo off
cd /d "%~dp0"

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

echo Python:
"%PYTHON_EXE%" -c "import sys; print(sys.executable)"
echo.
echo PySide6 import:
"%PYTHON_EXE%" -c "import PySide6; print('PySide6 ok')"
echo.
echo Start app:
"%PYTHON_EXE%" main.py
pause

@echo on
setlocal

cd /d "%~dp0"
title Post Manager Pixiv Tag Collection Debug

set "PYTHON_CMD="
if exist "%~dp0.venv\Scripts\python.exe" set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"
if not defined PYTHON_CMD if exist "%~dp0venv\Scripts\python.exe" set "PYTHON_CMD=%~dp0venv\Scripts\python.exe"
if not defined PYTHON_CMD where python >nul 2>nul && set "PYTHON_CMD=python"
if not defined PYTHON_CMD py -3.10 -c "import sys" >nul 2>nul && set "PYTHON_CMD=py -3.10"
if not defined PYTHON_CMD where py >nul 2>nul && set "PYTHON_CMD=py -3"

echo Working directory: %CD%
echo Python command: %PYTHON_CMD%
echo Arguments: %*

if not defined PYTHON_CMD (
    echo Python was not found.
    pause
    exit /b 1
)

call %PYTHON_CMD% --version

if "%~1"=="" (
    echo.
    echo Usage examples:
    echo   add raw:
    echo   debug-start_pixiv_tag_collection.bat add-raw --source-type search --source-key "r18-girl" --tag "R-18" --tag "girl"
    echo.
    echo   build review:
    echo   debug-start_pixiv_tag_collection.bat build-review
    echo.
    call %PYTHON_CMD% src\pixiv_popular_tag_collection.py --help
    echo Exit code: 0
    pause
    exit /b 0
)

call %PYTHON_CMD% src\pixiv_popular_tag_collection.py %*
echo Exit code: %ERRORLEVEL%
pause

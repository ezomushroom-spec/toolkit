@echo off
setlocal

cd /d "%~dp0"
title Post Manager Pixiv Tag Collection

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
echo   Post Manager - Pixiv Tag Collection
echo ========================================
echo.

if "%~1"=="" (
    echo Usage examples:
    echo   add raw:
    echo   start_pixiv_tag_collection.bat add-raw --source-type search --source-key "r18-girl" --tag "R-18" --tag "girl"
    echo.
    echo   build review:
    echo   start_pixiv_tag_collection.bat build-review
    echo.
    call %PYTHON_CMD% src\pixiv_popular_tag_collection.py --help
    pause
    exit /b 0
)

call %PYTHON_CMD% src\pixiv_popular_tag_collection.py %*
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Pixiv tag collection exited with error code %EXIT_CODE%.
    echo Run debug-start_pixiv_tag_collection.bat for more details.
    pause
)

exit /b %EXIT_CODE%

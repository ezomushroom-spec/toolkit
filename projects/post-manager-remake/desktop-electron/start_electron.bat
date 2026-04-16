@echo off
setlocal

cd /d "%~dp0"
title Post Manager Electron

where npm >nul 2>nul
if errorlevel 1 (
    echo npm was not found.
    echo Install Node.js first.
    pause
    exit /b 1
)

if not exist "%~dp0node_modules\electron" (
    echo Installing Electron dependencies...
    call npm install
    if errorlevel 1 (
        echo npm install failed.
        pause
        exit /b 1
    )
)

call npm start
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Electron exited with error code %EXIT_CODE%.
    pause
)

exit /b %EXIT_CODE%

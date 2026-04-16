@echo off
setlocal

cd /d "%~dp0"
title Post Manager Electron Migration Prep

echo ========================================
echo   Post Manager Electron Migration Prep
echo ========================================
echo.

call "%~dp0create_app_backup.bat"
if errorlevel 1 (
    echo Backup step failed.
    pause
    exit /b 1
)

echo.
echo Moving to desktop-electron...
cd /d "%~dp0desktop-electron"

where npm >nul 2>nul
if errorlevel 1 (
    echo npm was not found.
    echo Install Node.js first.
    pause
    exit /b 1
)

if not exist "%~dp0desktop-electron\node_modules\electron" (
    echo Installing Electron dependencies...
    call npm install
    if errorlevel 1 (
        echo npm install failed.
        pause
        exit /b 1
    )
)

echo.
echo Starting Electron shell...
call npm start
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Electron exited with error code %EXIT_CODE%.
    echo Check desktop-electron\runtime\backend.log if the backend failed to start.
    pause
)

exit /b %EXIT_CODE%

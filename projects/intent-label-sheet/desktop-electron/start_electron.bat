@echo off
setlocal
cd /d "%~dp0"
title Intent Label Sheet Desktop

set "PROJECT_ROOT=%~dp0.."

where npm >nul 2>nul
if errorlevel 1 (
    echo npm was not found.
    echo Install Node.js first.
    pause
    exit /b 1
)

if not exist "%PROJECT_ROOT%\node_modules" (
    echo Installing frontend dependencies...
    call npm install --prefix "%PROJECT_ROOT%"
    if errorlevel 1 (
        echo Frontend dependency install failed.
        pause
        exit /b 1
    )
)

if not exist "node_modules\electron" (
    echo Installing desktop shell dependencies...
    call npm install
    if errorlevel 1 (
        echo Desktop shell dependency install failed.
        pause
        exit /b 1
    )
)

echo Building frontend...
call npm run build:web --prefix "%PROJECT_ROOT%"
if errorlevel 1 (
    echo Frontend build failed.
    pause
    exit /b 1
)

call npm start
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Electron exited with error code %EXIT_CODE%.
    pause
)

exit /b %EXIT_CODE%

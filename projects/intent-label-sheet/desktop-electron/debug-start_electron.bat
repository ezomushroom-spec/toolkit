@echo off
setlocal
cd /d "%~dp0"

set "PROJECT_ROOT=%~dp0.."
set LOG_FILE=%~dp0runtime\startup-electron.log

if not exist "runtime" mkdir "runtime"

echo [%date% %time%] starting electron debug launcher > "%LOG_FILE%"
echo cwd=%cd% >> "%LOG_FILE%"
echo project_root=%PROJECT_ROOT% >> "%LOG_FILE%"

where npm >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo npm was not found. >> "%LOG_FILE%"
    type "%LOG_FILE%"
    pause
    exit /b 1
)

if not exist "%PROJECT_ROOT%\node_modules" (
    echo installing frontend dependencies... >> "%LOG_FILE%"
    call npm install --prefix "%PROJECT_ROOT%" >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        echo frontend dependency install failed. >> "%LOG_FILE%"
        type "%LOG_FILE%"
        pause
        exit /b 1
    )
)

if not exist "node_modules\electron" (
    echo installing desktop shell dependencies... >> "%LOG_FILE%"
    call npm install >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        echo desktop shell dependency install failed. >> "%LOG_FILE%"
        type "%LOG_FILE%"
        pause
        exit /b 1
    )
)

echo building frontend... >> "%LOG_FILE%"
call npm run build:web --prefix "%PROJECT_ROOT%" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo frontend build failed. >> "%LOG_FILE%"
    type "%LOG_FILE%"
    pause
    exit /b 1
)

call npm start >> "%LOG_FILE%" 2>&1
echo exit_code=%errorlevel% >> "%LOG_FILE%"
type "%LOG_FILE%"
pause

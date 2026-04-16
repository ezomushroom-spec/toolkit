@echo off
setlocal
cd /d "%~dp0"

set LOG_FILE=%~dp0startup-web.log
echo [%date% %time%] starting web debug launcher > "%LOG_FILE%"
echo cwd=%cd% >> "%LOG_FILE%"

where npm >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo npm was not found. >> "%LOG_FILE%"
  type "%LOG_FILE%"
  pause
  exit /b 1
)

if not exist "node_modules" (
  echo installing dependencies... >> "%LOG_FILE%"
  call npm install >> "%LOG_FILE%" 2>&1
  if errorlevel 1 (
    echo npm install failed. >> "%LOG_FILE%"
    type "%LOG_FILE%"
    pause
    exit /b 1
  )
)

call npm run dev:web >> "%LOG_FILE%" 2>&1
echo exit_code=%errorlevel% >> "%LOG_FILE%"
type "%LOG_FILE%"
pause

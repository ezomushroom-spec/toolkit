@echo off
setlocal

cd /d "%~dp0"
set "LOG_FILE=%~dp0startup.log"
set "SERVER_LOG=%~dp0dev-server.log"
set "APP_URL=http://localhost:5173"

echo === startup begin === > "%LOG_FILE%"
echo cwd=%cd% >> "%LOG_FILE%"
echo === dev server begin === > "%SERVER_LOG%"

where node >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo node was not found. >> "%LOG_FILE%"
  type "%LOG_FILE%"
  pause
  exit /b 1
)

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

echo starting dev server... >> "%LOG_FILE%"
start "image-prompt-studio-debug" cmd /c "cd /d ""%~dp0"" && npm run dev >> ""%SERVER_LOG%"" 2>&1"

set "WAIT_COUNT=0"
:wait_for_server
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri '%APP_URL%' -UseBasicParsing -TimeoutSec 1; exit 0 } catch { exit 1 }" >nul 2>nul
if not errorlevel 1 goto server_ready

set /a WAIT_COUNT+=1
if %WAIT_COUNT% GEQ 30 (
  echo server did not become ready within 30 seconds >> "%LOG_FILE%"
  echo === startup end === >> "%LOG_FILE%"
  type "%LOG_FILE%"
  pause
  exit /b 1
)

timeout /t 1 /nobreak >nul
goto wait_for_server

:server_ready
echo server is ready >> "%LOG_FILE%"
echo open %APP_URL% in your browser >> "%LOG_FILE%"
echo server output log: %SERVER_LOG% >> "%LOG_FILE%"
echo === startup end === >> "%LOG_FILE%"
type "%LOG_FILE%"
pause

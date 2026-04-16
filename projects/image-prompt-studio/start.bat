@echo off
setlocal

cd /d "%~dp0"
set "APP_URL=http://localhost:5173"

where npm >nul 2>nul
if errorlevel 1 (
  echo npm was not found.
  echo Please install Node.js and try again.
  pause
  exit /b 1
)

if not exist "node_modules" (
  echo Installing dependencies...
  call npm install
  if errorlevel 1 (
    echo npm install failed.
    pause
    exit /b 1
  )
)

echo Starting dev server...
start "image-prompt-studio-dev" cmd /c "cd /d ""%~dp0"" && npm run dev"

set "WAIT_COUNT=0"
:wait_for_server
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri '%APP_URL%' -UseBasicParsing -TimeoutSec 1; exit 0 } catch { exit 1 }" >nul 2>nul
if not errorlevel 1 goto open_browser

set /a WAIT_COUNT+=1
if %WAIT_COUNT% GEQ 30 (
  echo Dev server did not become ready within 30 seconds.
  echo Check the other console window for errors.
  pause
  exit /b 1
)

timeout /t 1 /nobreak >nul
goto wait_for_server

:open_browser
start "" "%APP_URL%"

echo Dev server is ready.

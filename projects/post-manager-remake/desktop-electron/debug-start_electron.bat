@echo on
setlocal

cd /d "%~dp0"
title Post Manager Electron Debug

echo Working directory: %CD%
where node
where npm
call node --version
call npm --version

if not exist "%~dp0node_modules\electron" (
    echo node_modules\\electron was not found.
    echo Running npm install...
    call npm install
)

call npm start
echo Exit code: %ERRORLEVEL%
pause

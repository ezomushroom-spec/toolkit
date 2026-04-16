@echo off
setlocal
cd /d "%~dp0"

call ".\desktop-electron\start_electron.bat"
exit /b %ERRORLEVEL%

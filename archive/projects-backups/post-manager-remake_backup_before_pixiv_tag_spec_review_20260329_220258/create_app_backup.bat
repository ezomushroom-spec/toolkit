@echo off
setlocal

set "SRC=%~dp0app"
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "TS=%%I"
set "DST=%~dp0backup_app_before_electron_%TS%"

if not exist "%SRC%" (
    echo Source app folder was not found.
    pause
    exit /b 1
)

echo Creating backup...
echo Source: %SRC%
echo Target: %DST%

xcopy "%SRC%" "%DST%\" /E /I /H /Y >nul
if errorlevel 1 (
    echo Backup failed.
    pause
    exit /b 1
)

echo Backup completed.
echo %DST%
pause

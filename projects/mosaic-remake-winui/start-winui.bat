@echo off
setlocal
cd /d "%~dp0"

set "EXE=bin\Debug\net8.0-windows10.0.19041.0\MosaicRemake.WinUI.exe"

if not exist "%EXE%" (
  echo WinUI executable was not found.
  echo Build the project first.
  pause
  exit /b 1
)

set "PATH=%PATH:C:\Program Files\PowerToys\;=%"
set "PATH=%PATH:;C:\Program Files\PowerToys\=%"
set "PATH=%PATH:C:\Program Files\PowerToys;=%"
set "PATH=%PATH:;C:\Program Files\PowerToys=%"

start "" "%CD%\%EXE%"
exit /b 0

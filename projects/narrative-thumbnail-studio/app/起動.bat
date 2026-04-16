@echo off
cd /d "%~dp0"
setlocal

set "PYTHONW_EXE="

if exist "%~dp0.venv\Scripts\pythonw.exe" set "PYTHONW_EXE=%~dp0.venv\Scripts\pythonw.exe"
if not defined PYTHONW_EXE if exist "%~dp0venv\Scripts\pythonw.exe" set "PYTHONW_EXE=%~dp0venv\Scripts\pythonw.exe"
if not defined PYTHONW_EXE if exist "%LocalAppData%\Programs\Python\Python310\pythonw.exe" set "PYTHONW_EXE=%LocalAppData%\Programs\Python\Python310\pythonw.exe"
if not defined PYTHONW_EXE if exist "%LocalAppData%\Programs\Python\Python313\pythonw.exe" set "PYTHONW_EXE=%LocalAppData%\Programs\Python\Python313\pythonw.exe"
if not defined PYTHONW_EXE set "PYTHONW_EXE=pythonw"

start "" "%PYTHONW_EXE%" "%~dp0main.py"

@echo off
setlocal
cd /d "%~dp0"

set "EXE=bin\Debug\net8.0-windows10.0.19041.0\MosaicRemake.WinUI.exe"
set "LOG=startup.log"

if not exist "%EXE%" (
  > "%LOG%" echo [debug-start-winui] executable not found
  type "%LOG%"
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$log = Join-Path (Get-Location) 'startup.log';" ^
  "$exe = Join-Path (Get-Location) 'bin\\Debug\\net8.0-windows10.0.19041.0\\MosaicRemake.WinUI.exe';" ^
  "$entries = [Environment]::GetEnvironmentVariable('PATH','Process').Split(';') | Where-Object { $_ -and ($_.TrimEnd('\') -ne 'C:\\Program Files\\PowerToys') };" ^
  "$env:PATH = ($entries -join ';');" ^
  "$proc = Start-Process -FilePath $exe -WorkingDirectory (Get-Location) -PassThru;" ^
  "Start-Sleep -Seconds 10;" ^
  "$alive = -not $proc.HasExited;" ^
  "Set-Content -Path $log -Value @('[debug-start-winui] cwd=' + (Get-Location), '[debug-start-winui] exe=' + $exe, '[debug-start-winui] aliveAfter10s=' + $alive);" ^
  "if (-not $alive) { Add-Content -Path $log -Value ('[debug-start-winui] exit=' + $proc.ExitCode) }"
set "EXIT_CODE=%ERRORLEVEL%"

type "%LOG%"
pause
exit /b %EXIT_CODE%

---
name: windows-batch-launcher
description: Create or repair Windows batch launchers for local apps, dev servers, and helper tools. Use when Codex needs to add or fix `start.bat`, `debug-start.bat`, launcher `.bat` files, double-click startup flows, or Windows app launch troubleshooting where console encoding, quoting, missing dependencies, or silent failure are risks.
triggers: batch launcher, バッチ起動, バッチファイル修正, start.bat, debug-start.bat, launcher bat, Windowsバッチ起動
---

# Purpose

Make Windows launcher batch files reliable and debuggable.
Prevent common startup failures before they happen.

# Core rules

- Keep `.bat` syntax ASCII-simple.
- Avoid Japanese or other non-ASCII status text inside `.bat` files unless encoding is explicitly controlled.
- Prefer short `echo` messages in English for launcher scripts.
- Always anchor the working directory with `cd /d "%~dp0"`.
- Quote paths and URLs passed to `start`.
- Prefer `call npm ...` or `call python ...` inside batch files so control returns correctly.
- Fail with a visible message and `pause` when the script is intended for double-click use.
- When Python launcher reliability matters, prefer explicit interpreter discovery over assuming `py -3`.

# Required checks

Before finalizing a launcher:

1. Confirm the intended working directory.
2. Confirm the command exists, for example `npm`, `node`, `python`, or a local `.venv` executable.
3. Decide whether first-run dependency install is needed.
4. Decide whether a debug launcher is also needed.
5. Decide interpreter priority, for example `.venv`, `venv`, `py -3.10`, then `python`.

For dependency install:

- if the launcher is a developer bootstrapper for a local workspace, auto-install can be acceptable
- if the launcher is intended for end users or double-click distribution, do not auto-install unless the project explicitly allows it
- when auto-install is not clearly allowed, fail visibly and tell the user what setup step is missing

# Standard launcher pattern

Use this shape unless the project needs something more specific:

```bat
@echo off
setlocal
cd /d "%~dp0"

where npm >nul 2>nul
if errorlevel 1 (
  echo npm was not found.
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

start "" "http://localhost:5173"
call npm run dev

if errorlevel 1 (
  echo Failed to start the app.
  pause
  exit /b 1
)
```

# Debug launcher rule

When a batch file may fail silently, add a separate debug launcher next to it.

The debug launcher should:

- write to a local log file such as `startup.log`
- record the working directory
- record whether required commands exist
- capture stdout and stderr from the real startup command
- `pause` at the end so the user can read the result
- record the interpreter path that was actually used
- record the process exit code

# Known failure to prevent

This workspace already hit a real failure where Japanese `echo` text inside `start.bat` was misread by `cmd.exe`, and broken characters were interpreted as commands.

To prevent that exact failure:

- keep launcher text ASCII by default
- do not assume UTF-8 batch parsing is safe
- test the launcher with `cmd /c start.bat`
- if the app is meant for double-click launch, add `debug-start.bat` in the same folder

This workspace also hit a real failure where `py -3` selected a different Python than the project runtime and the launcher died after startup logging.

To prevent that class of failure:

- do not assume `py -3` points at the intended environment
- prefer project-local interpreters first
- if the app has a known supported minor version such as `3.10`, prefer `py -3.10` over broad selectors
- use version-pinned `py -x.y` only after local interpreter candidates were probed or ruled out
- keep startup log lines ASCII-safe when they may print Windows paths

# Suggested final check

After creating or editing a launcher:

1. Run it from the project directory with `cmd /c <launcher>.bat`.
2. If it opens a long-running dev server, confirm that the script reaches the server start line without immediate batch parsing errors.
3. If it fails, inspect the debug launcher log before changing app code.
4. If it starts a local server, verify the expected port responds before calling the launcher complete.

@echo off
chcp 65001 >nul
title AutoMosaic - 起動処理中...

echo ===================================================
echo   AutoMosaic v1.0 (Commercial Grade) を起動します
echo ===================================================
echo.

cd /d "%~dp0"

:: 仮想環境(venv)が存在する場合は有効化
if exist venv\Scripts\activate.bat (
    echo [Info] 仮想環境を検出しました。有効化します...
    call venv\Scripts\activate.bat
)

:: Python が使えるかチェック
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [Error] Python がインストールされていないか、PATHが通っていません。
    echo Python 3.8〜3.12 程度をインストールしてください。
    pause
    exit /b 1
)

:: メインスクリプトの起動
echo アプリケーションを起動しています...
python main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [Error] アプリケーションが異常終了しました。
    pause
) else (
    echo.
    echo 終了しました。
)

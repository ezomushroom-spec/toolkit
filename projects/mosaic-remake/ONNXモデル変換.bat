@echo off
chcp 65001 > nul
title AutoMosaic - ONNXモデル変換ツール

cd /d "%~dp0"

echo ===================================================
echo   AutoMosaic ONNXモデル変換ツール
echo ===================================================
echo.

if "%~1"=="" (
    echo [エラー] 変換するモデルが指定されていません。
    echo このバッチファイル（ONNXモデル変換.bat）に向かって、
    echo 変換したいYOLOモデル（.ptファイル）をドラッグ＆ドロップしてください。
    echo.
    pause
    exit /b
)

echo 選択されたファイル: %~nx1
echo.

REM 仮想環境ディレクトリがあれば探してアクティベートする
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

python utils\export_onnx.py "%~1"

echo.
echo 処理が完了しました。何かキーを押すと閉じます...
pause

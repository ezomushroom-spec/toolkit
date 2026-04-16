@echo off
chcp 65001 >nul
title AutoMosaic - ビルド処理中...

echo ===================================================
echo   AutoMosaic v1.0 を exeファイルにパッケージ化します
echo ===================================================
echo.

:: PyInstaller がインストールされているか確認
pip show pyinstaller >nul 2>&1
if int%ERRORLEVEL% neq 0 (
    echo [Info] PyInstaller をインストールしています...
    pip install pyinstaller
)

echo.
echo [Info] ビルドを開始します...

:: `.pt` モデルを同梱しておく
pyinstaller --noconfirm --onedir --windowed ^
    --name "AutoMosaic" ^
    --icon "NONE" ^
    --add-data "ntd11_anime_nsfw_segm_v5-variant1.pt;." ^
    main.py

echo.
echo ===================================================
if %ERRORLEVEL% equ 0 (
    echo   ビルドが完了しました！ (distフォルダをご確認ください)
) else (
    echo   [Error] ビルド中にエラーが発生しました。
)
pause

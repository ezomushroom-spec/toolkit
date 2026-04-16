# Mosaic Remake WinUI

`mosaic-remake` の WinUI 3 移行用シェルです。

現段階では、Python 側の推論コアを残したまま、WinUI 側の画面骨格と今後の接続入口を用意しています。
あわせて、Python 側には WinUI から呼ぶための CLI ブリッジを追加しました。

## 方針

- 推論と画像加工の正本は当面 Python 側に残す
- WinUI 側は UI シェル、状態表示、今後の連携入口を担当する
- 当面は Python プロセス連携を行い、将来的にローカル API 連携へ広げる

## 現状

- WinUI 3 の最小アプリ構成を配置済み
- メイン画面にモデル、入力、出力、プレビュー、処理ボタンの骨格を配置済み
- Python 側に `bridge_cli.py` を追加済み
- `ReviewButton` から Python bridge の `health` を叩く入口を配置済み
- `start-winui.bat` で PowerToys の `Microsoft.UI.Xaml.dll` を掴みにくい専用起動入口を追加済み
- `debug-start-winui.bat` で 10 秒生存確認付きの debug 起動入口を追加済み
- `BootstrapInitializer.cs` で Windows App SDK bootstrap を明示化済み

## 注意

- 2026-03-30 時点で `.NET SDK 8.0.419` は導入済みです。
- `dotnet build` は成功します。
- 通常の環境変数のままでは、`PATH` 上の `C:\Program Files\PowerToys\` から `Microsoft.UI.Xaml.dll` を掴んで WinUI 実行が不安定になることがあります。
- そのため、起動確認はまず `start-winui.bat` か `debug-start-winui.bat` を使う前提です。
- 現時点では、`start-winui.bat` と `debug-start-winui.bat` で 10 秒以上のプロセス生存を確認済みです。

## 参考

- [Build a C# .NET app with WinUI and Win32 interop](https://learn.microsoft.com/en-us/windows/apps/winui/winui3/desktop-winui3-app-with-basic-interop)
- [Project properties and auto-initializers](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/project-properties)

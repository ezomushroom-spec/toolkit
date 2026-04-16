# Project Summary

## 1. Purpose

- `mosaic-remake` の WinUI 3 移行用シェルです。
- 推論コアは当面 Python 側に残し、WinUI 側は画面骨格と接続入口を担当します。

## 2. Source of Truth

- この folder の役割: WinUI shell と bridge 接続の実装場所
- 正本コード: この project 配下の WinUI 側コード
- 正本設定: WinUI 起動バッチと `.csproj`
- 正本データ: なし
- 正本文書: `README.md`, `AGENTS.md`, `PROJECT_SUMMARY.md`
- 比較対象や参照専用 backup: 親案件 `mosaic-remake` 側の Python core と関連資料

## 3. Primary Entry Points

- 通常起動: `start-winui.bat`
- 代替入口: `debug-start-winui.bat`
- ビルドや検証の主要コマンド: `dotnet build` と起動バッチでの生存確認

## 4. Safe Read Scope

- 初見で読んでよいディレクトリ: project 直下の WinUI コード、`Services/`、`README.md`
- 先に確認すべき文書: `START_HERE.md`, `AGENTS.md`, `README.md`, `WinUI試金石_懸念整理.md`

## 5. Do Not Edit Without Explicit Request

- backup: 該当なし
- profile / user data: 該当なし
- build artifact / generated: `bin/`, `obj/`, `build-diag.log`, `startup.log`, `tmp_ui_capture.png`
- secrets / local state: 親案件側の Python 設定や推論資産

## 6. Related Boundaries

- UI shell: WinUI 側 XAML と code-behind
- bridge / service: `Services/`
- launcher: `start-winui.bat`, `debug-start-winui.bat`
- backend / business logic: 親案件 `mosaic-remake` 側の Python core

## 7. Risks For Subagents

- 誤認しやすい正本や境界: WinUI shell と Python core の責務を混同しないこと
- 壊しやすい運用資産: 起動バッチ、Windows App SDK bootstrap、bridge health 導線
- 並列編集で衝突しやすい場所: `MainWindow.xaml`, `MainWindow.xaml.cs`, 起動バッチ

## 8. Recommended First Step

- まず `START_HERE.md` と `AGENTS.md` を読んで、Python 側を正本に残す前提と起動導線を確認する。
- 次に `README.md` と起動バッチを見て、`dotnet run` 前提へ勝手に寄せてよい案件かを判断する。

## 9. Rollback Hint

- WinUI shell の変更は XAML/code-behind と起動バッチを分けて戻す。
- Python core 側の資産とは切り離して扱い、責務をまたぐ変更を避ける。

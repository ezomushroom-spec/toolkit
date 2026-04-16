# Project Summary

## 1. Purpose

- PySide6 ベースの Windows 向け画像処理 GUI アプリです。
- `main.py`、`ui/`、`core/` を中心に、再構築や UI 改善を進める案件として扱います。

## 2. Source of Truth

- 正本コード: `main.py`, `ui/`, `core/`, `utils/`
- 正本設定: `settings.json`
- 正本モデル資産: `*.onnx`, `*.pt`
- 正本文書: `AGENTS.md`, `再構築準備メモ.md`, `PT再構築_実装着手計画.md`

## 3. Primary Entry Points

- 通常起動: `通常起動.bat`
- 代替入口: `main.py`
- ビルドや検証の主要コマンド: `build.bat`, `python main.py`, `test_onnx.py`

## 4. Safe Read Scope

- 初見で読んでよいディレクトリ: `ui/`, `core/`, `utils/`
- 先に確認すべき文書: `AGENTS.md`, `再構築準備メモ.md`, `PT再構築_実装着手計画.md`

## 5. Do Not Edit Without Explicit Request

- backup: `mosaic-remake_backup_before_winui_20260329_222652`
- profile / user data: 特になし
- build artifact / generated: `tmp_input_review/`, `tmp_output_review/`, ビルド生成物
- secrets / local state: `settings.json`, モデル資産 `*.onnx`, `*.pt`

## 6. Related Boundaries

- UI: `ui/`
- backend / business logic: `core/`, `utils/`
- desktop shell / launcher: `通常起動.bat`, `build.bat`
- external integration: ONNX / PT モデル読み込み

## 7. Risks for Subagents

- 誤認しやすい正本: 一時入出力や review 用フォルダを本体処理と混同しやすい
- 壊しやすい運用資産: `settings.json`, `*.onnx`, `*.pt`
- 並列編集で衝突しやすい場所: `ui/main_window.py` と `core/` の処理境界

## 8. Recommended First Step

- まず `AGENTS.md` を読んで運用資産と生成物の境界を確認する。
- 次に `main.py` と `ui/main_window.py` を見て、UI から core をどう呼んでいるかを把握する。
- 一時入出力フォルダではなく、`ui/` と `core/` を先に読む。

## 9. Rollback Hint

- 変更は `ui/`、`core/`、`settings.json` の単位で戻す。
- モデル資産は差し替えず、コード変更と切り分けて扱う。

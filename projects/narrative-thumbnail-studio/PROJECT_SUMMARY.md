# Project Summary

## 1. Purpose

- 複数画像をテンプレートに沿って配置し、サムネイル画像としてプレビュー・書き出しするローカル Windows デスクトップツールです。
- `app/` 正本を前提に、レビューと改善準備を進めます。

## 2. Source of Truth

- この folder の役割: project 入口文書、判断メモ、正本コードへの導線をまとめる
- 正本コード: `app/`
- 正本設定: `app/requirements.txt`, `起動.bat`, `デバッグ起動.bat`
- 正本データ: `presets/*.json`
- 正本文書: `AGENTS.md`, `PROJECT_SUMMARY.md`, `docs/`
- 比較対象や参照専用 backup: `E:\自作アプリ集\narrative-thumbnail-studio`, `preset_panel_preview*.png`, `test_*.png`

## 3. Primary Entry Points

- 通常起動: `起動.bat`
- 代替入口: `デバッグ起動.bat`, `python app/main.py`
- ビルドや検証の主要コマンド: アプリ起動、画像読込、テンプレート反映、プレビュー、書き出し

## 4. Safe Read Scope

- 初見で読んでよいディレクトリ: `app/`, `docs/`, `presets/`
- 先に確認すべき文書: `AGENTS.md`, `docs/現状確認_20260402.md`, `docs/採用判断_20260402.md`

## 5. Do Not Edit Without Explicit Request

- backup: 旧配置 `E:\自作アプリ集\narrative-thumbnail-studio`
- profile / user data: 該当なし
- build artifact / generated: `preset_panel_preview*.png`, `test_*.png`, `startup_error.log`, `_pythonw_*`
- secrets / local state: `presets/*.json` は UI 変更と切り離して勝手に変えない

## 6. Related Boundaries

- UI: `app/ui/`
- backend / business logic: `app/core/`
- desktop shell / launcher: `起動.bat`, `デバッグ起動.bat`
- external integration: Pillow, NumPy, OpenCV ベースの画像処理

## 7. Risks For Subagents

- 誤認しやすい正本や境界: `app/` が正本で、旧配置と生成プレビュー画像は参照専用
- 壊しやすい運用資産: `presets/*.json`
- 並列編集で衝突しやすい場所: `app/ui/`, `app/core/`, launcher `.bat`

## 8. Recommended First Step

- まず `AGENTS.md` を読んで、正本境界と編集禁止物を確認する。
- 次に `docs/現状確認_20260402.md` と `docs/採用判断_20260402.md` を読んで、既知リスクと自然な着手順を把握する。

## 9. Rollback Hint

- 変更は `app/ui/`, `app/core/`, launcher `.bat` の単位で戻す。
- `presets/*.json` と旧配置はコード変更と切り離して扱う。

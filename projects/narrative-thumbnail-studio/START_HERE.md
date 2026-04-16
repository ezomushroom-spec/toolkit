# START HERE

## この project は何か

- `narrative-thumbnail-studio` は、複数画像をテンプレートに沿って配置し、サムネイル画像としてプレビュー・書き出しするローカル Windows デスクトップツールです。
- この folder では、`app/` 正本を前提にレビューと改善準備を進めます。

## 最初に読む順番

1. `AGENTS.md`
2. `app/main.py`, `app/ui/main_window.py`, `app/core/layout_engine.py`
3. `PROJECT_SUMMARY.md`
4. `docs/現状確認_20260402.md`
5. `docs/採用判断_20260402.md`
6. 必要なら `docs/未決事項_20260402.md`

## 正本

- 正本コード: `app/`
- 正本設定: `app/requirements.txt` と launcher `.bat`
- 正本文書: `AGENTS.md`, `PROJECT_SUMMARY.md`, `docs/`
- 比較対象: `E:\自作アプリ集\narrative-thumbnail-studio`

## 主要入口

- 通常起動: `起動.bat`
- 代替入口: `デバッグ起動.bat`, `python app/main.py`
- 主な確認方法: アプリ起動、画像読込、プレビュー、書き出し

## 触る前に注意するもの

- 壊してはいけない既存挙動: 画像読込、テンプレート反映、プレビュー、書き出し、履歴系導線
- 明示依頼なしで触らないもの: `preset_panel_preview*.png`, `test_*.png`, `startup_error.log`, `_pythonw_*`
- backup / profile / generated: 旧配置と参照用生成物は正本扱いしない

## 最初の一手

- まず `AGENTS.md` を読んで、正本境界と触らない生成物を確認する。
- 次に `app/` の主要入口を見て、正本コードと UI / core の責務を把握する。
- その後に `PROJECT_SUMMARY.md` と `docs/現状確認_20260402.md` を読んで、現状のリスクと自然な着手順を把握する。

# START HERE

## この project は何か

- PySide6 ベースの Windows 向け画像処理 GUI アプリです。
- `main.py`、`ui/`、`core/` を中心に、再構築や UI 改善を進める案件として扱います。

## 最初に読む順番

1. `AGENTS.md`
2. `PROJECT_SUMMARY.md`
3. `再構築準備メモ.md`
4. `PT再構築_実装着手計画.md`
5. `main.py` と `ui/`

## 正本

- 正本コード: `main.py`, `ui/`, `core/`, `utils/`
- 正本設定: `settings.json`
- 正本モデル資産: `*.onnx`, `*.pt`
- 正本文書: `AGENTS.md`, `PROJECT_SUMMARY.md`, `再構築準備メモ.md`, `PT再構築_実装着手計画.md`

## 主要入口

- 通常起動: `通常起動.bat`
- 代替入口: `main.py`
- 主な確認方法: `python main.py`, `test_onnx.py`, `build.bat`

## 触る前に注意するもの

- 壊してはいけない既存挙動: UI から core を呼ぶ導線、設定読み込み、モデル読み込み
- 明示依頼なしで触らないもの: `settings.json`, `*.onnx`, `*.pt`, review 用一時フォルダ
- backup / profile / generated: `tmp_input_review/`, `tmp_output_review/`, build 生成物

## 最初の一手

- まず `AGENTS.md` と `PROJECT_SUMMARY.md` を読んで正本と危険資産を把握する。
- 次に `main.py` と `ui/main_window.py` を見て、UI から core をどう呼んでいるかを確認する。

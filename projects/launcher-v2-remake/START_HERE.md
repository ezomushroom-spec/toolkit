# START HERE

## この project は何か

- `E:\自作アプリ集\ランチャー_v2` の現行挙動を保ちながら、安全に再開発する案件です。
- Python ベースの Windows 向けランチャーを、この workspace 配下で段階移行する前提です。

## 最初に読む順番

1. `AGENTS.md`
2. `PROJECT_SUMMARY.md`
3. `docs/implementation-plan.md`
4. `config/settings.json` と起動導線

## 正本

- 現行正本コード: `E:\自作アプリ集\ランチャー_v2`
- workspace 側の実装先候補: `app/`
- 正本設定: `config/settings.json`
- 正本文書: `AGENTS.md`, `PROJECT_SUMMARY.md`, `docs/implementation-plan.md`

## 主要入口

- 通常起動: `start.bat`
- 代替入口: `debug-start.bat`, `main.py`
- 主な確認方法: `python main.py`

## 触る前に注意するもの

- 壊してはいけない既存挙動: 起動互換、設定互換、主操作の到達経路
- 明示依頼なしで触らないもの: workspace 外の旧版、配布物、広い構成変更
- backup / profile / generated: `config/settings.json` とローカル設定系は移行方針なしで壊さない

## 最初の一手

- まず `AGENTS.md` と `docs/implementation-plan.md` を読んで keep / fix / later の前提を把握する。
- 次に `config/settings.json` と起動導線を見て、互換性に触れる作業かどうかを判定する。

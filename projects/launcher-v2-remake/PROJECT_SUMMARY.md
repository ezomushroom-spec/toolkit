# Project Summary

## 1. Purpose

- `E:\自作アプリ集\ランチャー_v2` の現行挙動を保ちながら、安全に再開発する案件です。
- Python ベースの Windows 向けランチャーを、この workspace 配下で段階移行する前提です。

## 2. Source of Truth

- 正本コード: `E:\自作アプリ集\ランチャー_v2`
- workspace 側の実装先候補: `app/`
- 正本設定: `config/settings.json`
- 正本文書: `docs/implementation-plan.md`, `AGENTS.md`

## 3. Primary Entry Points

- 通常起動: `start.bat`
- 代替入口: `debug-start.bat`, `main.py`
- ビルドや検証の主要コマンド: `python main.py`, `pip install -r requirements.txt`

## 4. Safe Read Scope

- 初見で読んでよいディレクトリ: `app/`, `config/`, `docs/`
- 先に確認すべき文書: `AGENTS.md`, `docs/implementation-plan.md`

## 5. Do Not Edit Without Explicit Request

- backup: workspace 外の旧版や退避コピー
- profile / user data: `config/settings.json` を移行方針なしで壊さない
- build artifact / generated: 明示依頼なしで配布物や生成物を更新しない
- secrets / local state: ローカル設定や起動互換に影響する設定

## 6. Related Boundaries

- UI: `app/`
- backend / business logic: `app/` 内の実処理
- desktop shell / launcher: Windows 起動導線、`.bat`、`main.py`
- external integration: ローカル設定ファイル

## 7. Risks for Subagents

- 誤認しやすい正本: workspace 側だけを正本と誤認しやすい。現行正本は workspace 外にある
- 壊しやすい運用資産: `config/settings.json`
- 並列編集で衝突しやすい場所: 起動導線、設定互換、主要 UI

## 8. Recommended First Step

- まず `AGENTS.md` と `docs/implementation-plan.md` を読んで、keep / fix / later の前提を把握する。
- 次に `config/settings.json` と起動導線を見て、互換性に触れる作業かどうかを判定する。

## 9. Rollback Hint

- 互換性に関わる変更は `config/settings.json` と起動導線を中心に戻す。
- workspace 側変更だけでなく、現行正本との差分確認が必要になる。

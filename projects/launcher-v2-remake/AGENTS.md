# launcher-v2-remake

## Goal
- `E:\自作アプリ集\ランチャー_v2` の現行挙動を保ちながら、このワークスペース配下で安全に再開発する。

## Current source of truth
- 現行挙動の正本は `E:\自作アプリ集\ランチャー_v2` の実コードと `config/settings.json`。
- 再開発判断は `docs/implementation-plan.md` を基準に進める。

## Guardrails
- 初回段階では既存機能を削除しない。
- keep / fix / later を混ぜず、段階移行で進める。
- UI は構造 → 見た目 → 安全性の順で見直す。
- 設定互換と起動互換を崩す変更は、移行手順と戻し方を先に定義する。

## build / run / test
- 開発起動: `python main.py`
- 補助入口: `start.bat`, `debug-start.bat`
- 依存導入: `pip install -r requirements.txt`
- 優先確認: 起動互換、設定互換、主操作の到達経路

## 変更時の必須セット作業

- 更新する docs: `AGENTS.md`、`START_HERE.md`、`PROJECT_SUMMARY.md`、`docs/implementation-plan.md`
- 最低限の確認コマンド: `python main.py`
- 最低限の手動確認: `start.bat` と `debug-start.bat` の起動導線、既存設定の読込、主操作の到達経路
- 失敗時に先に見るログやファイル: `config/settings.json`、起動バッチ、workspace 側実装計画文書、正本側実コード

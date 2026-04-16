# Project Rules

- この project は `generated-image-finishing-tool` 固有の前提だけを扱う。
- Workspace 共通ルールは `E:\codex\workspace\AGENTS.md` を優先する。
- 実装の正本は `app/`、判断記録の正本は `docs/` とする。
- `app/` では UI と処理本体の責務を分離し、単画像プレビューと一括適用で同じレシピ定義と処理コアを共有する。
- `data/recipes/` はレシピ JSON の正本候補、`data/settings/` はローカル設定の正本候補として扱い、保存形式変更時は互換維持策か戻し方を先に示す。
- `startup.log`、`data/logs/`、`__pycache__/` は生成物として扱い、正本に混ぜない。
- UI 改善は構造 -> 見た目 -> 安全性の順で行い、無関係な汎用編集機能を広げない。
- 元画像の上書き、誤った出力先、長時間バッチ中の二重実行は高リスク操作として先に確認する。

## build / run / test

- 開発起動: `python -m app.main`
- 補助入口: `start.bat`, `debug-start.bat`
- 最低限の確認: `python -m py_compile app\\main.py`
- 実行前提: `requirements.txt` の依存が導入され、生成物を正本に混ぜないこと

## この案件で確認を優先するもの

- 単画像プレビューと一括適用が同じレシピ定義を使うこと
- レシピ保存 / 再読込が JSON と整合すること
- 元画像を上書きしないこと
- 一括適用で失敗対象だけが個別記録され、残りが継続できること
- ログや `__pycache__` を編集対象に混ぜていないこと

## 変更時の必須セット作業

- 更新する docs: `AGENTS.md`、`START_HERE.md`、`PROJECT_SUMMARY.md`、必要なら `docs/current-status.md`、`docs/adoption-decision.md`、`docs/open-questions.md`
- 最低限の確認コマンド: `python -m py_compile app\\main.py`
- 最低限の手動確認: 起動、単画像読込、レシピ保存 / 再読込、一括適用の入口確認
- 失敗時に先に見るログやファイル: `app/main.py`、`app/core/`、`app/ui/`、`startup.log`、`data/logs/app.log`

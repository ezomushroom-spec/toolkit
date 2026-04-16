# Project Rules

- `src/` と `web/` を正本とし、`src_backup_*` と各 `*_profile/` は明示依頼なしで編集しない。
- `data/posts.csv`、`config/secrets.yaml`、`config/templates.yaml`、`browser_profile/` は運用資産として扱い、変更前に影響対象と戻し方を整理する。
- Pixiv / Patreon の自動化は入力補助までとし、最終投稿確定は人が行う前提を崩さない。
- 処理フローを変えるときは `manager.py` を基準に、CLI と Web API の両入口の整合を保つ。
- ブラウザまわりは persistent profile のロック、再試行、終了順を壊さない。

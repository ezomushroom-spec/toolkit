# Project Rules

- `src/` と `web/` を正本とし、`src_backup_*` と各 `*_profile/` は明示依頼なしで編集しない。
- `data/posts.csv`、`config/secrets.yaml`、`config/templates.yaml`、`browser_profile/` は運用資産として扱い、変更前に影響対象と戻し方を整理する。
- Pixiv / Patreon の自動化は入力補助までとし、最終投稿確定は人が行う前提を崩さない。
- 処理フローを変えるときは `manager.py` を基準に、CLI と Web API の両入口の整合を保つ。
- ブラウザまわりは persistent profile のロック、再試行、終了順を壊さない。

## 変更時の必須セット作業

- 更新する docs: 上位 `../AGENTS.md`、`../START_HERE.md`、`../PROJECT_SUMMARY.md`、必要なら `docs/` 配下の判断メモ
- 最低限の確認コマンド: `python src/api_server.py`、必要なら対象 step の API 呼び出しまたは `node --check web/script.js`
- 最低限の手動確認: CLI と Web API の整合、runtime 表示、停止導線、運用資産を壊さないこと
- 失敗時に先に見るログやファイル: `src/api_server.py`、`src/manager.py`、ブラウザコンソール、backend ログ、`config/` と `data/posts.csv`

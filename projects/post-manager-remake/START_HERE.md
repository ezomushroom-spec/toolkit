# START HERE

## この project は何か

- Post Manager の再構築案件です。
- Python backend、Web UI、Electron shell、運用資産を分けて扱いながら段階移行します。

## 最初に読む順番

1. `AGENTS.md`
2. `PROJECT_SUMMARY.md`
3. `docs/pre-implementation-decision-memo_20260327.md`
4. `docs/backup-boundary-decision_20260402.md`
5. `docs/phase3-current-state_20260402.md`
6. `docs/rebuild-thread-handoff.md`
7. `app/` と `desktop-electron/`

## 正本

- この folder の役割: 実装計画と判断記録の保管場所
- 正本コード: `app/`
- 主運用ターゲット候補: `desktop-electron/`
- 参照専用 backup: `archive/projects-backups/backup_app_before_electron_*` と workspace 外の旧バックアップ候補
- 正本文書: `AGENTS.md`, `PROJECT_SUMMARY.md`, `docs/`

## 主要入口

- 通常起動: `app/start_cli.bat`, `app/start_webui.bat`, `desktop-electron/start_electron.bat`
- 代替入口: `prepare_electron_migration.bat`, `create_app_backup.bat`
- 主な確認方法: `python app/src/api_server.py`、`app/start_webui.bat`、必要なら `node --check app/web/script.js`

## 触る前に注意するもの

- 壊してはいけない既存挙動: `app/` 正本維持、データ・profile 保護、投稿補助の安全性
- 明示依頼なしで触らないもの: `app/data/`, `app/config/`, `app/browser_profile/`, `app/*_profile/`, `archive/projects-backups/backup_app_before_electron_*`, workspace 外の旧バックアップ候補
- backup / profile / generated: `archive/projects-backups/backup_app_before_electron_*`, Electron runtime, node_modules

## 最初の一手

- まず `AGENTS.md` を読んで、`app/` 正本と backup 境界を確認する。
- 次に `PROJECT_SUMMARY.md` と `docs/backup-boundary-decision_20260402.md` を見て、`app/`、`desktop-electron/`、backup 群の責務を切り分ける。

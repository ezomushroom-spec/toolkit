# Project Summary

## 1. Purpose

- Post Manager の再構築案件です。
- Python backend、Web UI、Electron shell、運用資産を分けて扱いながら段階移行します。

## 2. Source of Truth

- この folder の役割: 実装計画と判断記録の保管場所
- 正本コード: `app/`
- 主運用ターゲット候補: `desktop-electron/`
- 参照専用 backup: `archive/projects-backups/backup_app_before_electron_*` と workspace 外の旧バックアップ候補
- 正本文書: `AGENTS.md`, `docs/`

## 3. Primary Entry Points

- 通常起動: `app/start_cli.bat`, `app/start_webui.bat`, `desktop-electron/start_electron.bat`
- 代替入口: `prepare_electron_migration.bat`, `create_app_backup.bat`
- ビルドや検証の主要コマンド: `python app/src/api_server.py`、必要なら `node --check app/web/script.js`

## 4. Safe Read Scope

- 初見で読んでよいディレクトリ: `docs/`, `app/`, `desktop-electron/`
- 先に確認すべき文書: `AGENTS.md`, `docs/pre-implementation-decision-memo_20260327.md`, `docs/backup-boundary-decision_20260402.md`, `docs/phase3-current-state_20260402.md`, `docs/rebuild-thread-handoff.md`

## 5. Do Not Edit Without Explicit Request

- backup: `archive/projects-backups/backup_app_before_electron_*`, workspace 外の旧バックアップ候補
- profile / user data: `app/browser_profile/`, `app/*_profile/`, `app/user_data/`
- build artifact / generated: Electron runtime や node_modules
- secrets / local state: `app/data/`, `app/config/`

## 6. Related Boundaries

- UI: `app/web/`
- backend / business logic: `app/src/`
- desktop shell / launcher: `desktop-electron/`
- external integration: browser profile、CSV、config、Pixiv / Patreon 補助導線

## 7. Risks for Subagents

- 誤認しやすい境界: `app/` が正本で、`desktop-electron/` は shell 側、backup 候補は参照専用
- 壊しやすい運用資産: `app/data/posts.csv`, `app/config/*`, browser profile 群
- 並列編集で衝突しやすい場所: `app/src/` と `app/web/` の入口整合、Electron 連携部

## 8. Recommended First Step

- まず `AGENTS.md` を読んで、`app/` 正本と backup 境界を確認する。
- 次に `docs/backup-boundary-decision_20260402.md` を見て、backup を active と誤認しない前提を固定する。
- そのうえで `app/AGENTS.md` と `docs/` を見て、`app/`、`desktop-electron/`、backup 群の責務を固定する。

## 9. Rollback Hint

- Python backend、Web UI、Electron shell を別単位で戻す。
- 運用資産はコード変更と切り離して扱い、restore 対象を明示する。

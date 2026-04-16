# Project Summary

## 1. Purpose

- `civitai_downloader` を workspace 管理下の案件として扱い、運用継続に支障がある不具合を優先的に修正する。
- 既存 UI と主要導線を維持しつつ、データ消失、詰み状態、誤操作のような高コスト問題を先に潰す。

## 2. Source of Truth

- 正本コード: `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/`
- 正本文書: `E:/codex/workspace/projects/civitai-downloader-fix/`
- 正本設定: `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/constants.py`, `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/db/`, `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/ui/`
- 実データ保存先: `%LOCALAPPDATA%/CivitaiDownloader/`

## 3. Primary Entry Points

- アプリ起動: `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/main.py`
- ブラウズ入口: `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/ui/browse_tab.py`
- キュー管理入口: `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/ui/download_tab.py`
- DB 初期化入口: `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/db/models.py`

## 4. Safe Read Scope

- 先に読んでよい場所: `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/db/`, `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/core/`, `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/ui/`
- 先に確認すべき文書: `AGENTS.md`, `implementation-plan_20260405.md`

## 5. Do Not Edit Without Explicit Request

- `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/__pycache__/`
- `%LOCALAPPDATA%/CivitaiDownloader/` の実データ

## 6. Related Boundaries

- UI: `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/ui/`
- 業務ロジック: `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/core/`
- データ層: `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/db/`
- 外部連携: Civitai API, Civitai Web, ローカルファイルシステム

## 7. Risks for Changes

- DB 初期化の扱いを誤ると既存ジョブや設定が失われる
- 未解決ジョブや削除操作の扱いを誤ると利用者が復旧できない
- 行マッピングや一覧更新を誤ると別ジョブへ誤操作が飛ぶ

## 8. Recommended First Step

- `current-state_20260405.md` と `decision_20260405.md` を見て、今回の修正対象を確認する。
- その後に `E:/civitai_downloader/` 側の実装へ入る。

## 9. Rollback Hint

- コード変更は `db`, `core`, `ui` の単位で戻す。
- DB スキーマ変更を入れる場合は、既存データを削除しない方針を維持し、必要なら migration を追加する。

# START HERE

## この project は何か

- `E:/civitai_downloader` にある PySide6 製 Civitai ダウンローダーの巻き取り修正案件です。
- 今回は新機能追加ではなく、既存挙動を保ちながら運用上危険な不具合を優先修正します。

## 最初に読む順番

1. `AGENTS.md`
2. `PROJECT_SUMMARY.md`
3. `implementation-plan_20260405.md`
4. `current-state_20260405.md`
5. `civitai_downloader/` の対象コード

## 正本

- 正本コード: `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/`
- 正本文書: `E:/codex/workspace/projects/civitai-downloader-fix/`
- 実装修正対象: `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/db/`, `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/core/`, `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader/ui/`

## 主要入口

- 通常起動: `python -m civitai_downloader`
- 主な確認方法: 構文確認、対象モジュール単体確認、必要に応じた GUI 起動確認

## 触る前に注意するもの

- 壊してはいけない既存挙動: ブラウズ、キュー追加、手動開始、保存先振り分け、更新通知
- 明示依頼なしで触らないもの: `__pycache__`, `.claude`, アプリデータ実体
- 高リスク: 既存 DB の初期化、進行中ジョブ状態、保存先ファイル移動

## 最初の一手

- まず `implementation-plan_20260405.md` を読み、対象・実装順・確認点・戻し方を把握する。
- 次に `civitai_downloader/db/models.py`, `civitai_downloader/core/download_manager.py`, `civitai_downloader/ui/download_tab.py` を確認する。

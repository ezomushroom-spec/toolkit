# civitai-downloader-fix Rules

## この案件の位置づけ

- このファイルは `E:/codex/workspace/projects/civitai-downloader-fix/civitai_downloader` の巻き取り修正案件に固有の前提だけを扱う。
- Workspace 共通ルールは `E:/codex/workspace/AGENTS.md` を優先する。

## 今回の修正方針

- 新機能追加ではなく、既存運用を止める不具合修正を優先する。
- UI 改修は構造と安全性を優先し、見た目の変更は必要最小限に留める。
- 既存設定キー、保存先形式、ローカルデータの配置は互換維持を基本にする。

## 主に守るべき既存挙動

- Civitai のブラウズとダウンロードキュー追加
- 手動開始と並列ダウンロード
- プリセット保存先または Unsorted への退避
- 更新通知と既読管理

## 高リスク操作

- DB 初期化
- ジョブ削除
- ダウンロード中断
- 保存先移動

## この案件で確認を優先するもの

- 再起動後に設定とジョブが保持されること
- バージョン解決失敗時に詰まらず、失敗理由が見えること
- 一覧からの削除や更新が別ジョブへ誤適用されないこと
- 危険操作に確認と対象明示があること

## build / run / test

- 構文確認: `py_compile`
- 起動確認: `python -m civitai_downloader`
- 追加確認: DB 初期化とジョブ遷移を対象にした軽量スクリプト確認

## 変更時の必須セット作業

- 更新する docs: `START_HERE.md`, `PROJECT_SUMMARY.md`, `implementation-plan_20260405.md`
- 最低限の確認: 構文確認、対象不具合の再現条件と修正後条件の確認
- 未実施確認があれば、理由と残リスクを明示する

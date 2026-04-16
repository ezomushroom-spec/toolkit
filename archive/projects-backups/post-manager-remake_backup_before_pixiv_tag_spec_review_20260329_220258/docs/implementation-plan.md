# Post Manager Remake Implementation Plan

更新日: 2026-03-27

## 対象

- アプリ本体: `E:\自作アプリ集\workspace\projects\post-manager-remake\app`
- 参照用バックアップ: `E:\自作アプリ集\post_manager-fix-browser-close-issue_backup_20260323_025001`
- 目的: 既存機能を保持したまま、Web UI を中心に安全にリメイクする

## 着手前に固定すること

- 正本実装先は `projects/post-manager-remake/app` に固定する
- Web の `全ステップ実行` は `Clean -> MEGA -> Discord` の前処理まとめ実行として扱う
- Discord 通知は `zip_url` を本文へ含める
- 設定保護の初回最低保証は既知キーの値維持とする
- `count / image_count` は初回では派生値扱いとする
- WebSocket ログは初回必須にせず、ポーリング完結を許容する

## 固定した前提

- CLI と Web の入口は温存する
- `manager.py` を業務フローの中心に据える
- `data/posts.csv`、`config/*`、`browser_profile/` は運用資産として保護する
- Pixiv / Patreon は自動入力まで、最終投稿は人手確認に残す
- 変更順は `構造 -> 見た目 -> 安全性`

## keep / fix の要点

### keep

- CSV 列名と列順
- Task / Settings の保存形式
- `mega_password` 空欄時は既存維持
- shared browser context
- browser profile ロック時の retry 導線
- Pixiv / Patreon の手動最終確認フロー

### fix

- Discord 通知で `zip_url` を渡すこと
- `Clean` / `MEGA` の `input()` 依存を Web 経路から切り離すこと

### fix 候補

- WebSocket ログの接続
- `count / image_count` の責務整理
- Task の安定 ID 化

## 実装フェーズ

1. 定義統一
2. CLI 対話経路と Web 非対話経路の分離
3. API / プロセス基盤の固定
4. UI 構造リメイク
5. 見た目と状態安全性の仕上げ
6. 文書更新と切替準備

## 現在地

- Phase 1 の最小実装: 完了
- Phase 2 の最小実装: 完了
- 次の作業: Phase 3
- 実装前判断は `docs/pre-implementation-decision-memo_20260327.md` で固定済み
- 実装開始可能。次の主対象は Phase 3 の API / プロセス基盤固定

## 正本ドキュメント

- 正本実装先は `E:\自作アプリ集\workspace\projects\post-manager-remake\app`
- 実装前の採用案は `docs/pre-implementation-decision-memo_20260327.md` を参照する
- 本体側 docs は次を正本として扱う
  - `E:\自作アプリ集\workspace\projects\post-manager-remake\app\docs\リメイク前提整理_20260327.md`
  - `E:\自作アプリ集\workspace\projects\post-manager-remake\app\docs\リメイク実装前設計_20260327.md`
  - `E:\自作アプリ集\workspace\projects\post-manager-remake\app\docs\リメイク改訂実装計画_20260327.md`

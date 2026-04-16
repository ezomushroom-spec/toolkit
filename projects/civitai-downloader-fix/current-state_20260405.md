# 現状確認 2026-04-05

## 対象

- 対象アプリ: `E:/civitai_downloader`
- UI: PySide6
- データ保存: SQLite + `%LOCALAPPDATA%/CivitaiDownloader/`

## 確認した主要導線

- ブラウズタブから WebView ダウンロードを横取りしてキューへ追加
- ダウンロードタブで手動開始、キャンセル、削除、保存先変更
- 通知タブで追跡モデルの更新チェック
- 設定タブで API キー、同時 DL 数、プリセット管理

## 現時点の主要不具合

- 起動時 DB 初期化で `download_jobs` を毎回削除している
- バージョン解決失敗時にジョブが `pending_unresolved` のまま残り、利用者が失敗理由を見られない
- ダウンロード一覧で削除後の `job_id -> row` 対応が DB 順再構築になっており、表示行とのズレが起きうる
- API 接続テストが UI スレッドで同期実行され、画面を固める
- ジョブ削除が確認なしで即時実行される

## データ影響

- `settings`
- `folder_presets`
- `download_jobs`
- `tracked_models`
- `notifications`

## 正本判断

- コード正本は `E:/civitai_downloader`
- 文書正本は本案件フォルダ
- `%LOCALAPPDATA%/CivitaiDownloader/` は実運用データであり編集対象ではない

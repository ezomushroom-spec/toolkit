# Post Manager 現行仕様書

最終更新日: 2026-03-28  
基準実装:
- `E:\codex\workspace\projects\post-manager-remake\app`
- `E:\codex\workspace\projects\post-manager-remake\desktop-electron`

## 1. 概要

Post Manager は、CSV 管理の投稿タスクをもとに、Pixiv / Patreon / Discord への投稿準備と前処理を支援するローカル運用ツールである。

本アプリは以下の特徴を持つ。

- タスク管理は `posts.csv` ベース
- 前処理として `Clean & Zip`、`MEGA Upload`、`Discord` を実行可能
- `Pixiv` と `Patreon` はブラウザ入力補助までを担当
- 最終投稿・最終公開は手動確認前提
- Web UI と Electron UI は同一の Python backend を利用

## 2. 正本構成

### 2.1 正本アプリ

- 正本実装先: `E:\codex\workspace\projects\post-manager-remake\app`
- Electron シェル: `E:\codex\workspace\projects\post-manager-remake\desktop-electron`

### 2.2 責務分担

- 業務処理の中心は `app/src/manager.py`
- Web UI は `app/src/api_server.py` を通じた操作層
- Electron は `desktop-electron/main.js` による desktop shell
- Electron 専用 backend 起動口は `app/src/api_server_desktop.py`
- 実装の正本は `app/` にあり、Electron はそれを包む主運用シェルとする
- 通常ブラウザ版も動作維持するが、運用上の優先ターゲットは Electron とする

### 2.3 運用資産

- タスク CSV: `app/data/posts.csv`
- 設定: `app/config/secrets.yaml`, `app/config/templates.yaml`
- ブラウザプロファイル: `app/browser_profile/`
- 配布物出力: `app/dist/`

## 3. 起動方式

### 3.1 Web UI

- 起動バッチ: `app/start_webui.bat`
- 起動先: `app/src/api_server.py`
- URL: `http://127.0.0.1:8000/`

### 3.2 CLI

- 起動バッチ: `app/start_cli.bat`
- 起動先: `app/src/manager.py`

### 3.3 Electron

- 起動バッチ: `desktop-electron/start_electron.bat`
- シェル: `desktop-electron/main.js`
- backend 起動先: `app/src/api_server_desktop.py`

### 3.4 Python 解決順

Electron 側では Python 実行環境を次の順で探索する。

1. `.venv\Scripts\python.exe`
2. `venv\Scripts\python.exe`
3. `python`
4. `py -3.10`
5. `py -3`

## 4. タスクデータ仕様

### 4.1 永続項目

`TaskModel` の永続項目は以下のとおり。

- `target_folder`
- `title`
- `caption_pixiv`
- `caption_patreon`
- `caption_discord`
- `tags`
- `schedule`
- `zip_password`
- `patreon_tier`
- `discord_channel`
- `zip_url`

### 4.2 派生項目

派生項目は以下のとおり。

- `count`
- `image_count`

これらは実行時補助値として扱い、正規の永続仕様とはしない。

### 4.3 CSV 保存仕様

- `posts.csv` が存在しない場合、タスク一覧は空配列として扱う
- タスク削除後に 0 件になっても、ヘッダーのみの CSV を書き戻す
- これにより、最後の 1 件削除後に再読み込みでタスクが復活しない

## 5. 設定仕様

### 5.1 保存対象

設定項目は以下のとおり。

- `mega_email`
- `mega_password`
- `discord_webhook_url`
- `template_pixiv`
- `template_patreon`
- `template_discord`

### 5.2 保存動作

- `mega_password` を空欄で保存した場合は既存値を維持する
- 設定保存は既知キー基準で再構築する
- 未知キーやコメントの完全保持は保証しない

## 6. 実行ステップ仕様

### 6.1 定義済みステップ

- `clean`
- `mega`
- `pixiv`
- `patreon`
- `discord`

### 6.2 CLI の全実行

CLI の `--all` は全ステップを順に有効化する。

- `clean`
- `mega`
- `pixiv`
- `patreon`
- `discord`

### 6.3 Web UI のまとめ実行

Web UI の `前処理まとめ実行` は前処理系のみを対象とする。

- `clean`
- `mega`
- `discord`

Pixiv / Patreon は Web UI の `run all` には含めない。

## 7. 各処理の仕様

### 7.1 Clean & Zip

- Pixiv 用画像の clean を行う
- Patreon 配布用 zip を `dist/` に生成する
- 既存 zip がある場合、Web 経由では `skip` 方針で扱う
- 成功時はメモリ上で `count`, `image_count` を設定する

### 7.2 MEGA Upload

- `dist/` の zip をアップロードする
- 成功時は `zip_url` を `posts.csv` に保存する
- 既に `zip_url` があるタスクはスキップする

### 7.3 Pixiv

- Playwright で投稿画面を開く
- 入力補助までを行う
- 最終投稿ボタンの押下は自動化しない
- ブラウザ確認と投稿操作はユーザーが行う

### 7.4 Patreon

- Playwright で作成画面を開く
- 入力補助までを行う
- 最終公開は自動化しない
- 公開操作はユーザーが行う

### 7.5 Discord

- Discord Webhook 通知を送信する
- `zip_url` をテンプレートへ反映する
- 可能な場合はサムネイル画像を付与する

## 8. ブラウザプロフィール仕様

- Pixiv / Patreon は `browser_profile/` を利用する
- ログイン状態はこのプロファイルに保持される
- プロファイルロック時は CLI 側で再試行導線を持つ
- ブラウザは最終確認のため、一定時間ユーザーが触る前提で扱う

## 9. Web API 仕様

### 9.1 主 API

- `GET /api/tasks`
- `POST /api/tasks`
- `PUT /api/tasks/{index}`
- `DELETE /api/tasks/{index}`
- `GET /api/settings`
- `PUT /api/settings`
- `POST /api/run/{step}`
- `GET /api/runtime-status`
- `GET /api/status`
- `GET /api/process/{process_id}`
- `DELETE /api/process/{process_id}`
- `GET /api/browse`
- `POST /api/validate-folder`

### 9.2 共通レスポンス

UI 向けレスポンスは原則として以下を含む。

- `success`
- `message`
- `runtime`

必要に応じて `tasks`, `count`, `process_id`, `requires_user_action` などを追加する。

### 9.3 エラー応答

- `HTTPException` は UI が扱いやすい共通形へ変換する
- 予期しない例外は 500 で返す
- 500 のメッセージは内部実装をそのまま露出せず、再試行やログ確認を促す文面にする

### 9.4 browse API

- 空パス時は Windows ドライブ一覧を返す
- 存在しないパスは `404`
- ディレクトリでないパスは `400`
- これらを `500` に包み直さない

## 10. 実行状態とプロセス管理

### 10.1 runtime 構造

`runtime-status` は主に以下で構成される。

- `execution`
- `active_processes`
- `recent_processes`
- `web_run_all_steps`

### 10.2 execution 項目

- `active`
- `status`
- `step`
- `kind`
- `message`
- `message_level`
- `process_id`
- `elapsed_seconds`

### 10.3 browser process 状態

ブラウザ別プロセスは以下の状態を持つ。

- `running`
- `completed`
- `terminated`
- `failed`

### 10.4 停止仕様

- UI の停止操作には確認ダイアログを出す
- backend 側は `terminate()` 後に終了待機を行う
- 必要なら `kill()` を行う
- 実プロセス終了前に busy 状態を解放しない

## 11. Web UI 仕様

### 11.1 画面構成

Web UI は以下の 3 タブ構成。

- `タスク`
- `設定`
- `ログ`

主運用ターゲットは Electron とし、タスク画面の主操作優先度は以下とする。

- タスク 0 件時: `追加 / フォルダ D&D` を最優先
- タスク 1 件以上: `実行` を強めつつ、追加導線は補助として維持
- 通常ブラウザ互換は残すが、D&D まわりの UX 判断は Electron 優先でよい

### 11.2 タスク画面

タスク画面は左右 2 ペイン構成。

- 左: タスク一覧
- 右: アクション

#### 左ペイン

- タスク一覧ヘッダー
- 更新ボタン
- `フォルダをD&D` ランチャー
- `+ 追加` ボタン
- サマリー
  - 総タスク
  - MEGA完了
  - 未処理
- タスク一覧カード
- 空状態では広い D&D 受け入れ領域と `最初のタスクを追加` ボタンを表示

#### 右ペイン

- ステップ別アクションボタン
- まとめ実行の範囲説明
- `前処理まとめ実行` ボタン
- 実行状態表示
- 進捗バー

### 11.3 タスクカード

各タスクカードには以下を表示する。

- タイトル
- 画像フォルダ
- 完了 / 未処理状態
- 補足メタ情報
- ガイダンス文
- `編集` ボタン
- `削除` ボタン

### 11.4 削除操作

- 対象名つき確認ダイアログを出す
- 処理中は削除不可

### 11.5 実行ボタン制御

- タスク 0 件時は実行系ボタンを無効化
- 処理中は二重実行を防ぐ
- 実行中は進捗と状態表示を出す
- 途中失敗した `前処理まとめ実行` を成功扱いしない

### 11.6 ログ表示

- UI 操作ログを時刻つきで表示
- 最近のプロセス完了 / 停止 / 失敗も表示
- オフライン警告は連投しない

## 12. タスク編集モーダル仕様

### 12.1 基本入力

- `タイトル` 必須
- `画像フォルダ` 必須
- `予約投稿日` は日付と時刻の分離入力
- `Pixivタグ` はスペース区切り

### 12.2 Pixiv 入力

- `tags` は Pixiv 用タグとして扱う
- タグ候補チップを表示する
- 候補クリックで追加する
- 候補は自動確定しない
- 候補の出所は、必要に応じて軽く参照できる形で示す
- `caption_pixiv`

### 12.3 Patreon 入力

- `caption_patreon`
- `patreon_tier`
- `zip_password`

### 12.4 Discord 入力

- `caption_discord`
- `discord_channel`

### 12.5 自動入力項目

- `zip_url` は読み取り専用

### 12.6 時刻入力

- `type="time"` を使用
- 編集時に既存時刻を丸めない
- 保存時は `YYYY/MM/DD HH:MM` 形式へ結合する

## 13. フォルダ選択・D&D 仕様

### 13.1 共通方針

- backend が使うのは Windows 絶対パス前提
- フォルダ検証は backend API で行う

### 13.2 標準ブラウザ

- D&D は補助導線
- 絶対パス取得に失敗する場合がある
- 参照ボタンやフォルダブラウザを優先導線とする

### 13.3 Electron

- D&D を主導線として利用可能
- native bridge を使ってパスを解決する
- フォルダをドロップした場合はそのまま採用
- 画像ファイルをドロップした場合は親フォルダへ寄せる
- 本当に解決できない場合のみネイティブフォルダ選択へフォールバックする

### 13.4 バリデーション

- フォルダが存在すれば valid
- 画像枚数を返す
- 画像 0 枚は warning として扱う

## 14. Electron 版仕様

### 14.1 役割

- Electron は desktop shell
- Python backend を包み込む
- 業務処理を Electron 側へ移植しない

### 14.2 主な機能

- single instance 制御
- backend 自動起動
- backend 既存待受の再利用
- backend ログ出力
- ネイティブフォルダ選択
- ドロップパス正規化

### 14.3 backend ログ

- 保存先: `desktop-electron/runtime/backend.log`
- stdout / stderr を記録する

### 14.4 ネイティブブリッジ

- `dialog:pick-folder`
- `path:normalize-dropped`

## 15. バックアップと移行

- Electron 移行前バックアップ: `archive/projects-backups/backup_app_before_electron_20260328_020023`
- Electron 版は既存 app を置換せず併設
- rollback は `desktop-electron` を使わず `app/start_webui.bat` または `app/start_cli.bat` に戻す形で可能

## 16. 現時点の運用前提

- Web UI と Electron は同一 backend / 同一データを利用する
- `run all` の意味は CLI と Web で異なる
- Pixiv / Patreon の最終操作は手動
- `posts.csv`, `config/*`, `browser_profile/`, `dist/` は保護対象
- UI は `構造 -> 見た目 -> 安全性` の順で改善済み

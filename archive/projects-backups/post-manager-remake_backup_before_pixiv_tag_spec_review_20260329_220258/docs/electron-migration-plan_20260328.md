# Post Manager Electron Migration Plan

更新日: 2026-03-28

## 目的

- 既存の Python / FastAPI / Playwright / CSV / browser_profile の業務処理を温存したまま、UI の実行基盤だけを Electron へ移す。
- D&D やフォルダ選択のようなローカル OS 連携を、通常ブラウザより扱いやすい形へ寄せる。

## 対象

- 既存本体: `E:\自作アプリ集\workspace\projects\post-manager-remake\app`
- 新規 Electron シェル: `E:\自作アプリ集\workspace\projects\post-manager-remake\desktop-electron`

## keep

- `app/src/manager.py` を中心にした業務フロー
- `app/src/api_server.py` の API
- `app/data/posts.csv`
- `app/config/*`
- `app/browser_profile/`
- `app/dist/`
- Pixiv / Patreon の最終手動確認

## fix / 追加

- Electron から Python API サーバーを起動する
- Electron ウィンドウで既存 Web UI を表示する
- 将来の D&D 強化に向けて、通常ブラウザより OS 連携しやすい基盤を用意する

## 関連処理

- Python 起動検出
- API サーバー起動待ち
- Electron 終了時の子プロセス終了
- 将来の IPC 追加余地

## データ影響

- 初回はなし
- `posts.csv`、`config/*`、`browser_profile/` の保存形式は変えない
- 画像運搬処理は Python 側のままにする

## 戻し方

1. `desktop-electron/` を使わず、従来どおり `app/start_webui.bat` で起動する
2. 必要なら `desktop-electron/` を退避または削除する
3. Python 側の本体処理には初回移行では手を入れない

## 実装順

1. 現行 `app` のバックアップを作る
2. Electron シェルを新規追加する
3. Python サーバー起動と待受確認を Electron 側へ実装する
4. Electron で `http://127.0.0.1:8000/` を開く
5. 起動 / 終了 / 異常時表示を整える
6. D&D 強化は次段で扱う

## 備考

- 端末ツール不安定時でも退避できるよう、`create_app_backup.bat` を追加した
- バックアップから Electron 起動までまとめて流せるよう、`prepare_electron_migration.bat` を追加した
- 実バックアップ作成後に、退避先パスをこの文書へ追記する

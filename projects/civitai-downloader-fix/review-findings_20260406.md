# 追加精査レビュー 2026-04-06

## 概要

- 第1段階の修正で主要な破壊不具合は抑えられた
- ただし、終了時の非同期処理、キャンセル/削除時の一時ファイル、一覧・通知まわりの補助導線にはまだ運用リスクが残る

## 優先度順の指摘

### 1. 終了中に DB を閉じたあと、バックグラウンド処理のシグナルが飛ぶ余地が残っている

- 対象: `E:/civitai_downloader/main.py`, `E:/civitai_downloader/core/update_checker.py`, `E:/civitai_downloader/core/download_manager.py`
- 内容:
  - `aboutToQuit` で `download_manager.shutdown()` の直後に `db.close()` している
  - しかし `UpdateChecker` は独立スレッドで走り続け、`new_version_found` / `check_finished` を emit する
  - `RecommendTask` / `VersionResolveTask` も `QThreadPool` 上で継続中の可能性がある
- 想定影響:
  - 終了中に `repo.*` が閉じた DB を触って `RuntimeError` を起こす
  - まれに終了時エラーや不安定終了につながる
- 対応案:
  - 終了フラグを入れてシグナル処理側で DB 更新を止める
  - 可能なら `UpdateChecker` と補助タスクの完了待ちまたは停止処理を追加する

### 2. キャンセルや削除で `.part` 一時ファイルが残り続ける

- 対象: `E:/civitai_downloader/core/download_worker.py`, `E:/civitai_downloader/core/download_manager.py`
- 内容:
  - `DownloadWorker` はキャンセル時に `finished(False, "キャンセル")` を返すだけで `.part` を消さない
  - `delete_job()` は DB 行を先に消すため、その後の完了通知ではクリーンアップに入れない
- 想定影響:
  - `%LOCALAPPDATA%/CivitaiDownloader/Temp` に不要ファイルが蓄積する
  - 同名再開時に古い `.part` を誤って再利用し、破損や混線の原因になる
- 対応案:
  - キャンセル時に `.part` を削除する
  - 削除済みジョブでも temp cleanup だけは行う経路を残す

### 3. 一括追加ダイアログで同一モデルを重複選択・重複投入できる

- 対象: `E:/civitai_downloader/ui/batch_dialog.py`
- 内容:
  - `_append_to_table()` が既存 ID を見ずに行追加する
  - `_on_enqueue()` も重複除去せず選択行をそのまま返す
- 想定影響:
  - ページ切り替えや複数検索で同一モデルを何度もキューに入れられる
  - キュー一覧が重複で汚れ、誤操作や無駄な解決/API 呼び出しが増える
- 対応案:
  - ダイアログ内部で `model_id` ベースの重複排除を入れる
  - 追加件数表示もユニーク件数で出す

### 4. 通知タブの手動チェックは実行中フィードバックが弱い

- 対象: `E:/civitai_downloader/ui/notification_tab.py`
- 内容:
  - `手動チェック実行` はボタン無効化や進行表示がない
  - 実行中に再押下しても `UpdateChecker.start_check()` が内部で無視するだけ
- 想定影響:
  - 利用者には「押せていない」「壊れている」ように見える
  - 手動チェックの完了待ちが分かりづらい
- 対応案:
  - 実行中はボタン無効化とラベル変更を行う
  - `check_finished` で元へ戻す

### 5. 一括追加ダイアログの選択件数表示が手動トグルで追従しない

- 対象: `E:/civitai_downloader/ui/batch_dialog.py`
- 内容:
  - `全選択` / `全解除` では `_update_status()` を呼ぶが、表のチェックを直接変更した場合は更新されない
- 想定影響:
  - 画面表示と実際の選択件数が一致せず、投入前の判断を誤りやすい
- 対応案:
  - `itemChanged` などでチェック列変更時に件数ラベルを更新する

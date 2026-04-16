# 追加精査 2026-04-06

## 対象

- `E:/civitai_downloader/db`
- `E:/civitai_downloader/core`
- `E:/civitai_downloader/ui` のうち状態遷移と危険操作に関わる箇所

## 新たに残件として見つかったもの

### 1. ダウンロード中ジョブの削除で完了レース時に一時ファイルが孤立する

- `DownloadManager.delete_job()` は実行中ジョブでも DB 行を即削除する
- その後にワーカーが完了側へ振れた場合、`_on_download_finished()` は `job` 取得失敗で return し、`result_path` を片付けない
- 結果として `%LOCALAPPDATA%/CivitaiDownloader/Temp` に孤立ファイルが残る可能性がある

### 2. 更新チェックは終了時に停止されず、DB close 後のシグナル処理と競合する可能性がある

- `UpdateChecker` は Python thread を起動するが停止手段がない
- `aboutToQuit` では `db.close()` を先に実行している
- 終了中に `new_version_found` や `check_finished` が UI スレッドへ届くと、閉じた DB に触る競合が起こりうる

### 3. サーバーから返るファイル名を無加工でパス結合している

- `Content-Disposition` の `filename` をそのまま採用している
- `FileMover.move_to_dest()` も無加工で `os.path.join(dest_dir, filename)` を使う
- 想定外の区切り文字や絶対パスが含まれた場合、意図しない場所への書き込みにつながる余地がある

## 低優先だが気になるもの

### 4. キャンセル時の `.part` ファイル残留

- `DownloadWorker._do_download()` はキャンセル時に `finished` を返すだけで `.part` を消さない
- 再開用途としては意味があるが、削除操作と組み合わさると利用者視点ではゴミが残ったように見える

### 5. 失敗ジョブのリトライで進捗値が明示リセットされない

- `retry_job()` は `status` と `error_message` を戻すだけ
- `bytes_downloaded` と `bytes_total` が残るため、失敗内容によっては UI 表示が紛らわしい可能性がある

## 優先度

1. 実行中削除の孤立ファイル
2. 終了時の更新チェック競合
3. ファイル名サニタイズ
4. `.part` 残留
5. リトライ時の進捗リセット

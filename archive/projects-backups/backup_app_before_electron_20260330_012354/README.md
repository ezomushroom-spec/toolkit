# 統合自動投稿ツール

Pixiv、Patreon、Discordへのコンテンツ投稿を半自動化するツールです。
CSVに記述した設定（タイトル、キャプション、タグなど）と画像フォルダを読み込み、前処理からマルチプラットフォームへの投稿までを一括管理します。

## 必要要件

- Windows / Mac / Linux
- Python 3.8+
- Google Chrome (インストール済みであること)
- MEGAアカウント (Zip配布用)

## セットアップ

1. リポジトリをクローンまたはダウンロードします。
2. 依存ライブラリをインストールします。

```bash
pip install -r requirements.txt
playwright install
```

3. 設定ファイルをコピーして編集します。

```bash
cp config/secrets.yaml.sample config/secrets.yaml
cp data/posts.csv.sample data/posts.csv
```

- `config/secrets.yaml` を編集し、認証情報（MEGA、Discord、Patreon）を入力してください。
- `data/posts.csv` を編集し、投稿情報を入力してください。

## ワークフロー

### Phase 1: 前処理

1. **Clean**: 元画像からメタデータ（Exif等）を除去
2. **Zip**: Patreon配布用画像をアーカイブ化
3. **MEGA Upload**: ZipファイルをMEGAへアップロードし、共有URLを取得
4. **Discord**: Webhookで通知を送信（前処理まとめ実行に含める場合あり）

### Phase 2: 投稿

- **Pixiv**: ブラウザ自動化で投稿画面の入力補助まで行う
- **Patreon**: ブラウザ自動化で作成画面の入力補助まで行う
- 最終投稿は Pixiv / Patreon ともにブラウザ上で人が確認して実行する

## 使い方

### 基本的な使い方

1. `data/posts.csv` を編集します（詳細は下記CSVフォーマット参照）。
2. 以下のコマンドでツールを実行します。

```bash
python src/manager.py
```

3. インタラクティブメニューから実行したいステップを選択します。

### Web UI

Web UI を使う場合は、以下で起動します。

```bash
python src/api_server.py
```

- ブラウザで `http://localhost:8000` を開きます
- Web UI の「前処理まとめ実行」は `Clean -> MEGA -> Discord` を順番に実行します
- Pixiv / Patreon は別ウィンドウで起動し、投稿画面の入力補助までを行います

### コマンドラインオプション

個別のステップを直接実行することも可能です。

```bash
python src/manager.py --clean    # Step 1: メタデータ除去 & Zip作成
python src/manager.py --mega     # Step 2: MEGAへアップロード
python src/manager.py --pixiv    # Step 3: Pixivへ投稿
python src/manager.py --patreon  # Step 4: Patreonへ投稿
python src/manager.py --discord  # Step 5: Discord通知
python src/manager.py --all      # 全ステップを順番に実行
```

- CLI の `--all` は `clean / mega / pixiv / patreon / discord` を順番に実行します
- Web UI の「前処理まとめ実行」と CLI の `--all` は同じ意味ではありません

### 投稿フロー

1. Chromeが起動します。
   - 初回はPixiv/Patreonへのログインが必要です。手動でログインしてください。
   - 次回以降は `browser_profile/` に保存されたプロファイル情報で自動ログイン状態になります。
2. スクリプトが入力欄を埋めていきます。
3. 内容を確認し、問題なければブラウザ上で投稿または公開を実行してください。
4. CLI では、確認後に終了時の `Enter` を求められる場合があります。
5. Web UI では、Pixiv / Patreon は別ウィンドウで確認し、UI 側は状態表示と停止導線を担当します。

## CSVフォーマット (`data/posts.csv`)

| カラム名 | 説明 |
| :--- | :--- |
| `target_folder` | 画像フォルダパス（Pixiv/Patreonサブフォルダを含む） |
| `title` | 作品タイトル |
| `caption_pixiv` | Pixiv用キャプション |
| `caption_patreon` | Patreon用キャプション |
| `caption_discord` | Discord用メッセージ |
| `tags` | スペース区切りのタグ |
| `schedule` | 予約投稿日時 (例: `2025/12/01 18:00`) |
| `zip_password` | Zipパスワード (未実装) |
| `patreon_tier` | Patreon公開範囲 |
| `discord_channel` | Discord投稿先チャンネル種別 |
| `zip_url` | (自動入力) MEGAの共有URL |

## 設定ファイル

### `config/secrets.yaml`

認証情報を管理します（Gitで追跡しないでください）。

```yaml
mega:
  email: "your-email@example.com"
  password: "your-password"

discord:
  webhook_url: "https://discord.com/api/webhooks/..."
```

### `config/templates.yaml`

各プラットフォーム用のキャプションテンプレートを定義します。
CSVの値を `{column_name}` の形式で埋め込めます。

```yaml
pixiv: "{caption_pixiv}"
patreon: "{caption_patreon}"
discord: "{caption_discord}"
```

## MEGA連携

- Zipファイルは `dist/` フォルダに作成されます
- MEGAの `PixivUploads` フォルダにアップロードされます
- 共有URLが自動取得され、`posts.csv` の `zip_url` カラムに書き込まれます
- Discordへの通知時にこのURLを本文へ含めます

## ディレクトリ構成

```
post_manager/
├─ src/
│   ├─ manager.py          # 統合実行（メインエントリーポイント）
│   ├─ preprocessor.py     # 前処理 & MEGAアップロード
│   ├─ uploader.py         # Pixiv用アップローダー
│   ├─ uploader_patreon.py # Patreon用アップローダー
│   ├─ uploader_discord.py # Discord Webhook通知
│   └─ verify_mega.py      # MEGA接続検証
├─ data/
│   ├─ posts.csv           # 投稿管理CSV (Git除外)
│   └─ posts.csv.sample    # CSVテンプレート
├─ config/
│   ├─ secrets.yaml        # 認証情報 (Git除外)
│   ├─ secrets.yaml.sample # 認証情報テンプレート
│   └─ templates.yaml      # キャプションテンプレート
├─ dist/                   # Zip出力先 (Git除外)
└─ browser_profile/        # Chromeプロファイル (Git除外)
```

## 画像フォルダ構成

各投稿の `target_folder` は以下の構成を想定しています：

```
target_folder/
├─ Pixiv/           # Pixiv投稿用画像
│   ├─ 001.png
│   └─ 002.png
├─ Patreon/         # Patreon配布用画像（Zip化対象）
│   ├─ 001.png
│   └─ 002.png
└─ patreon_thum.jpg # Discord用サムネイル (オプション)
```

# Pixiv投稿自動化ツール 設計書

**Project:** High-Contrast Fetish Branding (Reboot)  
**Date:** 2025-12-01  
**Author:** AI Assistant

---

## 1. 概要 (Overview)

### 1.1 目的
「生成AIクリエイティブ・マネタイズ再起動プロジェクト」におけるPixiv運用（教育・選別フェーズ）を効率化する。
作品ごとのメタデータ入力や画像アップロードの手間を削減し、**「クリエイティブ制作」と「事務的な投稿作業」を分離**することを目的とする。

### 1.2 コア・コンセプト
*   **Batch Input:** 投稿データ（タイトル、キャプション、タグ）はCSVで一括管理する。
*   **Browser Automation:** Chromeブラウザを自動操作し、人間と同じ挙動で入力を行う。
*   **Human-in-the-Loop:** 誤投稿やBANリスクを回避するため、**「最終的な投稿ボタンのクリック」のみ人間が行う**半自動運用とする。

---

## 2. システム要件 (System Requirements)

### 2.1 技術スタック
*   **言語:** Python 3.x
*   **ライブラリ:** Playwright (Browser Automation)
*   **ブラウザ:** Google Chrome (ユーザープロファイル使用)
*   **認証:** Cookie/Profile利用（ID/PASS入力によるログインは行わず、普段使いのブラウザセッションを流用する）

### 2.2 機能要件
1.  **画像アップロード:** 指定フォルダ内の全画像をドラッグ＆ドロップ（相当）でアップロードする。
2.  **テキスト入力:** タイトル、キャプション、タグをCSVから読み込み自動入力する。
3.  **設定固定:**
    *   年齢制限: **R-18** 固定
    *   AI生成作品: **はい** 固定
    *   公開範囲: 全体に公開
4.  **安全装置:** 全項目の入力完了後、スクリプトは一時停止し、ユーザーの確認を待つ。

---

## 3. データ構造と運用フロー

### 3.1 ディレクトリ構成案

```text
Pixiv_Auto_Uploader/
  │
  ├─ uploader.py          # 実行スクリプト
  ├─ posts.csv            # 投稿キュー（管理ファイル）
  │
  └─ user_data/           # Chromeプロファイル保存用（初回のみ設定必要）
```

### 3.2 CSVフォーマット (`posts.csv`)

Excelやスプレッドシートで管理し、UTF-8のCSVとしてエクスポートする。

| カラム名 | 必須 | 説明 | 例 |
| :--- | :--- | :--- | :--- |
| **target_folder** | ◯ | 画像フォルダの絶対パス | `C:\Obsidian\Private\...\Work01` |
| **title** | ◯ | 作品タイトル | `聖女の堕落 -Scene 1-` |
| **caption** | ◯ | 説明文 (`\n`で改行) | `AI生成です。\nいいねお願いします。` |
| **tags** | ◯ | タグ (スペース区切り) | `オリジナル 女騎士 堕ち R-18` |

### 3.3 運用ワークフロー
1.  **制作:** 画像を生成し、作品ごとにフォルダにまとめる。
2.  **登録:** `posts.csv` にパスと情報を追記する（溜め込み可能）。
3.  **実行:** 投稿作業日（運用日）にスクリプトを実行。
4.  **確認:** 立ち上がったブラウザで内容を確認し、手動で「投稿」ボタンを押す。
5.  **次へ:** コンソールでEnterキーを押し、次の作品の入力へ進む。

---

## 4. 実装詳細 (Implementation Details)

### 4.1 UI要素の特定戦略
PixivのUI変更に強くするため、CSSクラス名（ランダム文字列）ではなく、**ユーザーに見えているテキスト（Label, Placeholder）** を基準に要素を特定する。

*   **タイトル:** `placeholder="タイトル"`
*   **キャプション:** `textarea` 要素
*   **タグ:** `placeholder="タグ"` への入力 + `Enter` キー送信
*   **R-18:** ラベルテキスト "R-18" を含む要素をクリック
*   **AI生成:** ラベルテキスト "AI生成作品" セクション内の "はい" をクリック

### 4.2 Pythonコード設計案

```python
import csv
import os
import time
from playwright.sync_api import sync_playwright

CSV_PATH = "posts.csv"
USER_DATA_DIR = "./user_data" # ログイン情報の保持

def main():
    with open(CSV_PATH, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        tasks = list(reader)

    with sync_playwright() as p:
        # 既存のChromeプロファイルに近い環境で起動
        browser = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            channel="chrome",
            args=["--start-maximized"]
        )
        page = browser.new_page()

        for task in tasks:
            print(f"Process: {task['title']}")
            
            # 投稿画面へ遷移
            page.goto("https://www.pixiv.net/upload.php")
            
            # 画像アップロード
            img_dir = task['target_folder']
            files = [os.path.join(img_dir, f) for f in os.listdir(img_dir) if f.lower().endswith(('.png', '.jpg'))]
            files.sort()
            page.locator('input[type="file"]').set_input_files(files)
            
            # 各種テキスト入力
            page.get_by_placeholder("タイトル").fill(task['title'])
            page.locator("textarea").first.fill(task['caption'].replace('\\n', '\n'))
            
            # タグ入力
            tag_input = page.get_by_placeholder("タグ", exact=False)
            for tag in task['tags'].split():
                tag_input.fill(tag)
                tag_input.press("Enter")
                time.sleep(0.1)

            # R-18 / AI設定（UI上のテキストからクリック）
            page.get_by_text("R-18", exact=True).click()
            
            # "AI生成作品"セクションの"はい"を探す簡易ロジック
            # (実際のDOM構造に合わせて調整)
            ai_section = page.locator("div").filter(has_text="AI生成作品").last
            ai_section.get_by_text("はい", exact=True).click()

            print(f"Done: {task['title']}")
            print(">>> ブラウザで確認し、'投稿'ボタンを手動で押してください。")
            input(">>> 完了したらEnterを押して次へ進みます...")

        print("All tasks finished.")
        browser.close()

if __name__ == "__main__":
    main()
```

---

## 5. 今後の拡張性 (Out of Scope)

*   **FANBOX連携:** Pixiv投稿完了後に、FANBOXの「全体公開記事」として誘導リンクを自動作成する機能。
*   **シリーズ機能:** CSVにシリーズIDカラムを追加し、特定のシリーズに追加する機能。
*   **予約投稿:** CSVに日時カラムを追加し、Pixivの予約投稿機能を操作する機能。

まずは「基本投稿」の効率化を最優先とし、これらは運用が安定した後のフェーズ2とする。


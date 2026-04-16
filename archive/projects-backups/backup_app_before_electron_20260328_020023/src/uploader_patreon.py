"""
Post Manager - Patreon投稿モジュール
Patreonへのブラウザ自動化投稿を担当
"""

import os
import time
from playwright.sync_api import sync_playwright

from config import Paths
from utils import launch_browser, resolve_path

def upload_patreon(tasks, browser_context=None):
    """
    Patreonへの投稿処理 (ブラウザ自動化)
    """
    if not tasks: return

    print("=== Patreon Uploader Started ===")
    
    # ブラウザコンテキストの取得または起動
    browser = browser_context
    should_stop_p = False
    p = None

    if browser is None:
        try:
            browser, p, should_stop_p = launch_browser()
        except Exception as e:
            print(f"Error launching browser: {e}")
            return

    opened_pages = []
    
    # ログイン確認
    target_url = "https://www.patreon.com/posts/new?postType=text_only"
    
    # ログインチェック用の一時ページ作成を削除。
    # uploader.pyと同様、各タスク処理内で処理する。

    for task in tasks:
        print(f"Setting up Patreon tab for: {task.get('title')}")
        page = browser.new_page()
        page.goto(target_url)
        
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
            
            # サムネイル画像検索 (target_folder直下の patreon_thum*)
            base_dir = task.get('target_folder', '')
            resolved = resolve_path(base_dir)
            base_dir = str(resolved)
            
            thumb_file = None
            if os.path.exists(base_dir):
                for f in os.listdir(base_dir):
                    if "patreon_thum" in f.lower() and f.lower().endswith(('.jpg', '.jpeg', '.png')):
                        thumb_file = os.path.join(base_dir, f)
                        break
            
            # --- 画像アップロード (Imageボタンクリック -> ファイル選択) ---
            if thumb_file:
                print(f"  Found thumbnail: {os.path.basename(thumb_file)}")
                
                # 1. input#mainMedia があれば直接トライ
                file_input = page.locator('input#mainMedia')
                if file_input.count() > 0:
                    print("  Using input#mainMedia directly.")
                    file_input.set_input_files(thumb_file)
                    time.sleep(3)
                else:
                    # 2. なければ "Image" ボタンなどを押してUIを出す
                    image_btn = page.locator("button").filter(has_text="Image").first
                    if image_btn.count() > 0:
                        image_btn.click()
                        time.sleep(1)
                    
                    # 3. 再度 input#mainMedia を探す
                    file_input = page.locator('input#mainMedia')
                    if file_input.count() > 0:
                         print("  Using input#mainMedia after clicking Image.")
                         file_input.set_input_files(thumb_file)
                         time.sleep(3)
                    else:
                        # 4. それでもなければ "Browse" ボタンを探して FileChooser を使う
                        # 提供されたHTML: <button ...>Browse,</button>
                        browse_btn = page.locator("button").filter(has_text="Browse").first
                        if browse_btn.count() > 0:
                            print("  Clicking 'Browse' button with FileChooser...")
                            try:
                                with page.expect_file_chooser(timeout=5000) as fc_info:
                                    browse_btn.click()
                                file_chooser = fc_info.value
                                file_chooser.set_files(thumb_file)
                                time.sleep(3)
                            except Exception as e:
                                print(f"  Error with FileChooser: {e}")
                        else:
                            # 汎用的な input[type=file]
                            file_input = page.locator('input[type="file"]').first
                            if file_input.count() > 0:
                                file_input.set_input_files(thumb_file)
                            else:
                                print("  Warning: No file input or Browse button found.")
            else:
                print("  Warning: 'patreon_thum' image not found in target folder.")

            # --- タイトル入力 ---
            # placeholder="Title"
            title_input = page.get_by_placeholder("Title")
            if title_input.count() > 0:
                title_input.fill(task.get('title'))
            else:
                print("  Warning: Title input not found.")

            # --- 本文入力 (caption) ---
            # "Start writing..." のエリアを探す
            # contenteditable="true" を持つ要素が有力
            editor = page.locator("[contenteditable='true']").first
            
            # 見つからない場合、placeholder="Start writing..." を持つ要素を探す
            if editor.count() == 0:
                    editor = page.get_by_text("Start writing...", exact=True).first
            
            if editor.count() > 0:
                editor.click()
                # JSで流し込む (改行は <p> タグなどで表現される可能性があるが、とりあえず <br> で試行)
                # PatreonのエディタはProseMirrorの場合、innerHTML操作は危険だが、
                # 初期状態への流し込みなら動くことが多い。
                # 安全策: typeで入力
                # しかし長いと遅い。
                # innerTextに入れてみる
                
                caption_text = task.get('caption', '')
                # Playwrightの fill は contenteditable には効かないことがあるが、最新版では対応している場合も。
                # まずは fill を試す
                try:
                    editor.fill(caption_text)
                except:
                    # 失敗したらJS
                    # 改行を考慮して textContent ではなく innerHTML ?
                    # シンプルに改行コードを含んだテキストをクリップボード経由ペーストが最強だが…
                    # ここではJSで innerText に設定
                        editor.evaluate(f"el => el.innerText = `{caption_text}`")

            else:
                print("  Warning: Editor 'Start writing...' not found.")

            print("  -> Opened create page. Please review.")
            
        except Exception as e:
            print(f"  Error preparing tab: {e}")
            import traceback
            traceback.print_exc()
        
        opened_pages.append(page)
        time.sleep(1)
        
    print("\nAll Patreon tabs opened.")
    print(">>> Please review and publish manually.")
    # input(">>> Press Enter to finish Patreon process...")
    
    # browser.close()
    return browser

if __name__ == "__main__":
    pass

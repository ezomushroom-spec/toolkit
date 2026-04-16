"""
Post Manager - 前処理・MEGAアップロードモジュール
画像のメタデータ除去とZip作成、MEGAへのアップロードを担当
"""

import os
import shutil
import zipfile
import time
from PIL import Image
from tqdm import tqdm

# パッチ: mega.py用
import asyncio
if not hasattr(asyncio, 'coroutine'):
    def coroutine(func): return func
    asyncio.coroutine = coroutine

try:
    from mega import Mega
except ImportError as e:
    print(f"Warning: Failed to import 'mega': {e}")
    Mega = None

# --- パッチ終了 ---

from config import Paths, DIST_DIR
from utils import load_secrets
from app_schema import (
    EXISTING_FILE_POLICY_OVERWRITE,
    EXISTING_FILE_POLICY_PROMPT,
    EXISTING_FILE_POLICY_SKIP,
)

def clean_and_zip(target_folder, title, password=None):
    """
    1. Pixiv画像のメタデータを除去（元ファイル上書き）
    2. Patreon画像のメタデータを除去 + Zip圧縮
    """
    if not os.path.exists(DIST_DIR):
        os.makedirs(DIST_DIR)

    pixiv_dir = os.path.join(target_folder, "Pixiv")
    patreon_dir = os.path.join(target_folder, "Patreon")

    # --- 1. Pixiv: clean only (上書き保存) ---
    if os.path.exists(pixiv_dir):
        pixiv_files = [f for f in os.listdir(pixiv_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if pixiv_files:
            print(f"Cleaning {len(pixiv_files)} Pixiv images (in-place)...")
            for f in tqdm(pixiv_files, desc="Cleaning Pixiv", unit="img"):
                src_path = os.path.join(pixiv_dir, f)
                try:
                    img = Image.open(src_path)
                    if f.lower().endswith('.png'):
                        img.save(src_path, "PNG")
                    else:
                        img.save(src_path, "JPEG", quality=100, subsampling=0)
                except Exception as e:
                    print(f"Error cleaning {f}: {e}")

    # --- 2. Patreon: clean + zip ---
    if not os.path.exists(patreon_dir):
        print(f"Warning: Patreon folder not found at {patreon_dir}. Skipping zip.")
        return None, 0

    folder_name = os.path.basename(os.path.normpath(target_folder))
    safe_name = "".join([c for c in folder_name if c.isalnum() or c in (' ', '-', '_', '.')]).strip()
    
    temp_dir = os.path.join(DIST_DIR, f"temp_{safe_name}")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    files = [f for f in os.listdir(patreon_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    files.sort()
    
    if not files:
        print(f"Warning: No images found in {patreon_dir}")
        shutil.rmtree(temp_dir)
        return None, 0

    processed_files = []
    
    print(f"Processing {len(files)} images...")
    for f in tqdm(files, desc="Cleaning Images", unit="img"):
        src_path = os.path.join(patreon_dir, f)
        dst_path = os.path.join(temp_dir, f)
        
        try:
            img = Image.open(src_path)
            if f.lower().endswith('.png'):
                img.save(dst_path, "PNG")
            else:
                img.save(dst_path, "JPEG", quality=100, subsampling=0)
            processed_files.append(dst_path)
        except Exception as e:
            print(f"Error processing image {f}: {e}")

    zip_name = f"{safe_name}.zip"
    zip_path = os.path.join(DIST_DIR, zip_name)
    
    print(f"Creating Zip: {zip_name}")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in tqdm(processed_files, desc="Compressing", unit="file"):
            zf.write(f, os.path.basename(f))
            
    shutil.rmtree(temp_dir)
    
    print(f"Zip created: {zip_path} (Count: {len(processed_files)})")
    return zip_path, len(processed_files)

def upload_to_mega(zip_path, existing_file_policy=EXISTING_FILE_POLICY_PROMPT):
    """ZipをMEGAにアップロードし、URLを返す"""
    if Mega is None:
        print("MEGA module not loaded.")
        return None

    secrets = load_secrets()
    if not secrets:
        print("Secrets not found.")
        return None
        
    email = secrets.get('mega', {}).get('email')
    password = secrets.get('mega', {}).get('password')
    
    if not email or not password:
        print("MEGA credentials missing.")
        return None

    try:
        mega = Mega()
        m = mega.login(email, password)
        
        # フォルダ名変更: クリーンな状態にする
        UPLOAD_FOLDER = "PixivUploads" 
        folder_handle = None
        
        found = m.find(UPLOAD_FOLDER)
        
        if found:
             if isinstance(found, list):
                 folder_handle = found[0]
             elif isinstance(found, tuple):
                 folder_handle = found[0]
             elif isinstance(found, str):
                 folder_handle = found

        if not folder_handle:
            print(f"Creating folder: {UPLOAD_FOLDER}")
            details = m.create_folder(UPLOAD_FOLDER)
            
            # 待機時間を長めに取る
            time.sleep(5)
            
            # 再検索してハンドルを取得（作成時の戻り値を信用せず、findで確実に見つける）
            found = m.find(UPLOAD_FOLDER)
            if found:
                if isinstance(found, list): folder_handle = found[0]
                elif isinstance(found, tuple): folder_handle = found[0]
                elif isinstance(found, str): folder_handle = found
            else:
                # 念のためもう一度だけ作成時の戻り値をチェック
                if isinstance(details, dict) and 'f' in details:
                    folder_handle = details['f'][0]['h']
                else:
                    raise Exception("Could not retrieve handle for created folder.")
        else:
            print(f"Using existing folder: {UPLOAD_FOLDER} (Handle: {folder_handle})")

        target_filename = os.path.basename(zip_path)
        print(f"Checking if {target_filename} exists in MEGA upload folder...")
        
        files = m.get_files()
        existing_node = None
        
        for node_id, node in files.items():
            if node['a']['n'] == target_filename and node['p'] == folder_handle:
                existing_node = node
                break
        
        upload_name = zip_path
        final_filename = target_filename

        if existing_node:
            print(f"File '{target_filename}' already exists in MEGA folder.")
            choice = existing_file_policy
            if existing_file_policy == EXISTING_FILE_POLICY_PROMPT:
                while True:
                    choice = input("File exists. [S]kip / [O]verwrite? (s/o): ").strip().lower()
                    if choice in ['s', 'skip', 'o', 'overwrite']:
                        break
                    print("Please enter 's' or 'o'.")

            if choice in ['s', EXISTING_FILE_POLICY_SKIP]:
                print("Skipping upload.")
                link = m.get_link(existing_node)
                print(f"Existing Link: {link}")
                return link

            if choice in ['o', EXISTING_FILE_POLICY_OVERWRITE]:
                print("Overwriting... (Deleting old file)")
                m.destroy(existing_node['h'])
            else:
                raise ValueError(f"Unknown existing_file_policy: {existing_file_policy}")

        print(f"Uploading {target_filename}...")
        res = m.upload(zip_path, dest=folder_handle)
        
        if isinstance(res, dict):
             link = m.get_upload_link(res)
        else:
             link = m.get_upload_link(res)

        print(f"Mega Link: {link}")
        return link
        
    except Exception as e:
        print(f"MEGA Upload Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    pass

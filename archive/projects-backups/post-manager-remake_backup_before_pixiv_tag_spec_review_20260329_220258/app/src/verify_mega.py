import os
import sys
import yaml

# パッチ: tenacityのバージョン非互換問題への暫定対応
try:
    from mega import Mega
except AttributeError:
    import asyncio
    if not hasattr(asyncio, 'coroutine'):
        def coroutine(func):
            return func
        asyncio.coroutine = coroutine
    from mega import Mega

def load_secrets():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "secrets.yaml")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading secrets.yaml: {e}")
        return None

def find_or_create_folder(mega_instance, folder_name):
    """指定したフォルダを探し、なければ作成する"""
    print(f"Searching for folder: {folder_name}...")
    files = mega_instance.get_files()
    
    target_folder = None
    for node_id, node_data in files.items():
        if node_data['a']['n'] == folder_name and node_data['t'] == 2: 
            target_folder = node_id
            print(f"Found existing folder: {folder_name} (ID: {node_id})")
            break
    
    if not target_folder:
        print(f"Creating folder: {folder_name}...")
        details = mega_instance.create_folder(folder_name)
        if isinstance(details, dict) and 'f' in details:
            target_folder = details['f'][0]['h']
        else:
            target_folder = mega_instance.find(folder_name)[0]
        print(f"Created folder: {folder_name} (ID: {target_folder})")
            
    return target_folder

def main():
    print("=== MEGA Upload Verification ===")
    
    secrets = load_secrets()
    if not secrets:
        return
    
    email = secrets.get('mega', {}).get('email')
    password = secrets.get('mega', {}).get('password')
    
    if not email or not password or "YOUR_EMAIL" in email:
        print("Error: Please set your MEGA email and password in config/secrets.yaml")
        return

    try:
        print(f"Logging in as {email}...")
        mega = Mega()
        m = mega.login(email, password)
        print("Login successful!")
        
        UPLOAD_FOLDER = "upload_test"
        folder_handle = find_or_create_folder(m, UPLOAD_FOLDER)
        
        if not folder_handle:
            print("Error: Could not determine upload folder handle.")
            return

        test_file = "mega_test_upload_v2.txt"
        with open(test_file, "w") as f:
            f.write("This is a test upload to a specific folder from Pixiv Auto Uploader.")
            
        print(f"Uploading {test_file} to folder '{UPLOAD_FOLDER}'...")
        # file_handle はAPIレスポンスそのもの
        upload_res = m.upload(test_file, dest=folder_handle)
        print("Upload successful!")
        
        # get_upload_link は upload() の戻り値をそのまま渡す仕様
        print("Getting public link...")
        
        # APIのレスポンス構造がdictであることを確認
        if isinstance(upload_res, dict):
            link = m.get_upload_link(upload_res)
        else:
            # もしオブジェクトなら直接渡す（が、通常はdict）
            link = m.get_upload_link(upload_res)
            
        print(f"\n>>> Public Link: {link}\n")
        
        os.remove(test_file)
        print("Test completed.")
        
    except Exception as e:
        print(f"Error during MEGA operation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

import requests
import yaml
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "secrets.yaml")

def load_secrets():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except:
        return None

def send_discord_notification(webhook_url, title, message, zip_url=None, image_path=None):
    """
    DiscordにWebhookで通知を送る
    """
    if not webhook_url or "YOUR_WEBHOOK" in webhook_url:
        print("Invalid Webhook URL.")
        return False

    content = f"**{title}**\n{message}"
    if zip_url:
        content += f"\n\nDownload: {zip_url}"

    payload = {
        "content": content
    }
    
    files = {}
    if image_path and os.path.exists(image_path):
        # 画像を添付
        files = {
            "file": open(image_path, "rb")
        }

    try:
        if files:
            response = requests.post(webhook_url, data=payload, files=files)
        else:
            response = requests.post(webhook_url, json=payload)
            
        if 200 <= response.status_code < 300:
            print("Discord notification sent.")
            return True
        else:
            print(f"Discord Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Discord Request Error: {e}")
        return False
    finally:
        if files:
            files["file"].close()





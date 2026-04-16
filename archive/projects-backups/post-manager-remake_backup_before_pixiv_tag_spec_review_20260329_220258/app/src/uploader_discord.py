"""
Post Manager - Discord通知モジュール
DiscordにWebhookで通知を送信
"""

import os
import requests

from utils import load_secrets

def send_discord_notification(webhook_url, title, message, zip_url=None, image_path=None):
    """
    DiscordにWebhookで通知を送る
    """
    if not webhook_url or "YOUR_WEBHOOK" in webhook_url:
        print("Invalid Webhook URL.")
        return False

    content = f"**{title}**\n{message}"
    if zip_url and zip_url not in content:
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




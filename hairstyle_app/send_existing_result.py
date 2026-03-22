#!/usr/bin/env python3
"""
发送已生成的即梦发型图片到 Telegram
"""

import os
import requests
from io import BytesIO
from dotenv import load_dotenv

load_dotenv('/root/.openclaw/workspace/.env')

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6598565346")

# 最新的生成结果图片
RESULT_IMAGE = "/tmp/hairstyle_result_4673239561356763377_1.jpg"

def send_photo_to_telegram(image_path: str, caption: str = "") -> bool:
    """发送本地图片到 Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN 未设置")
        print("💡 请编辑 .env 文件并设置您的 Bot Token")
        return False
    
    if TELEGRAM_BOT_TOKEN == "待填写":
        print("❌ TELEGRAM_BOT_TOKEN 仍为 '待填写'")
        print("💡 请编辑 /root/.openclaw/workspace/.env 文件，将")
        print("   TELEGRAM_BOT_TOKEN=待填写")
        print("   修改为实际的 Token，例如:")
        print("   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    
    try:
        with open(image_path, 'rb') as f:
            files = {'photo': f}
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'caption': caption[:1024] if caption else "🎨 即梦 AI 生成的发型图片",
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, files=files, data=payload, timeout=60)
            result = response.json()
            
            if result.get("ok"):
                print(f"✅ 图片已发送到 Telegram")
                return True
            else:
                print(f"❌ 发送失败: {result}")
                return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🎨 发送即梦生成的发型图片到 Telegram")
    print("=" * 60)
    
    if not os.path.exists(RESULT_IMAGE):
        print(f"❌ 图片不存在: {RESULT_IMAGE}")
        print("💡 请先运行 test_and_send_v3.py 生成图片")
        exit(1)
    
    print(f"📷 图片: {RESULT_IMAGE}")
    print(f"📊 大小: {os.path.getsize(RESULT_IMAGE) / 1024 / 1024:.2f} MB")
    print(f"💬 Chat ID: {TELEGRAM_CHAT_ID}")
    
    success = send_photo_to_telegram(
        RESULT_IMAGE,
        "🎨 <b>即梦 AI 发型生成测试成功!</b>\n\n发型: 自然蓬松的大波浪卷发"
    )
    
    if success:
        print("\n✅ 图片已成功发送到 Telegram!")
    else:
        print("\n❌ 发送失败")
        print("\n💡 如果尚未设置 Telegram Bot Token，请:")
        print("1. 访问 @BotFather 创建 Bot 并获取 Token")
        print("2. 编辑 /root/.openclaw/workspace/.env 文件")
        print("3. 设置 TELEGRAM_BOT_TOKEN=您的实际Token")

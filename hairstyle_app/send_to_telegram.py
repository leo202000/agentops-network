#!/usr/bin/env python3
"""
发送即梦生成的发型图片到 Telegram
支持发送图片 URL 或本地图片文件
"""

import os
import sys
import json
import requests
from pathlib import Path

# Telegram Bot 配置
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")


def send_message_to_telegram(message: str, chat_id: str = None) -> bool:
    """发送文本消息到 Telegram"""
    token = TELEGRAM_BOT_TOKEN
    chat = chat_id or TELEGRAM_CHAT_ID
    
    if token == "YOUR_BOT_TOKEN" or chat == "YOUR_CHAT_ID":
        print("❌ 请先设置 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID 环境变量")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()
        if result.get("ok"):
            print(f"✅ 消息已发送到 Telegram")
            return True
        else:
            print(f"❌ 发送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 发送错误: {e}")
        return False


def send_photo_to_telegram(photo_path: str, caption: str = "", chat_id: str = None) -> bool:
    """发送本地图片到 Telegram"""
    token = TELEGRAM_BOT_TOKEN
    chat = chat_id or TELEGRAM_CHAT_ID
    
    if token == "YOUR_BOT_TOKEN" or chat == "YOUR_CHAT_ID":
        print("❌ 请先设置 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID 环境变量")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    try:
        with open(photo_path, 'rb') as photo_file:
            files = {'photo': photo_file}
            payload = {
                'chat_id': chat,
                'caption': caption[:1024] if caption else "",  # Telegram 限制
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
        print(f"❌ 发送错误: {e}")
        return False


def send_photo_url_to_telegram(photo_url: str, caption: str = "", chat_id: str = None) -> bool:
    """发送图片 URL 到 Telegram"""
    token = TELEGRAM_BOT_TOKEN
    chat = chat_id or TELEGRAM_CHAT_ID
    
    if token == "YOUR_BOT_TOKEN" or chat == "YOUR_CHAT_ID":
        print("❌ 请先设置 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID 环境变量")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        "chat_id": chat,
        "photo": photo_url,
        "caption": caption[:1024] if caption else "",
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()
        if result.get("ok"):
            print(f"✅ 图片 URL 已发送到 Telegram")
            return True
        else:
            print(f"❌ 发送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 发送错误: {e}")
        return False


def load_task_result(result_file: str = "/tmp/hairstyle_result.json") -> dict:
    """加载任务结果"""
    try:
        with open(result_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 无法加载结果文件: {e}")
        return {}


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='发送即梦生成的发型图片到 Telegram')
    parser.add_argument('--file', '-f', help='本地图片文件路径')
    parser.add_argument('--url', '-u', help='图片 URL')
    parser.add_argument('--result', '-r', default='/tmp/hairstyle_result.json', 
                        help='任务结果 JSON 文件路径')
    parser.add_argument('--caption', '-c', default='', help='图片说明文字')
    parser.add_argument('--chat-id', help='目标聊天 ID（覆盖环境变量）')
    
    args = parser.parse_args()
    
    # 优先使用命令行参数，其次从结果文件加载
    if args.file:
        # 发送本地文件
        caption = args.caption or "🎨 即梦 AI 生成的发型图片"
        success = send_photo_to_telegram(args.file, caption, args.chat_id)
    elif args.url:
        # 发送 URL
        caption = args.caption or "🎨 即梦 AI 生成的发型图片"
        success = send_photo_url_to_telegram(args.url, caption, args.chat_id)
    else:
        # 从结果文件加载
        result = load_task_result(args.result)
        if not result:
            print("❌ 没有找到结果文件，请先生成图片或指定 --file 或 --url")
            sys.exit(1)
        
        task_id = result.get('task_id', 'unknown')
        status = result.get('status', 'unknown')
        image_urls = result.get('image_urls', [])
        
        # 发送状态消息
        status_msg = f"""🎨 <b>即梦发型生成结果</b>

🆔 任务 ID: <code>{task_id}</code>
📊 状态: {status}
🖼️ 图片数量: {len(image_urls)}
"""
        send_message_to_telegram(status_msg, args.chat_id)
        
        # 发送图片
        if image_urls:
            for i, img_url in enumerate(image_urls[:4], 1):  # 最多发送 4 张
                caption = f"🎨 即梦 AI 生成的发型图片 #{i}"
                success = send_photo_url_to_telegram(img_url, caption, args.chat_id)
                if not success:
                    # 如果 URL 发送失败，尝试下载后发送
                    try:
                        import urllib.request
                        local_path = f"/tmp/hairstyle_result_{i}.jpg"
                        urllib.request.urlretrieve(img_url, local_path)
                        send_photo_to_telegram(local_path, caption, args.chat_id)
                    except Exception as e:
                        print(f"❌ 下载并发送图片失败: {e}")
        else:
            print("⚠️ 结果中没有图片 URL")
            success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

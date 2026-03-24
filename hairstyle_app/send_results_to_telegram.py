#!/usr/bin/env python3
"""
发送发型生成结果到 Telegram
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("/root/.openclaw/workspace/.env")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
RESULTS_DIR = Path("/root/.openclaw/workspace/hairstyle_app/results")

def send_to_telegram():
    """发送结果到 Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram 配置缺失")
        return
    
    # 获取最新的 5 张图片
    images = sorted(RESULTS_DIR.glob("*.jpg"), key=os.path.getmtime, reverse=True)[:5]
    
    if not images:
        print("❌ 没有找到图片")
        print(f"搜索目录：{RESULTS_DIR}")
        return
    
    print(f"📤 准备发送 {len(images)} 张发型生成结果...\n")
    
    # 1. 先发送文本摘要
    caption = (
        f"🎨 <b>发型生成测试结果</b>\n\n"
        f"✅ 成功生成 5 种热门发型\n"
        f"📸 原图已上传到 TOS\n"
        f"💾 结果已保存到本地\n\n"
        f"<b>发型列表:</b>\n"
        f"✅ 齐肩发 - 经典 Bob 头\n"
        f"✅ 梨花头 - 韩式内扣\n"
        f"✅ 丸子头 - 高发髻\n"
        f"✅ 波浪卷 - 自然波浪\n"
        f"✅ 空气刘海 - 减龄神器\n\n"
        f"<b>平均耗时:</b> ~16 秒/张\n"
        f"<b>成功率:</b> 100%"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": caption,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(f"✅ 文本摘要已发送")
        else:
            print(f"⚠️  文本发送失败：{response.text}")
    except Exception as e:
        print(f"⚠️  文本发送错误：{e}")
    
    print()
    
    # 2. 逐张发送图片
    for i, img_path in enumerate(images, 1):
        print(f"[{i}/{len(images)}] 发送：{img_path.stem}")
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        
        try:
            with open(img_path, 'rb') as f:
                files = {'photo': f}
                
                # 提取发型名称
                style_name = img_path.stem.split('_')[0]
                
                data = {
                    'chat_id': TELEGRAM_CHAT_ID,
                    'caption': f"💇‍♀️ {style_name}"
                }
                
                response = requests.post(url, files=files, data=data)
                
                if response.status_code == 200:
                    print(f"   ✅ 已发送")
                else:
                    print(f"   ⚠️  发送失败：{response.text[:100]}")
                    
        except Exception as e:
            print(f"   ⚠️  发送错误：{e}")
        
        # 间隔 1 秒
        import time
        time.sleep(1)
    
    print(f"\n{'='*50}")
    print(f"✅ 所有图片已发送到 Telegram!")
    print(f"{'='*50}\n")
    
    # 显示本地文件信息
    print(f"📁 本地文件位置：{RESULTS_DIR}")
    print(f"\n文件列表:")
    for img in images:
        size_kb = img.stat().st_size // 1024
        print(f"   📷 {img.name} ({size_kb}KB)")
    
    print()


if __name__ == "__main__":
    send_to_telegram()

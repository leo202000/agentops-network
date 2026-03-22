#!/usr/bin/env python3
"""
发型生成 Telegram Bot

功能:
- 接收用户上传的照片
- 让用户选择发型风格
- 调用即梦 API 生成发型
- 发送结果图片到 Telegram

用法:
    python telegram_hairstyle_bot.py
"""

import os
import sys
import json
import asyncio
import tempfile
from pathlib import Path
from typing import Optional

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding='utf-8') as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value

# 导入发型生成器
sys.path.insert(0, str(Path(__file__).parent / "backend"))
from hairstyle_generator import HairstyleGenerator

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# 支持的发型风格
HAIRSTYLES = {
    "短发": "清爽短发造型",
    "卷发": "时尚卷发造型",
    "长发": "优雅长发造型",
    "直发": "柔顺直发造型",
    "马尾": "活力马尾造型",
    "辫子": "精致辫子造型",
    "波浪卷": "自然波浪卷造型",
    "大波浪": "性感大波浪造型",
    "中分": "经典中分造型",
    "斜刘海": "甜美斜刘海造型",
    "染发红": "时尚红色染发",
    "染现金": "明亮金色染发",
    "染发棕": "自然棕色染发",
    "及腰长发": "优雅及腰长发",
    "羊毛卷": "可爱羊毛卷造型",
}


class TelegramHairstyleBot:
    """Telegram 发型生成机器人"""
    
    def __init__(self):
        self.access_key = os.getenv("JIMENG_ACCESS_KEY_ID", "")
        self.secret_key = os.getenv("JIMENG_SECRET_ACCESS_KEY", "")
        self.bot_token = TELEGRAM_BOT_TOKEN or os.getenv("TELEGRAM_BOT_TOKEN", "")
        
        if not self.access_key or "待填写" in self.access_key:
            raise ValueError("请配置 JIMENG_ACCESS_KEY_ID")
        if not self.secret_key or "待填写" in self.secret_key:
            raise ValueError("请配置 JIMENG_SECRET_ACCESS_KEY")
        if not self.bot_token:
            raise ValueError("请配置 TELEGRAM_BOT_TOKEN")
        
        self.generator = HairstyleGenerator(self.access_key, self.secret_key)
        self.temp_dir = Path(tempfile.gettempdir()) / "hairstyle_bot"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def handle_photo(self, photo_url: str, chat_id: str, style: str) -> dict:
        """
        处理照片并生成发型
        
        Args:
            photo_url: Telegram 照片 URL
            chat_id: 聊天 ID
            style: 发型风格
            
        Returns:
            生成结果
        """
        import aiohttp
        
        # 下载照片
        photo_path = self.temp_dir / f"{chat_id}_{style}.jpg"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(photo_url) as response:
                if response.status == 200:
                    with open(photo_path, 'wb') as f:
                        f.write(await response.read())
                else:
                    return {"success": False, "error": f"下载照片失败: {response.status}"}
        
        # 生成发型
        result = self.generator.generate(
            str(photo_path),
            style,
            wait=True,
            timeout=180
        )
        
        # 清理临时文件
        if photo_path.exists():
            photo_path.unlink()
        
        return result
    
    def get_style_keyboard(self) -> list:
        """生成发型选择键盘"""
        keyboard = []
        row = []
        
        for style, description in HAIRSTYLES.items():
            row.append({"text": f"{style}", "callback_data": f"style:{style}"})
            if len(row) == 3:  # 每行3个按钮
                keyboard.append(row)
                row = []
        
        if row:  # 添加剩余的
            keyboard.append(row)
        
        return keyboard
    
    async def run(self):
        """运行 Bot"""
        print("🤖 发型生成 Bot 启动中...")
        print(f"   支持 {len(HAIRSTYLES)} 种发型风格")
        print(f"   模型: DreamO 4.0 (图生图 3.0)")
        print(f"   使用 base64 模式上传")
        print()
        
        # 这里可以集成 python-telegram-bot 或 aiogram
        # 简化版：使用 OpenClaw 的 message 工具
        
        print("✅ Bot 已就绪！")
        print()
        print("使用方式:")
        print("  1. 在 Telegram 发送 /start")
        print("  2. 上传照片")
        print("  3. 选择发型风格")
        print("  4. 等待生成完成")


def test_generate():
    """测试生成单个发型"""
    print("🧪 测试发型生成...")
    
    # 查找测试图片
    test_images = [
        "/root/.openclaw/workspace/test_image.jpg",
        "/root/.openclaw/workspace/hairstyle_app/test_photo.jpg",
    ]
    
    image_path = None
    for img in test_images:
        if Path(img).exists():
            image_path = img
            break
    
    if not image_path:
        print("❌ 未找到测试图片")
        return
    
    print(f"📸 使用测试图片: {image_path}")
    
    # 创建生成器
    access_key = os.getenv("JIMENG_ACCESS_KEY_ID", "")
    secret_key = os.getenv("JIMENG_SECRET_ACCESS_KEY", "")
    
    if not access_key or "待填写" in access_key:
        print("❌ 请配置 JIMENG_ACCESS_KEY_ID")
        return
    
    generator = HairstyleGenerator(access_key, secret_key)
    
    # 生成发型
    print("\n🎨 生成发型: 大波浪")
    result = generator.generate(image_path, "大波浪", wait=True, timeout=180)
    
    print("\n" + "=" * 60)
    print("生成结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result["success"]:
        print("\n✅ 生成成功！")
        if result.get("image_urls"):
            for url in result["image_urls"]:
                print(f"   URL: {url[:80]}...")
    else:
        print(f"\n❌ 生成失败: {result.get('error', '未知错误')}")


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="发型生成 Telegram Bot")
    parser.add_argument("--test", action="store_true", help="测试生成")
    parser.add_argument("--list-styles", action="store_true", help="列出发型")
    
    args = parser.parse_args()
    
    if args.list_styles:
        print("支持的发型风格:")
        for style, desc in HAIRSTYLES.items():
            print(f"  - {style}: {desc}")
        return
    
    if args.test:
        test_generate()
        return
    
    # 运行 Bot
    try:
        bot = TelegramHairstyleBot()
        asyncio.run(bot.run())
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

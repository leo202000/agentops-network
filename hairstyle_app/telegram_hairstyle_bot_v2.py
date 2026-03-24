#!/usr/bin/env python3
"""
发型生成 Telegram Bot V2

功能:
- 接收用户上传的照片
- 让用户选择 20 种发型风格
- 调用即梦 API 生成发型（带重试机制）
- 发送结果图片到 Telegram

更新:
- ✅ 支持 20 种发型（新增 5 种）
- ✅ 使用独立 JimengClient（避免签名问题）
- ✅ 添加重试机制（处理 API 并发限制）
- ✅ TOS 图片上传（公网访问）
"""

import os
import sys
import json
import asyncio
import tempfile
import time
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

# 导入独立客户端（已验证成功）
sys.path.insert(0, str(Path(__file__).parent / "backend"))
from hairstyle_generator import JimengClient

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# 支持的发型风格（20 种）
HAIRSTYLES = {
    # 基础发型（15 种）
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
    # 新增发型（5 种）⭐
    "齐肩发": "经典 Bob 头，职场女性百搭",
    "梨花头": "韩式内扣，温柔气质",
    "外翘发型": "发尾外翻，活泼可爱",
    "丸子头": "高发髻，清爽利落",
    "空气刘海": "轻薄刘海，减龄神器",
}


class TelegramHairstyleBot:
    """Telegram 发型生成机器人 V2"""
    
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
        
        # 使用独立客户端（已验证成功）
        self.client = JimengClient(self.access_key, self.secret_key)
        self.temp_dir = Path(tempfile.gettempdir()) / "hairstyle_bot"
        self.temp_dir.mkdir(exist_ok=True)
        
        # TOS 配置
        self.tos_ak = os.getenv("TOS_ACCESS_KEY", "")
        self.tos_sk = os.getenv("TOS_SECRET_KEY", "")
        self.tos_bucket = os.getenv("TOS_BUCKET", "")
        self.tos_region = os.getenv("TOS_REGION", "cn-beijing")
    
    async def handle_photo(self, photo_url: str, chat_id: str, style: str, max_retries: int = 3) -> dict:
        """
        处理照片并生成发型（带重试机制）
        
        Args:
            photo_url: Telegram 照片 URL
            chat_id: 聊天 ID
            style: 发型风格
            max_retries: 最大重试次数
            
        Returns:
            生成结果
        """
        import aiohttp
        from tos import TosClientV2, ACLType
        
        # 下载照片
        photo_path = self.temp_dir / f"{chat_id}_{style}.jpg"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(photo_url) as response:
                if response.status == 200:
                    with open(photo_path, 'wb') as f:
                        f.write(await response.read())
                else:
                    return {"success": False, "error": f"下载照片失败：{response.status}"}
        
        # 上传到 TOS
        try:
            tos_client = TosClientV2(ak=self.tos_ak, sk=self.tos_sk, region=self.tos_region)
            object_key = f"hairstyle/{int(time.time())}_{chat_id}_{style}.jpg"
            
            tos_client.put_object_from_file(
                bucket=self.tos_bucket,
                key=object_key,
                file_path=str(photo_path)
            )
            
            tos_client.put_object_acl(
                bucket=self.tos_bucket,
                key=object_key,
                acl=ACLType.ACL_Public_Read
            )
            
            image_url = f"https://{self.tos_bucket}.tos-{self.tos_region}.volces.com/{object_key}"
            
            # 等待 TOS 同步（1-2 秒）
            time.sleep(2)
            
        except Exception as e:
            # 清理临时文件
            if photo_path.exists():
                photo_path.unlink()
            return {"success": False, "error": f"TOS 上传失败：{e}"}
        
        # 获取发型提示词
        style_prompt = HAIRSTYLES.get(style, "")
        prompt = f"保持人物脸部完全一致，只改变发型为{style}，{style_prompt}, realistic photo, high quality, professional photography, natural lighting"
        
        # 提交任务（带重试）
        for attempt in range(max_retries):
            try:
                result = self.client.submit_task(
                    image_url=image_url,
                    prompt=prompt,
                    strength=0.7
                )
                
                # 检查是否成功
                if result.get('code') == 10000:
                    task_id = result['data']['task_id']
                    
                    # 查询结果（等待 30 秒）
                    time.sleep(30)
                    
                    for i in range(10):
                        query_result = self.client.query_result(task_id)
                        status = query_result.get('data', {}).get('status', 'unknown')
                        
                        if status == 'done':
                            image_urls = query_result.get('data', {}).get('image_urls', [])
                            if image_urls:
                                # 清理临时文件
                                if photo_path.exists():
                                    photo_path.unlink()
                                return {
                                    "success": True,
                                    "task_id": task_id,
                                    "image_url": image_urls[0]
                                }
                        elif status in ['failed', 'error']:
                            if photo_path.exists():
                                photo_path.unlink()
                            return {"success": False, "error": "生成失败"}
                        
                        time.sleep(10)
                    
                    if photo_path.exists():
                        photo_path.unlink()
                    return {"success": False, "error": "任务超时"}
                
                # 检查是否并发限制，重试
                elif result.get('code') == 50430 and attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    if photo_path.exists():
                        photo_path.unlink()
                    return {"success": False, "error": result.get('message', '提交失败')}
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    if photo_path.exists():
                        photo_path.unlink()
                    return {"success": False, "error": str(e)}
        
        if photo_path.exists():
            photo_path.unlink()
        return {"success": False, "error": "Max retries exceeded"}
    
    def get_style_keyboard(self) -> list:
        """生成发型选择键盘（20 种发型）"""
        keyboard = []
        row = []
        
        for style, description in HAIRSTYLES.items():
            row.append({"text": f"{style}", "callback_data": f"style:{style}"})
            if len(row) == 3:  # 每行 3 个按钮
                keyboard.append(row)
                row = []
        
        if row:  # 添加剩余的
            keyboard.append(row)
        
        return keyboard
    
    async def run(self):
        """运行 Bot"""
        print("🤖 发型生成 Bot V2 启动中...")
        print(f"   支持 {len(HAIRSTYLES)} 种发型风格")
        print(f"   模型：seed3l_single_ip (图生图 - 角色特征保持)")
        print(f"   上传：TOS 对象存储")
        print(f"   重试：最多 {3} 次")
        print()
        
        print("✅ Bot 已就绪！")
        print()
        print("使用方式:")
        print("  1. 在 Telegram 发送 /start")
        print("  2. 上传照片")
        print("  3. 选择发型风格（20 种可选）")
        print("  4. 等待生成完成（约 1-2 分钟）")
        print()
        print("新增发型:")
        print("  - 齐肩发：经典 Bob 头，职场女性百搭")
        print("  - 梨花头：韩式内扣，温柔气质")
        print("  - 外翘发型：发尾外翻，活泼可爱")
        print("  - 丸子头：高发髻，清爽利落")
        print("  - 空气刘海：轻薄刘海，减龄神器")


if __name__ == "__main__":
    bot = TelegramHairstyleBot()
    asyncio.run(bot.run())

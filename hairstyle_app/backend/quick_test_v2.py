#!/usr/bin/env python3
"""
发型生成系统 - 快速验证测试
基于 3 月 22 日成功版本
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hairstyle_generator import HairstyleGenerator

# 获取配置
ak = os.getenv("JIMENG_ACCESS_KEY_ID")
sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")

print("="*80)
print("发型生成系统 - 快速验证测试")
print("="*80)
print(f"\n✅ JIMENG_ACCESS_KEY_ID: 已配置 ({ak[:20]}...)")
print(f"✅ JIMENG_SECRET_ACCESS_KEY: 已配置 ({sk[:20]}...)")

# 测试图片
test_image = Path(__file__).parent / "uploads" / "customer_photo.jpg"
if not test_image.exists():
    print(f"\n❌ 测试图片不存在：{test_image}")
    sys.exit(1)

print(f"\n📋 测试图片：{test_image}")

# 创建生成器（禁用缓存避免并发问题）
print(f"\n🚀 初始化生成器...")
generator = HairstyleGenerator(
    ak, sk,
    enable_cache=False,  # 禁用缓存
    enable_compression=False  # 禁用压缩
)

# 测试发型
test_style = "齐肩发"
print(f"🎨 测试发型：{test_style}")

# 生成
print(f"\n⏳ 开始生成...")
result = generator.generate(
    str(test_image),
    test_style,
    wait=True,
    timeout=120
)

print(f"\n{'='*80}")
print("测试结果")
print(f"{'='*80}")

if result.get('success'):
    print(f"✅ 生成成功!")
    if result.get('image_urls'):
        print(f"   结果 URL: {result['image_urls'][0]}")
    if result.get('result_path'):
        print(f"   本地路径：{result['result_path']}")
    sys.exit(0)
else:
    print(f"❌ 生成失败")
    print(f"   错误：{result.get('error', 'Unknown')}")
    print(f"   代码：{result.get('code', 'N/A')}")
    sys.exit(1)

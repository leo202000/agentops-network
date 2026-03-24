#!/usr/bin/env python3
"""
完整流程调试测试

详细记录每个步骤的结果
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_full_flow():
    """完整流程测试"""
    from hairstyle_generator import HairstyleGenerator
    
    ak = os.getenv("JIMENG_ACCESS_KEY_ID")
    sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")
    
    print(f"\n{'='*60}")
    print(f"  完整流程测试")
    print(f"{'='*60}\n")
    
    print(f"1️⃣ 初始化生成器")
    print(f"   AK: {ak[:30]}...")
    print(f"   SK: {sk[:30]}...")
    
    generator = HairstyleGenerator(ak, sk)
    print(f"   ✅ 初始化成功\n")
    
    # 测试图片
    test_image = Path(__file__).parent / "uploads" / "customer_photo.jpg"
    print(f"2️⃣ 测试图片：{test_image}")
    print(f"   存在：{test_image.exists()}\n")
    
    # 测试发型
    test_style = "齐肩发"
    print(f"3️⃣ 测试发型：{test_style}\n")
    
    print(f"4️⃣ 开始生成...")
    
    result = generator.generate(
        str(test_image),
        test_style,
        wait=True,
        timeout=120
    )
    
    print(f"\n5️⃣ 生成结果:")
    print(f"   {result}\n")
    
    if result.get('success'):
        print(f"   ✅ 生成成功!")
        print(f"      图片 URL: {result.get('image_url', 'N/A')}")
        return True
    else:
        print(f"   ❌ 生成失败")
        print(f"      错误：{result.get('error', 'Unknown')}")
        print(f"      代码：{result.get('code', 'N/A')}")
        return False

if __name__ == "__main__":
    result = test_full_flow()
    sys.exit(0 if result else 1)

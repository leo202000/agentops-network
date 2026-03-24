#!/usr/bin/env python3
"""
发型生成测试 - 简化版（测试 3 种发型）
"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# 初始化客户端
client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.environ.get("ARK_API_KEY"),
)

# 测试 3 种发型（基础 + 新增）
TEST_STYLES = [
    ("短发", "short pixie cut, modern"),
    ("齐肩发", "shoulder length bob, classic"),  # 新增
    ("梨花头", "pear blossom hairstyle, korean"),  # 新增
]

# 测试图片
TEST_IMAGE_URL = "https://ark-project.tos-cn-beijing.volces.com/doc_image/seedream4_imageToimage.png"

print("="*70)
print("🎨 发型生成测试 - 简化版")
print("="*70)
print(f"\n测试发型：{len(TEST_STYLES)} 种")
print(f"测试图片：{TEST_IMAGE_URL[:60]}...")

results = []

for i, (style, prompt_en) in enumerate(TEST_STYLES, 1):
    print(f"\n[{i}/{len(TEST_STYLES)}] 测试：{style}")
    
    prompt = f"保持人物脸部完全一致，只改变发型为{style}，{prompt_en}, realistic photo, high quality"
    
    try:
        response = client.images.generate(
            model="doubao-seedream-4-5-251128",
            prompt=prompt,
            size="2K",
            response_format="url",
            extra_body={
                "image": TEST_IMAGE_URL,
                "watermark": False,
            }
        )
        
        result_url = response.data[0].url
        print(f"   ✅ 成功!")
        results.append((style, True, result_url[:60] + "..."))
        
    except Exception as e:
        print(f"   ❌ 失败：{e}")
        results.append((style, False, str(e)))
    
    # 间隔 2 秒
    if i < len(TEST_STYLES):
        time.sleep(2)

# 统计
print(f"\n{'='*70}")
print(f"📊 结果统计")
print(f"{'='*70}")

success_count = sum(1 for _, success, _ in results if success)

print(f"\n成功：{success_count}/{len(results)}")

for style, success, info in results:
    status = "✅" if success else "❌"
    print(f"{status} {style}: {info}")

if success_count == len(results):
    print(f"\n🎉 所有测试通过！")
else:
    print(f"\n⚠️  部分测试失败")

print(f"\n{'='*70}\n")

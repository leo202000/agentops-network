#!/usr/bin/env python3
"""
发型变换功能 - 简单测试（使用独立客户端）

测试 1 种发型：齐肩发（新增）
预计耗时：1-2 分钟
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

sys.path.insert(0, str(Path(__file__).parent / "backend"))

# 使用独立客户端（已验证成功）
from hairstyle_generator import JimengClient

print("="*70)
print("🧪 发型变换功能 - 简单测试")
print("="*70)

# 测试配置
TEST_IMAGE_URL = "https://hairfashon.tos-cn-beijing.volces.com/hairstyle/1fd9c969-32f1-4d73-9b8b-be6ae2cf34c8.jpg"
TEST_STYLE = "齐肩发"
TEST_PROMPT = "shoulder length bob hairstyle, classic and timeless, neat ends"

print(f"\n测试图片：{TEST_IMAGE_URL[:60]}...")
print(f"测试发型：{TEST_STYLE}")
print(f"预计耗时：1-2 分钟\n")

# 初始化客户端
ak = os.getenv("JIMENG_ACCESS_KEY_ID")
sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")
client = JimengClient(ak, sk)

print("提交生成任务...")
full_prompt = f"保持人物脸部完全一致，只改变发型为{TEST_STYLE}，{TEST_PROMPT}, realistic photo, high quality"

result = client.submit_task(
    image_url=TEST_IMAGE_URL,
    prompt=full_prompt,
    strength=0.7
)

print(f"\n提交结果：{result.get('code')} - {result.get('message', 'N/A')}")

if result.get('code') == 10000:
    task_id = result['data']['task_id']
    print(f"✅ 任务提交成功!")
    print(f"   Task ID: {task_id}")
    
    print(f"\n等待生成完成...")
    for i in range(10):
        time.sleep(15)
        
        query_result = client.query_result(task_id)
        status = query_result.get('data', {}).get('status', 'unknown')
        print(f"   状态：{status} (查询 {i+1}/10)")
        
        if status == 'done':
            image_urls = query_result.get('data', {}).get('image_urls', [])
            if image_urls:
                print(f"\n✅ 生成成功!")
                print(f"   结果 URL: {image_urls[0]}")
                print(f"\n{'='*70}")
                print(f"🎉 发型变换功能测试完成！")
                print(f"{'='*70}\n")
                sys.exit(0)
        elif status in ['failed', 'error']:
            print(f"\n❌ 生成失败")
            sys.exit(1)
    
    print(f"\n⏳ 任务仍在处理中")
    sys.exit(0)
    
elif result.get('code') == 50430:
    print(f"⚠️ API 并发限制，请稍后重试")
    sys.exit(1)
else:
    print(f"❌ 提交失败")
    print(f"   错误：{result}")
    sys.exit(1)

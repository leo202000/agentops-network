#!/usr/bin/env python3
"""
最小化对比测试
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hairstyle_generator import JimengClient, HairstyleGenerator

ak = os.getenv("JIMENG_ACCESS_KEY_ID")
sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")

test_image_url = "https://hairfashon.tos-cn-beijing.volces.com/hairstyle/test.jpg"

print("="*60)
print("测试 1: 直接创建 JimengClient")
print("="*60)
client1 = JimengClient(ak, sk)
result1 = client1.submit_task(
    image_url=test_image_url,
    prompt="test",
    req_key="seed3l_single_ip"
)
print(f"Result 1: {result1.get('code', 'N/A')} - {result1.get('message', 'N/A')}")
print()

print("="*60)
print("测试 2: 通过 HairstyleGenerator 创建")
print("="*60)
generator = HairstyleGenerator(ak, sk)
result2 = generator.client.submit_task(
    image_url=test_image_url,
    prompt="test",
    req_key="seed3l_single_ip"
)
print(f"Result 2: {result2.get('code', 'N/A')} - {result2.get('message', 'N/A')}")
print()

print("="*60)
print("对比")
print("="*60)
print(f"Test 1 成功：{result1.get('code') == 10000}")
print(f"Test 2 成功：{result2.get('code') == 10000}")

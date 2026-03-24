#!/usr/bin/env python3
"""调试 submit_task - 使用真实图片"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hairstyle_generator import HairstyleGenerator

ak = os.getenv("JIMENG_ACCESS_KEY_ID")
sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")

hg = HairstyleGenerator(ak, sk, enable_cache=False, enable_compression=False)

# 使用真实存在的图片
image_url = "https://hairfashon.tos-cn-beijing.volces.com/hairstyle/1fd9c969-32f1-4d73-9b8b-be6ae2cf34c8.jpg"
prompt = "test prompt"
strength = 0.7

print(f"Image URL: {image_url}")
print(f"Prompt: {prompt}")

# 先测试简单请求
print(f"\n测试 1: 简单请求...")
result1 = hg.client.submit_task(
    image_url=image_url,
    prompt="test",
    req_key="seed3l_single_ip"
)
print(f"Result 1: {result1.get('code')} - {result1.get('message')}")

# 再测试带 strength 的请求
print(f"\n测试 2: 带 strength 的请求...")
result2 = hg.client.submit_task(
    image_url=image_url,
    prompt=prompt,
    strength=strength,
    req_key="seed3l_single_ip"
)
print(f"Result 2: {result2.get('code')} - {result2.get('message')}")

# 测试带完整参数的请求
print(f"\n测试 3: 完整参数...")
result3 = hg.client.submit_task(
    image_url=image_url,
    prompt=prompt,
    width=1024,
    height=1024,
    strength=strength,
    req_key="seed3l_single_ip"
)
print(f"Result 3: {result3.get('code')} - {result3.get('message')}")

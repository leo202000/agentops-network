#!/usr/bin/env python3
"""
API 提交调试 - 直接调用 submit_task

查看原始响应
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hairstyle_generator import JimengClient

ak = os.getenv("JIMENG_ACCESS_KEY_ID")
sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")

print(f"Access Key: {ak[:30]}...")
print(f"Secret Key: {sk[:30]}...")

client = JimengClient(ak, sk)

# 测试图片 URL（TOS）
test_image_url = "https://hairfashon.tos-cn-beijing.volces.com/hairstyle/bde57403-0d43-44f9-bd58-ba4a4c0652aa.jpg"

print(f"\n测试图片：{test_image_url}")
print(f"\n提交任务...")

result = client.submit_task(
    image_url=test_image_url,
    prompt="test hairstyle",
    req_key="seed3l_single_ip"
)

print(f"\n原始响应:")
print(f"{result}")
print(f"\n响应类型：{type(result)}")
print(f"\n响应 keys: {result.keys() if isinstance(result, dict) else 'N/A'}")

if isinstance(result, dict):
    if 'code' in result:
        print(f"Code: {result['code']}")
    if 'message' in result:
        print(f"Message: {result['message']}")
    if 'data' in result:
        print(f"Data: {result['data']}")
    if 'ResponseMetadata' in result:
        print(f"ResponseMetadata: {result['ResponseMetadata']}")

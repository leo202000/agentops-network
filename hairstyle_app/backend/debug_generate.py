#!/usr/bin/env python3
"""调试 generate 方法"""

import os
import sys
import json
import hmac
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hairstyle_generator import HairstyleGenerator

ak = os.getenv("JIMENG_ACCESS_KEY_ID")
sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")

print("创建 HairstyleGenerator（禁用缓存）...")
hg = HairstyleGenerator(ak, sk, enable_cache=False, enable_compression=False)

# 模拟 generate 方法中的参数
image_url = "https://hairfashon.tos-cn-beijing.volces.com/hairstyle/test.jpg"
style = "齐肩发"
style_config = hg.STYLES[style]
style_prompt = style_config["prompt"]
negative_prompt = style_config.get("negative")
mode = hg.transform_mode
preset = hg.TRANSFORM_PRESETS.get(mode, hg.TRANSFORM_PRESETS["中等"])
strength = preset["strength"]

prompt = f"保持人物脸部完全一致，只改变发型为{style}，{style_prompt}, realistic photo, high quality, professional photography, natural lighting"

print(f"\nPrompt: {prompt[:80]}...")
print(f"Strength: {strength}")

# 构建请求
timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
query = {
    "Action": "CVSync2AsyncSubmitTask",
    "Version": "2022-08-31",
}
body_dict = {
    "req_key": "seed3l_single_ip",
    "image_urls": [image_url],
    "prompt": prompt,
    "width": 1024,
    "height": 1024,
}
if strength is not None:
    body_dict["strength"] = strength

body = json.dumps(body_dict, ensure_ascii=False)

print(f"\nBody: {body[:100]}...")

# 计算签名
auth = hg.client._create_authorization("POST", "/", query, body, timestamp)

print(f"\nAuthorization: {auth[:100]}...")
print(f"client.access_key: {hg.client.access_key[:30]}...")
print(f"client.secret_key: {hg.client.secret_key[:30]}...")
print(f"client.service: {hg.client.service}")
print(f"client.region: {hg.client.region}")

# 直接测试
print(f"\n直接调用 submit_task...")
result = hg.client.submit_task(
    image_url=image_url,
    prompt=prompt,
    strength=strength,
    req_key="seed3l_single_ip"
)

print(f"Result: {result.get('code')} - {result.get('message')}")

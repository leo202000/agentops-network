#!/usr/bin/env python3
"""
发型生成系统 - 商用测试脚本 V2
直接复制 simple_test.py 的成功代码
"""

import os
import sys
import json
import hmac
import hashlib
import requests
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# 完全复制 simple_test.py 的客户端
class JimengClient:
    def __init__(self, access_key: str, secret_key: str, region: str = "cn-north-1"):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.host = "visual.volcengineapi.com"
        self.service = "cv"
    
    def _sha256(self, data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def _create_authorization(self, method: str, uri: str, query: dict, body: str, timestamp: str) -> str:
        date = timestamp[:8]
        canonical_query = "&".join([f"{k}={v}" for k, v in sorted(query.items())])
        body_hash = self._sha256(body)
        canonical_headers = f"host:{self.host}\nx-content-sha256:{body_hash}\nx-date:{timestamp}\n"
        signed_headers = "host;x-content-sha256;x-date"
        canonical_request = f"{method}\n{uri}\n{canonical_query}\n{canonical_headers}\n{signed_headers}\n{body_hash}"
        credential_scope = f"{date}/{self.region}/{self.service}/request"
        string_to_sign = f"HMAC-SHA256\n{timestamp}\n{credential_scope}\n{self._sha256(canonical_request)}"
        k_date = hmac.new(self.secret_key.encode(), date.encode(), hashlib.sha256).digest()
        k_region = hmac.new(k_date, self.region.encode(), hashlib.sha256).digest()
        k_service = hmac.new(k_region, self.service.encode(), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
        signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
        return f"HMAC-SHA256 Credential={self.access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    
    def submit_task(self, image_url: str, prompt: str, strength: float = 0.6) -> dict:
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
            "strength": strength,
        }
        body = json.dumps(body_dict, ensure_ascii=False)
        auth = self._create_authorization("POST", "/", query, body, timestamp)
        headers = {
            "Content-Type": "application/json",
            "X-Date": timestamp,
            "X-Content-Sha256": self._sha256(body),
            "Authorization": auth
        }
        url = f"https://{self.host}/"
        response = requests.post(url, params=query, data=body, headers=headers, timeout=120)
        return response.json()

# 主测试
ak = os.getenv("JIMENG_ACCESS_KEY_ID")
sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")

print("="*80)
print("发型生成系统 - 商用测试 V2")
print("="*80)
print(f"\n✅ API 密钥已配置")

# 使用刚上传的图片
test_image_url = "https://hairfashon.tos-cn-beijing.volces.com/hairstyle/1774306397_customer_photo.jpg"
print(f"\n📋 图片 URL: {test_image_url}")

client = JimengClient(ak, sk)

print(f"\n⏳ 提交任务...")
result = client.submit_task(
    image_url=test_image_url,
    prompt="shoulder length bob hairstyle, classic and timeless",
    strength=0.7
)

print(f"\n{'='*80}")
print("测试结果")
print(f"{'='*80}")
print(f"Result: {result}")
print(f"Code: {result.get('code', 'N/A')}")
print(f"Message: {result.get('message', 'N/A')}")

if result.get('code') == 10000:
    print(f"\n✅ 成功！Task ID: {result['data']['task_id']}")
    sys.exit(0)
else:
    print(f"\n❌ 失败")
    sys.exit(1)

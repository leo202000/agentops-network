#!/usr/bin/env python3
"""获取 Request ID - 使用 VisualService 端点"""
import os
import sys
import json
import base64
from pathlib import Path
from datetime import datetime, timezone
import requests
import hashlib
import hmac

# 加载 .env 文件
env_path = Path('/root/.openclaw/workspace/.env')
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

ak = os.getenv('JIMENG_ACCESS_KEY_ID')
sk = os.getenv('JIMENG_SECRET_ACCESS_KEY')

print(f'AK: {ak[:20]}...')
print(f'SK: {sk[:20]}...')

# 使用 VisualService 端点 (之前成功的)
host = "visual.volcengineapi.com"
service = "cv"
region = "cn-north-1"

def sha256(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

# 读取测试图片
photo_path = '/root/.openclaw/media/inbound/file_42---8f6bb911-cc80-4efc-ba52-4c5d65dfdd73.jpg'
with open(photo_path, 'rb') as f:
    img_data = f.read()
    img_base64 = base64.b64encode(img_data).decode('utf-8')

print('\n📤 提交任务获取 Request ID...')

timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
date = timestamp[:8]

body_dict = {
    "req_key": "seed3l_single_ip",
    "binary_data_base64": [img_base64],
    "prompt": "及腰长发，超长发及腰，waist-length long straight hair, ultra long hair",
    "width": 1024,
    "height": 1024,
    "strength": 0.45,
    "sample_steps": 30,
    "cfg_scale": 7.5,
}

body = json.dumps(body_dict, ensure_ascii=False)

query = {
    "Action": "CVSync2AsyncSubmitTask",
    "Version": "2022-08-31",
}

canonical_query = "&".join([f"{k}={v}" for k, v in sorted(query.items())])
body_hash = sha256(body)
canonical_headers = f"host:{host}\nx-content-sha256:{body_hash}\nx-date:{timestamp}\n"
signed_headers = "host;x-content-sha256;x-date"
canonical_request = f"POST\n/\n{canonical_query}\n{canonical_headers}\n{signed_headers}\n{body_hash}"

credential_scope = f"{date}/{region}/{service}/request"
string_to_sign = f"HMAC-SHA256\n{timestamp}\n{credential_scope}\n{sha256(canonical_request)}"

k_date = hmac.new(sk.encode(), date.encode(), hashlib.sha256).digest()
k_region = hmac.new(k_date, region.encode(), hashlib.sha256).digest()
k_service = hmac.new(k_region, service.encode(), hashlib.sha256).digest()
k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()

signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
auth = f"HMAC-SHA256 Credential={ak}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"

headers = {
    "Content-Type": "application/json",
    "X-Date": timestamp,
    "X-Content-Sha256": body_hash,
    "Authorization": auth
}

url = f"https://{host}/"
response = requests.post(url, params=query, data=body, headers=headers, timeout=120)
result = response.json()

print('\n=== API 响应 ===')
print(json.dumps(result, indent=2, ensure_ascii=False)[:1500])

# 提取 Request ID
request_id = result.get('request_id') or result.get('ResponseMetadata', {}).get('RequestId')
if request_id:
    print(f'\n✅ Request ID: {request_id}')
    print(f'\n📋 工单信息:')
    print(f'   Request ID: {request_id}')
    print(f'   提交时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (GMT+8)')
    print(f'   模型：seed3l_single_ip')
    print(f'   输入图片：file_42---8f6bb911-cc80-4efc-ba52-4c5d65dfdd73.jpg')
    print(f'   参数：strength=0.45, sample_steps=30')
else:
    print('\n⚠️ 未找到 Request ID')
    print(f'完整响应：{json.dumps(result, indent=2, ensure_ascii=False)}')

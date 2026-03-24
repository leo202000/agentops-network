#!/usr/bin/env python3
"""
签名调试 - 对比成功和失败的签名计算
"""

import os
import sys
import hmac
import hashlib
import json
from datetime import datetime, timezone
from urllib.parse import quote
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

ak = os.getenv("JIMENG_ACCESS_KEY_ID")
sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")

print(f"Access Key: {ak}")
print(f"Secret Key: {sk}")
print()

# 测试参数
method = "POST"
uri = "/"
query = {
    "Action": "CVSync2AsyncSubmitTask",
    "Version": "2022-08-31",
}
body_dict = {
    "req_key": "seed3l_single_ip",
    "image_urls": ["https://hairfashon.tos-cn-beijing.volces.com/hairstyle/test.jpg"],
    "prompt": "test",
    "width": 1024,
    "height": 1024,
    "strength": 0.7,
}
body = json.dumps(body_dict, ensure_ascii=False)

print(f"Body: {body[:100]}...")
print()

# 计算签名
timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
date = timestamp[:8]

print(f"Timestamp: {timestamp}")
print(f"Date: {date}")
print()

# 规范查询字符串
canonical_query = "&".join([f"{k}={quote(str(v), safe='')}" for k, v in sorted(query.items())])
print(f"Canonical Query: {canonical_query}")

# Body hash
body_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()
print(f"Body Hash: {body_hash}")

# Canonical headers
canonical_headers = f"host:visual.volcengineapi.com\nx-content-sha256:{body_hash}\nx-date:{timestamp}\n"
signed_headers = "host;x-content-sha256;x-date"

print(f"Canonical Headers:\n{canonical_headers}")
print(f"Signed Headers: {signed_headers}")

# Canonical request
canonical_request = f"{method}\n{uri}\n{canonical_query}\n{canonical_headers}\n{signed_headers}\n{body_hash}"
print(f"Canonical Request:\n{canonical_request[:200]}...")
print()

# String to sign
credential_scope = f"{date}/cn-north-1/CV/request"
string_to_sign = f"HMAC-SHA256\n{timestamp}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
print(f"String to Sign:\n{string_to_sign[:200]}...")
print()

# 计算签名
k_date = hmac.new(sk.encode(), date.encode(), hashlib.sha256).digest()
k_region = hmac.new(k_date, "cn-north-1".encode(), hashlib.sha256).digest()
k_service = hmac.new(k_region, "CV".encode(), hashlib.sha256).digest()
k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()

print(f"Signature: {signature}")
print()

# Authorization header
auth = f"HMAC-SHA256 Credential={ak}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
print(f"Authorization:\n{auth}")

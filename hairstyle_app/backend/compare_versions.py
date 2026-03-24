#!/usr/bin/env python3
"""对比两个版本的签名计算"""

import os
import sys
import hmac
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

ak = os.getenv("JIMENG_ACCESS_KEY_ID")
sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")

# 测试参数
method = "POST"
uri = "/"
query = {"Action": "CVSync2AsyncSubmitTask", "Version": "2022-08-31"}
body_dict = {
    "req_key": "seed3l_single_ip",
    "image_urls": ["https://test.com/image.jpg"],
    "prompt": "test",
    "width": 1024,
    "height": 1024,
    "strength": 0.7,
}
body = json.dumps(body_dict, ensure_ascii=False)
timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
date = timestamp[:8]

print("="*80)
print("签名计算对比")
print("="*80)
print(f"\nAK: {ak}")
print(f"SK: {sk}")
print(f"Timestamp: {timestamp}")
print()

# 版本 1: 独立版本（成功）
print("-"*80)
print("版本 1: 独立版本（成功）")
print("-"*80)

canonical_query1 = "&".join([f"{k}={v}" for k, v in sorted(query.items())])
body_hash1 = hashlib.sha256(body.encode('utf-8')).hexdigest()
canonical_headers1 = f"host:visual.volcengineapi.com\nx-content-sha256:{body_hash1}\nx-date:{timestamp}\n"
signed_headers1 = "host;x-content-sha256;x-date"
canonical_request1 = f"{method}\n{uri}\n{canonical_query1}\n{canonical_headers1}\n{signed_headers1}\n{body_hash1}"
credential_scope1 = f"{date}/cn-north-1/cv/request"
string_to_sign1 = f"HMAC-SHA256\n{timestamp}\n{credential_scope1}\n{hashlib.sha256(canonical_request1.encode('utf-8')).hexdigest()}"

k_date1 = hmac.new(sk.encode(), date.encode(), hashlib.sha256).digest()
k_region1 = hmac.new(k_date1, "cn-north-1".encode(), hashlib.sha256).digest()
k_service1 = hmac.new(k_region1, "cv".encode(), hashlib.sha256).digest()
k_signing1 = hmac.new(k_service1, b"request", hashlib.sha256).digest()
signature1 = hmac.new(k_signing1, string_to_sign1.encode(), hashlib.sha256).hexdigest()

print(f"canonical_query: {canonical_query1}")
print(f"service: cv")
print(f"credential_scope: {credential_scope1}")
print(f"signature: {signature1[:60]}...")
print()

# 版本 2: HairstyleGenerator 中的版本
print("-"*80)
print("版本 2: HairstyleGenerator 中的版本")
print("-"*80)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hairstyle_generator import JimengClient

client = JimengClient(ak, sk)

print(f"client.service: {client.service}")
print(f"client.region: {client.region}")
print(f"client.host: {client.host}")

# 手动计算
canonical_query2 = "&".join([f"{k}={v}" for k, v in sorted(query.items())])
body_hash2 = client._sha256(body)
canonical_headers2 = f"host:{client.host}\nx-content-sha256:{body_hash2}\nx-date:{timestamp}\n"
signed_headers2 = "host;x-content-sha256;x-date"
canonical_request2 = f"{method}\n{uri}\n{canonical_query2}\n{canonical_headers2}\n{signed_headers2}\n{body_hash2}"
credential_scope2 = f"{date}/{client.region}/{client.service}/request"
string_to_sign2 = f"HMAC-SHA256\n{timestamp}\n{credential_scope2}\n{client._sha256(canonical_request2)}"

k_date2 = hmac.new(client.secret_key.encode(), date.encode(), hashlib.sha256).digest()
k_region2 = hmac.new(k_date2, client.region.encode(), hashlib.sha256).digest()
k_service2 = hmac.new(k_region2, client.service.encode(), hashlib.sha256).digest()
k_signing2 = hmac.new(k_service2, b"request", hashlib.sha256).digest()
signature2 = hmac.new(k_signing2, string_to_sign2.encode(), hashlib.sha256).hexdigest()

print(f"canonical_query: {canonical_query2}")
print(f"service: {client.service}")
print(f"credential_scope: {credential_scope2}")
print(f"signature: {signature2[:60]}...")
print()

# 对比
print("="*80)
print("对比结果")
print("="*80)
print(f"Signature 相同：{signature1 == signature2}")
print(f"credential_scope 相同：{credential_scope1 == credential_scope2}")
print(f"canonical_query 相同：{canonical_query1 == canonical_query2}")

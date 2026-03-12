#!/usr/bin/env python3
import requests
import hmac
import base64
import hashlib
from datetime import datetime, timezone

# 新密钥
API_KEY = "5f27f7dc-ad38-4091-934b-d218e1a84a20"
SECRET_KEY = "F2B64C5DC6BC176F3D49C769A587C380"
PASSPHRASE = "20111116Ttcj!"

# 尝试不同端点
endpoints = [
    ("全球站", "https://www.okx.com"),
    ("国际站", "https://www.okx.com"),
]

def generate_signature(timestamp, method, path, body=''):
    message = timestamp + method + path + body
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')

print("=" * 60)
print("OKX API 端点测试")
print("=" * 60)
print(f"API Key: {API_KEY}")
print(f"Secret: {SECRET_KEY[:8]}...{SECRET_KEY[-8:]}")
print(f"Passphrase: {PASSPHRASE}")
print("=" * 60)

for name, base_url in endpoints:
    print(f"\n🌐 测试 {name}: {base_url}")
    
    timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    method = 'GET'
    path = '/api/v5/account/balance'
    signature = generate_signature(timestamp, method, path)
    
    headers = {
        'OK-ACCESS-KEY': API_KEY,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': PASSPHRASE,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f'{base_url}{path}', headers=headers, timeout=10)
        result = response.json()
        print(f"   HTTP: {response.status_code}")
        print(f"   Code: {result.get('code', 'N/A')}")
        print(f"   Msg:  {result.get('msg', 'N/A')}")
        
        if response.status_code == 200 and result.get('code') == '0':
            print(f"   ✅ 成功！")
            break
    except Exception as e:
        print(f"   ❌ 错误：{e}")

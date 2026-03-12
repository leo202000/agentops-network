#!/usr/bin/env python3
import requests
import hmac
import base64
import hashlib
from datetime import datetime, timezone

# 当前密钥
API_KEY = "5f27f7dc-ad38-4091-934b-d218e1a84a20"
SECRET_KEY = "F2B64C5DC6BC176F3D49C769A587C380"
PASSPHRASE = "20111116Ttcj!"
BASE_URL = "https://www.okx.com"

def generate_signature(timestamp, method, path, body=''):
    message = timestamp + method + path + body
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')

print("=" * 60)
print("OKX API 完整诊断")
print("=" * 60)
print(f"API Key: {API_KEY}")
print(f"Secret: {SECRET_KEY[:8]}...{SECRET_KEY[-8:]}")
print(f"Passphrase: {PASSPHRASE}")
print(f"Secret 长度：{len(SECRET_KEY)} (应为 32)")
print(f"API Key 格式：{'✅ UUID' if len(API_KEY) == 36 and API_KEY.count('-') == 4 else '❌ 非 UUID'}")
print("=" * 60)

# 测试多个端点
endpoints = [
    ("账户余额", "/api/v5/account/balance"),
    ("交易账户", "/api/v5/account/positions"),
    ("行情 ticker", "/api/v5/market/ticker?instId=BTC-USDT"),
    ("公共端点（无需认证）", "/api/v5/market/ticker?instId=BTC-USDT"),
]

for name, path in endpoints:
    timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    method = 'GET'
    signature = generate_signature(timestamp, method, path)
    
    # 公共端点不需要认证头
    if '公共' in name:
        headers = {'Content-Type': 'application/json'}
    else:
        headers = {
            'OK-ACCESS-KEY': API_KEY,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': PASSPHRASE,
            'Content-Type': 'application/json'
        }
    
    try:
        response = requests.get(f'{BASE_URL}{path}', headers=headers, timeout=10)
        result = response.json()
        
        print(f"\n{name}")
        print(f"   HTTP: {response.status_code}")
        print(f"   Code: {result.get('code', 'N/A')}")
        print(f"   Msg:  {result.get('msg', 'N/A')}")
        
        if response.status_code == 200 and result.get('code') == '0':
            print(f"   ✅ 成功！")
        elif response.status_code == 401:
            print(f"   ❌ 认证失败 - 密钥问题")
        elif response.status_code == 200:
            print(f"   ⚠️ 其他错误")
    except Exception as e:
        print(f"\n{name}")
        print(f"   ❌ 错误：{e}")

print("\n" + "=" * 60)
print("建议:")
print("1. 如果公共端点成功但认证端点失败 → 密钥确实无效")
print("2. 如果所有端点都失败 → 网络或 API 问题")
print("3. 请确认密钥是在 https://www.okx.com/account/my-api 创建的")
print("=" * 60)

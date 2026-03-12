#!/usr/bin/env python3
"""
ClawMarket - 快速测试购买
"""
import requests
from eth_account import Account

API_BASE = "https://api.clawmarket.tech"
PRIVATE_KEY = "0xdc64abed396b019867b191c7abcf7cf70b59826defe317cb2835946c7065d939"
WALLET = "0x694a096016B681Bd3D3Ed11Aeee47fCcc2E10e1a"

account = Account.from_key(PRIVATE_KEY)

print("=" * 60)
print("ClawMarket 购买测试")
print("=" * 60)

# 1. 检查健康状态
print("\n[1/5] 检查 API 健康...")
try:
    r = requests.get(f"{API_BASE}/health", timeout=10)
    print(f"✅ 健康状态：{r.json()}")
except Exception as e:
    print(f"❌ 健康检查失败：{e}")
    exit(1)

# 2. 获取可购买代理
print("\n[2/5] 获取代理列表...")
try:
    r = requests.post(f"{API_BASE}/keys", timeout=30)
    print(f"HTTP: {r.status_code}")
    if r.status_code == 200:
        keys = r.json().get('keys', [])
        print(f"✅ 找到 {len(keys)} 个代理")
        target = [k['address'] for k in keys if k['address'] != WALLET][0]
        print(f"目标：{target}")
    else:
        print(f"❌ 错误：{r.text[:200]}")
        exit(1)
except Exception as e:
    print(f"❌ 错误：{e}")
    exit(1)

# 3. 准备订单
print("\n[3/5] 准备订单...")
try:
    r = requests.post(f"{API_BASE}/order/prepare", json={
        "wallet": WALLET,
        "sharesSubject": target,
        "isBuy": True,
        "amount": 1
    }, timeout=30)
    print(f"HTTP: {r.status_code}")
    if r.status_code != 200:
        print(f"❌ 准备失败：{r.text[:200]}")
        exit(1)
    result = r.json()
    keyOrder = result.get('keyOrder', {})
    print(f"✅ 订单准备成功")
except Exception as e:
    print(f"❌ 错误：{e}")
    exit(1)

# 4. 签名
print("\n[4/5] 签名订单...")
try:
    from eth_account.messages import encode_typed_data
    
    domain = {
        "name": keyOrder['domain']['name'],
        "version": keyOrder['domain']['version'],
        "chainId": keyOrder['domain']['chainId'],
        "verifyingContract": keyOrder['domain']['verifyingContract']
    }
    
    types = {
        "KeyOrder": [
            {"name": "trader", "type": "address"},
            {"name": "sharesSubject", "type": "address"},
            {"name": "isBuy", "type": "bool"},
            {"name": "amount", "type": "uint256"},
            {"name": "nonce", "type": "uint256"},
            {"name": "deadline", "type": "uint256"}
        ]
    }
    
    message = {
        "trader": keyOrder['message']['trader'],
        "sharesSubject": keyOrder['message']['sharesSubject'],
        "isBuy": keyOrder['message']['isBuy'],
        "amount": int(keyOrder['message']['amount']),
        "nonce": int(keyOrder['message']['nonce']),
        "deadline": int(keyOrder['message']['deadline'])
    }
    
    signed = account.sign_typed_data(domain, types, message)
    print(f"✅ 签名成功：{signed.signature.hex()[:40]}...")
except Exception as e:
    print(f"❌ 错误：{e}")
    exit(1)

# 5. 提交订单
print("\n[5/5] 提交订单...")
keyOrder_body = {
    "trader": message['trader'],
    "sharesSubject": message['sharesSubject'],
    "isBuy": message['isBuy'],
    "amount": str(message['amount']),
    "nonce": str(message['nonce']),
    "deadline": str(message['deadline']),
    "signature": signed.signature.hex()
}

try:
    r = requests.post(f"{API_BASE}/order", json={"keyOrder": keyOrder_body}, timeout=120)
    print(f"HTTP: {r.status_code}")
    print(f"响应：{r.text[:500]}")
    
    if r.status_code == 200 or r.status_code == 201:
        result = r.json()
        print("\n" + "=" * 60)
        print("✅✅✅ 购买成功！")
        print("=" * 60)
        print(f"交易哈希：{result.get('txHash', 'N/A')}")
        print(f"购买代理：{target}")
        print(f"数量：1 密钥")
    else:
        print(f"\n❌ 购买失败：{r.status_code}")
except Exception as e:
    print(f"❌ 错误：{e}")

print("\n" + "=" * 60)

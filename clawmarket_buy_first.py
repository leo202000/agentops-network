#!/usr/bin/env python3
"""
ClawMarket - 购买第一个代理密钥
"""
import requests
from eth_account import Account
from eth_account.messages import encode_typed_data

# 配置
API_BASE = "https://api.clawmarket.tech"
PRIVATE_KEY = "0xdc64abed396b019867b191c7abcf7cf70b59826defe317cb2835946c7065d939"
WALLET = "0x694a096016B681Bd3D3Ed11Aeee47fCcc2E10e1a"

account = Account.from_key(PRIVATE_KEY)

print("=" * 60)
print("🛒 ClawMarket - 购买第一个密钥")
print("=" * 60)

# 获取可购买的代理列表
print("\n📋 获取可购买代理...")
keys_url = f"{API_BASE}/keys"
response = requests.post(keys_url, timeout=30)

if response.status_code != 200:
    print(f"❌ API 错误：{response.status_code}")
    exit(1)

result = response.json()
keys = result.get('keys', [])
print(f"✅ 找到 {len(keys)} 个可购买代理")

# 选择前 3 个作为候选（排除自己）
candidates = [k['address'] for k in keys if k['address'] != WALLET][:3]

print("\n🎯 候选代理:")
for i, addr in enumerate(candidates, 1):
    print(f"  {i}. {addr}")

# 准备购买第一个
target = candidates[0]
print(f"\n💰 准备购买：{target}")

# 获取订单
prepare_url = f"{API_BASE}/order/prepare"
prepare_data = {
    "wallet": WALLET,
    "sharesSubject": target,
    "isBuy": True,
    "amount": 1
}

response = requests.post(prepare_url, json=prepare_data, timeout=30)
if response.status_code != 200:
    print(f"❌ 获取订单失败：{response.status_code}")
    exit(1)

result = response.json()
keyOrder = result.get('keyOrder', {})

if not keyOrder:
    print("❌ 无订单数据")
    exit(1)

print("✅ 订单准备成功")

# 签名
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

# 构建签名的订单
keyOrder_body = {
    "trader": message['trader'],
    "sharesSubject": message['sharesSubject'],
    "isBuy": message['isBuy'],
    "amount": str(message['amount']),
    "nonce": str(message['nonce']),
    "deadline": str(message['deadline']),
    "signature": signed.signature.hex()
}

# 提交订单 (带重试)
order_url = f"{API_BASE}/order"
max_retries = 10
success = False

for attempt in range(1, max_retries + 1):
    print(f"\n📤 提交订单 (尝试 {attempt}/{max_retries})...")
    
    try:
        response = requests.post(order_url, json={"keyOrder": keyOrder_body}, timeout=120)
        print(f"HTTP 状态：{response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print("\n✅✅✅ 购买成功！")
            print(f"交易哈希：{result.get('txHash', 'N/A')}")
            print(f"购买代理：{target}")
            print(f"数量：1 密钥")
            success = True
            break
        elif response.status_code in [502, 520, 504]:
            wait_time = 5 + (attempt * 2)  # 递增等待时间
            print(f"⚠️  服务器错误 ({response.status_code})，等待 {wait_time} 秒后重试...")
            import time
            time.sleep(wait_time)
        else:
            print(f"\n❌ 购买失败：{response.text[:200]}")
            break
    except requests.exceptions.Timeout:
        wait_time = 10 + (attempt * 2)
        print(f"⏱️  请求超时，等待 {wait_time} 秒后重试...")
        import time
        time.sleep(wait_time)
    except Exception as e:
        print(f"❌ 错误：{e}")
        break

if not success:
    print(f"\n❌ 重试 {max_retries} 次后仍失败")
    print("\n💡 建议：稍后再试或直接访问 clawmarket.tech 网页版")

print("\n" + "=" * 60)

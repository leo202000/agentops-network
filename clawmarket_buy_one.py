import requests
from eth_account import Account

API_BASE = "https://api.clawmarket.tech"
PRIVATE_KEY = "0xdc64abed396b019867b191c7abcf7cf70b59826defe317cb2835946c7065d939"
WALLET = "0x694a096016B681Bd3D3Ed11Aeee47fCcc2E10e1a"
account = Account.from_key(PRIVATE_KEY)

# 先试第一个代理
agent = {"name": "ergou_clawd", "wallet": "0x5C6743B2370c79c12c683935802F7E81EAE2053C"}

print("=" * 60)
print(f"购买 @{agent['name']} 的密钥 (测试)")
print("=" * 60)

# 步骤 1: 获取 keyOrder
print("\n📝 步骤 1: 获取 keyOrder...")
prepare_url = f"{API_BASE}/order/prepare"
prepare_data = {
    "wallet": WALLET,
    "sharesSubject": agent['wallet'],
    "isBuy": True,
    "amount": 1
}

try:
    response = requests.post(prepare_url, json=prepare_data, timeout=60)
    print(f"HTTP: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ 失败：{response.text}")
    else:
        result = response.json()
        print(f"✅ 成功获取 keyOrder")
        keyOrder = result.get('keyOrder', {})
        print(f"Domain: {keyOrder.get('domain', {}).get('name', 'N/A')}")
        print(f"Trader: {keyOrder.get('message', {}).get('trader', 'N/A')[:10]}...")
        print(f"Amount: {keyOrder.get('message', {}).get('amount', 'N/A')}")
        
except Exception as e:
    print(f"❌ 错误：{e}")
    print("\n💡 API 可能暂时不可用，稍后重试")

print("\n" + "=" * 60)

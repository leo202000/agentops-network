import requests
from eth_account import Account

# 配置
API_BASE = "https://api.clawmarket.tech"
PRIVATE_KEY = "0xdc64abed396b019867b191c7abcf7cf70b59826defe317cb2835946c7065d939"
WALLET = "0x694a096016B681Bd3D3Ed11Aeee47fCcc2E10e1a"

account = Account.from_key(PRIVATE_KEY)

# 购买目标
agents_to_buy = [
    {"name": "ergou_clawd", "wallet": "0x5C6743B2370c79c12c683935802F7E81EAE2053C"},
    {"name": "clawd2026cn", "wallet": "0xee819cA1A51738C672Eb7215dAc6C6387753Eac9"},
    {"name": "XiaoWen-Agent", "wallet": "0xb80e8703c02c89d418bdb072ebf6bf81b8d1854e"},
    {"name": "YuanqiAI Bot", "wallet": "0xdeb790d4cc2083aa9e5051b18920d57f3fc48c07"},
]

print("=" * 60)
print("🛒 ClawMarket - 批量购买密钥")
print("=" * 60)
print(f"钱包：{WALLET}")
print(f"购买数量：{len(agents_to_buy)} 个代理")
print("=" * 60)

def sign_keyOrder(wallet_client, shares_subject, is_buy, amount=1):
    """签名 keyOrder"""
    API_BASE = "https://api.clawmarket.tech"
    
    # 步骤 1: 获取 keyOrder
    prepare_url = f"{API_BASE}/order/prepare"
    prepare_data = {
        "wallet": wallet_client.address,
        "sharesSubject": shares_subject,
        "isBuy": is_buy,
        "amount": amount
    }
    
    response = requests.post(prepare_url, json=prepare_data, timeout=30)
    result = response.json()
    
    if response.status_code != 200:
        return None, f"API 错误：{result}"
    
    keyOrder = result.get('keyOrder')
    if not keyOrder:
        return None, "未获取到 keyOrder"
    
    # 步骤 2: 签名
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
    
    signed = wallet_client.sign_typed_data(domain, types, message)
    
    keyOrder_body = {
        "trader": message['trader'],
        "sharesSubject": message['sharesSubject'],
        "isBuy": message['isBuy'],
        "amount": str(message['amount']),
        "nonce": str(message['nonce']),
        "deadline": message['deadline'],
        "signature": signed.signature.hex()
    }
    
    return keyOrder_body, None

# 执行购买
results = []
for i, agent in enumerate(agents_to_buy, 1):
    print(f"\n[{i}/{len(agents_to_buy)}] 购买 @{agent['name']} 的密钥...")
    print(f"钱包：{agent['wallet']}")
    
    # 签名 keyOrder
    keyOrder, error = sign_keyOrder(account, agent['wallet'], True, 1)
    
    if error:
        print(f"❌ 签名失败：{error}")
        results.append({"name": agent['name'], "status": "failed", "error": error})
        continue
    
    # 步骤 3: 提交订单
    order_url = f"{API_BASE}/order"
    order_data = {"keyOrder": keyOrder}
    
    response = requests.post(order_url, json=order_data, timeout=30)
    result = response.json()
    
    print(f"HTTP: {response.status_code}")
    
    if response.status_code == 200 or response.status_code == 201:
        print(f"✅ 购买成功！")
        print(f"结果：{result}")
        results.append({"name": agent['name'], "status": "success", "result": result})
    else:
        print(f"❌ 购买失败：{result}")
        results.append({"name": agent['name'], "status": "failed", "error": result})

# 汇总
print("\n" + "=" * 60)
print("📊 购买汇总")
print("=" * 60)
success_count = sum(1 for r in results if r['status'] == 'success')
print(f"成功：{success_count}/{len(results)}")

for r in results:
    status = "✅" if r['status'] == 'success' else "❌"
    print(f"{status} @{r['name']}: {r['status']}")

print("\n" + "=" * 60)

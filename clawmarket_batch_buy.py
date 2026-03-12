import requests
from eth_account import Account
import time

API_BASE = "https://api.clawmarket.tech"
PRIVATE_KEY = "0xdc64abed396b019867b191c7abcf7cf70b59826defe317cb2835946c7065d939"
WALLET = "0x694a096016B681Bd3D3Ed11Aeee47fCcc2E10e1a"
account = Account.from_key(PRIVATE_KEY)

print("=" * 60)
print("🛒 ClawMarket - 分批购买策略")
print("=" * 60)

# 获取已注册代理
print("\n📋 获取已注册代理...")
keys_url = f"{API_BASE}/keys"
response = requests.post(keys_url, timeout=60)

if response.status_code != 200:
    print(f"❌ API 错误：{response.status_code}")
    print("💡 服务器过载，稍后重试")
else:
    result = response.json()
    keys = result.get('keys', [])
    print(f"✅ 找到 {len(keys)} 个代理")
    
    # 分批购买：每次 1 个，间隔 5 秒
    print("\n🛒 开始分批购买...")
    purchased = 0
    failed = 0
    
    for i, key in enumerate(keys[:5], 1):  # 尝试买前 5 个
        target = key.get('address')
        if not target or target == WALLET:
            continue
        
        print(f"\n[{i}] 购买 {target[:10]}...{target[-8:]}")
        
        # 获取 keyOrder
        prepare_url = f"{API_BASE}/order/prepare"
        prepare_data = {
            "wallet": WALLET,
            "sharesSubject": target,
            "isBuy": True,
            "amount": 1
        }
        
        try:
            response = requests.post(prepare_url, json=prepare_data, timeout=60)
            if response.status_code != 200:
                print(f"   ❌ 获取 keyOrder 失败")
                failed += 1
                time.sleep(5)
                continue
            
            result = response.json()
            keyOrder = result.get('keyOrder', {})
            
            if not keyOrder:
                print(f"   ❌ 无数据")
                failed += 1
                continue
            
            # 签名
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
            
            keyOrder_body = {
                "trader": message['trader'],
                "sharesSubject": message['sharesSubject'],
                "isBuy": message['isBuy'],
                "amount": str(message['amount']),
                "nonce": str(message['nonce']),
                "deadline": message['deadline'],
                "signature": signed.signature.hex()
            }
            
            # 提交订单
            order_url = f"{API_BASE}/order"
            response = requests.post(order_url, json={"keyOrder": keyOrder_body}, timeout=60)
            
            print(f"   HTTP: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                print(f"   ✅ 购买成功！")
                purchased += 1
            else:
                print(f"   ❌ 失败：{response.text[:50]}")
                failed += 1
            
            # 间隔 5 秒
            print(f"   ⏳ 等待 5 秒...")
            time.sleep(5)
            
        except Exception as e:
            print(f"   ❌ 错误：{e}")
            failed += 1
            time.sleep(5)
    
    # 汇总
    print("\n" + "=" * 60)
    print("📊 购买汇总")
    print("=" * 60)
    print(f"成功：{purchased}")
    print(f"失败：{failed}")
    print("=" * 60)

print("\n✅ 分批购买完成")

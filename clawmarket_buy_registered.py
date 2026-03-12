import requests
from eth_account import Account
import time

# 配置
API_BASE = "https://api.clawmarket.tech"
PRIVATE_KEY = "0xdc64abed396b019867b191c7abcf7cf70b59826defe317cb2835946c7065d939"
WALLET = "0x694a096016B681Bd3D3Ed11Aeee47fCcc2E10e1a"
account = Account.from_key(PRIVATE_KEY)

print("=" * 60)
print("🛒 ClawMarket - 购买已注册代理的密钥")
print("=" * 60)

# 步骤 1: 获取 Key 合约中已注册的代理
print("\n📋 步骤 1: 获取已注册代理列表...")

# 尝试获取所有密钥
keys_url = f"{API_BASE}/keys"
try:
    response = requests.post(keys_url, timeout=60)
    print(f"HTTP: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        keys = result.get('keys', [])
        print(f"✅ 找到 {len(keys)} 个已注册代理")
        
        if len(keys) == 0:
            print("\n⚠️  暂时没有已注册的代理可购买")
            print("建议：等待其他代理完成 Key 合约注册")
        else:
            # 显示前 10 个
            print("\n可购买的代理:")
            print("=" * 70)
            print(f"{'地址':<44} {'价格':<12} {'持有者':<10}")
            print("=" * 70)
            
            for key in keys[:10]:
                address = key.get('address', 'N/A')
                price = key.get('price', 0)
                holders = key.get('holders', 0)
                print(f"{address:<44} {price:<12.2f} {holders:<10}")
            
            print("=" * 70)
            
            # 步骤 2: 购买前几个代理
            print("\n🛒 步骤 2: 开始购买...")
            
            for i, key in enumerate(keys[:4], 1):  # 买前 4 个
                target_wallet = key.get('address')
                if not target_wallet or target_wallet == WALLET:
                    continue
                
                print(f"\n[{i}] 购买 {target_wallet}...")
                
                # 获取 keyOrder
                prepare_url = f"{API_BASE}/order/prepare"
                prepare_data = {
                    "wallet": WALLET,
                    "sharesSubject": target_wallet,
                    "isBuy": True,
                    "amount": 1
                }
                
                try:
                    response = requests.post(prepare_url, json=prepare_data, timeout=60)
                    if response.status_code != 200:
                        print(f"   ❌ 获取 keyOrder 失败")
                        continue
                    
                    result = response.json()
                    keyOrder = result.get('keyOrder', {})
                    
                    if not keyOrder:
                        print(f"   ❌ 无 keyOrder 数据")
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
                        print(f"   🎉 购买成功！")
                        print(f"   结果：{result}")
                    else:
                        print(f"   ❌ 购买失败：{response.text[:100]}")
                    
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"   ❌ 错误：{e}")
                    time.sleep(2)
    else:
        print(f"❌ 错误：{response.text}")
        
except Exception as e:
    print(f"❌ 错误：{e}")

print("\n" + "=" * 60)
print("📊 总结")
print("=" * 60)

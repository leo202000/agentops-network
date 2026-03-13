#!/usr/bin/env python3
"""
ClawMarket - 快速购买 (带重试)

安全提示：私钥必须通过环境变量设置，不要硬编码在代码中！
设置方法：export CLAWMARKET_PRIVATE_KEY="your_private_key"
"""
import os
import requests
import time
from eth_account import Account

API_BASE = "https://api.clawmarket.tech"

# 从环境变量读取私钥 (安全做法)
PRIVATE_KEY = os.getenv("CLAWMARKET_PRIVATE_KEY")
if not PRIVATE_KEY:
    raise ValueError("⚠️ 错误：请设置环境变量 CLAWMARKET_PRIVATE_KEY")

# 从私钥派生钱包地址
account = Account.from_key(PRIVATE_KEY)
WALLET = account.address

def try_buy(target, max_retries=15):
    for attempt in range(1, max_retries + 1):
        print(f"\n [{'='*55}]")
        print(f"尝试 {attempt}/{max_retries}")
        print(f"[{'='*60}]")
        
        try:
            # 1. 准备订单
            r = requests.post(f"{API_BASE}/order/prepare", json={
                "wallet": WALLET,
                "sharesSubject": target,
                "isBuy": True,
                "amount": 1
            }, timeout=30)
            
            if r.status_code != 200:
                print(f"准备订单失败：{r.status_code}")
                time.sleep(3)
                continue
            
            keyOrder = r.json().get('keyOrder', {})
            if not keyOrder:
                print("无订单数据")
                time.sleep(3)
                continue
            
            # 2. 签名
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
            
            # 3. 提交
            keyOrder_body = {
                "trader": message['trader'],
                "sharesSubject": message['sharesSubject'],
                "isBuy": message['isBuy'],
                "amount": str(message['amount']),
                "nonce": str(message['nonce']),
                "deadline": str(message['deadline']),
                "signature": signed.signature.hex()
            }
            
            r = requests.post(f"{API_BASE}/order", json={"keyOrder": keyOrder_body}, timeout=120)
            print(f"提交订单 HTTP: {r.status_code}")
            
            if r.status_code in [200, 201]:
                result = r.json()
                print("\n" + "🎉"*30)
                print("✅✅✅ 购买成功！")
                print("🎉"*30)
                print(f"交易哈希：{result.get('txHash', 'N/A')}")
                print(f"代理：{target}")
                return True
            elif r.status_code in [502, 504, 520]:
                wait = 5 + attempt * 2
                print(f"服务器错误 ({r.status_code})，等待 {wait} 秒...")
                time.sleep(wait)
            else:
                print(f"失败：{r.text[:200]}")
                time.sleep(3)
                
        except Exception as e:
            print(f"错误：{e}")
            time.sleep(5)
    
    return False

if __name__ == "__main__":
    print("="*60)
    print("ClawMarket 自动购买")
    print("="*60)
    
    # 获取代理列表
    r = requests.post(f"{API_BASE}/keys", timeout=30)
    keys = r.json().get('keys', [])
    print(f"可购买代理：{len(keys)} 个")
    
    # 选择第一个 (排除自己)
    target = [k['address'] for k in keys if k['address'] != WALLET][0]
    print(f"目标：{target}")
    
    # 开始购买
    success = try_buy(target)
    
    if not success:
        print("\n❌ 购买失败，稍后重试")

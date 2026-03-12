import requests
import json
from eth_account import Account
from eth_account.messages import encode_typed_data

# 配置
API_BASE = "https://api.clawmarket.tech"
MOLT_API_KEY = "moltbook_sk_3Y-R3S8dP291uZ_CuX_R0RVTCbHdNpgN"
PRIVATE_KEY = "0xdc64abed396b019867b191c7abcf7cf70b59826defe317cb2835946c7065d939"
WALLET = "0x694a096016B681Bd3D3Ed11Aeee47fCcc2E10e1a"
POST_ID = "716ecdf9-801f-4dd5-a187-28c2a2b30d13"

# 获取账户
account = Account.from_key(PRIVATE_KEY)

print("=" * 60)
print("ClawMarket 注册流程")
print("=" * 60)
print(f"钱包：{WALLET}")
print(f"帖子 ID: {POST_ID}")
print("=" * 60)

# 步骤 1: 调用 /register/prepare 获取 permit
print("\n📝 步骤 1: 获取 permit...")
prepare_url = f"{API_BASE}/register/prepare"
prepare_data = {"wallet": WALLET}

try:
    response = requests.post(prepare_url, json=prepare_data, timeout=30)
    result = response.json()
    print(f"HTTP: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ 错误：{result}")
    else:
        print(f"✅ 成功获取 permit")
        permit = result.get('permit')
        print(f"Permit: {json.dumps(permit, indent=2)[:500]}...")
        
        # 步骤 2: 签名 permit
        print("\n✍️  步骤 2: 签名 permit...")
        # TODO: 实现签名逻辑
        
except Exception as e:
    print(f"❌ 错误：{e}")

print("\n" + "=" * 60)

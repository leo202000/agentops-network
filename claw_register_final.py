import requests
import json
from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_utils import to_checksum_address

# 配置
API_BASE = "https://api.clawmarket.tech"
PRIVATE_KEY = "0xdc64abed396b019867b191c7abcf7cf70b59826defe317cb2835946c7065d939"
WALLET = "0x694a096016B681Bd3D3Ed11Aeee47fCcc2E10e1a"
POST_ID = "716ecdf9-801f-4dd5-a187-28c2a2b30d13"

# 获取账户
account = Account.from_key(PRIVATE_KEY)

print("=" * 60)
print("ClawMarket 注册 - 完整流程")
print("=" * 60)

# 步骤 1: 获取 permit
print("\n📝 步骤 1: 获取 permit...")
prepare_url = f"{API_BASE}/register/prepare"
prepare_data = {"wallet": WALLET}

response = requests.post(prepare_url, json=prepare_data, timeout=30)
result = response.json()

if response.status_code != 200:
    print(f"❌ 失败：{result}")
    exit(1)

permit = result.get('permit')
print(f"✅ Permit 获取成功")

# 步骤 2: 签名 permit
print("\n✍️  步骤 2: 签名 permit...")

# 构建 EIP-712 消息
domain = {
    "name": permit['domain']['name'],
    "version": permit['domain']['version'],
    "chainId": permit['domain']['chainId'],
    "verifyingContract": permit['domain']['verifyingContract']
}

types = {
    "Permit": [
        {"name": "owner", "type": "address"},
        {"name": "spender", "type": "address"},
        {"name": "value", "type": "uint256"},
        {"name": "nonce", "type": "uint256"},
        {"name": "deadline", "type": "uint256"}
    ]
}

message = {
    "owner": permit['message']['owner'],
    "spender": permit['message']['spender'],
    "value": int(permit['message']['value']),
    "nonce": int(permit['message']['nonce']),
    "deadline": int(permit['message']['deadline'])
}

# 签名
signed_message = account.sign_typed_data(domain, types, message)
signature = signed_message.signature

print(f"✅ 签名成功")
print(f"签名：0x{signature.hex()[:64]}...")

# 步骤 3: 构建 permit body
from eth_utils import to_bytes, hexstr_if_str

# 解析签名
v = signed_message.v
r = signature[:32].hex()
s = signature[32:64].hex()

permit_body = {
    "owner": message['owner'],
    "spender": message['spender'],
    "value": str(message['value']),
    "deadline": message['deadline'],
    "v": v,
    "r": f"0x{r}",
    "s": f"0x{s}"
}

# 步骤 4: 调用 /register
print("\n📤 步骤 3: 提交注册...")
register_url = f"{API_BASE}/register"
register_data = {
    "post_id": POST_ID,
    "permit": permit_body
}

response = requests.post(register_url, json=register_data, timeout=30)
result = response.json()

print(f"HTTP: {response.status_code}")

if response.status_code == 200 or response.status_code == 201:
    print(f"\n🎉 注册成功！")
    print(f"结果：{json.dumps(result, indent=2)}")
else:
    print(f"\n❌ 注册失败：{result}")

print("\n" + "=" * 60)

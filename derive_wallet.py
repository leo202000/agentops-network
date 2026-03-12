from eth_account import Account
import os

# 从 .env 读取私钥
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('CLAW_PRIVATE_KEY='):
            private_key = line.split('=')[1].strip()
            break

# 派生钱包地址
account = Account.from_key(private_key)
print(f"钱包地址：{account.address}")
print(f"公钥：{account.key.hex()[:16]}...")

#!/usr/bin/env python3
"""
对比两个客户端的签名
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hairstyle_generator import JimengClient, HairstyleGenerator

ak = os.getenv("JIMENG_ACCESS_KEY_ID")
sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")

print(f"AK: {ak}")
print(f"SK: {sk}")
print()

# 测试 1: 直接创建 JimengClient
print("="*60)
print("测试 1: JimengClient 直接创建")
print("="*60)
client1 = JimengClient(ak, sk)
print(f"client1.access_key: {client1.access_key}")
print(f"client1.secret_key: {client1.secret_key}")
print(f"client1.service: {client1.service}")
print()

# 测试 2: 通过 HairstyleGenerator 创建
print("="*60)
print("测试 2: HairstyleGenerator 创建")
print("="*60)
generator = HairstyleGenerator(ak, sk)
client2 = generator.client
print(f"client2.access_key: {client2.access_key}")
print(f"client2.secret_key: {client2.secret_key}")
print(f"client2.service: {client2.service}")
print()

# 对比
print("="*60)
print("对比")
print("="*60)
print(f"AK 相同：{client1.access_key == client2.access_key}")
print(f"SK 相同：{client1.secret_key == client2.secret_key}")
print(f"Service 相同：{client1.service == client2.service}")

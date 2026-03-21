#!/usr/bin/env python3
"""
对象存储配置检查与测试脚本
"""
import os
import sys
from pathlib import Path

# 检查 .env 文件
env_path = Path('/root/.openclaw/workspace/.env')

print("=" * 80)
print("对象存储配置检查")
print("=" * 80)

if not env_path.exists():
    print(f"\n❌ .env 文件不存在：{env_path}")
    sys.exit(1)

print(f"\n✅ .env 文件存在：{env_path}")

# 读取配置
with open(env_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 检查 TOS 配置
tos_configured = all(key in content for key in ['TOS_BUCKET', 'TOS_ACCESS_KEY', 'TOS_SECRET_KEY'])
oss_configured = all(key in content for key in ['OSS_BUCKET', 'OSS_ACCESS_KEY_ID', 'OSS_ACCESS_KEY_SECRET'])

print("\n📋 配置状态:")
print("-" * 80)

if tos_configured:
    print("✅ 火山引擎 TOS 已配置")
    print("   - TOS_BUCKET: 已设置")
    print("   - TOS_ACCESS_KEY: 已设置")
    print("   - TOS_SECRET_KEY: 已设置")
    storage_type = "tos"
elif oss_configured:
    print("✅ 阿里云 OSS 已配置")
    print("   - OSS_BUCKET: 已设置")
    print("   - OSS_ACCESS_KEY_ID: 已设置")
    print("   - OSS_ACCESS_KEY_SECRET: 已设置")
    storage_type = "oss"
else:
    print("❌ 未配置对象存储")
    print("\n💡 请按照以下步骤配置:")
    print("   1. 编辑 .env 文件：vim /root/.openclaw/workspace/.env")
    print("   2. 添加以下配置（选择一种）:")
    print("\n   【火山引擎 TOS（推荐）】")
    print("   TOS_BUCKET=your-bucket-name")
    print("   TOS_ACCESS_KEY=your-access-key-id")
    print("   TOS_SECRET_KEY=your-secret-access-key")
    print("   TOS_REGION=cn-beijing")
    print("\n   【阿里云 OSS】")
    print("   OSS_BUCKET=your-bucket-name")
    print("   OSS_ACCESS_KEY_ID=your-access-key-id")
    print("   OSS_ACCESS_KEY_SECRET=your-access-key-secret")
    print("   OSS_REGION=oss-cn-hangzhou")
    print("\n   3. 保存后重新运行此脚本")
    sys.exit(1)

print(f"\n✅ 对象存储配置完成！")
print(f"\n🚀 下一步:")
print(f"   运行测试脚本：python3 quick_test_dabolang.py")

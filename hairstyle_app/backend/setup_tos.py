#!/usr/bin/env python3
"""
火山引擎 TOS 对象存储配置脚本
"""
import os
import sys
from pathlib import Path

env_path = Path('/root/.openclaw/workspace/.env')

print("=" * 80)
print("火山引擎 TOS 对象存储配置")
print("=" * 80)

print("\n📖 配置说明:")
print("-" * 80)
print("1. 登录火山引擎控制台：https://console.volcengine.com/")
print("2. 进入 TOS 控制台：https://console.volcengine.com/tos/")
print("3. 创建存储桶（Bucket），记录名称")
print("4. 进入 IAM 控制台：https://console.volcengine.com/iam/")
print("5. 创建访问密钥，记录 Access Key ID 和 Secret Access Key")
print("-" * 80)

print("\n请输入配置信息（按 Enter 跳过）:")
print()

tos_bucket = input("TOS_BUCKET (存储桶名称): ").strip()
tos_ak = input("TOS_ACCESS_KEY (访问密钥 ID): ").strip()
tos_sk = input("TOS_SECRET_KEY (访问密钥): ").strip()
tos_region = input("TOS_REGION (区域，默认 cn-beijing): ").strip() or "cn-beijing"

if not all([tos_bucket, tos_ak, tos_sk]):
    print("\n❌ 配置信息不完整，已取消配置")
    sys.exit(1)

# 读取现有 .env 文件
existing_content = ""
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        existing_content = f.read()
    
    # 移除旧的 TOS 配置
    lines = existing_content.split('\n')
    new_lines = []
    for line in lines:
        if not line.strip().startswith('TOS_'):
            new_lines.append(line)
    existing_content = '\n'.join(new_lines)

# 添加新配置
new_config = f"""
# 火山引擎 TOS 对象存储配置
TOS_BUCKET={tos_bucket}
TOS_ACCESS_KEY={tos_ak}
TOS_SECRET_KEY={tos_sk}
TOS_REGION={tos_region}
"""

# 写入 .env 文件
with open(env_path, 'w', encoding='utf-8') as f:
    f.write(existing_content.rstrip() + new_config)

print("\n✅ TOS 配置已保存到 .env 文件")

# 设置文件权限
os.chmod(env_path, 0o600)
print("🔒 已设置 .env 文件权限为 600（仅所有者可读写）")

# 安装 TOS SDK
print("\n📦 检查 TOS SDK...")
try:
    import tos
    print("✅ TOS SDK 已安装")
except ImportError:
    print("⚠️  正在安装 TOS SDK...")
    os.system("pip install tos -q")
    try:
        import tos
        print("✅ TOS SDK 安装成功")
    except ImportError:
        print("❌ TOS SDK 安装失败，请手动安装：pip install tos")

print("\n🎉 配置完成！")
print("\n🚀 下一步:")
print("   运行测试脚本：python3 quick_test_dabolang.py")

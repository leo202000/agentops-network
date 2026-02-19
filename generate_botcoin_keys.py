#!/usr/bin/env python3
"""
生成用于 botcoin.farm 的 Ed25519 密钥对
"""

import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import secrets

def generate_ed25519_keypair():
    """
    生成 Ed25519 密钥对
    """
    # 生成私钥
    private_key = Ed25519PrivateKey.generate()
    
    # 获取公钥
    public_key = private_key.public_key()
    
    # 将密钥转换为 base64 编码
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    
    private_key_b64 = base64.b64encode(private_bytes).decode('utf-8')
    public_key_b64 = base64.b64encode(public_bytes).decode('utf-8')
    
    return public_key_b64, private_key_b64

def generate_keypair_alternative():
    """
    使用另一种方法生成密钥对（如果 cryptography 不可用）
    """
    try:
        import nacl.signing
        import nacl.encoding
        
        # 生成密钥对
        signing_key = nacl.signing.SigningKey.generate()
        verify_key = signing_key.verify_key
        
        # 转换为 base64
        public_key_b64 = base64.b64encode(verify_key.encode()).decode('utf-8')
        private_key_b64 = base64.b64encode(signing_key.encode()).decode('utf-8')
        
        return public_key_b64, private_key_b64
    except ImportError:
        print("警告: 未安装 PyNaCl 库")
        print("请运行: pip install PyNaCl")
        return None, None

if __name__ == "__main__":
    try:
        import cryptography
        import cryptography.hazmat.primitives.asymmetric.ed25519
        import cryptography.hazmat.primitives.serialization as serialization
        print("使用 cryptography 库生成密钥对...")
        
        public_key, private_key = generate_ed25519_keypair()
        
    except ImportError:
        print("cryptography 库不可用，尝试使用 PyNaCl...")
        print("请先安装: pip install PyNaCl")
        public_key, private_key = generate_keypair_alternative()
    
    if public_key and private_key:
        print("\n=== Botcoin.farm 密钥对 ===")
        print(f"公钥 (publicKey): {public_key}")
        print(f"私钥 (secretKey): {private_key}")
        print("=========================")
        print("重要提示：")
        print("1. 请安全保存您的私钥，切勿泄露给他人")
        print("2. 私钥一旦丢失无法找回")
        print("3. 公钥可以安全地分享用于注册")
        print("=========================")
        
        # 验证密钥长度
        print(f"\n密钥验证:")
        print(f"公钥长度: {len(public_key)} 字符 (应为43或44)")
        print(f"私钥长度: {len(private_key)} 字符 (应为86或88)")
    else:
        print("\n错误: 请先安装必要的库")
        print("pip install cryptography") 
        print("或")
        print("pip install PyNaCl")
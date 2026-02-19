#!/usr/bin/env python3
"""
AgentCoin 钱包生成器
生成 Base 链兼容的以太坊钱包
"""

import json
import os
from datetime import datetime
from pathlib import Path

def generate_wallet():
    """生成新的以太坊钱包"""
    try:
        from eth_account import Account
        from eth_account.signers.local import LocalAccount
        
        # 启用新的 Mnemonic 功能
        Account.enable_unaudited_hdwallet_features()
        
        # 方法 1：简单账户生成
        account = Account.create()
        
        wallet_info = {
            "address": account.address,
            "private_key": account.key.hex(),
            "created_at": datetime.now().isoformat(),
            "purpose": "AgentCoin (AGC) Registration",
            "network": "Base Mainnet",
            "chain_id": 8453,
            "rpc_url": "https://mainnet.base.org"
        }
        
        return wallet_info, account
        
    except ImportError:
        print("⚠️ 未安装 eth_account 库")
        print("请运行：pip install eth-account")
        print("\n或者使用在线钱包生成器：")
        print("https://www.myetherwallet.com/wallet/access")
        return None, None

def save_wallet_securely(wallet_info: dict):
    """安全保存钱包信息"""
    
    # 创建配置目录
    config_dir = Path.home() / ".openclaw" / "wallets"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # 钱包文件路径
    wallet_file = config_dir / "agentcoin_wallet.json"
    
    # ⚠️ 安全警告：生产环境应该加密私钥！
    # 这里为了演示使用明文存储，实际使用请加密
    
    # 设置文件权限（仅所有者可读写）
    with open(wallet_file, 'w') as f:
        json.dump(wallet_info, f, indent=2)
    
    # 设置文件权限为 600（Unix/Linux/Mac）
    try:
        os.chmod(wallet_file, 0o600)
        print(f"✅ 文件权限已设置为 600（仅所有者可读写）")
    except Exception as e:
        print(f"⚠️ 无法设置文件权限：{e}")
    
    return wallet_file

def display_wallet_info(wallet_info: dict):
    """显示钱包信息"""
    print("\n" + "="*60)
    print("🎉 AgentCoin 钱包生成成功！")
    print("="*60)
    print(f"\n📍 钱包地址:")
    print(f"   {wallet_info['address']}")
    print(f"\n🔑 私钥:")
    print(f"   {wallet_info['private_key']}")
    print(f"\n⛓️  网络信息:")
    print(f"   网络：{wallet_info['network']}")
    print(f"   链 ID: {wallet_info['chain_id']}")
    print(f"   RPC:   {wallet_info['rpc_url']}")
    print(f"\n📅 创建时间:")
    print(f"   {wallet_info['created_at']}")
    print(f"\n💡 用途:")
    print(f"   {wallet_info['purpose']}")
    print("="*60)
    
    print("\n⚠️  安全警告：")
    print("   1. 永远不要分享您的私钥！")
    print("   2. 安全备份私钥（建议离线存储）")
    print("   3. 不要将私钥上传到网络或发送给他人")
    print("   4. 考虑使用硬件钱包存储大额资金")
    print("="*60)

def get_base_network_config():
    """获取 Base 网络配置（用于 MetaMask）"""
    return {
        "networkName": "Base Mainnet",
        "rpcUrl": "https://mainnet.base.org",
        "chainId": 8453,
        "currencySymbol": "ETH",
        "blockExplorerUrl": "https://basescan.org"
    }

def display_metamask_setup():
    """显示 MetaMask 设置指南"""
    config = get_base_network_config()
    
    print("\n" + "="*60)
    print("🦊 MetaMask 添加 Base 网络指南")
    print("="*60)
    print(f"\n1. 打开 MetaMask")
    print(f"2. 点击网络选择器（顶部）")
    print(f"3. 选择 '添加网络'")
    print(f"4. 填写以下信息:")
    print(f"\n   网络名称：{config['networkName']}")
    print(f"   新 RPC URL: {config['rpcUrl']}")
    print(f"   链 ID:      {config['chainId']}")
    print(f"   货币符号：  {config['currencySymbol']}")
    print(f"   区块浏览器：{config['blockExplorerUrl']}")
    print(f"\n5. 点击 '保存'")
    print("="*60)

def main():
    print("🪙 AgentCoin 钱包生成器")
    print("="*60)
    print("正在生成 Base 链兼容的以太坊钱包...")
    print()
    
    # 生成钱包
    wallet_info, account = generate_wallet()
    
    if not wallet_info:
        print("\n❌ 钱包生成失败")
        print("\n您可以选择:")
        print("1. 安装依赖：pip install eth-account")
        print("2. 使用 MetaMask 创建钱包")
        print("3. 使用其他钱包工具")
        return
    
    # 显示钱包信息
    display_wallet_info(wallet_info)
    
    # 保存钱包
    print("\n💾 正在安全保存钱包信息...")
    wallet_file = save_wallet_securely(wallet_info)
    print(f"✅ 钱包已保存到：{wallet_file}")
    
    # 显示 MetaMask 设置指南
    display_metamask_setup()
    
    # 下一步指南
    print("\n" + "="*60)
    print("📋 下一步行动")
    print("="*60)
    print("\n1. ✅ 钱包已生成")
    print("2. 🔷 向钱包添加少量 ETH（用于 Base 链 GAS）")
    print("   - 可以从交易所提现到该地址")
    print("   - 或使用跨链桥从其他链转移")
    print("3. 🐦 准备 X (Twitter) 账户进行验证")
    print("4. 🌐 访问 https://agentcoin.site/bind-x.html")
    print("5. 📝 按照流程完成注册")
    print("="*60)
    
    print("\n💡 提示：")
    print("   - Base 链 GAS 费用非常低（通常<$0.05）")
    print("   - 建议添加价值$5-10 的 ETH 用于多次交互")
    print("   - 可以使用 https://bridge.base.org 从其他链转移 ETH")
    print("="*60)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
USDC 支付测试脚本 - Base Sepolia
测试 USDC 转账功能
"""

from web3 import Web3
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class USDCTest:
    def __init__(self):
        # Base Sepolia 配置
        self.rpc_url = "https://sepolia.base.org"
        self.chain_id = 84532
        self.usdc_address = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
        
        # 连接 Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # USDC ABI (简化 ERC20)
        self.usdc_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]
        
        # 账户
        self.private_key = os.getenv("PRIVATE_KEY")
        if self.private_key:
            self.account = self.w3.eth.account.from_key(self.private_key)
            self.address = self.account.address
        else:
            self.account = None
            self.address = None
    
    def check_connection(self):
        """检查连接"""
        try:
            is_connected = self.w3.is_connected()
            print(f"连接状态：{'✅ 已连接' if is_connected else '❌ 未连接'}")
            return is_connected
        except Exception as e:
            print(f"连接错误：{e}")
            return False
    
    def get_balances(self):
        """获取余额"""
        if not self.address:
            print("⚠️  未配置私钥")
            return None, None
        
        try:
            # ETH 余额
            eth_balance = self.w3.eth.get_balance(self.address)
            eth_balance_eth = self.w3.from_wei(eth_balance, 'ether')
            
            # USDC 余额
            usdc_contract = self.w3.eth.contract(
                address=self.usdc_address,
                abi=self.usdc_abi
            )
            usdc_balance = usdc_contract.functions.balanceOf(self.address).call()
            decimals = usdc_contract.functions.decimals().call()
            usdc_balance_usdc = usdc_balance / (10 ** decimals)
            
            return float(eth_balance_eth), float(usdc_balance_usdc)
            
        except Exception as e:
            print(f"查询余额错误：{e}")
            return None, None
    
    def test_transfer(self, to_address, amount_usdc):
        """测试转账"""
        if not self.account:
            print("❌ 未配置私钥")
            return None
        
        try:
            usdc_contract = self.w3.eth.contract(
                address=self.usdc_address,
                abi=self.usdc_abi
            )
            
            decimals = usdc_contract.functions.decimals().call()
            amount_wei = int(amount_usdc * (10 ** decimals))
            
            print(f"\n准备转账:")
            print(f"  from: {self.address}")
            print(f"  to: {to_address}")
            print(f"  amount: {amount_usdc} USDC")
            
            # 构建交易
            tx = usdc_contract.functions.transfer(
                to_address,
                amount_wei
            ).build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'maxFeePerGas': self.w3.eth.gas_price,
                'maxPriorityFeePerGas': self.w3.eth.gas_price,
                'chainId': self.chain_id
            })
            
            # 签名交易
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            
            # 发送交易
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            print(f"\n交易已发送:")
            print(f"  Hash: {tx_hash.hex()}")
            print(f"  链接：https://sepolia.basescan.org/tx/{tx_hash.hex()}")
            
            # 等待确认
            print("\n等待确认...")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            
            if receipt['status'] == 1:
                print(f"✅ 转账成功！")
                print(f"  Gas 使用：{receipt['gasUsed']}")
                print(f"  区块：{receipt['blockNumber']}")
                return tx_hash.hex()
            else:
                print(f"❌ 交易失败")
                return None
                
        except Exception as e:
            print(f"转账错误：{e}")
            return None
    
    def run_test(self):
        """运行完整测试"""
        print("="*70)
        print("🧪 USDC 支付测试 - Base Sepolia")
        print("="*70)
        print()
        
        # 1. 检查连接
        print("1️⃣ 检查连接...")
        if not self.check_connection():
            print("\n❌ 无法连接到 Base Sepolia")
            return False
        print()
        
        # 2. 检查配置
        print("2️⃣ 检查配置...")
        if not self.address:
            print("\n⚠️  未配置私钥")
            print("\n请创建 .env 文件:")
            print("PRIVATE_KEY=0x 你的私钥")
            return False
        
        print(f"钱包地址：{self.address}")
        print()
        
        # 3. 查询余额
        print("3️⃣ 查询余额...")
        eth_balance, usdc_balance = self.get_balances()
        
        if eth_balance is not None:
            print(f"ETH 余额：{eth_balance:.4f} ETH")
        else:
            print("ETH 余额：查询失败")
        
        if usdc_balance is not None:
            print(f"USDC 余额：{usdc_balance:.2f} USDC")
        else:
            print("USDC 余额：查询失败")
        
        if eth_balance == 0 or eth_balance is None:
            print("\n⚠️  ETH 余额不足！")
            print("请获取测试 ETH: https://faucet.circle.com/")
            return False
        
        if usdc_balance == 0 or usdc_balance is None:
            print("\n⚠️  USDC 余额不足！")
            print("请获取测试 USDC: https://faucet.circle.com/")
            return False
        
        print()
        
        # 4. 测试转账
        print("4️⃣ 测试转账...")
        print("\n请输入接收地址 (或按回车使用测试地址):")
        to_address = input("> ").strip()
        
        if not to_address:
            # 使用自己的地址作为测试
            to_address = self.address
            print(f"使用自己的地址进行测试：{to_address}")
        
        print("\n请输入转账金额 USDC (默认 0.1):")
        amount = input("> ").strip()
        amount_usdc = float(amount) if amount else 0.1
        
        tx_hash = self.test_transfer(to_address, amount_usdc)
        
        if tx_hash:
            print("\n" + "="*70)
            print("✅ 测试完成！")
            print("="*70)
            return True
        else:
            print("\n" + "="*70)
            print("❌ 测试失败")
            print("="*70)
            return False


def main():
    """主函数"""
    tester = USDCTest()
    success = tester.run_test()
    
    print("\n💡 提示:")
    print("  - 获取测试资源：https://faucet.circle.com/")
    print("  - Base Sepolia 浏览器：https://sepolia.basescan.org/")
    print("  - 配置私钥：创建 .env 文件，添加 PRIVATE_KEY=0x...")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())

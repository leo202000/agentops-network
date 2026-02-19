#!/usr/bin/env python3
"""
AgentCoin 注册交互式助手
逐步指导完成注册流程
"""

import json
import os
from datetime import datetime
from pathlib import Path

class AgentCoinRegisterHelper:
    def __init__(self):
        self.config_dir = Path.home() / ".openclaw" / "agentcoin"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.progress_file = self.config_dir / "registration_progress.json"
        self.load_progress()
        
    def load_progress(self):
        """加载注册进度"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                "started_at": datetime.now().isoformat(),
                "current_step": 0,
                "steps": {
                    "wallet_created": False,
                    "wallet_address": None,
                    "base_network_added": False,
                    "eth_prepared": False,
                    "eth_amount": None,
                    "x_account_ready": False,
                    "x_username": None,
                    "verification_code": None,
                    "tweet_posted": False,
                    "tweet_url": None,
                    "registered_onchain": False,
                    "agent_id": None,
                    "transaction_hash": None
                }
            }
            
    def save_progress(self):
        """保存注册进度"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)
            
    def display_welcome(self):
        """显示欢迎信息"""
        print("\n" + "="*70)
        print("🪙 AgentCoin (AGC) 注册助手")
        print("="*70)
        print("\n欢迎使用 AgentCoin 注册助手！")
        print("我将指导您完成整个注册流程。")
        print("\n预计时间：15-30 分钟")
        print("所需准备：浏览器、X (Twitter) 账户")
        print("="*70)
        
    def step_1_wallet(self):
        """步骤 1：创建钱包"""
        print("\n" + "="*70)
        print("📦 步骤 1/6: 创建钱包")
        print("="*70)
        
        print("\n请选择您想使用的方式:")
        print("\n1️⃣  使用 MetaMask（⭐ 最推荐，适合新手）")
        print("2️⃣  使用现有钱包（已有 MetaMask 或其他兼容钱包）")
        print("3️⃣  使用 Coinbase Wallet")
        print("4️⃣  我稍后会手动完成，继续下一步")
        
        choice = input("\n请输入选项 (1-4): ").strip()
        
        if choice == '1':
            print("\n✅ 好选择！MetaMask 是最流行的钱包。")
            print("\n📋 MetaMask 创建步骤:")
            print("   1. 打开浏览器访问：https://metamask.io")
            print("   2. 点击 'Download' 下载安装")
            print("   3. 选择 'Create a new wallet'")
            print("   4. 创建强密码")
            print("   5. ⚠️ 重要：备份助记词（12 个单词）")
            print("      - 写在纸上")
            print("      - 存放在安全地方")
            print("      - 不要截图或存储云端")
            print("      - 不要分享给任何人！")
            print("   6. 完成创建")
            
            confirm = input("\n完成创建后，输入 'y' 继续：").strip().lower()
            if confirm == 'y':
                self.progress['steps']['wallet_created'] = True
                
        elif choice == '2':
            print("\n✅ 好的，使用现有钱包。")
            wallet_address = input("请输入您的钱包地址 (0x 开头): ").strip()
            if wallet_address.startswith('0x') and len(wallet_address) == 42:
                self.progress['steps']['wallet_created'] = True
                self.progress['steps']['wallet_address'] = wallet_address
                print(f"✅ 钱包地址已记录：{wallet_address[:20]}...{wallet_address[-10:]}")
            else:
                print("⚠️ 钱包地址格式不正确，请检查")
                return
                
        elif choice == '3':
            print("\n✅ Coinbase Wallet 也是不错的选择。")
            print("\n📋 Coinbase Wallet 步骤:")
            print("   1. 下载 Coinbase Wallet 应用")
            print("   2. 创建新钱包")
            print("   3. 备份恢复短语")
            print("   4. 获取钱包地址")
            
            confirm = input("\n完成后输入 'y' 继续：").strip().lower()
            if confirm == 'y':
                self.progress['steps']['wallet_created'] = True
                
        else:
            print("\n⚠️ 您可以稍后手动完成这一步。")
            print("\n📖 详细指南已保存到：agentcoin_wallet_setup.md")
            
        self.save_progress()
        
    def step_2_base_network(self):
        """步骤 2：添加 Base 网络"""
        print("\n" + "="*70)
        print("🌐 步骤 2/6: 添加 Base 网络")
        print("="*70)
        
        print("\nBase 是一个快速、低成本的 Layer 2 网络。")
        print("\n📋 在 MetaMask 中添加 Base 网络:")
        print("\n   1. 点击 MetaMask 顶部的网络选择器")
        print("   2. 点击 'Add network'")
        print("   3. 点击 'Add a network manually'")
        print("\n   4. 填写以下信息:")
        print("      ┌─────────────────────────────────────┐")
        print("      │ 网络名称：Base Mainnet              │")
        print("      │ RPC URL:    https://mainnet.base.org│")
        print("      │ 链 ID:      8453                     │")
        print("      │ 货币符号：  ETH                      │")
        print("      │ 区块浏览器：https://basescan.org    │")
        print("      └─────────────────────────────────────┘")
        print("\n   5. 点击 'Save' 保存")
        
        print("\n💡 提示：Base 网络 GAS 费用非常低，通常<$0.05")
        
        confirm = input("\n添加完成后输入 'y' 继续：").strip().lower()
        if confirm == 'y':
            self.progress['steps']['base_network_added'] = True
            self.save_progress()
            print("✅ Base 网络已添加！")
            
    def step_3_eth(self):
        """步骤 3：获取 ETH"""
        print("\n" + "="*70)
        print("💰 步骤 3/6: 获取 ETH 用于 GAS 费用")
        print("="*70)
        
        print("\n您需要一些 ETH 来支付 Base 链上的交易费用。")
        print("\n📋 获取 ETH 的方式:")
        
        print("\n方式 1️⃣: 从交易所提现（推荐）")
        print("   - 在币安/OKX/Coinbase 等购买 ETH")
        print("   - 选择提现/转账")
        print("   - ⚠️ 网络选择：BASE (不是 ERC20!)")
        print("   - 粘贴您的钱包地址")
        print("   - 确认提现")
        
        print("\n方式 2️⃣: 使用官方桥接")
        print("   - 访问：https://bridge.base.org")
        print("   - 连接钱包")
        print("   - 从 Ethereum 或其他链桥接")
        
        print("\n方式 3️⃣: 使用第三方桥接")
        print("   - https://bridge.bungee.exchange")
        print("   - https://app.across.to")
        print("   - https://hop.exchange")
        
        print("\n💡 建议金额:")
        print("   - 最低：$1-2 USD（足够注册）")
        print("   - 推荐：$5-10 USD（可多次交互）")
        
        has_eth = input("\n您是否已经有 Base 链上的 ETH？(y/n): ").strip().lower()
        
        if has_eth == 'y':
            self.progress['steps']['eth_prepared'] = True
            amount = input("大约有多少 ETH (USD 价值)？").strip()
            self.progress['steps']['eth_amount'] = amount
            print(f"✅ ETH 已准备：约${amount}")
        else:
            print("\n⚠️ 请先获取一些 ETH，然后再继续。")
            print("\n📖 提示：")
            print("   - Base 链非常便宜，$5 就足够很多次交互")
            print("   - 从交易所提现通常需要 10-30 分钟")
            print("   - 桥接通常需要 5-15 分钟")
            
        self.save_progress()
        
    def step_4_x_account(self):
        """步骤 4：准备 X 账户"""
        print("\n" + "="*70)
        print("🐦 步骤 4/6: 准备 X (Twitter) 账户")
        print("="*70)
        
        print("\nAgentCoin 需要验证您的 X 账户。")
        
        has_x = input("\n您有 X (Twitter) 账户吗？(y/n): ").strip().lower()
        
        if has_x == 'y':
            username = input("请输入您的 X 用户名 (不含@): ").strip()
            self.progress['steps']['x_account_ready'] = True
            self.progress['steps']['x_username'] = username
            print(f"✅ X 账户已准备：@{username}")
        else:
            print("\n📋 创建 X 账户:")
            print("   1. 访问 https://twitter.com")
            print("   2. 点击 'Sign up'")
            print("   3. 按照提示创建账户")
            print("   4. 完成邮箱/手机验证")
            
            confirm = input("\n创建完成后输入 'y' 继续：").strip().lower()
            if confirm == 'y':
                username = input("请输入您的 X 用户名 (不含@): ").strip()
                self.progress['steps']['x_account_ready'] = True
                self.progress['steps']['x_username'] = username
                
        self.save_progress()
        
    def step_5_registration(self):
        """步骤 5：开始注册"""
        print("\n" + "="*70)
        print("🎯 步骤 5/6: 开始注册 AgentCoin")
        print("="*70)
        
        print("\n现在让我们开始正式注册！")
        
        print("\n📋 注册步骤:")
        print("\n1️⃣  打开 AgentCoin 注册页面:")
        print("   👉 https://agentcoin.site/bind-x.html")
        
        print("\n2️⃣  连接钱包:")
        print("   - 点击 'Connect Wallet' 按钮")
        print("   - 选择您的钱包类型")
        print("   - 在钱包中授权连接")
        
        print("\n3️⃣  获取验证代码:")
        print("   - 连接后，系统会显示一个验证代码")
        print("   - 复制这个代码（类似：ABC123XYZ）")
        
        verification_code = input("\n请输入您获得的验证代码：").strip()
        if verification_code:
            self.progress['steps']['verification_code'] = verification_code
            print(f"✅ 验证代码已记录：{verification_code}")
            
        print("\n4️⃣  发布验证推文:")
        print("   - 登录 X (Twitter)")
        print("   - 发布新推文，内容示例:")
        print(f"""
   🤖 Registering my AI Agent @AgentCoin!
   Verification Code: {verification_code}
   #AgentCoin #AI #Base #Crypto
""")
        print("   - 确保推文是公开的（不是保护账户）")
        
        tweet_posted = input("\n发布推文后输入 'y' 继续：").strip().lower()
        if tweet_posted == 'y':
            self.progress['steps']['tweet_posted'] = True
            tweet_url = input("请输入推文 URL (可选): ").strip()
            if tweet_url:
                self.progress['steps']['tweet_url'] = tweet_url
                
        print("\n5️⃣  验证推文:")
        print("   - 返回 AgentCoin 网站")
        print("   - 点击 'Verify' 或 'Check Tweet' 按钮")
        print("   - 等待系统验证（通常几秒到 1 分钟）")
        
        verified = input("\n验证成功后输入 'y' 继续：").strip().lower()
        if verified == 'y':
            print("✅ X 账户验证成功！")
            
        self.save_progress()
        
    def step_6_onchain(self):
        """步骤 6：链上注册"""
        print("\n" + "="*70)
        print("⛓️  步骤 6/6: 完成链上注册")
        print("="*70)
        
        print("\n最后一步：在 Base 链上注册您的 AI 代理！")
        
        print("\n📋 链上注册步骤:")
        
        print("\n1️⃣  填写代理信息:")
        print("   - 代理名称（例如：贝贝 AI Assistant）")
        print("   - 代理描述（简短介绍您的 AI 代理）")
        print("   - 能力标签（例如：AI, Assistant, Automation）")
        print("   - 社交媒体链接（可选）")
        
        agent_name = input("\n请输入代理名称：").strip()
        if agent_name:
            print(f"✅ 代理名称：{agent_name}")
            
        print("\n2️⃣  确认注册:")
        print("   - 检查所有信息是否正确")
        print("   - 点击 'Register on-chain' 或类似按钮")
        
        print("\n3️⃣  批准交易:")
        print("   - 钱包会弹出交易确认")
        print("   - 查看 GAS 费用（应该很低，<$0.05）")
        print("   - 点击 'Confirm' 或 '确认'")
        
        print("\n4️⃣  等待确认:")
        print("   - 交易提交后，等待区块确认")
        print("   - 通常需要 30 秒 - 2 分钟")
        print("   - 可以在 https://basescan.org 查看交易状态")
        
        tx_hash = input("\n交易完成后，输入交易哈希 (可选): ").strip()
        if tx_hash:
            self.progress['steps']['transaction_hash'] = tx_hash
            
        registered = input("\n注册成功后输入 'y' 完成：").strip().lower()
        if registered == 'y':
            self.progress['steps']['registered_onchain'] = True
            agent_id = input("如果显示了代理 ID，请输入：").strip()
            if agent_id:
                self.progress['steps']['agent_id'] = agent_id
            print("\n🎉 恭喜！注册完成！")
            
        self.save_progress()
        
    def display_summary(self):
        """显示注册摘要"""
        print("\n" + "="*70)
        print("📊 注册完成摘要")
        print("="*70)
        
        steps = self.progress['steps']
        
        print(f"\n✅ 钱包创建：{'已完成' if steps['wallet_created'] else '未完成'}")
        if steps['wallet_address']:
            print(f"   地址：{steps['wallet_address'][:20]}...{steps['wallet_address'][-10:]}")
            
        print(f"✅ Base 网络：{'已添加' if steps['base_network_added'] else '未添加'}")
        print(f"✅ ETH 准备：{'已准备' if steps['eth_prepared'] else '未准备'}")
        if steps['eth_amount']:
            print(f"   金额：${steps['eth_amount']}")
            
        print(f"✅ X 账户：{'已准备' if steps['x_account_ready'] else '未准备'}")
        if steps['x_username']:
            print(f"   用户名：@{steps['x_username']}")
            
        print(f"✅ 验证代码：{steps['verification_code'] or '未记录'}")
        print(f"✅ 推文发布：{'已完成' if steps['tweet_posted'] else '未完成'}")
        if steps['tweet_url']:
            print(f"   URL: {steps['tweet_url']}")
            
        print(f"✅ 链上注册：{'已完成' if steps['registered_onchain'] else '未完成'}")
        if steps['agent_id']:
            print(f"   代理 ID: {steps['agent_id']}")
            
        if steps['transaction_hash']:
            print(f"✅ 交易哈希：{steps['transaction_hash']}")
            print(f"   查看：https://basescan.org/tx/{steps['transaction_hash']}")
            
        # 检查是否全部完成
        all_done = all([
            steps['wallet_created'],
            steps['base_network_added'],
            steps['eth_prepared'],
            steps['x_account_ready'],
            steps['tweet_posted'],
            steps['registered_onchain']
        ])
        
        if all_done:
            print("\n" + "="*70)
            print("🎉🎉🎉 注册全部完成！🎉🎉🎉")
            print("="*70)
            print("\n您现在可以:")
            print("   ✅ 开始浏览 AgentCoin 平台")
            print("   ✅ 参与任务赚取 AGC 代币")
            print("   ✅ 与其他 AI 代理协作")
            print("   ✅ 参与社区治理")
            print("\n📖 下一步:")
            print("   1. 探索平台功能")
            print("   2. 了解可用任务")
            print("   3. 加入社区 Discord")
            print("   4. 开始赚取 AGC！")
        else:
            print("\n⚠️ 还有部分步骤未完成，可以继续完成注册。")
            
        print("\n" + "="*70)
        
    def run(self):
        """运行完整注册流程"""
        self.display_welcome()
        
        # 检查是否有进行中的进度
        current_step = self.progress['current_step']
        
        if current_step == 0:
            self.step_1_wallet()
            self.progress['current_step'] = 1
            self.save_progress()
            
        if current_step <= 1:
            self.step_2_base_network()
            self.progress['current_step'] = 2
            self.save_progress()
            
        if current_step <= 2:
            self.step_3_eth()
            self.progress['current_step'] = 3
            self.save_progress()
            
        if current_step <= 3:
            self.step_4_x_account()
            self.progress['current_step'] = 4
            self.save_progress()
            
        if current_step <= 4:
            self.step_5_registration()
            self.progress['current_step'] = 5
            self.save_progress()
            
        if current_step <= 5:
            self.step_6_onchain()
            self.progress['current_step'] = 6
            self.save_progress()
            
        self.display_summary()


def main():
    helper = AgentCoinRegisterHelper()
    helper.run()


if __name__ == "__main__":
    main()

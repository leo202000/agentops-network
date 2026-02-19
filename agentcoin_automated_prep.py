#!/usr/bin/env python3
"""
AgentCoin 自动化准备脚本
完成所有可以自动化的准备工作
"""

import json
import os
from datetime import datetime
from pathlib import Path

class AgentCoinAutoPrep:
    def __init__(self):
        self.config_dir = Path.home() / ".openclaw" / "agentcoin"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    def prepare_network_config(self):
        """准备 Base 网络配置"""
        config = {
            "network_name": "Base Mainnet",
            "rpc_url": "https://mainnet.base.org",
            "chain_id": 8453,
            "currency_symbol": "ETH",
            "block_explorer": "https://basescan.org"
        }
        
        config_file = self.config_dir / "base_network_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        print("✅ Base 网络配置已准备")
        print(f"   文件：{config_file}")
        return config
        
    def prepare_tweet_template(self, verification_code="[YOUR_CODE]"):
        """准备推文模板"""
        template = f"""🤖 Registering my AI Agent @AgentCoin!
Verification Code: {verification_code}
#AgentCoin #AI #Base #Crypto

Registering at: https://agentcoin.site/bind-x.html
"""
        
        template_file = self.config_dir / "tweet_template.txt"
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(template)
            
        print("✅ 推文模板已准备")
        print(f"   文件：{template_file}")
        return template
        
    def prepare_registration_checklist(self):
        """准备注册检查清单"""
        checklist = {
            "title": "AgentCoin 注册检查清单",
            "created_at": datetime.now().isoformat(),
            "steps": [
                {
                    "step": 1,
                    "action": "安装 MetaMask",
                    "url": "https://metamask.io",
                    "status": "pending",
                    "automated": False
                },
                {
                    "step": 2,
                    "action": "创建钱包并备份助记词",
                    "status": "pending",
                    "automated": False,
                    "warning": "助记词必须安全备份，不要分享给任何人"
                },
                {
                    "step": 3,
                    "action": "添加 Base 网络",
                    "config_file": str(self.config_dir / "base_network_config.json"),
                    "status": "pending",
                    "automated": True
                },
                {
                    "step": 4,
                    "action": "获取 ETH 到 Base 链",
                    "amount_usd": "5-10",
                    "methods": [
                        "交易所提现（Binance/OKX/Coinbase）",
                        "官方桥接：https://bridge.base.org",
                        "第三方桥接：https://bridge.bungee.exchange"
                    ],
                    "status": "pending",
                    "automated": False
                },
                {
                    "step": 5,
                    "action": "访问 AgentCoin 注册页面",
                    "url": "https://agentcoin.site/bind-x.html",
                    "status": "pending",
                    "automated": False
                },
                {
                    "step": 6,
                    "action": "连接钱包并获取验证代码",
                    "status": "pending",
                    "automated": False
                },
                {
                    "step": 7,
                    "action": "发布验证推文",
                    "template_file": str(self.config_dir / "tweet_template.txt"),
                    "status": "pending",
                    "automated": False
                },
                {
                    "step": 8,
                    "action": "验证推文并完成链上注册",
                    "estimated_gas": "$0.01-0.05",
                    "status": "pending",
                    "automated": False
                }
            ]
        }
        
        checklist_file = self.config_dir / "registration_checklist.json"
        with open(checklist_file, 'w', encoding='utf-8') as f:
            json.dump(checklist, f, indent=2, ensure_ascii=False)
            
        print("✅ 注册检查清单已准备")
        print(f"   文件：{checklist_file}")
        return checklist
        
    def prepare_quick_guide(self):
        """准备快速指南"""
        guide = """
╔══════════════════════════════════════════════════════════════╗
║          AgentCoin (AGC) 快速注册指南                        ║
╚══════════════════════════════════════════════════════════════╝

📱 第一步：安装 MetaMask（2 分钟）
   访问：https://metamask.io
   点击：Download → 安装浏览器扩展
   
🔐 第二步：创建钱包（3 分钟）
   点击：Create a new wallet
   操作：设置密码 → 写下 12 个助记词（重要！）
   ⚠️  助记词必须写在纸上，安全保存！
   
🌐 第三步：添加 Base 网络（1 分钟）
   点击 MetaMask 顶部网络选择器
   选择：Add network → Add a network manually
   
   复制以下配置：
   ┌─────────────────────────────────────────┐
   │ 网络名称：Base Mainnet                  │
   │ RPC URL:    https://mainnet.base.org    │
   │ 链 ID:      8453                         │
   │ 货币符号：  ETH                          │
   │ 区块浏览器：https://basescan.org        │
   └─────────────────────────────────────────┘
   
💰 第四步：获取 ETH（10-30 分钟）
   方法 1：从交易所提现到 Base 链
   方法 2：使用 https://bridge.base.org 桥接
   金额：$5-10 USD
   
🎯 第五步：注册 AgentCoin（5 分钟）
   访问：https://agentcoin.site/bind-x.html
   
   1. 点击"Connect Wallet" → 选择 MetaMask → 确认
   2. 复制验证代码（类似：ABC123XYZ）
   3. 打开 X (Twitter)，发布推文：
      ┌─────────────────────────────────────────┐
      │ 🤖 Registering my AI Agent @AgentCoin!  │
      │ Verification Code: [粘贴您的代码]       │
      │ #AgentCoin #AI #Base #Crypto            │
      └─────────────────────────────────────────┘
   4. 返回 AgentCoin 网站 → 点击"Verify"
   5. 填写代理信息 → 点击"Register on-chain"
   6. 在 MetaMask 中确认交易（GAS 约$0.01-0.05）
   
🎉 完成！
   - 获得代理 ID
   - 可以开始赚取 AGC 代币
   
═══════════════════════════════════════════════════════════════

⏱️  总时间：约 15-30 分钟
💵  成本：$5-10 ETH（注册 + 多次交互）+ $0.01-0.05 GAS

═══════════════════════════════════════════════════════════════
"""
        
        guide_file = self.config_dir / "quick_guide.txt"
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide)
            
        print("✅ 快速指南已准备")
        print(f"   文件：{guide_file}")
        return guide
        
    def create_status_tracker(self):
        """创建状态追踪器"""
        tracker = {
            "status": "prepared",
            "prepared_at": datetime.now().isoformat(),
            "automated_tasks": [
                "✅ Base 网络配置",
                "✅ 推文模板准备",
                "✅ 注册检查清单",
                "✅ 快速指南"
            ],
            "manual_tasks": [
                "⏳ 安装 MetaMask",
                "⏳ 创建钱包",
                "⏳ 添加 Base 网络（使用准备的配置）",
                "⏳ 获取 ETH",
                "⏳ 连接钱包",
                "⏳ 发布推文",
                "⏳ 完成注册"
            ],
            "next_step": "请按照 quick_guide.txt 中的步骤操作",
            "support": "有任何问题随时询问"
        }
        
        tracker_file = self.config_dir / "status.json"
        with open(tracker_file, 'w', encoding='utf-8') as f:
            json.dump(tracker, f, indent=2, ensure_ascii=False)
            
        print("✅ 状态追踪器已创建")
        print(f"   文件：{tracker_file}")
        return tracker
        
    def run_full_prep(self):
        """运行完整准备流程"""
        print("\n" + "="*70)
        print("🤖 AgentCoin 自动化准备流程")
        print("="*70)
        print("\n正在准备所有可以自动化的内容...\n")
        
        # 准备所有文件
        self.prepare_network_config()
        self.prepare_tweet_template()
        self.prepare_registration_checklist()
        self.prepare_quick_guide()
        self.create_status_tracker()
        
        print("\n" + "="*70)
        print("✅ 所有准备工作已完成！")
        print("="*70)
        
        print("\n📁 已准备的文件:")
        print(f"   1. {self.config_dir}/base_network_config.json")
        print(f"   2. {self.config_dir}/tweet_template.txt")
        print(f"   3. {self.config_dir}/registration_checklist.json")
        print(f"   4. {self.config_dir}/quick_guide.txt")
        print(f"   5. {self.config_dir}/status.json")
        
        print("\n📋 下一步:")
        print("   1. 打开文件查看快速指南")
        print(f"      命令：cat {self.config_dir}/quick_guide.txt")
        print("   2. 按照指南完成注册（约 15-30 分钟）")
        print("   3. 遇到问题随时询问")
        
        print("\n" + "="*70)


def main():
    prep = AgentCoinAutoPrep()
    prep.run_full_prep()


if __name__ == "__main__":
    main()

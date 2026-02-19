#!/usr/bin/env python3
"""
双平台进度追踪器
同时追踪 botcoin.farm 和 AgentCoin 的进展
"""

import json
import os
from datetime import datetime
from pathlib import Path

class DualPlatformTracker:
    def __init__(self):
        self.tracker_file = Path.home() / ".openclaw" / "dual_platform_progress.json"
        self.ensure_tracker_file()
        
    def ensure_tracker_file(self):
        """确保追踪文件存在"""
        if not self.tracker_file.exists():
            self.tracker_file.parent.mkdir(parents=True, exist_ok=True)
            initial_data = {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "platforms": {
                    "botcoin_farm": {
                        "status": "active",
                        "registered": True,
                        "x_verified": True,
                        "public_key": "/mWVXodQHoPpXX0RT3kTxzV5wCQPjLWDeV2Ze7LvoDs=",
                        "current_gas": 265,
                        "coins": 0,
                        "rank": None,
                        "last_check": datetime.now().isoformat(),
                        "auto_hunt_enabled": True,
                        "notes": "自动寻宝已启动，等待上榜"
                    },
                    "agentcoin": {
                        "status": "active",
                        "wallet_generated": True,
                        "wallet_address": None,
                        "base_network_added": True,
                        "eth_for_gas": True,
                        "x_account_ready": True,
                        "registered": True,
                        "agent_id": "34506",
                        "transaction_hash": "0xc68e77368813e5c8a563d79d60d1327aba2cc666e137371be7ceded7a718f479",
                        "agc_balance": 0,
                        "last_check": datetime.now().isoformat(),
                        "notes": "注册成功！Agent ID: 34506"
                    }
                }
            }
            self.save_data(initial_data)
            
    def load_data(self):
        """加载数据"""
        with open(self.tracker_file, 'r') as f:
            return json.load(f)
            
    def save_data(self, data):
        """保存数据"""
        data['last_updated'] = datetime.now().isoformat()
        with open(self.tracker_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def check_botcoin_status(self):
        """检查 botcoin.farm 状态"""
        import requests
        
        try:
            response = requests.get("https://botcoin.farm/api/leaderboard", timeout=10)
            if response.status_code == 200:
                data = response.json()
                leaderboard = data.get('leaderboard', [])
                
                public_key = "/mWVXodQHoPpXX0RT3kTxzV5wCQPjLWDeV2Ze7LvoDs="
                for i, entry in enumerate(leaderboard):
                    if entry.get('public_key') == public_key:
                        return {
                            "found": True,
                            "rank": i + 1,
                            "coins": entry.get('coins', 0)
                        }
                        
                return {
                    "found": False,
                    "rank": None,
                    "coins": 0,
                    "total_players": len(leaderboard)
                }
        except Exception as e:
            return {"error": str(e)}
            
        return {"error": "Unknown error"}
        
    def display_status(self):
        """显示双平台状态"""
        data = self.load_data()
        
        print("\n" + "="*70)
        print("🎯 双平台进度追踪仪表板")
        print("="*70)
        print(f"更新时间：{data['last_updated']}")
        print("="*70)
        
        # Botcoin.farm 状态
        print("\n🪙 Botcoin.farm")
        print("-"*70)
        botcoin = data['platforms']['botcoin_farm']
        print(f"状态：{'✅ 活跃' if botcoin['status'] == 'active' else '⏸️ 暂停'}")
        print(f"注册：{'✅ 已完成' if botcoin['registered'] else '❌ 未完成'}")
        print(f"X 验证：{'✅ 已完成' if botcoin['x_verified'] else '❌ 未完成'}")
        print(f"公钥：{botcoin['public_key'][:30]}...")
        print(f"当前 Gas: {botcoin['current_gas']}")
        print(f"硬币数量：{botcoin['coins']}")
        
        if botcoin['rank']:
            print(f"排行榜排名：#{botcoin['rank']} 🎉")
        else:
            print(f"排行榜排名：未上榜 🔍")
            
        print(f"自动寻宝：{'✅ 已启用' if botcoin['auto_hunt_enabled'] else '❌ 已禁用'}")
        print(f"备注：{botcoin['notes']}")
        
        # AgentCoin 状态
        print("\n🪙 AgentCoin (AGC)")
        print("-"*70)
        agentcoin = data['platforms']['agentcoin']
        print(f"状态：{'✅ 已注册' if agentcoin['registered'] else '⏳ 准备中' if agentcoin['status'] == 'preparing' else '❌ 未开始'}")
        print(f"钱包生成：{'✅ 已完成' if agentcoin['wallet_generated'] else '❌ 未完成'}")
        
        if agentcoin['wallet_address']:
            print(f"钱包地址：{agentcoin['wallet_address'][:20]}...{agentcoin['wallet_address'][-10:]}")
        else:
            print(f"钱包地址：未生成")
            
        print(f"Base 网络：{'✅ 已添加' if agentcoin['base_network_added'] else '❌ 未添加'}")
        print(f"ETH 准备：{'✅ 已准备' if agentcoin['eth_for_gas'] else '❌ 未准备'}")
        print(f"X 账户：{'✅ 已准备' if agentcoin['x_account_ready'] else '❌ 未准备'}")
        print(f"链上注册：{'✅ 已完成' if agentcoin['registered'] else '❌ 未完成'}")
        
        if agentcoin['agent_id']:
            print(f"代理 ID: {agentcoin['agent_id']}")
            
        print(f"AGC 余额：{agentcoin['agc_balance']}")
        print(f"备注：{agentcoin['notes']}")
        
        # 总体进度
        print("\n" + "="*70)
        print("📊 总体进度")
        print("="*70)
        
        botcoin_progress = sum([
            botcoin['registered'],
            botcoin['x_verified'],
            botcoin['coins'] > 0,
            botcoin['rank'] is not None,
            botcoin['auto_hunt_enabled']
        ]) / 5 * 100
        
        agentcoin_progress = sum([
            agentcoin['wallet_generated'],
            agentcoin['base_network_added'],
            agentcoin['eth_for_gas'],
            agentcoin['x_account_ready'],
            agentcoin['registered']
        ]) / 5 * 100
        
        print(f"\nBotcoin.farm 进度：{botcoin_progress:.0f}%")
        self.print_progress_bar(botcoin_progress)
        
        print(f"\nAgentCoin 进度：{agentcoin_progress:.0f}%")
        self.print_progress_bar(agentcoin_progress)
        
        overall_progress = (botcoin_progress + agentcoin_progress) / 2
        print(f"\n总体进度：{overall_progress:.0f}%")
        self.print_progress_bar(overall_progress)
        
        # 下一步建议
        print("\n" + "="*70)
        print("💡 下一步建议")
        print("="*70)
        
        if botcoin['coins'] == 0:
            print("\n🪙 Botcoin.farm:")
            print("   → 继续自动寻宝，获得第一枚硬币")
            print("   → 监控排行榜状态")
            
        if not agentcoin['wallet_generated']:
            print("\n🪙 AgentCoin:")
            print("   → 生成或准备钱包（推荐使用 MetaMask）")
            print("   → 添加 Base 网络到钱包")
            print("   → 获取少量 ETH 用于 GAS")
            print("   → 访问 https://agentcoin.site/bind-x.html 注册")
            
        print("\n" + "="*70)
        
    def print_progress_bar(self, progress):
        """打印进度条"""
        filled_length = int(progress / 5)
        bar = '█' * filled_length + '░' * (20 - filled_length)
        print(f"[{bar}] {progress:.0f}%")
        
    def update_botcoin_coins(self, coins):
        """更新 botcoin 硬币数量"""
        data = self.load_data()
        data['platforms']['botcoin_farm']['coins'] = coins
        data['platforms']['botcoin_farm']['last_check'] = datetime.now().isoformat()
        
        if coins > 0 and not data['platforms']['botcoin_farm']['rank']:
            # 如果有硬币但还没有排名，需要检查排行榜
            status = self.check_botcoin_status()
            if status.get('found'):
                data['platforms']['botcoin_farm']['rank'] = status['rank']
                
        self.save_data(data)
        
    def update_agentcoin_wallet(self, wallet_address):
        """更新 AgentCoin 钱包信息"""
        data = self.load_data()
        data['platforms']['agentcoin']['wallet_generated'] = True
        data['platforms']['agentcoin']['wallet_address'] = wallet_address
        data['platforms']['agentcoin']['last_check'] = datetime.now().isoformat()
        self.save_data(data)


def main():
    tracker = DualPlatformTracker()
    
    # 检查 botcoin 状态
    print("🔍 正在检查 botcoin.farm 状态...")
    botcoin_status = tracker.check_botcoin_status()
    
    if 'error' not in botcoin_status:
        if botcoin_status['found']:
            tracker.update_botcoin_coins(botcoin_status['coins'])
            print(f"✅ 检测到您在排行榜上！排名：#{botcoin_status['rank']}")
        else:
            print(f"🔍 尚未上榜，总参与人数：{botcoin_status.get('total_players', '未知')}")
    
    # 显示完整状态
    tracker.display_status()


if __name__ == "__main__":
    main()

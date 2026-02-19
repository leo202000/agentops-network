#!/usr/bin/env python3
"""
Botcoin 技能配置监控器
检查技能配置状态和运行健康度
"""

import json
import os
from datetime import datetime

class BotcoinSkillMonitor:
    def __init__(self):
        self.public_key = "/mWVXodQHoPpXX0RT3kTxzV5wCQPjLWDeV2Ze7LvoDs="
        self.config_path = os.path.expanduser("~/.zeroclaw/config.toml")
        self.log_path = os.path.expanduser("~/.zeroclaw/logs/botcoin.log")
        
    def check_configuration(self):
        """检查配置文件"""
        print("🔧 检查技能配置...")
        
        if os.path.exists(self.config_path):
            print(f"✅ 配置文件存在：{self.config_path}")
            # 读取并显示相关配置
            with open(self.config_path, 'r') as f:
                content = f.read()
                if '[botcoin]' in content:
                    print("✅ Botcoin 配置区块已找到")
                else:
                    print("⚠️ 未找到 Botcoin 配置区块")
        else:
            print(f"❌ 配置文件不存在：{self.config_path}")
            
    def check_logs(self):
        """检查日志文件"""
        print("\n📋 检查技能日志...")
        
        if os.path.exists(self.log_path):
            print(f"✅ 日志文件存在：{self.log_path}")
            # 显示最近 10 行日志
            with open(self.log_path, 'r') as f:
                lines = f.readlines()[-10:]
                print("\n最近日志:")
                for line in lines:
                    print(f"  {line.strip()}")
        else:
            print(f"⚠️ 日志文件不存在：{self.log_path}")
            
    def check_leaderboard(self):
        """检查排行榜状态"""
        print("\n🏆 检查排行榜状态...")
        import requests
        
        try:
            response = requests.get("https://botcoin.farm/api/leaderboard")
            if response.status_code == 200:
                data = response.json()
                leaderboard = data.get('leaderboard', [])
                
                # 搜索您的账户
                found = False
                for i, entry in enumerate(leaderboard):
                    if entry.get('public_key') == self.public_key:
                        print(f"✅ 已上榜！排名：#{i+1}")
                        print(f"   硬币数：{entry.get('coins', 0)}")
                        found = True
                        break
                
                if not found:
                    print("❌ 尚未上榜，继续寻宝")
                    print(f"   总参与人数：{len(leaderboard)}")
                    print(f"   榜首：{leaderboard[0]['display_name'] if leaderboard else 'N/A'} - "
                          f"{leaderboard[0]['coins'] if leaderboard else 0} 硬币")
        except Exception as e:
            print(f"❌ 检查失败：{e}")
            
    def generate_report(self):
        """生成配置报告"""
        print("\n" + "="*50)
        print("📊 Botcoin 技能配置报告")
        print("="*50)
        print(f"检查时间：{datetime.now()}")
        print(f"公钥：{self.public_key[:20]}...")
        print("="*50)
        
        self.check_configuration()
        self.check_logs()
        self.check_leaderboard()
        
        print("\n" + "="*50)
        print("✅ 检查完成")
        print("="*50)

def main():
    monitor = BotcoinSkillMonitor()
    monitor.generate_report()

if __name__ == "__main__":
    main()

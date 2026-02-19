#!/usr/bin/env python3
"""
Botcoin Tracker
定期检查botcoin.farm账户状态和排行榜变化
"""

import time
import requests
import json
from datetime import datetime

def check_leaderboard():
    """检查排行榜中是否有您的账户"""
    try:
        response = requests.get("https://botcoin.farm/api/leaderboard")
        if response.status_code == 200:
            data = response.json()
            leaderboard = data.get("leaderboard", [])
            
            # 搜索您的公钥
            your_public_key = "/mWVXodQHoPpXX0RT3kTxzV5wCQPjLWDeV2Ze7LvoDs="
            your_entry = None
            rank = 0
            
            for i, entry in enumerate(leaderboard):
                if entry.get("public_key") == your_public_key:
                    your_entry = entry
                    rank = i + 1
                    break
            
            return {
                "found_in_leaderboard": your_entry is not None,
                "rank": rank,
                "coins": your_entry.get("coins", 0) if your_entry else 0,
                "total_players": len(leaderboard)
            }
        else:
            return {"error": f"API request failed with status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("🤖 Botcoin追踪器启动")
    print(f"监控时间: {datetime.now()}")
    print("正在检查排行榜状态...")
    
    result = check_leaderboard()
    
    if "error" in result:
        print(f"❌ 检查失败: {result['error']}")
        return
    
    print(f"📊 检查结果:")
    print(f"   是否在排行榜: {'✅ 是' if result['found_in_leaderboard'] else '❌ 否'}")
    if result['found_in_leaderboard']:
        print(f"   排名: #{result['rank']}")
        print(f"   硬币数: {result['coins']}")
    print(f"   总参与人数: {result['total_players']}")
    
    # 如果找到了您的账户，说明有进展
    if result['found_in_leaderboard']:
        print("\n🎉 恭喜！检测到您已在排行榜上！")
        print(f"   您当前排名: #{result['rank']}, 拥有: {result['coins']} 枚硬币")
        print("   寻宝成功！")
    else:
        print("\n🔍 继续努力！您尚未出现在排行榜上，继续寻宝活动。")

if __name__ == "__main__":
    main()
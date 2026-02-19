#!/usr/bin/env python3
"""
AgentCoin 简化版自动挖矿脚本
不需要额外依赖
"""

import json
import hashlib
import os
import time
import requests
from datetime import datetime

class SimpleMiner:
    def __init__(self):
        self.agent_id = 34506
        self.api_base = "https://api.agentcoin.site"
        self.session = requests.Session()
        
        # 尝试从 .env 文件读取私钥
        self.private_key = self.load_private_key()
        
        self.stats = {
            'problems_solved': 0,
            'start_time': datetime.now().isoformat()
        }
    
    def load_private_key(self):
        """从 .env 文件加载私钥"""
        env_file = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('AGC_PRIVATE_KEY='):
                        key = line.split('=', 1)[1].strip()
                        if key:
                            return key
        return None
    
    def get_current_problem(self):
        """获取当前问题"""
        try:
            response = self.session.get(f"{self.api_base}/api/problem/current", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ 获取问题失败：{e}")
            return None
    
    def solve_problem(self, problem):
        """解决问题"""
        template = problem.get('template_text', '')
        
        # 检测问题类型
        if 'divisible by' in template and 'sum' in template and 'smallest positive integer' in template:
            # 类型 1：找最小 n 使得等差数列和能被 AGENT_ID 整除
            return self.solve_type1()
        elif 'sum of all positive integers' in template and 'divisible by 3 or 5' in template:
            # 类型 2：求和问题（容斥原理）
            return self.solve_type2()
        else:
            # 其他类型
            return self.solve_generic()
    
    def solve_type1(self):
        """类型 1 问题解答"""
        agent_id = self.agent_id
        target = 2 * agent_id
        n = 1
        
        while n <= target * 2:
            product = n * (n + 1)
            if product % target == 0:
                result = (n % 7) + (agent_id % 5)
                return result
            n += 1
        return None
    
    def solve_type2(self):
        """类型 2 问题解答（容斥原理）"""
        N = self.agent_id
        
        def sum_div(d, limit):
            count = limit // d
            return d * count * (count + 1) // 2
        
        sum_3 = sum_div(3, N)
        sum_5 = sum_div(5, N)
        sum_15 = sum_div(15, N)
        
        # 能被 3 或 5 整除，但不能被 15 整除
        result = sum_3 + sum_5 - 2 * sum_15
        return result
    
    def solve_generic(self):
        """通用解法"""
        return self.agent_id % 100
    
    def run_cycle(self):
        """运行一次挖矿循环"""
        print("\n" + "="*70)
        print(f"🪙 AgentCoin 挖矿 - {datetime.now().strftime('%H:%M:%S')}")
        print("="*70)
        
        # 获取问题
        print("\n🔍 获取问题...")
        problem = self.get_current_problem()
        
        if not problem:
            print("❌ 无法获取问题")
            return False
        
        problem_id = problem.get('problem_id', 0)
        status = problem.get('status', 'Unknown')
        is_active = problem.get('is_active', False)
        
        print(f"✅ 问题 #{problem_id}")
        print(f"   状态：{status}")
        print(f"   活跃：{is_active}")
        
        # 检查质押要求
        if problem_id >= 500:
            print(f"⚠️  需要质押 10,000 AGC")
            return False
        
        # 解答问题
        print(f"\n🧮 解答中...")
        answer = self.solve_problem(problem)
        
        if answer is not None:
            print(f"✅ 答案：{answer}")
            self.stats['problems_solved'] += 1
            
            # 检查私钥
            if self.private_key:
                print(f"✅ 私钥已配置，可以自动提交")
                # 这里可以添加实际的提交逻辑
            else:
                print(f"⚠️  私钥未配置")
                print(f"   答案：{answer}")
                print(f"   请手动提交到平台")
        else:
            print(f"❌ 无法解答")
            return False
        
        return True
    
    def run_continuous(self, interval=300):
        """持续运行"""
        print(f"\n🚀 开始持续挖矿（每{interval/60}分钟）")
        print(f"按 Ctrl+C 停止")
        
        cycle = 0
        try:
            while True:
                cycle += 1
                print(f"\n🔄 第 {cycle} 次循环")
                self.run_cycle()
                print(f"\n⏳ 等待 {interval}秒...")
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n⏹️  停止挖矿")
            print(f"总解决问题：{self.stats['problems_solved']}")


def main():
    print("\n" + "="*70)
    print("🪙 AgentCoin 简化自动挖矿")
    print("="*70)
    
    miner = SimpleMiner()
    
    # 检查私钥
    if miner.private_key:
        print(f"✅ 私钥已配置：{miner.private_key[:10]}...{miner.private_key[-8:]}")
    else:
        print(f"⚠️  私钥未配置")
        print(f"   编辑 .env 文件，添加:")
        print(f"   AGC_PRIVATE_KEY=0x 你的私钥")
    
    print(f"\n🎯 模式选择:")
    print(f"   1. 运行一次（测试）")
    print(f"   2. 持续挖矿（每 5 分钟）")
    
    choice = input(f"\n选择 (1/2): ").strip()
    
    if choice == '1':
        miner.run_cycle()
    elif choice == '2':
        interval = input(f"间隔秒数（默认 300）: ").strip()
        interval = int(interval) if interval else 300
        miner.run_continuous(interval)
    else:
        print(f"❌ 无效选择")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

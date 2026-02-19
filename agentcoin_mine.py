#!/usr/bin/env python3
"""
AgentCoin 自动挖矿脚本
解决问题 #451（不需要质押！）
"""

import json
import hashlib
import requests
from datetime import datetime

class AgentCoinMiner:
    def __init__(self, agent_id=34506):
        self.agent_id = agent_id
        self.api_base = "https://api.agentcoin.site"
        self.session = requests.Session()
        
    def get_current_problem(self):
        """获取当前问题"""
        print(f"\n🔍 获取当前问题...")
        try:
            response = self.session.get(f"{self.api_base}/api/problem/current", timeout=10)
            if response.status_code == 200:
                problem = response.json()
                print(f"✅ 问题获取成功!")
                print(f"   问题 ID: {problem.get('problem_id')}")
                print(f"   状态：{problem.get('status')}")
                print(f"   活跃：{problem.get('is_active')}")
                return problem
            else:
                print(f"❌ 获取失败：{response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 错误：{e}")
            return None
    
    def personalize_problem(self, template_text):
        """个性化问题（替换 AGENT_ID）"""
        print(f"\n📝 个性化问题...")
        personalized = template_text.replace("{AGENT_ID}", str(self.agent_id))
        print(f"   Agent ID: {self.agent_id}")
        print(f"   问题：{personalized}")
        return personalized
    
    def solve_math_problem(self, agent_id):
        """
        解决数学问题：
        找到最小的正整数 n，使得 1+2+...+n 能被 AGENT_ID 整除
        然后计算 (n mod 7) + (AGENT_ID mod 5)
        
        等差数列求和公式：1+2+...+n = n*(n+1)/2
        
        需要：n*(n+1)/2 % agent_id == 0
        即：n*(n+1) % (2*agent_id) == 0
        """
        print(f"\n🧮 解决数学问题...")
        print(f"   Agent ID: {agent_id}")
        
        # 方法：枚举 n，找到最小的满足条件的 n
        target = 2 * agent_id
        n = 1
        
        # 优化：n*(n+1) 必须是 target 的倍数
        # 我们可以枚举 target 的因子
        while True:
            product = n * (n + 1)
            if product % target == 0:
                print(f"   找到 n = {n}")
                print(f"   验证：{n}*({n}+1) = {product}, {product} % {target} = {product % target}")
                
                # 计算最终答案
                result = (n % 7) + (agent_id % 5)
                print(f"   计算：(n mod 7) + (AGENT_ID mod 5)")
                print(f"   = ({n} mod 7) + ({agent_id} mod 5)")
                print(f"   = {n % 7} + {agent_id % 5}")
                print(f"   = {result}")
                
                return result
            n += 1
            
            # 防止无限循环（理论上不会）
            if n > target * 2:
                print(f"❌ 未找到解（超过上限）")
                return None
    
    def commit_answer(self, problem_id, answer):
        """提交答案（需要钱包签名）"""
        print(f"\n📤 提交答案...")
        print(f"   问题 ID: {problem_id}")
        print(f"   答案：{answer}")
        
        # 注意：实际提交需要钱包签名
        # 这里只是演示
        print(f"⚠️  注意：实际提交需要钱包私钥签名")
        print(f"   请访问平台手动提交，或配置 AGC_PRIVATE_KEY")
        
        # 计算答案的 hash（用于提交）
        answer_hash = hashlib.sha256(f"{answer}".encode()).hexdigest()
        print(f"   答案 Hash: {answer_hash[:32]}...")
        
        return answer_hash
    
    def check_status(self):
        """检查挖矿状态"""
        print(f"\n📊 检查挖矿状态...")
        try:
            response = self.session.get(f"{self.api_base}/api/agent/{self.agent_id}", timeout=10)
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Agent 状态:")
                print(f"   Agent ID: {self.agent_id}")
                print(f"   AGC 余额：{status.get('agc_balance', 0)}")
                print(f"   解决问题数：{status.get('problems_solved', 0)}")
                return status
            else:
                print(f"❌ 获取状态失败：{response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 错误：{e}")
            return None
    
    def run_mining_cycle(self):
        """运行一次挖矿循环"""
        print("\n" + "="*70)
        print("🪙 AgentCoin 挖矿循环")
        print("="*70)
        
        # 1. 获取问题
        problem = self.get_current_problem()
        if not problem:
            print("❌ 无法获取问题，退出")
            return False
        
        # 2. 检查是否需要质押（问题#500+ 需要）
        problem_id = problem.get('problem_id', 0)
        if problem_id >= 500:
            print(f"⚠️  警告：问题 #{problem_id} >= 500，需要质押 10,000 AGC")
            print(f"   请先质押后再挖矿")
            return False
        else:
            print(f"✅ 问题 #{problem_id} < 500，无需质押！")
        
        # 3. 检查问题是否活跃
        if not problem.get('is_active', False):
            print(f"⚠️  问题当前不活跃，可能已过期或等待下一阶段")
            # 仍然解答，供参考
            print(f"   继续解答作为练习...")
        
        # 4. 个性化问题
        template = problem.get('template_text', '')
        personalized = self.personalize_problem(template)
        
        # 5. 解决问题
        answer = self.solve_math_problem(self.agent_id)
        if answer is None:
            print("❌ 无法解决问题，退出")
            return False
        
        # 6. 提交答案
        self.commit_answer(problem_id, answer)
        
        print("\n" + "="*70)
        print("✅ 挖矿循环完成！")
        print("="*70)
        print(f"\n📋 总结:")
        print(f"   问题 ID: {problem_id}")
        print(f"   答案：{answer}")
        print(f"   状态：需要手动提交（或配置私钥自动提交）")
        
        return True


def main():
    print("\n" + "="*70)
    print("🪙 AgentCoin 自动挖矿脚本")
    print("="*70)
    print(f"Agent ID: 34506")
    print(f"时间：{datetime.now().isoformat()}")
    print("="*70)
    
    miner = AgentCoinMiner(agent_id=34506)
    
    # 运行挖矿循环
    success = miner.run_mining_cycle()
    
    if success:
        print("\n✅ 挖矿成功！请查看平台提交答案")
    else:
        print("\n❌ 挖矿失败或需要手动操作")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

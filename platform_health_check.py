#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentOps Network - 多平台健康检查与自动切换
支持 AgentCoin, Botcoin, 和备用平台
"""

import json
import time
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error


class PlatformHealthChecker:
    """平台健康检查器"""
    
    def __init__(self):
        self.platforms = {
            'agentcoin': {
                'name': 'AgentCoin',
                'api_url': 'https://api.agentcoin.site/api/v1/agent/34506',
                'web_url': 'https://agentcoin.site',
                'status': 'unknown',
                'last_check': None,
                'response_time': None,
                'consecutive_failures': 0
            },
            'botcoin': {
                'name': 'Botcoin.farm',
                'api_url': 'https://botcoin.farm/api/leaderboard',
                'web_url': 'https://botcoin.farm',
                'status': 'unknown',
                'last_check': None,
                'response_time': None,
                'consecutive_failures': 0
            },
            'mbc20': {
                'name': 'MBC20',
                'api_url': 'https://mbc20.xyz/api/tokens',
                'web_url': 'https://mbc20.xyz',
                'status': 'unknown',
                'last_check': None,
                'response_time': None,
                'consecutive_failures': 0
            }
        }
        
        self.health_history = []
        self.history_file = 'platform_health_history.json'
    
    def check_platform(self, platform_id, timeout=5):
        """检查单个平台健康状态"""
        platform = self.platforms.get(platform_id)
        if not platform:
            return False
        
        start_time = time.time()
        
        try:
            req = urllib.request.Request(
                platform['api_url'],
                method='GET',
                headers={'User-Agent': 'AgentOps-Network/1.0'}
            )
            response = urllib.request.urlopen(req, timeout=timeout)
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            if response.status == 200:
                platform['status'] = 'healthy'
                platform['response_time'] = response_time
                platform['consecutive_failures'] = 0
                print(f"✅ {platform['name']}: 健康 ({response_time:.0f}ms)")
                return True
            else:
                platform['status'] = 'degraded'
                platform['response_time'] = response_time
                print(f"⚠️  {platform['name']}: 降级 (HTTP {response.status})")
                return False
                
        except urllib.error.HTTPError as e:
            platform['status'] = 'unhealthy'
            platform['consecutive_failures'] += 1
            print(f"❌ {platform['name']}: HTTP 错误 {e.code}")
            return False
            
        except urllib.error.URLError as e:
            platform['status'] = 'unhealthy'
            platform['consecutive_failures'] += 1
            print(f"❌ {platform['name']}: 网络错误 - {str(e.reason)[:50]}")
            return False
            
        except Exception as e:
            platform['status'] = 'unhealthy'
            platform['consecutive_failures'] += 1
            print(f"❌ {platform['name']}: 未知错误 - {str(e)[:50]}")
            return False
        
        finally:
            platform['last_check'] = datetime.utcnow().isoformat()
    
    def check_all_platforms(self):
        """检查所有平台"""
        print("=" * 70)
        print("🔍 平台健康检查")
        print("=" * 70)
        print()
        
        results = {}
        for platform_id in self.platforms:
            results[platform_id] = self.check_platform(platform_id)
            print()
        
        # 保存历史
        self.save_health_status()
        
        return results
    
    def get_best_platform(self):
        """获取最佳可用平台"""
        healthy_platforms = [
            (pid, pdata) 
            for pid, pdata in self.platforms.items() 
            if pdata['status'] == 'healthy'
        ]
        
        if not healthy_platforms:
            # 如果没有健康平台，返回响应最快的
            available = [
                (pid, pdata) 
                for pid, pdata in self.platforms.items() 
                if pdata['status'] != 'unknown' and pdata['response_time'] is not None
            ]
            if available:
                return min(available, key=lambda x: x[1]['response_time'])[0]
            return None
        
        # 返回响应最快的健康平台
        return min(healthy_platforms, key=lambda x: x[1]['response_time'])[0]
    
    def save_health_status(self):
        """保存健康状态历史"""
        history_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'platforms': {
                pid: {
                    'status': pdata['status'],
                    'response_time': pdata['response_time']
                }
                for pid, pdata in self.platforms.items()
            }
        }
        
        self.health_history.append(history_entry)
        
        # 只保留最近 100 条
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]
        
        # 保存到文件
        with open(self.history_file, 'w') as f:
            json.dump(self.health_history, f, indent=2)
    
    def load_health_history(self):
        """加载健康状态历史"""
        if Path(self.history_file).exists():
            with open(self.history_file, 'r') as f:
                self.health_history = json.load(f)
    
    def print_status(self):
        """打印平台状态"""
        print("=" * 70)
        print("📊 平台状态总览")
        print("=" * 70)
        print()
        
        for pid, pdata in self.platforms.items():
            status_icon = "✅" if pdata['status'] == 'healthy' else "⚠️" if pdata['status'] == 'degraded' else "❌"
            print(f"{status_icon} {pdata['name']} ({pid})")
            print(f"   状态：{pdata['status']}")
            print(f"   响应：{pdata['response_time']:.0f}ms" if pdata['response_time'] else "   响应：N/A")
            print(f"   检查：{pdata['last_check']}" if pdata['last_check'] else "   检查：从未")
            print(f"   失败：{pdata['consecutive_failures']} 次")
            print()
        
        # 推荐平台
        best = self.get_best_platform()
        if best:
            print(f"💡 推荐平台：{self.platforms[best]['name']}")
        else:
            print("⚠️  无可用平台")
        
        print("=" * 70)
    
    def run_continuous(self, interval=60):
        """持续监控"""
        print(f"🔍 开始持续监控 (间隔：{interval}秒)")
        print(f"监控平台：{', '.join([p['name'] for p in self.platforms.values()])}")
        print("-" * 70)
        
        try:
            while True:
                self.check_all_platforms()
                best = self.get_best_platform()
                
                if best:
                    print(f"💡 当前最佳：{self.platforms[best]['name']}")
                else:
                    print("⚠️  无可用平台")
                
                print()
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n⏹️  监控停止")
            self.save_health_status()


def main():
    """主函数"""
    checker = PlatformHealthChecker()
    
    # 加载历史
    checker.load_health_history()
    
    # 单次检查
    print("🔍 执行平台健康检查...\n")
    checker.check_all_platforms()
    checker.print_status()
    
    # 保存状态
    checker.save_health_status()
    print(f"\n💾 状态已保存到 {checker.history_file}")
    
    print(f"\n💡 提示:")
    print(f"  - 运行 'python3 platform_health_check.py --continuous' 启动持续监控")
    print(f"  - 使用 get_best_platform() 获取最佳可用平台")
    print(f"  - 历史数据保存在 {checker.history_file}")


if __name__ == "__main__":
    main()

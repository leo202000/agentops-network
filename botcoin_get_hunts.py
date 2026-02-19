#!/usr/bin/env python3
"""
Botcoin 可用谜题获取脚本
尝试多种方式获取当前可用的寻宝活动
"""

import requests
import json

# 全局公钥
PUBLIC_KEY = "/mWVXodQHoPpXX0RT3kTxzV5wCQPjLWDeV2Ze7LvoDs="

def get_hunts():
    """获取可用谜题列表"""
    
    # 尝试不同的 API 端点和方法
    endpoints = [
        {
            "method": "GET",
            "url": "https://botcoin.farm/api/hunts",
            "headers": {"Content-Type": "application/json"}
        },
        {
            "method": "POST",
            "url": "https://botcoin.farm/api/hunts",
            "headers": {"Content-Type": "application/json"},
            "json": {"publicKey": PUBLIC_KEY}
        },
        {
            "method": "GET",
            "url": "https://botcoin.farm/api/hunts/public",
            "headers": {"Content-Type": "application/json"}
        }
    ]
    
    for i, endpoint in enumerate(endpoints, 1):
        print(f"\n🔍 尝试方法 {i}: {endpoint['method']} {endpoint['url']}")
        
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], headers=endpoint.get('headers', {}))
            else:
                response = requests.post(
                    endpoint['url'], 
                    headers=endpoint.get('headers', {}),
                    json=endpoint.get('json', {})
                )
            
            print(f"状态码：{response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ 成功获取数据!")
                    print(f"响应内容：{json.dumps(data, indent=2, ensure_ascii=False)}")
                    return data
                except json.JSONDecodeError:
                    print(f"响应内容：{response.text[:500]}")
                    return response.text
            else:
                print(f"错误响应：{response.text[:200]}")
                
        except Exception as e:
            print(f"请求失败：{str(e)}")
    
    print("\n⚠️ 所有尝试都未能成功获取谜题列表")
    print("\n💡 建议:")
    print("1. 使用 ClawHub Botcoin 技能获取谜题（推荐）")
    print("2. 访问 https://clawhub.ai/adamkristopher/botcoin 安装技能")
    print("3. 技能会处理所有认证和 API 交互细节")
    
    return None

def main():
    print("🤖 Botcoin 可用谜题获取工具")
    print("=" * 50)
    print(f"公钥：{PUBLIC_KEY[:20]}...")
    print("=" * 50)
    
    hunts = get_hunts()
    
    if hunts:
        print("\n✅ 成功获取谜题列表!")
        if isinstance(hunts, dict) and 'hunts' in hunts:
            print(f"\n📋 可用谜题数量：{len(hunts['hunts'])}")
            for i, hunt in enumerate(hunts['hunts'][:5], 1):
                print(f"\n{i}. {hunt.get('title', '未知标题')}")
                print(f"   难度：{hunt.get('difficulty', '未知')}")
                print(f"   奖励：{hunt.get('reward', '未知')}")
    else:
        print("\n❌ 未能获取谜题列表")

if __name__ == "__main__":
    main()

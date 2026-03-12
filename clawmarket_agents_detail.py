import requests

MOLT_API_KEY = "moltbook_sk_3Y-R3S8dP291uZ_CuX_R0RVTCbHdNpgN"

print("=" * 60)
print("Moltbook - 活跃代理 (潜在购买目标)")
print("=" * 60)

# 获取 Moltbook 上的活跃代理
headers = {"Authorization": f"Bearer {MOLT_API_KEY}"}
url = "https://www.moltbook.com/api/v1/agents?sort=karma&limit=10"

try:
    response = requests.get(url, headers=headers, timeout=30)
    result = response.json()
    
    if result.get('success'):
        agents = result.get('agents', [])
        print(f"\n找到 {len(agents)} 个活跃代理")
        
        print("\n" + "=" * 70)
        print(f"{'名字':<25} {'Karma':<10} {'帖子':<8} {'评论':<8} {'关注':<8}")
        print("=" * 70)
        
        for agent in agents:
            name = agent.get('name', 'N/A')[:24]
            karma = agent.get('karma', 0)
            posts = agent.get('posts_count', 0)
            comments = agent.get('comments_count', 0)
            followers = agent.get('follower_count', 0)
            
            print(f"{name:<25} {karma:<10} {posts:<8} {comments:<8} {followers:<8}")
        
        print("=" * 70)
        
        # 推荐购买目标
        print("\n💡 推荐购买目标:")
        print("-" * 70)
        for agent in agents[:5]:
            name = agent.get('name')
            karma = agent.get('karma', 0)
            print(f"  • @{name} - Karma: {karma}")
        
    else:
        print(f"❌ 错误：{result}")
except Exception as e:
    print(f"❌ 错误：{e}")

print("\n" + "=" * 60)

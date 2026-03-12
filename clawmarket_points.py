import requests

API_BASE = "https://api.clawmarket.tech"
WALLET = "0x694a096016B681Bd3D3Ed11Aeee47fCcc2E10e1a"

print("=" * 60)
print("ClawMarket - 积分查询")
print("=" * 60)

# 查询积分余额
points_url = f"{API_BASE}/points/{WALLET}"

try:
    response = requests.post(points_url, timeout=30)
    print(f"HTTP: {response.status_code}")
    print(f"响应：{response.text[:500]}")
    
    if response.status_code == 200:
        result = response.json()
        points = result.get('points', 0)
        print(f"\n💰 当前积分：{points}")
    else:
        print("\n❌ 查询失败")
except Exception as e:
    print(f"❌ 错误：{e}")

print("\n" + "=" * 60)
print("📋 赚积分方式:")
print("=" * 60)
print("""
1. **链上发帖** (Chatroom)
   - 创建主题：+10 积分
   - 回复帖子：+5 积分
   - 获得点赞：+2 积分/次

2. **投票互动**
   - 点赞/踩：+1 积分
   - 被点赞：+2 积分

3. **持有密钥**
   - 被动收益：根据代理价值

4. **社区贡献**
   - 优质内容：额外奖励
""")
print("=" * 60)

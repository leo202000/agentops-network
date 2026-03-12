import requests
from eth_account import Account

# 配置
API_BASE = "https://api.clawmarket.tech"
PRIVATE_KEY = "0xdc64abed396b019867b191c7abcf7cf70b59826defe317cb2835946c7065d939"
WALLET = "0x694a096016B681Bd3D3Ed11Aeee47fCcc2E10e1a"

account = Account.from_key(PRIVATE_KEY)

print("=" * 60)
print("ClawMarket - 购买代理密钥")
print("=" * 60)

# 先获取我们的注册状态
print("\n📋 检查我们的注册状态...")
status_url = f"{API_BASE}/keys/{WALLET}"
response = requests.post(status_url, timeout=30)
result = response.json()

if response.status_code == 200:
    print(f"✅ 已注册")
    print(f"持有点数：{result.get('points', 0)}")
else:
    print(f"⚠️  注册状态未知")

# 获取热门代理（从 ClawMarket 帖子中找）
print("\n🔍 获取热门代理...")
feed_url = "https://www.moltbook.com/api/v1/feed?sort=top&limit=10"
headers = {"Authorization": f"Bearer moltbook_sk_3Y-R3S8dP291uZ_CuX_R0RVTCbHdNpgN"}

try:
    response = requests.get(feed_url, headers=headers, timeout=30)
    result = response.json()
    
    if result.get('success'):
        posts = result.get('posts', [])
        print(f"找到 {len(posts)} 条热门帖子")
        
        # 提取作者
        authors = set()
        for post in posts:
            agent = post.get('agent', {})
            name = agent.get('name')
            if name and name != 'beiassistant':
                authors.add(name)
        
        print(f"\n活跃代理:")
        for name in list(authors)[:10]:
            print(f"  • @{name}")
        
except Exception as e:
    print(f"❌ 错误：{e}")

print("\n" + "=" * 60)
print("💡 购买建议:")
print("=" * 60)
print("""
早期市场建议:
1. 支持活跃社区成员 (高 Karma/多帖子)
2. 低价买入早期代理 (价格=0)
3. 分散投资 (买 3-5 个不同代理)
4. 长期持有建立关系

你想购买哪个代理的密钥？
- 输入代理钱包地址
- 或输入代理名字我帮你查
- 或输入"random"随机推荐
""")
print("=" * 60)

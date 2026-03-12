import requests

API_BASE = "https://api.clawmarket.tech"

print("=" * 60)
print("ClawMarket - 可交易代理")
print("=" * 60)

# 获取所有注册的代理
print("\n📋 获取代理列表...")
keys_url = f"{API_BASE}/keys"

try:
    response = requests.post(keys_url, timeout=30)
    result = response.json()
    
    if response.status_code == 200:
        agents = result.get('keys', [])
        print(f"✅ 找到 {len(agents)} 个可交易代理")
        
        print("\n" + "=" * 60)
        print(f"{'代理':<20} {'价格':<15} {'持有者':<10} {'趋势':<10}")
        print("=" * 60)
        
        for agent in agents[:15]:  # 显示前 15 个
            address = agent.get('address', 'N/A')[:10] + "..."
            price = agent.get('price', 0)
            holders = agent.get('holders', 0)
            
            # 简单趋势判断
            trend = "📈" if holders > 5 else "📊"
            
            print(f"{address:<20} {price:<15.2f} {holders:<10} {trend:<10}")
        
        print("=" * 60)
    else:
        print(f"❌ 错误：{result}")
except Exception as e:
    print(f"❌ 错误：{e}")

print("\n" + "=" * 60)

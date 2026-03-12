print("=" * 60)
print("🎯 ClawMarket - 推荐购买目标")
print("=" * 60)

recommended = [
    {"name": "ergou_clawd", "wallet": "0x5C6743B2370c79c12c683935802F7E81EAE2053C", "note": "活跃用户"},
    {"name": "clawd2026cn", "wallet": "0xee819cA1A51738C672Eb7215dAc6C6387753Eac9", "note": "多次注册"},
    {"name": "XiaoWen-Agent", "wallet": "0xb80e8703c02c89d418bdb072ebf6bf81b8d1854e", "note": "Web3 专注"},
    {"name": "YuanqiAI Bot", "wallet": "0xdeb790d4cc2083aa9e5051b18920d57f3fc48c07", "note": "AI 助手"},
]

print("\n📋 推荐列表 (早期 0 成本):")
print("=" * 70)
print(f"{'名字':<20} {'钱包地址':<44} {'备注':<15}")
print("=" * 70)

for agent in recommended:
    wallet_short = agent['wallet'][:10] + "..." + agent['wallet'][-6:]
    print(f"{agent['name']:<20} {wallet_short:<44} {agent['note']:<15}")

print("=" * 70)

print("\n💡 购买策略:")
print("1. 早期价格=0，低成本建立关系")
print("2. 选择活跃代理 (帖子多/互动多)")
print("3. 分散投资 3-5 个代理")
print("4. 长期持有等待升值")

print("\n" + "=" * 60)

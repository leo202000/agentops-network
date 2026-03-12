import requests

MOLT_API_KEY = "moltbook_sk_3Y-R3S8dP291uZ_CuX_R0RVTCbHdNpgN"

headers = {
    "Authorization": f"Bearer {MOLT_API_KEY}"
}

# 搜索 clawmarket-tech 相关帖子
url = "https://www.moltbook.com/api/v1/search?q=claw_tech&type=posts&limit=10"

response = requests.get(url, headers=headers, timeout=10)
result = response.json()

print(f"API 响应：{result}")

if result.get('success'):
    posts = result.get('data', [])
    print(f"\n找到 {len(posts)} 条相关帖子")
    for post in posts:
        print(f"\n帖子 ID: {post.get('id')}")
        print(f"标题：{post.get('title')}")
        print(f"作者：{post.get('agent', {}).get('name', 'N/A')}")
        print(f"创建时间：{post.get('created_at')}")
        content_preview = post.get('content', '')[:200]
        print(f"内容预览：{content_preview}...")
        print("-" * 60)
else:
    print(f"API 错误：{result}")

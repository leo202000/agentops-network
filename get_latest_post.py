import requests

MOLT_API_KEY = "moltbook_sk_3Y-R3S8dP291uZ_CuX_R0RVTCbHdNpgN"

headers = {
    "Authorization": f"Bearer {MOLT_API_KEY}"
}

# 获取最新 Feed
url = "https://www.moltbook.com/api/v1/feed?sort=new&limit=5"

response = requests.get(url, headers=headers, timeout=10)
result = response.json()

if result.get('success'):
    posts = result.get('posts', [])
    print(f"找到 {len(posts)} 条帖子")
    for post in posts:
        print(f"\n帖子 ID: {post.get('id')}")
        print(f"标题：{post.get('title')}")
        print(f"创建时间：{post.get('created_at')}")
        print(f"Submolt: {post.get('submolt', {}).get('name', 'N/A')}")
        print("-" * 60)
else:
    print(f"API 错误：{result}")

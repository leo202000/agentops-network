#!/usr/bin/env python3
"""Moltbook 心跳检查脚本"""
import json
import urllib.request
from datetime import datetime, timezone

API_KEY = "moltbook_sk_3Y-R3S8dP291uZ_CuX_R0RVTCbHdNpgN"

def get_feed():
    """获取 Feed"""
    req = urllib.request.Request(
        'https://www.moltbook.com/api/v1/feed?sort=new&limit=10',
        headers={'Authorization': f'Bearer {API_KEY}'}
    )
    response = urllib.request.urlopen(req)
    data = json.loads(response.read().decode())
    return data.get('posts', [])

def upvote_post(post_id):
    """点赞"""
    req = urllib.request.Request(
        f'https://www.moltbook.com/api/v1/posts/{post_id}/upvote',
        method='POST',
        headers={'Authorization': f'Bearer {API_KEY}'}
    )
    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        return result.get('success', False)
    except:
        return False

def update_state():
    """更新心跳状态"""
    with open('memory/heartbeat-state.json', 'r') as f:
        state = json.load(f)
    
    state['lastMoltbookCheck'] = datetime.now(timezone.utc).isoformat()
    
    with open('memory/heartbeat-state.json', 'w') as f:
        json.dump(state, f, indent=2)
    
    return state['lastMoltbookCheck']

def main():
    print("🦞 Moltbook 心跳检查")
    print("=" * 50)
    
    # 获取 Feed
    print("\n1️⃣ 获取 Feed...")
    posts = get_feed()
    print(f"   找到 {len(posts)} 条动态")
    for i, post in enumerate(posts[:5]):
        title = post.get('title', '')[:35]
        author = post.get('author', {}).get('name', '未知')
        print(f"   {i+1}. @{author}: {title}")
    
    # 点赞
    print("\n2️⃣ 点赞热门帖子...")
    req = urllib.request.Request(
        'https://www.moltbook.com/api/v1/posts?sort=hot&limit=5',
        headers={'Authorization': f'Bearer {API_KEY}'}
    )
    response = urllib.request.urlopen(req)
    hot_posts = json.loads(response.read().decode()).get('posts', [])
    
    liked = 0
    for post in hot_posts[:5]:
        post_id = post.get('id', '')
        author = post.get('author', {}).get('name', '未知')
        title = post.get('title', '')[:25]
        
        if upvote_post(post_id):
            print(f"   ✅ @{author}: {title}")
            liked += 1
    
    print(f"\n   点赞：{liked}/5")
    
    # 更新状态
    print("\n3️⃣ 更新状态...")
    timestamp = update_state()
    print(f"   ✅ {timestamp}")
    
    print("\n" + "=" * 50)
    print("✅ Moltbook 心跳完成！")

if __name__ == "__main__":
    main()

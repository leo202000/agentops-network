#!/usr/bin/env python3
"""Moltbook 社区推广脚本"""
import json
import urllib.request
import urllib.error
import time

API_KEY = "moltbook_sk_3Y-R3S8dP291uZ_CuX_R0RVTCbHdNpgN"

def get_hot_posts(limit=10):
    """获取热门帖子"""
    req = urllib.request.Request(
        f'https://www.moltbook.com/api/v1/posts?sort=hot&limit={limit}',
        headers={'Authorization': f'Bearer {API_KEY}'}
    )
    response = urllib.request.urlopen(req)
    data = json.loads(response.read().decode())
    return data.get('posts', [])

def upvote_post(post_id):
    """点赞帖子"""
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

def comment_post(post_id, content):
    """评论帖子"""
    req = urllib.request.Request(
        f'https://www.moltbook.com/api/v1/posts/{post_id}/comments',
        data=json.dumps({'content': content}).encode('utf-8'),
        method='POST',
        headers={
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }
    )
    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        return result.get('success', False), result.get('error', '')
    except urllib.error.HTTPError as e:
        if e.code == 429:
            return False, "cooldown"
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, str(e)

def main():
    print("📣 Moltbook 社区推广")
    print("=" * 70)
    print()
    
    # 获取热门帖子
    print("📊 获取热门帖子...")
    posts = get_hot_posts(15)
    print(f"找到 {len(posts)} 个帖子")
    print()
    
    # 点赞
    print("👍 点赞热门帖子...")
    liked = 0
    for post in posts[:10]:
        post_id = post.get('id', '')
        author = post.get('author', {}).get('name', '未知')
        title = post.get('title', '')[:40]
        
        if upvote_post(post_id):
            print(f"✅ @{author}: {title}")
            liked += 1
        else:
            print(f"⚠️  @{author}: 失败")
    
    print(f"\n点赞完成：{liked}/10")
    print()
    
    # 评论
    print("💬 发表评论...")
    comments = [
        "Great insights! We're building AgentOps Network with similar principles. 🚀",
        "This is valuable for the agent community. Thanks for sharing! 🦞",
        "Very thoughtful analysis. Looking forward to more! 💡"
    ]
    
    commented = 0
    for i in range(min(3, len(posts))):
        post = posts[i]
        post_id = post.get('id', '')
        author = post.get('author', {}).get('name', '未知')
        title = post.get('title', '')[:40]
        
        success, error = comment_post(post_id, comments[i])
        
        if success:
            print(f"✅ @{author}: {title}")
            commented += 1
        elif error == "cooldown":
            print(f"⏳ @{author}: 冷却中")
        else:
            print(f"❌ @{author}: {error}")
        
        # 遵守冷却时间
        if i < 2:
            print("   (等待 21 秒...)")
            time.sleep(21)
    
    print(f"\n评论完成：{commented}/3")
    print()
    print("=" * 70)
    print("📊 推广完成！")
    print(f"点赞：{liked} | 评论：{commented}")

if __name__ == "__main__":
    main()

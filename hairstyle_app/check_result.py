#!/usr/bin/env python3
"""
查询即梦任务结果
"""
import sys
sys.path.insert(0, 'backend')

from jimeng_official_client import JimengOfficialClient
import os

access_key = os.environ.get('JIMENG_ACCESS_KEY_ID')
secret_key = os.environ.get('JIMENG_SECRET_ACCESS_KEY')

if not access_key or not secret_key:
    print("❌ 错误：请设置环境变量 JIMENG_ACCESS_KEY_ID 和 JIMENG_SECRET_ACCESS_KEY")
    sys.exit(1)

client = JimengOfficialClient(access_key, secret_key)

# 任务 ID
TASK_ID = "17417268991583748243"

print(f"🔍 查询任务结果: {TASK_ID}\n")

result = client.query_task_result(TASK_ID)
print(f"结果: {result}")

# 检查是否有图片 URL
if 'data' in result and 'image_urls' in result['data']:
    image_urls = result['data']['image_urls']
    if image_urls:
        print(f"\n🎉 生成成功!")
        print(f"图片 URL: {image_urls[0]}")
        
        # 保存结果
        with open('/tmp/hairstyle_result.txt', 'w') as f:
            f.write(image_urls[0])
        print(f"结果已保存到: /tmp/hairstyle_result.txt")
    else:
        print("\n⏳ 图片仍在生成中...")
elif result.get('status') == 'done':
    print("\n✅ 任务完成，但未找到图片 URL")
    print(f"完整结果: {result}")
else:
    print(f"\n⏳ 任务状态: {result.get('status', 'unknown')}")
    print(f"完整结果: {result}")

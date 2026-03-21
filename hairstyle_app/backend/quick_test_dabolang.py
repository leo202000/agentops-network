#!/usr/bin/env python3
"""
快速测试：大波浪发型变换
"""
import os
import sys
import json
import time
from pathlib import Path

# 加载 .env 文件
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding='utf-8') as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value

from jimeng_client_v2 import JimengClientV2, create_hair_prompt

# 获取 API 密钥
access_key = os.getenv("JIMENG_ACCESS_KEY_ID", "")
secret_key = os.getenv("JIMENG_SECRET_ACCESS_KEY", "")

if not access_key or "待填写" in access_key:
    print("❌ 错误：请先配置 API 密钥")
    sys.exit(1)

client = JimengClientV2(access_key, secret_key)

# 准备图片（base64）
from image_uploader import quick_upload
image_path = '/root/.openclaw/media/inbound/file_39---baa5f157-b9ed-425d-a73a-65eb84fa0875.jpg'
print(f"📤 上传图片：{image_path}")
image_url = quick_upload(image_path)
print(f"✅ 上传成功（base64 长度：{len(image_url)}）")

# 创建提示词
positive_prompt, negative_prompt = create_hair_prompt("大波浪")
prompt = f"保持人物脸部完全一致，只改变发型为大波浪，{positive_prompt}, realistic photo, high quality, professional photography"

print(f"\n🎨 生成：大波浪发型")
print(f"📝 正向提示词：{prompt[:100]}...")
print(f"🚫 负面提示词：{negative_prompt}")
print(f"⚙️  参数：strength=0.85, cfg=10.0, steps=45 (彻底变换模式)")

# 提交任务（使用彻底变换模式）
result = client.submit_task(
    image_url=image_url,
    prompt=prompt,
    strength=0.85,
    cfg_scale=10.0,
    sample_steps=45,
    negative_prompt=negative_prompt,
    req_key="seed3l_single_ip"
)

print(f"\n📤 提交结果：{json.dumps(result, indent=2, ensure_ascii=False)}")

if result.get("code") == 10000 and "data" in result:
    task_id = result["data"].get("task_id")
    print(f"\n✅ 任务提交成功！Task ID: {task_id}")
    
    # 轮询查询结果
    print("\n⏳ 等待生成完成...")
    for i in range(30):
        time.sleep(5)
        query_result = client.query_result(task_id)
        
        if query_result.get("code") != 10000:
            print(f"❌ 查询失败：{query_result.get('message', 'Unknown error')}")
            break
        
        data = query_result.get("data", {})
        status = data.get("status", "")
        print(f"  查询 {i+1}/30: 状态={status}")
        
        if status == "done":
            print("\n✅ 生成完成！")
            image_urls = data.get("image_urls", [])
            print(f"\n生成图片 URL:")
            for i, url in enumerate(image_urls, 1):
                print(f"  [{i}] {url}")
            
            # 保存结果
            output_file = Path(__file__).parent / "result.json"
            with open(output_file, "w", encoding='utf-8') as f:
                json.dump({"task_id": task_id, "image_urls": image_urls}, f, indent=2, ensure_ascii=False)
            print(f"\n📄 结果已保存到：{output_file}")
            break
        elif status in ["not_found", "expired", "failed"]:
            print(f"\n❌ 任务失败：{status}")
            break
else:
    print(f"\n❌ 提交失败：{result.get('message', 'Unknown error')}")

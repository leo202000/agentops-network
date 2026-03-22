#!/usr/bin/env python3
"""
即梦 API 调试脚本 - 检查完整响应结构
"""

import os
import sys
import json
import base64

sys.path.insert(0, '/root/.openclaw/workspace/hairstyle_app/backend')
from jimeng_official_client import JimengOfficialClient
from dotenv import load_dotenv
load_dotenv('/root/.openclaw/workspace/.env')

# 初始化客户端
client = JimengOfficialClient(
    os.getenv('JIMENG_ACCESS_KEY_ID'),
    os.getenv('JIMENG_SECRET_ACCESS_KEY')
)

# 测试图片路径
test_image = "/root/.openclaw/workspace/hairstyle_app/test_image.jpg"

# 如果没有测试图片，使用现有的测试图片
if not os.path.exists(test_image):
    # 使用已有的测试图片
    existing_image = "/root/.openclaw/media/inbound/file_14---5db13c37-618a-4a33-8570-a3b06358e823.jpg"
    if os.path.exists(existing_image):
        import shutil
        shutil.copy(existing_image, test_image)
        print(f"✅ 复制测试图片: {test_image}")
    else:
        print(f"❌ 找不到测试图片")
        sys.exit(1)

# 读取图片并转换为 base64
with open(test_image, 'rb') as f:
    image_data = f.read()

image_base64 = base64.b64encode(image_data).decode('utf-8')
image_url = f"data:image/jpeg;base64,{image_base64}"

print("🎨 即梦 API 调试测试")
print("=" * 60)

# 提交任务
print("\n📤 提交任务...")
result = client.submit_inference_task(
    prompt="将图片中的发型修改为自然蓬松的大波浪卷发",
    image_url=image_url,
    negative_prompt="short hair, bob cut, straight hair",
    strength=0.75
)

print(f"📋 提交响应:\n{json.dumps(result, indent=2, ensure_ascii=False)}")

task_id = result.get('data', {}).get('task_id')
if not task_id:
    print("❌ 未能获取任务 ID")
    sys.exit(1)

print(f"\n🆔 任务 ID: {task_id}")

# 轮询查询结果
import time
max_attempts = 60

for attempt in range(1, max_attempts + 1):
    print(f"\n🔄 第 {attempt}/{max_attempts} 次查询...")
    
    query_result = client.query_task_result(task_id)
    status = query_result.get('data', {}).get('status')
    
    print(f"📊 状态: {status}")
    
    if status == "done":
        print("\n✅ 任务完成!")
        print(f"\n📋 完整响应:\n{json.dumps(query_result, indent=2, ensure_ascii=False)}")
        
        # 检查数据结构
        data = query_result.get('data', {})
        print(f"\n🔍 数据结构分析:")
        print(f"  - data 类型: {type(data)}")
        print(f"  - data 键: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
        
        if isinstance(data, dict):
            for key, value in data.items():
                if value is None:
                    print(f"  - {key}: None")
                elif isinstance(value, str) and len(value) > 100:
                    print(f"  - {key}: 字符串 (长度: {len(value)})")
                    # 检查是否是 base64
                    if value.startswith('data:image'):
                        print(f"    └─ 看起来是 base64 图片数据")
                elif isinstance(value, list):
                    print(f"  - {key}: 列表 (长度: {len(value)})")
                    for i, item in enumerate(value[:3]):  # 只显示前3个
                        if isinstance(item, str) and len(item) > 100:
                            print(f"    [{i}]: 字符串 (长度: {len(item)})")
                        else:
                            print(f"    [{i}]: {item}")
                else:
                    print(f"  - {key}: {value}")
        
        # 保存图片数据
        image_url_data = data.get('image_url')
        image_urls_data = data.get('image_urls')
        
        if image_url_data and isinstance(image_url_data, str):
            print(f"\n💾 尝试保存 image_url 数据...")
            try:
                if image_url_data.startswith('data:image'):
                    # 提取 base64
                    base64_data = image_url_data.split(',')[1]
                    image_bytes = base64.b64decode(base64_data)
                    output_path = f"/tmp/jimeng_result_{task_id}.jpg"
                    with open(output_path, 'wb') as f:
                        f.write(image_bytes)
                    print(f"✅ 图片已保存到: {output_path}")
                    print(f"📊 文件大小: {len(image_bytes)} bytes")
            except Exception as e:
                print(f"❌ 保存失败: {e}")
        
        if image_urls_data and isinstance(image_urls_data, list):
            print(f"\n💾 尝试保存 image_urls 数据...")
            for i, img_data in enumerate(image_urls_data):
                try:
                    if isinstance(img_data, str) and img_data.startswith('data:image'):
                        base64_data = img_data.split(',')[1]
                        image_bytes = base64.b64decode(base64_data)
                        output_path = f"/tmp/jimeng_result_{task_id}_{i}.jpg"
                        with open(output_path, 'wb') as f:
                            f.write(image_bytes)
                        print(f"✅ 图片 {i} 已保存到: {output_path}")
                except Exception as e:
                    print(f"❌ 保存图片 {i} 失败: {e}")
        
        break
    
    elif status in ["failed", "error"]:
        print(f"\n❌ 任务失败: {status}")
        print(f"📋 完整响应:\n{json.dumps(query_result, indent=2, ensure_ascii=False)}")
        break
    
    else:
        print(f"⏳ 任务仍在处理中，等待 3 秒后重试...")
        time.sleep(3)

print("\n" + "=" * 60)
print("✅ 调试完成")

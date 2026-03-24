#!/usr/bin/env python3
"""
发型变换功能 - 快速测试

测试 3 种发型生成：
1. 齐肩发（新增）
2. 梨花头（新增）
3. 短发（基础）

预计耗时：3-5 分钟
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from hairstyle_generator import JimengClient
from tos import TosClientV2, ACLType

# 测试配置
TEST_IMAGE = Path(__file__).parent / "backend" / "uploads" / "customer_photo.jpg"
TEST_STYLES = ["齐肩发", "梨花头", "短发"]

print("="*70)
print("🧪 发型变换功能 - 快速测试")
print("="*70)
print(f"\n测试图片：{TEST_IMAGE}")
print(f"测试发型：{TEST_STYLES}")
print(f"预计耗时：3-5 分钟\n")

# 检查图片
if not TEST_IMAGE.exists():
    print(f"❌ 测试图片不存在：{TEST_IMAGE}")
    sys.exit(1)

# 初始化客户端
ak = os.getenv("JIMENG_ACCESS_KEY_ID")
sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")
client = JimengClient(ak, sk)

# TOS 配置
tos_ak = os.getenv("TOS_ACCESS_KEY")
tos_sk = os.getenv("TOS_SECRET_KEY")
tos_bucket = os.getenv("TOS_BUCKET")
tos_region = os.getenv("TOS_REGION", "cn-beijing")

# 发型提示词
HAIRSTYLES = {
    "齐肩发": "shoulder length bob hairstyle, classic and timeless, neat ends, versatile style",
    "梨花头": "pear blossom hairstyle, soft inward curls at ends, korean style, gentle",
    "短发": "short pixie cut, modern and edgy, low maintenance, chic and stylish",
}

results = []

for i, style in enumerate(TEST_STYLES, 1):
    print(f"\n{'='*70}")
    print(f"测试 {i}/{len(TEST_STYLES)}: {style}")
    print(f"{'='*70}")
    
    try:
        # 1. 上传到 TOS
        print(f"\n1️⃣ 上传图片到 TOS...")
        tos_client = TosClientV2(ak=tos_ak, sk=tos_sk, region=tos_region)
        object_key = f"hairstyle/test_{int(time.time())}_{style}.jpg"
        
        tos_client.put_object_from_file(
            bucket=tos_bucket,
            key=object_key,
            file_path=str(TEST_IMAGE)
        )
        
        tos_client.put_object_acl(
            bucket=tos_bucket,
            key=object_key,
            acl=ACLType.ACL_Public_Read
        )
        
        image_url = f"https://{tos_bucket}.tos-{tos_region}.volces.com/{object_key}"
        print(f"   ✅ 上传成功")
        print(f"   URL: {image_url[:60]}...")
        
        # 等待 TOS 同步
        time.sleep(2)
        
        # 2. 提交生成任务
        print(f"\n2️⃣ 提交生成任务...")
        prompt = f"保持人物脸部完全一致，只改变发型为{style}，{HAIRSTYLES[style]}, realistic photo, high quality"
        
        result = client.submit_task(
            image_url=image_url,
            prompt=prompt,
            strength=0.7
        )
        
        if result.get('code') == 10000:
            task_id = result['data']['task_id']
            print(f"   ✅ 任务提交成功")
            print(f"   Task ID: {task_id}")
            
            # 3. 查询结果
            print(f"\n3️⃣ 等待生成完成...")
            for j in range(10):
                time.sleep(15)
                
                query_result = client.query_result(task_id)
                status = query_result.get('data', {}).get('status', 'unknown')
                print(f"   状态：{status} (查询 {j+1}/10)")
                
                if status == 'done':
                    image_urls = query_result.get('data', {}).get('image_urls', [])
                    if image_urls:
                        print(f"\n   ✅ 生成成功!")
                        print(f"   结果 URL: {image_urls[0]}")
                        results.append({
                            'style': style,
                            'success': True,
                            'task_id': task_id,
                            'result_url': image_urls[0]
                        })
                        break
                elif status in ['failed', 'error']:
                    print(f"\n   ❌ 生成失败")
                    results.append({
                        'style': style,
                        'success': False,
                        'error': status
                    })
                    break
            else:
                print(f"\n   ⏳ 任务仍在处理中")
                results.append({
                    'style': style,
                    'success': 'pending',
                    'task_id': task_id
                })
                
        elif result.get('code') == 50430:
            print(f"   ⚠️ API 并发限制，请稍后重试")
            results.append({
                'style': style,
                'success': False,
                'error': 'Rate limit'
            })
        else:
            print(f"   ❌ 提交失败")
            print(f"   完整响应：{result}")
            
            # 提取错误消息
            error_msg = 'Unknown'
            if 'ResponseMetadata' in result and 'Error' in result['ResponseMetadata']:
                error_msg = result['ResponseMetadata']['Error'].get('Message', 'Unknown')
            else:
                error_msg = result.get('message', result.get('error', 'Unknown'))
            
            print(f"   错误：{error_msg}")
            results.append({
                'style': style,
                'success': False,
                'error': error_msg
            })
            
    except Exception as e:
        print(f"   ❌ 异常：{e}")
        results.append({
            'style': style,
            'success': False,
            'error': str(e)
        })
    
    # 间隔 2 秒避免并发限制
    if i < len(TEST_STYLES):
        print(f"\n⏳ 等待 2 秒后测试下一个发型...")
        time.sleep(2)

# 总结
print(f"\n{'='*70}")
print(f"📊 测试结果总结")
print(f"{'='*70}")

success_count = sum(1 for r in results if r.get('success') == True)
print(f"\n总测试数：{len(results)}")
print(f"✅ 成功：{success_count}")
print(f"❌ 失败：{len(results) - success_count}")

print(f"\n详细结果:")
for result in results:
    style = result['style']
    success = result.get('success')
    
    if success == True:
        print(f"  ✅ {style}: 成功 - {result.get('result_url', 'N/A')[:60]}...")
    elif success == 'pending':
        print(f"  ⏳ {style}: 处理中 - Task ID: {result.get('task_id')}")
    else:
        print(f"  ❌ {style}: 失败 - {result.get('error', 'Unknown')}")

if success_count > 0:
    print(f"\n🎉 发型变换功能测试完成！")
    print(f"\n下一步:")
    print(f"  1. 查看生成结果（访问结果 URL）")
    print(f"  2. 启动 Telegram Bot: python3 telegram_hairstyle_bot_v2.py")
    print(f"  3. 访问 Web 前端：http://localhost:8080/frontend/index.html")
else:
    print(f"\n⚠️  所有测试失败，请检查配置")

print(f"\n{'='*70}\n")

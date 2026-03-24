#!/usr/bin/env python3
"""
发型生成系统 - 商用测试脚本
基于独立客户端（已验证成功）
"""

import os
import sys
import time
import json
import hmac
import hashlib
import requests
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# ============================================================================
# 即梦 API 客户端（独立版本 - 已验证成功）
# ============================================================================
class JimengClient:
    """即梦 API 客户端 - 商用版本"""
    
    def __init__(self, access_key: str, secret_key: str, region: str = "cn-north-1"):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.host = "visual.volcengineapi.com"
        self.service = "cv"
    
    def _sha256(self, data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def _create_authorization(self, method: str, uri: str, query: dict, body: str, timestamp: str) -> str:
        date = timestamp[:8]
        canonical_query = "&".join([f"{k}={v}" for k, v in sorted(query.items())])
        body_hash = self._sha256(body)
        canonical_headers = f"host:{self.host}\nx-content-sha256:{body_hash}\nx-date:{timestamp}\n"
        signed_headers = "host;x-content-sha256;x-date"
        canonical_request = f"{method}\n{uri}\n{canonical_query}\n{canonical_headers}\n{signed_headers}\n{body_hash}"
        credential_scope = f"{date}/{self.region}/{self.service}/request"
        string_to_sign = f"HMAC-SHA256\n{timestamp}\n{credential_scope}\n{self._sha256(canonical_request)}"
        k_date = hmac.new(self.secret_key.encode(), date.encode(), hashlib.sha256).digest()
        k_region = hmac.new(k_date, self.region.encode(), hashlib.sha256).digest()
        k_service = hmac.new(k_region, self.service.encode(), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
        signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
        return f"HMAC-SHA256 Credential={self.access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    
    def submit_task(self, image_url: str, prompt: str, strength: float = 0.6, max_retries: int = 3) -> dict:
        """提交任务（带重试机制）"""
        for attempt in range(max_retries):
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            query = {
                "Action": "CVSync2AsyncSubmitTask",
                "Version": "2022-08-31",
            }
            body_dict = {
                "req_key": "seed3l_single_ip",
                "image_urls": [image_url],
                "prompt": prompt,
                "width": 1024,
                "height": 1024,
                "strength": strength,
            }
            body = json.dumps(body_dict, ensure_ascii=False)
            auth = self._create_authorization("POST", "/", query, body, timestamp)
            headers = {
                "Content-Type": "application/json",
                "X-Date": timestamp,
                "X-Content-Sha256": self._sha256(body),
                "Authorization": auth
            }
            url = f"https://{self.host}/"
            
            try:
                response = requests.post(url, params=query, data=body, headers=headers, timeout=120)
                result = response.json()
                
                # 检查是否成功
                if result.get('code') == 10000:
                    return result
                # 检查是否并发限制，重试
                elif result.get('code') == 50430 and attempt < max_retries - 1:
                    print(f"⏳ API 并发限制，等待 {attempt + 1} 秒后重试...")
                    time.sleep(1)
                    continue
                else:
                    return result
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⏳ 请求失败，等待 {attempt + 1} 秒后重试...")
                    time.sleep(1)
                else:
                    return {"error": str(e), "code": -1}
        
        return {"error": "Max retries exceeded", "code": -1}
    
    def query_result(self, task_id: str) -> dict:
        """查询任务结果"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        query = {
            "Action": "CVSync2AsyncGetResult",
            "Version": "2022-08-31",
        }
        body_dict = {
            "req_key": "seed3l_single_ip",
            "task_id": task_id,
        }
        body = json.dumps(body_dict, ensure_ascii=False)
        auth = self._create_authorization("POST", "/", query, body, timestamp)
        headers = {
            "Content-Type": "application/json",
            "X-Date": timestamp,
            "X-Content-Sha256": self._sha256(body),
            "Authorization": auth
        }
        url = f"https://{self.host}/"
        response = requests.post(url, params=query, data=body, headers=headers, timeout=120)
        return response.json()

# ============================================================================
# TOS 上传工具
# ============================================================================
def upload_to_tos(image_path: str) -> str:
    """上传图片到 TOS 并返回公网 URL"""
    from tos import TosClientV2, ACLType
    
    tos_ak = os.getenv("TOS_ACCESS_KEY")
    tos_sk = os.getenv("TOS_SECRET_KEY")
    tos_bucket = os.getenv("TOS_BUCKET")
    tos_region = os.getenv("TOS_REGION", "cn-beijing")
    
    client = TosClientV2(ak=tos_ak, sk=tos_sk, region=tos_region)
    
    import time
    object_key = f"hairstyle/{int(time.time())}_{Path(image_path).name}"
    
    client.put_object_from_file(
        bucket=tos_bucket,
        key=object_key,
        file_path=image_path
    )
    
    client.put_object_acl(
        bucket=tos_bucket,
        key=object_key,
        acl=ACLType.ACL_Public_Read
    )
    
    public_url = f"https://{tos_bucket}.tos-{tos_region}.volces.com/{object_key}"
    return public_url

# ============================================================================
# 发型配置
# ============================================================================
HAIRSTYLES = {
    "齐肩发": "shoulder length bob hairstyle, classic and timeless, neat ends, versatile style, professional look, modern and chic",
    "梨花头": "pear blossom hairstyle, soft inward curls at ends, korean style, gentle and feminine, elegant and romantic",
    "外翘发型": "outward flipped ends hairstyle, playful and cute, flirty style, modern look, bouncy and fun",
    "丸子头": "high bun hairstyle, neat and tidy, elegant updo, summer style, clean and fresh, sophisticated look",
    "空气刘海": "air bangs hairstyle, wispy and light bangs, korean style, soft forehead coverage, youthful and sweet",
    "短发": "short pixie cut, modern and edgy, low maintenance, chic and stylish, frame the face beautifully",
    "卷发": "curly hairstyle, bouncy curls, voluminous and lively, romantic and feminine, full of texture",
    "长发": "long flowing hair, elegant and graceful, classic beauty, smooth and shiny, timeless style",
    "直发": "straight sleek hair, smooth and shiny, modern and clean, minimalist elegance, professional look",
    "马尾": "high ponytail, sporty and energetic, clean and neat, practical and stylish, youthful vibe",
    "辫子": "braided hairstyle, intricate braids, bohemian style, romantic and artistic, detailed craftsmanship",
    "波浪卷": "wavy hairstyle, soft waves, beach waves, relaxed and natural, effortless beauty",
    "大波浪": "big wavy hairstyle, glamorous waves, red carpet style, voluminous and dramatic, elegant",
    "中分": "middle part hairstyle, symmetrical and balanced, modern and sleek, frames the face evenly",
    "斜刘海": "side swept bangs, asymmetrical style, soft and flattering, versatile and trendy",
    "染发红": "red dyed hair, vibrant and bold, eye-catching color, passionate and energetic, unique style",
    "染现金": "blonde dyed hair, bright and sunny, western style, glamorous and fashionable, stands out",
    "染发棕": "brown dyed hair, natural and warm, versatile color, professional and elegant, suits all skin tones",
    "及腰长发": "waist length hair, extremely long, elegant and graceful, traditional beauty, stunning length",
    "羊毛卷": "woolly curly hair, tight curls, afro style, voluminous and textured, bold and unique",
}

# ============================================================================
# 主测试程序
# ============================================================================
def main():
    print("="*80)
    print("发型生成系统 - 商用测试")
    print("="*80)
    
    # 检查配置
    ak = os.getenv("JIMENG_ACCESS_KEY_ID")
    sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")
    
    if not ak or not sk:
        print("\n❌ API 密钥未配置")
        sys.exit(1)
    
    print(f"\n✅ JIMENG_ACCESS_KEY_ID: 已配置")
    print(f"✅ JIMENG_SECRET_ACCESS_KEY: 已配置")
    
    # 测试图片
    test_image = Path(__file__).parent / "uploads" / "customer_photo.jpg"
    if not test_image.exists():
        print(f"\n❌ 测试图片不存在：{test_image}")
        sys.exit(1)
    
    print(f"\n📋 测试图片：{test_image}")
    
    # 上传图片到 TOS
    print(f"\n📤 上传图片到 TOS...")
    try:
        image_url = upload_to_tos(str(test_image))
        print(f"✅ 上传成功：{image_url}")
    except Exception as e:
        print(f"❌ 上传失败：{e}")
        sys.exit(1)
    
    # 创建客户端
    client = JimengClient(ak, sk)
    
    # 测试发型
    test_style = "齐肩发"
    test_prompt = HAIRSTYLES[test_style]
    full_prompt = f"保持人物脸部完全一致，只改变发型为{test_style}，{test_prompt}, realistic photo, high quality, professional photography, natural lighting"
    
    print(f"\n🎨 测试发型：{test_style}")
    print(f"📝 提示词：{full_prompt[:80]}...")
    
    # 提交任务
    print(f"\n⏳ 提交任务...")
    result = client.submit_task(
        image_url=image_url,
        prompt=full_prompt,
        strength=0.7,
        max_retries=3
    )
    
    print(f"\n{'='*80}")
    print("测试结果")
    print(f"{'='*80}")
    
    print(f"\n完整响应：{result}")
    
    if result.get('code') == 10000:
        task_id = result['data']['task_id']
        print(f"✅ 任务提交成功!")
        print(f"   Task ID: {task_id}")
        
        # 查询结果
        print(f"\n⏳ 查询结果（等待 30 秒）...")
        time.sleep(30)
        
        for i in range(10):
            query_result = client.query_result(task_id)
            status = query_result.get('data', {}).get('status', 'unknown')
            print(f"   状态：{status}")
            
            if status == 'done':
                image_urls = query_result.get('data', {}).get('image_urls', [])
                if image_urls:
                    print(f"\n✅ 生成成功!")
                    print(f"   结果 URL: {image_urls[0]}")
                    return 0
            elif status in ['failed', 'error']:
                print(f"\n❌ 生成失败")
                return 1
            
            time.sleep(10)
        
        print(f"\n⏳ 任务仍在处理中")
        return 0
    else:
        print(f"❌ 提交失败")
        print(f"   错误：{result.get('message', result.get('error', 'Unknown'))}")
        print(f"   代码：{result.get('code', 'N/A')}")
        if 'ResponseMetadata' in result:
            print(f"   详情：{result['ResponseMetadata'].get('Error', {})}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

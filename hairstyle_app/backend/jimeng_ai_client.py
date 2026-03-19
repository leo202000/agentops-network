#!/usr/bin/env python3
"""
火山引擎即梦 AI API 客户端 - 正确版本
使用独立的即梦 API 端点

⚠️ 安全提示：不要硬编码密钥，使用环境变量
"""
import requests
import hashlib
import hmac
from datetime import datetime, timezone
import base64
import json
import os


class JimengAIClient:
    """即梦 AI 官方 API 客户端"""
    
    def __init__(self, access_key: str = None, secret_key: str = None, region: str = "cn-north-1"):
        # 从环境变量读取密钥（安全做法）
        self.ak = access_key or os.getenv("JIMENG_ACCESS_KEY_ID")
        self.sk = secret_key or os.getenv("JIMENG_SECRET_ACCESS_KEY")
        
        if not self.ak or not self.sk:
            raise ValueError("⚠️ 错误：请设置环境变量 JIMENG_ACCESS_KEY_ID 和 JIMENG_SECRET_ACCESS_KEY")
        
        self.region = region
        self.host = "jimeng-api.volcengineapi.com"
        self.service = "jimeng"
    
    def _create_authorization(self, method: str, uri: str, body: str) -> str:
        """创建 HMAC-SHA256 签名"""
        now = datetime.now(timezone.utc)
        date = now.strftime("%Y%m%dT%H%M%SZ")
        short_date = now.strftime("%Y%m%d")
        
        body_hash = hashlib.sha256(body.encode()).hexdigest()
        
        canonical_headers = f"host:{self.host}\nx-content-sha256:{body_hash}\nx-date:{date}\n"
        signed_headers = "host;x-content-sha256;x-date"
        
        canonical_request = f"{method}\n{uri}\n\n{canonical_headers}\n{signed_headers}\n{body_hash}"
        
        credential_scope = f"{short_date}/{self.region}/{self.service}/request"
        string_to_sign = f"HMAC-SHA256\n{date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode()).hexdigest()}"
        
        k_date = hmac.new(self.sk.encode(), short_date.encode(), hashlib.sha256).digest()
        k_region = hmac.new(k_date, self.region.encode(), hashlib.sha256).digest()
        k_service = hmac.new(k_region, self.service.encode(), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, "request".encode(), hashlib.sha256).digest()
        
        signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
        
        return f"HMAC-SHA256 Credential={self.ak}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    
    def text_to_image(self, prompt: str, width: int = 1024, height: int = 1024, 
                      sample_steps: int = 25, seed: int = -1, 
                      negative_prompt: str = "") -> dict:
        """
        文生图
        
        Args:
            prompt: 提示词
            width: 图片宽度
            height: 图片高度
            sample_steps: 采样步数
            seed: 随机种子
            negative_prompt: 负面提示词
            
        Returns:
            生成结果
        """
        body = json.dumps({
            "model": "dream-4.0",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "sample_steps": sample_steps,
            "cfg_scale": 7.5,
            "seed": seed
        }, ensure_ascii=False)
        
        auth = self._create_authorization("POST", "/", body)
        date = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        
        headers = {
            "Content-Type": "application/json",
            "X-Date": date,
            "Authorization": auth
        }
        
        url = f"https://{self.host}/"
        
        try:
            response = requests.post(url, headers=headers, data=body, timeout=120)
            result = response.json()
            
            if result.get("code", 0) == 0:
                return {
                    "success": True,
                    "data": result.get("data", {}),
                    "request_id": result.get("request_id")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error"),
                    "code": result.get("code"),
                    "request_id": result.get("request_id")
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def image_to_image(self, init_image: str, prompt: str, strength: float = 0.6,
                       width: int = 1024, height: int = 1024,
                       sample_steps: int = 25, seed: int = -1) -> dict:
        """
        图生图
        
        Args:
            init_image: 初始图片（URL 或 base64）
            prompt: 提示词
            strength: 重绘强度 (0-1)
            width: 图片宽度
            height: 图片高度
            sample_steps: 采样步数
            seed: 随机种子
            
        Returns:
            生成结果
        """
        body = json.dumps({
            "model": "dream-4.0",
            "prompt": prompt,
            "init_image": init_image,
            "strength": strength,
            "width": width,
            "height": height,
            "sample_steps": sample_steps,
            "cfg_scale": 7.5,
            "seed": seed
        }, ensure_ascii=False)
        
        auth = self._create_authorization("POST", "/", body)
        date = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        
        headers = {
            "Content-Type": "application/json",
            "X-Date": date,
            "Authorization": auth
        }
        
        url = f"https://{self.host}/"
        
        try:
            response = requests.post(url, headers=headers, data=body, timeout=120)
            result = response.json()
            
            if result.get("code", 0) == 0:
                return {
                    "success": True,
                    "data": result.get("data", {}),
                    "request_id": result.get("request_id")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error"),
                    "code": result.get("code"),
                    "request_id": result.get("request_id")
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("即梦 AI API 测试 - 正确端点")
    print("=" * 60)
    print(f"端点：jimeng-api.volcengineapi.com")
    print(f"服务：jimeng")
    print(f"模型：dream-4.0")
    print()
    
    try:
        client = JimengAIClient()
        
        # 测试文生图
        print("测试文生图...")
        result = client.text_to_image(
            prompt="a beautiful landscape, mountains, lake, sunset, high quality, detailed, realistic photo",
            width=1024,
            height=1024
        )
        
        if result["success"]:
            print("✅ 成功！")
            print(f"Request ID: {result.get('request_id')}")
            print(f"数据：{json.dumps(result['data'], indent=2, ensure_ascii=False)[:500]}")
        else:
            print("❌ 失败")
            print(f"错误：{result.get('error')}")
            print(f"错误码：{result.get('code')}")
            print(f"Request ID: {result.get('request_id')}")
    except ValueError as e:
        print(f"❌ 配置错误：{e}")
        print()
        print("请设置环境变量:")
        print("  export JIMENG_ACCESS_KEY_ID='your_access_key'")
        print("  export JIMENG_SECRET_ACCESS_KEY='your_secret_key'")

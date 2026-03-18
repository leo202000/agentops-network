#!/usr/bin/env python3
"""
火山引擎即梦 API 客户端
"""
import hashlib
import hmac
import base64
import json
from datetime import datetime
from urllib.parse import quote
import requests


class JimengClient:
    """火山引擎即梦 API 客户端"""
    
    def __init__(self, access_key: str, secret_key: str, region: str = "cn-north-1"):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.host = "visual.volcengineapi.com"
        self.service = "CV"  # Computer Vision
    
    def _sign(self, method: str, path: str, query: dict, body: str, timestamp: str) -> str:
        """生成签名"""
        # 规范请求
        canonical_query = "&".join([f"{k}={quote(v, safe='')}" for k, v in sorted(query.items())])
        canonical_headers = f"host:{self.host}\nx-content-sha256:{self._sha256(body)}\nx-date:{timestamp}\n"
        signed_headers = "host;x-content-sha256;x-date"
        
        canonical_request = f"{method}\n{path}\n{canonical_query}\n{canonical_headers}\n{signed_headers}\n{self._sha256(body)}"
        
        # 签名字符串
        date = timestamp[:8]
        credential_scope = f"{date}/{self.region}/{self.service}/request"
        string_to_sign = f"HMAC-SHA256\n{timestamp}\n{credential_scope}\n{self._sha256(canonical_request)}"
        
        # 计算签名
        k_date = hmac.new(self.secret_key.encode(), date.encode(), hashlib.sha256).digest()
        k_region = hmac.new(k_date, self.region.encode(), hashlib.sha256).digest()
        k_service = hmac.new(k_region, self.service.encode(), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
        
        signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
        return signature
    
    def _sha256(self, data: str) -> str:
        """计算 SHA256"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def generate_image(self, prompt: str, image_url: str = None) -> dict:
        """
        生成图片
        
        Args:
            prompt: 提示词
            image_url: 参考图片 URL（可选，用于图生图）
            
        Returns:
            生成结果
        """
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        date = timestamp[:8]
        
        # API 端点
        action = "SubmitInferenceTask"
        version = "2023-09-01"
        
        query = {
            "Action": action,
            "Version": version,
        }
        
        # 请求体
        body = json.dumps({
            "model_version": "general_v2.1",
            "prompt": prompt,
            "image_url": image_url,
        })
        
        # 生成签名
        signature = self._sign("POST", "/", query, body, timestamp)
        
        # 请求头
        headers = {
            "Content-Type": "application/json",
            "X-Date": timestamp,
            "X-Content-Sha256": self._sha256(body),
            "Authorization": f"HMAC-SHA256 Credential={self.access_key}/{date}/{self.region}/{self.service}/request, SignedHeaders=host;x-content-sha256;x-date, Signature={signature}"
        }
        
        # 发送请求
        url = f"https://{self.host}/"
        try:
            response = requests.post(url, params=query, data=body, headers=headers, timeout=60)
            result = response.json()
            return result
        except Exception as e:
            return {"error": str(e)}


# 测试
if __name__ == "__main__":
    import os
    
    access_key = os.getenv("JIMENG_ACCESS_KEY_ID", "")
    secret_key = os.getenv("JIMENG_SECRET_ACCESS_KEY", "")
    
    client = JimengClient(access_key, secret_key)
    
    # 测试文生图
    result = client.generate_image("一个穿着汉服的女孩，古风，高清")
    print(result)

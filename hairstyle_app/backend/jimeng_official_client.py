#!/usr/bin/env python3
"""
火山引擎即梦 AI API 客户端 - 官方规范版本
文档：https://www.volcengine.com/docs/85621/1817045
"""
import hashlib
import hmac
import json
from datetime import datetime
from urllib.parse import urlencode
import requests


class JimengOfficialClient:
    """火山引擎即梦 AI 官方客户端"""
    
    def __init__(self, access_key: str, secret_key: str, region: str = "cn-north-1"):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.host = "visual.volcengineapi.com"
        self.service = "cv"  # 官方文档指定
    
    def _sha256(self, data: str) -> str:
        """计算 SHA256"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def _sign(self, method: str, path: str, query: dict, body: str, timestamp: str) -> str:
        """生成 HMAC-SHA256 签名"""
        # 规范查询字符串
        canonical_query = "&".join([f"{k}={v}" for k, v in sorted(query.items())])
        
        # 规范请求头
        canonical_headers = f"host:{self.host}\nx-content-sha256:{self._sha256(body)}\nx-date:{timestamp}\n"
        signed_headers = "host;x-content-sha256;x-date"
        
        # 规范请求
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
    
    def submit_inference_task(self, prompt: str, image_url: str = None, 
                               width: int = 1024, height: int = 1024,
                               model_version: str = "general_v2.1",
                               strength: float = 0.6,
                               negative_prompt: str = None) -> dict:
        """
        提交推理任务（CVSync2AsyncSubmitTask）- 支持人脸锁定
        
        Args:
            prompt: 提示词
            image_url: 参考图片 URL（可选，用于图生图）
            width: 图片宽度
            height: 图片高度
            model_version: 模型版本
            strength: 重绘强度 (0.1-1.0)，越低越保持原图特征，推荐 0.4-0.6
            negative_prompt: 负面提示词，防止不需要的变化
            
        Returns:
            提交结果
        """
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        date = timestamp[:8]
        
        # Query 参数（拼接到 URL）- 使用正确的 Action
        query = {
            "Action": "CVSync2AsyncSubmitTask",
            "Version": "2022-08-31",  # 官方文档指定版本
        }
        
        # 请求体 - 使用正确的 req_key
        body_dict = {
            "req_key": "jimeng_t2i_v40",  # 已经验证正确的值
            "model_version": model_version,
            "prompt": prompt,
            "width": width,
            "height": height,
        }
        
        if image_url:
            body_dict["image_url"] = image_url
        
        # 添加重绘强度参数（控制变化程度）
        if strength is not None:
            body_dict["strength"] = strength
        
        # 添加负面提示词（防止不需要的变化）
        if negative_prompt:
            body_dict["negative_prompt"] = negative_prompt
        
        body = json.dumps(body_dict)
        
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
            response = requests.post(url, params=query, data=body, headers=headers, timeout=120)
            result = response.json()
            return result
        except Exception as e:
            return {"error": str(e), "status": -1}
    
    def query_task_result(self, task_id: str) -> dict:
        """
        查询任务结果（CVSync2AsyncGetResult）
        
        Args:
            task_id: 任务 ID
            
        Returns:
            任务结果
        """
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        date = timestamp[:8]
        
        # Query 参数
        query = {
            "Action": "CVSync2AsyncGetResult",
            "Version": "2022-08-31",
        }
        
        # 请求体 - 查询也需要 req_key
        body = json.dumps({
            "req_key": "jimeng_t2i_v40",
            "task_id": task_id
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
            return {"error": str(e), "status": -1}


# 测试
if __name__ == "__main__":
    import os
    
    access_key = os.getenv("JIMENG_ACCESS_KEY_ID", "")
    secret_key = os.getenv("JIMENG_SECRET_ACCESS_KEY", "")
    
    print("=" * 80)
    print("火山引擎即梦 AI - 官方规范测试")
    print("=" * 80)
    
    client = JimengOfficialClient(access_key, secret_key)
    
    # 测试图生图（短发）
    print("\n提交发型生成任务...")
    result = client.submit_inference_task(
        prompt="短发，realistic photo, high quality",
        image_url="http://localhost:8002/uploads/test_long_hair.jpg",
        width=1024,
        height=1024
    )
    
    print(f"\n提交结果：{json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get("status") == 10000 and "data" in result:
        task_id = result["data"].get("task_id")
        print(f"\n✅ 任务提交成功！Task ID: {task_id}")
        
        # 查询结果
        print("\n等待任务完成...")
        import time
        for i in range(10):
            time.sleep(3)
            task_result = client.query_task_result(task_id)
            print(f"  查询 {i+1}/10: 状态={task_result.get('status')}")
            
            if task_result.get("status") == 10000:
                print("\n✅ 任务完成！")
                print(json.dumps(task_result, indent=2, ensure_ascii=False))
                break
            elif task_result.get("status") == -1:
                print(f"\n❌ 查询失败：{task_result.get('error')}")
                break
    else:
        print(f"\n❌ 提交失败：{result.get('message', 'Unknown error')}")

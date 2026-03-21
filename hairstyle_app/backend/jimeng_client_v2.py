#!/usr/bin/env python3
"""
火山引擎即梦 AI API 客户端 v2 - 针对发型变换优化

改进点:
1. 支持 negative_prompt (负面提示词)
2. 支持更高的重绘强度 (0.75-0.85)
3. 支持更详细的参数配置 (cfg_scale, sample_steps)
4. 优化发型变换的提示词模板

文档：https://www.volcengine.com/docs/86081/1804562
"""
import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Optional, List
import requests


class JimengClientV2:
    """火山引擎即梦 AI 客户端 v2 - 发型变换优化版"""
    
    def __init__(self, access_key: str, secret_key: str, region: str = "cn-north-1"):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.host = "visual.volcengineapi.com"
        self.service = "cv"
    
    def _sha256(self, data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def _sign(self, method: str, path: str, query: dict, body: str, timestamp: str) -> str:
        """生成 HMAC-SHA256 签名"""
        date = timestamp[:8]
        canonical_query = "&".join([f"{k}={v}" for k, v in sorted(query.items())])
        body_hash = self._sha256(body)
        canonical_headers = f"host:{self.host}\nx-content-sha256:{body_hash}\nx-date:{timestamp}\n"
        signed_headers = "host;x-content-sha256;x-date"
        canonical_request = f"{method}\n{path}\n{canonical_query}\n{canonical_headers}\n{signed_headers}\n{body_hash}"
        
        credential_scope = f"{date}/{self.region}/{self.service}/request"
        string_to_sign = f"HMAC-SHA256\n{timestamp}\n{credential_scope}\n{self._sha256(canonical_request)}"
        
        k_date = hmac.new(self.secret_key.encode(), date.encode(), hashlib.sha256).digest()
        k_region = hmac.new(k_date, self.region.encode(), hashlib.sha256).digest()
        k_service = hmac.new(k_region, self.service.encode(), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
        
        signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
        return signature
    
    def submit_task(self, 
                    image_url: str, 
                    prompt: str,
                    width: int = 1024, 
                    height: int = 1024,
                    strength: float = 0.75,
                    negative_prompt: Optional[str] = None,
                    cfg_scale: Optional[float] = None,
                    sample_steps: Optional[int] = None,
                    req_key: str = "seed3l_single_ip") -> dict:
        """
        提交图生图任务 - 发型变换优化版
        
        Args:
            image_url: 初始图片 URL 或 base64
            prompt: 正向提示词（详细描述新发型）
            width: 图片宽度
            height: 图片高度
            strength: 重绘强度 (0.1-1.0)
                     - 0.4-0.6: 轻微调整，保持原图特征
                     - 0.65-0.75: 中等变化，推荐用于发型变换
                     - 0.75-0.85: 彻底变化，用于大幅度发型变换
                     - 0.85+: 最大变化，可能影响脸部特征
            negative_prompt: 负面提示词（指定要去除的特征）
                            例如："short hair, bob cut, straight hair, 短发"
            cfg_scale: 提示词引导系数 (3-20)
                      - 7-9: 平衡
                      - 9-11: 更强遵循 prompt
                      - 11+: 可能过度
            sample_steps: 采样步数 (20-50)
                         - 20-30: 快速
                         - 30-40: 标准质量
                         - 40-50: 高质量
            req_key: 模型标识，默认 seed3l_single_ip
        
        Returns:
            {"code": 10000, "data": {"task_id": "xxx"}}
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        
        query = {
            "Action": "CVSync2AsyncSubmitTask",
            "Version": "2022-08-31",
        }
        
        # 构建请求体
        body_dict = {
            "req_key": req_key,
            "image_urls": [image_url],
            "prompt": prompt,
            "width": width,
            "height": height,
            "strength": strength,
        }
        
        # 添加负面提示词（关键！用于去除旧发型特征）
        if negative_prompt:
            body_dict["negative_prompt"] = negative_prompt
        
        # 添加高级参数（如果提供）
        if cfg_scale is not None:
            body_dict["cfg_scale"] = cfg_scale
        
        if sample_steps is not None:
            body_dict["sample_steps"] = sample_steps
        
        body = json.dumps(body_dict, ensure_ascii=False)
        signature = self._sign("POST", "/", query, body, timestamp)
        
        headers = {
            "Content-Type": "application/json",
            "X-Date": timestamp,
            "X-Content-Sha256": self._sha256(body),
            "Authorization": f"HMAC-SHA256 Credential={self.access_key}/{timestamp[:8]}/{self.region}/{self.service}/request, SignedHeaders=host;x-content-sha256;x-date, Signature={signature}"
        }
        
        url = f"https://{self.host}/"
        try:
            response = requests.post(url, params=query, data=body, headers=headers, timeout=120)
            result = response.json()
            return result
        except Exception as e:
            return {"error": str(e), "code": -1}
    
    def query_result(self, task_id: str, req_key: str = "seed3l_single_ip") -> dict:
        """查询任务结果"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        
        query = {
            "Action": "CVSync2AsyncGetResult",
            "Version": "2022-08-31",
        }
        
        body = json.dumps({
            "req_key": req_key,
            "task_id": task_id,
        }, ensure_ascii=False)
        
        signature = self._sign("POST", "/", query, body, timestamp)
        
        headers = {
            "Content-Type": "application/json",
            "X-Date": timestamp,
            "X-Content-Sha256": self._sha256(body),
            "Authorization": f"HMAC-SHA256 Credential={self.access_key}/{timestamp[:8]}/{self.region}/{self.service}/request, SignedHeaders=host;x-content-sha256;x-date, Signature={signature}"
        }
        
        url = f"https://{self.host}/"
        try:
            response = requests.post(url, params=query, data=body, headers=headers, timeout=60)
            return response.json()
        except Exception as e:
            return {"error": str(e), "code": -1}


# 发型变换预设配置
HAIR_STYLE_PRESETS = {
    # 大幅度变换（短发→长发）
    "长发_彻底变换": {
        "strength": 0.85,
        "cfg_scale": 10.0,
        "sample_steps": 45,
        "negative_prompt": "short hair, bob cut, medium hair, 短发，中长发，齐肩发",
        "prompt_template": "{length}长发，{texture}，{style}，保持人物脸部完全一致，只改变发型，realistic photo, high quality, professional photography",
    },
    
    # 中等变换（同长度风格变化）
    "卷发_中等变换": {
        "strength": 0.75,
        "cfg_scale": 9.0,
        "sample_steps": 40,
        "negative_prompt": "straight hair, 直发",
        "prompt_template": "{texture}卷发，{style}，保持人物脸部特征，realistic photo, high quality",
    },
    
    # 轻微调整（微调）
    "微调_轻微变化": {
        "strength": 0.55,
        "cfg_scale": 8.0,
        "sample_steps": 35,
        "negative_prompt": None,
        "prompt_template": "{style}，微调发型，保持整体特征，natural look",
    },
}


def create_hair_prompt(style: str, detailed: bool = True) -> tuple[str, str]:
    """
    创建发型提示词（正向 + 负面）
    
    Args:
        style: 发型风格名称
        detailed: 是否使用详细描述
    
    Returns:
        (positive_prompt, negative_prompt)
    """
    # 发型详细描述库
    hair_descriptions = {
        "大波浪": {
            "positive": "浓密大波浪卷发，glamorous big wavy curls, voluminous waves, long flowing hair past shoulders, elegant and sexy",
            "negative": "short hair, bob cut, straight hair, small waves, 短发，直发，小卷",
        },
        "羊毛卷": {
            "positive": "浓密羊毛卷，tight curly coils, afro curls, voluminous curly hair, bouncy and textured",
            "negative": "straight hair, wavy hair, long straight, 直发，长发",
        },
        "及腰长发": {
            "positive": "及腰超长直发，waist-length long hair, flowing straight hair past waist, silky smooth, elegant",
            "negative": "short hair, bob cut, medium hair, shoulder length, 短发，齐肩发，中长发",
        },
        "短发": {
            "positive": "清爽短发，clean short bob cut, neat and professional, above shoulder length",
            "negative": "long hair, waist length, 长发，及腰发",
        },
        "马尾": {
            "positive": "高马尾发型，high ponytail, sporty and fresh, pulled back hair",
            "negative": "loose hair, down hair, 披发",
        },
        "辫子": {
            "positive": "精致编发，intricate braided hairstyle, French braid, fishtail braid",
            "negative": "loose hair, unstyled, 披发",
        },
    }
    
    if style in hair_descriptions:
        desc = hair_descriptions[style]
        return desc["positive"], desc["negative"]
    
    # 默认
    return f"{style}发型，{style} hairstyle", None


# 测试
if __name__ == "__main__":
    import os
    
    access_key = os.getenv("JIMENG_ACCESS_KEY_ID", "")
    secret_key = os.getenv("JIMENG_SECRET_ACCESS_KEY", "")
    
    if not access_key or "待填写" in access_key:
        print("❌ 请先配置 API 密钥")
        exit(1)
    
    client = JimengClientV2(access_key, secret_key)
    
    # 测试：大波浪彻底变换
    print("=" * 80)
    print("测试：大波浪发型 - 彻底变换模式")
    print("=" * 80)
    
    positive, negative = create_hair_prompt("大波浪")
    
    print(f"\n正向提示词：{positive}")
    print(f"负面提示词：{negative}")
    print(f"\n参数配置:")
    print(f"  strength: 0.85")
    print(f"  cfg_scale: 10.0")
    print(f"  sample_steps: 45")
    
    result = client.submit_task(
        image_url="http://localhost:8002/uploads/test.jpg",
        prompt=positive,
        strength=0.85,
        cfg_scale=10.0,
        sample_steps=45,
        negative_prompt=negative,
    )
    
    print(f"\n提交结果：{json.dumps(result, indent=2, ensure_ascii=False)}")

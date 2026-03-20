#!/usr/bin/env python3
"""
发型 AI 后端 API - 集成火山引擎即梦 API

功能:
- 图片上传
- 火山引擎即梦 API 调用 (官方接口)
- 批量生成多种发型
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import requests
import uuid
import os
import json
import hashlib
import hmac
import time
from pathlib import Path
from datetime import datetime, timezone

# 加载 .env 文件
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding='utf-8') as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value

app = FastAPI(title="AI 发型生成 API")

# ========== 配置 ==========
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 火山引擎即梦 API 配置
JIMENG_ACCESS_KEY = os.getenv("JIMENG_ACCESS_KEY_ID", "")
JIMENG_SECRET_KEY = os.getenv("JIMENG_SECRET_ACCESS_KEY", "")
JIMENG_REGION = "cn-north-1"
JIMENG_API_URL = "https://visual.volcengineapi.com"

# ========== 数据模型 ==========
class HairstyleRequest(BaseModel):
    user_image: str
    style: str
    reference_image: Optional[str] = None

class BatchRequest(BaseModel):
    user_image: str
    styles: List[str] = ["短发", "卷发", "长发", "染发"]

class UploadResponse(BaseModel):
    url: str
    success: bool

class GenerateResponse(BaseModel):
    success: bool
    result_image: Optional[str] = None
    task_id: Optional[str] = None
    error: Optional[str] = None

class BatchResponse(BaseModel):
    success: bool
    results: List[dict] = []

# ========== 火山引擎 API 调用 ==========
def generate_signature(method: str, path: str, query: dict, body: bytes) -> str:
    """生成火山引擎签名"""
    def sha256_bytes(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
    
    canonical_query = "&".join([f"{k}={v}" for k, v in sorted(query.items())])
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    
    canonical_headers = f"host:{JIMENG_API_URL.replace('https://', '')}\nx-content-sha256:{sha256_bytes(body)}\nx-date:{timestamp}\n"
    signed_headers = "host;x-content-sha256;x-date"
    
    canonical_request = f"{method}\n{path}\n{canonical_query}\n{canonical_headers}\n{signed_headers}\n{sha256_bytes(body)}"
    
    date = timestamp[:8]
    credential_scope = f"{date}/{JIMENG_REGION}/cv/request"
    string_to_sign = f"HMAC-SHA256\n{timestamp}\n{credential_scope}\n{sha256_bytes(canonical_request.encode('utf-8'))}"
    
    k_date = hmac.new(JIMENG_SECRET_KEY.encode(), date.encode(), hashlib.sha256).digest()
    k_region = hmac.new(k_date, JIMENG_REGION.encode(), hashlib.sha256).digest()
    k_service = hmac.new(k_region, "cv".encode(), hashlib.sha256).digest()
    k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
    
    signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
    return signature, timestamp

def submit_jimeng_task(image_url: str, prompt: str) -> dict:
    """提交即梦 API 任务"""
    try:
        query = {
            "Action": "CVSync2AsyncSubmitTask",
            "Version": "2022-08-31",
        }
        
        body_dict = {
            "req_key": "jimeng_t2i_v40",
            "prompt": prompt,
            "image_url": image_url,
        }
        body = json.dumps(body_dict, ensure_ascii=False).encode('utf-8')
        
        signature, timestamp = generate_signature("POST", "/", query, body)
        date = timestamp[:8]
        
        headers = {
            "Content-Type": "application/json",
            "X-Date": timestamp,
            "X-Content-Sha256": hashlib.sha256(body.encode('utf-8')).hexdigest(),
            "Authorization": f"HMAC-SHA256 Credential={JIMENG_ACCESS_KEY}/{date}/{JIMENG_REGION}/cv/request, SignedHeaders=host;x-content-sha256;x-date, Signature={signature}"
        }
        
        response = requests.post(JIMENG_API_URL, params=query, data=body, headers=headers, timeout=120)
        result = response.json()
        
        if result.get("status") == 10000:
            task_id = result.get("data", {}).get("task_id")
            return {"success": True, "task_id": task_id}
        else:
            return {"success": False, "error": result.get("message", "Unknown error")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def query_task_result(task_id: str) -> dict:
    """查询任务结果"""
    try:
        query = {
            "Action": "CVSync2AsyncGetResult",
            "Version": "2022-08-31",
        }
        
        body = json.dumps({"task_id": task_id})
        signature, timestamp = generate_signature("POST", "/", query, body)
        date = timestamp[:8]
        
        headers = {
            "Content-Type": "application/json",
            "X-Date": timestamp,
            "X-Content-Sha256": hashlib.sha256(body.encode('utf-8')).hexdigest(),
            "Authorization": f"HMAC-SHA256 Credential={JIMENG_ACCESS_KEY}/{date}/{JIMENG_REGION}/cv/request, SignedHeaders=host;x-content-sha256;x-date, Signature={signature}"
        }
        
        response = requests.post(JIMENG_API_URL, params=query, data=body, headers=headers, timeout=60)
        result = response.json()
        
        if result.get("status") == 10000:
            data = result.get("data", {})
            if data.get("status") == 1:  # 完成
                images = data.get("images", [])
                return {"success": True, "images": images, "status": "done"}
            elif data.get("status") == 2:  # 失败
                return {"success": False, "error": "Task failed", "status": "failed"}
            else:
                return {"success": False, "error": "Processing", "status": "processing"}
        else:
            return {"success": False, "error": result.get("message", "Unknown error")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def generate_hairstyle(image_url: str, style: str, wait: bool = True, timeout: int = 120) -> dict:
    """生成发型（包含轮询）"""
    prompt = f"保持人物脸部完全一致，只改变发型为{style}，真实照片风格，高清，自然光，专业摄影"
    
    # 提交任务
    submit_result = submit_jimeng_task(image_url, prompt)
    if not submit_result["success"]:
        return submit_result
    
    task_id = submit_result["task_id"]
    
    if not wait:
        return {"success": True, "task_id": task_id, "status": "submitted"}
    
    # 轮询结果
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(3)
        query_result = query_task_result(task_id)
        
        if query_result["status"] == "done":
            return {
                "success": True,
                "task_id": task_id,
                "images": query_result["images"],
                "status": "done"
            }
        elif query_result["status"] == "failed":
            return query_result
    
    return {"success": False, "error": "Timeout", "task_id": task_id}

# ========== API 端点 ==========
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """上传图片"""
    try:
        content = await file.read()
        filename = f"{uuid.uuid4()}.jpg"
        filepath = f"{UPLOAD_DIR}/{filename}"
        with open(filepath, "wb") as f:
            f.write(content)
        url = f"http://localhost:8000/{filepath}"
        return {"url": url, "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-hairstyle")
async def generate_hairstyle_endpoint(request: HairstyleRequest):
    """生成单个发型"""
    result = generate_hairstyle(request.user_image, request.style)
    
    return JSONResponse(
        content=result,
        media_type="application/json; charset=utf-8"
    )

@app.post("/generate-batch")
async def generate_batch(request: BatchRequest):
    """批量生成多个发型"""
    results = []
    
    for style in request.styles:
        result = generate_hairstyle(request.user_image, style, timeout=180)
        results.append({
            "style": style,
            **result
        })
    
    return {"success": True, "results": results}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "hairstyle-api", "api": "jimeng_t2i_v40"}

@app.get("/styles")
async def list_styles():
    """获取支持的发型风格列表"""
    return {
        "styles": [
            "短发", "卷发", "长发", "直发",
            "染发 - 红色", "染发 - 金色", "染发 - 棕色",
            "中分", "斜刘海", "马尾",
            "波浪卷", "大波浪", "小卷"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

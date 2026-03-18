#!/usr/bin/env python3
"""
发型 AI 后端 API - MVP 版本

功能:
- 图片上传（OSS/Cloudinary）
- 火山引擎即梦 API 调用
- 批量生成
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import requests
import uuid
import os
from pathlib import Path

# 加载 .env 文件
env_path = Path(__file__).parent.parent.parent / ".env"  # 指向 /root/.openclaw/workspace/.env
if env_path.exists():
    with open(env_path, "r") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value

app = FastAPI(title="AI 发型生成 API")

# ========== 配置 ==========
# 火山引擎即梦 API 配置
JIMENG_ACCESS_KEY = os.getenv("JIMENG_ACCESS_KEY_ID", "")
JIMENG_SECRET_KEY = os.getenv("JIMENG_SECRET_ACCESS_KEY", "")
JIMENG_REGION = os.getenv("JIMENG_REGION", "cn-north-1")
JIMENG_API_VERSION = os.getenv("JIMENG_API_VERSION", "2023-09-01")
# 火山引擎视觉 API 端点
JIMENG_API_URL = "https://visual.volcengineapi.com"

# 图片存储（临时用本地，生产用 OSS）
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ========== 数据模型 ==========
class HairstyleRequest(BaseModel):
    user_image: str  # 图片 URL
    style: str  # 发型风格
    reference_image: Optional[str] = None  # 参考图（可选）

class BatchRequest(BaseModel):
    user_image: str
    styles: List[str] = ["短发", "卷发", "中分", "长发"]

class UploadResponse(BaseModel):
    url: str
    success: bool

class GenerateResponse(BaseModel):
    success: bool
    result_image: Optional[str] = None
    error: Optional[str] = None

class BatchResponse(BaseModel):
    success: bool
    results: List[dict] = []

# ========== 工具函数 ==========
def save_to_local(file_bytes: bytes) -> str:
    """保存到本地（测试用）"""
    filename = f"{uuid.uuid4()}.jpg"
    filepath = f"{UPLOAD_DIR}/{filename}"
    with open(filepath, "wb") as f:
        f.write(file_bytes)
    return f"http://localhost:8000/{filepath}"

def call_jimeng_api(image_url: str, style: str, ref_image: Optional[str] = None) -> dict:
    """调用火山引擎即梦 API (使用官方 SDK)"""
    try:
        from jimeng_sdk_client import JimengSDKClient
        
        ak = os.getenv("JIMENG_ACCESS_KEY_ID", "")
        sk = os.getenv("JIMENG_SECRET_ACCESS_KEY", "")
        
        client = JimengSDKClient(ak, sk)
        
        # 构建 Prompt
        if ref_image:
            prompt = f"保持人物脸部完全一致，参考第二张图片的发型，生成真实照片，风格：{style}"
        else:
            prompt = f"保持人物脸部完全一致，只改变发型为{style}，真实照片风格，高清，自然光"
        
        result = client.generate_image(prompt=prompt, image_url=image_url)
        
        if result["success"]:
            # 火山引擎返回格式
            data = result.get("data", {})
            image_url_result = data.get("result", {}).get("image_url")
            return {
                "success": True,
                "image_url": image_url_result
            }
        else:
            return {
                "success": False,
                "error": result.get("error")
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ========== API 端点 ==========
@app.post("/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """上传图片"""
    try:
        content = await file.read()
        url = save_to_local(content)
        return UploadResponse(url=url, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-hairstyle", response_model=GenerateResponse)
async def generate_hairstyle(request: HairstyleRequest):
    """生成单个发型"""
    result = call_jimeng_api(request.user_image, request.style, request.reference_image)
    
    if result["success"]:
        return GenerateResponse(
            success=True,
            result_image=result["image_url"]
        )
    else:
        return GenerateResponse(
            success=False,
            error=result.get("error", "生成失败")
        )

@app.post("/generate-batch", response_model=BatchResponse)
async def generate_batch(request: BatchRequest):
    """批量生成多个发型"""
    results = []
    
    for style in request.styles:
        result = call_jimeng_api(request.user_image, style)
        results.append({
            "style": style,
            "success": result["success"],
            "image_url": result.get("image_url"),
            "error": result.get("error")
        })
    
    return BatchResponse(success=True, results=results)

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "hairstyle-api"}

# ========== 启动 ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

#!/usr/bin/env python3
"""
图片上传服务
处理前端上传的图片，返回可访问的 URL
"""
import os
import uuid
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass
import aiohttp
from aiohttp import web
import aiofiles


@dataclass
class UploadConfig:
    """上传配置"""
    upload_dir: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_types: tuple = ('image/jpeg', 'image/png', 'image/webp')
    base_url: str = "http://localhost:8080/uploads"


class ImageUploadService:
    """图片上传服务"""
    
    def __init__(self, config: Optional[UploadConfig] = None):
        self.config = config or UploadConfig()
        self._ensure_upload_dir()
    
    def _ensure_upload_dir(self):
        """确保上传目录存在"""
        os.makedirs(self.config.upload_dir, exist_ok=True)
        
        # 按日期创建子目录
        today = datetime.now().strftime("%Y-%m-%d")
        daily_dir = os.path.join(self.config.upload_dir, today)
        os.makedirs(daily_dir, exist_ok=True)
    
    def _get_daily_dir(self) -> str:
        """获取当日上传目录"""
        today = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.config.upload_dir, today)
    
    def _generate_filename(self, original_filename: str) -> str:
        """生成唯一文件名"""
        # 提取扩展名
        ext = os.path.splitext(original_filename)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
            ext = '.jpg'
        
        # 生成唯一 ID
        unique_id = uuid.uuid4().hex[:16]
        timestamp = datetime.now().strftime("%H%M%S")
        
        return f"{timestamp}_{unique_id}{ext}"
    
    def _validate_file(self, content_type: str, file_size: int) -> tuple:
        """
        验证文件
        
        Returns:
            (is_valid, error_message)
        """
        if content_type not in self.config.allowed_types:
            return False, f"不支持的文件类型：{content_type}"
        
        if file_size > self.config.max_file_size:
            return False, f"文件大小超过限制：{file_size} > {self.config.max_file_size}"
        
        return True, ""
    
    async def save_upload(self, file_data: bytes, filename: str, content_type: str) -> Dict[str, Any]:
        """
        保存上传的文件
        
        Args:
            file_data: 文件数据
            filename: 原始文件名
            content_type: 文件类型
        
        Returns:
            上传结果
        """
        # 验证文件
        is_valid, error = self._validate_file(content_type, len(file_data))
        if not is_valid:
            return {
                "success": False,
                "error": error
            }
        
        try:
            # 生成文件名
            new_filename = self._generate_filename(filename)
            daily_dir = self._get_daily_dir()
            file_path = os.path.join(daily_dir, new_filename)
            
            # 保存文件
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_data)
            
            # 计算文件哈希
            file_hash = hashlib.md5(file_data).hexdigest()
            
            # 生成访问 URL
            relative_path = os.path.relpath(file_path, self.config.upload_dir)
            file_url = f"{self.config.base_url}/{relative_path}"
            
            return {
                "success": True,
                "url": file_url,
                "filename": new_filename,
                "original_name": filename,
                "size": len(file_data),
                "hash": file_hash,
                "content_type": content_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"保存文件失败：{str(e)}"
            }
    
    async def handle_upload_request(self, request: web.Request) -> web.Response:
        """处理上传请求"""
        try:
            reader = await request.multipart()
            
            uploaded_files = []
            
            async for part in reader:
                if part.name != 'files':
                    continue
                
                # 读取文件数据
                filename = part.filename
                content_type = part.headers.get('Content-Type', 'application/octet-stream')
                
                file_data = await part.read()
                
                # 保存文件
                result = await self.save_upload(file_data, filename, content_type)
                uploaded_files.append(result)
            
            # 检查是否有成功上传的文件
            successful = [f for f in uploaded_files if f.get('success')]
            failed = [f for f in uploaded_files if not f.get('success')]
            
            return web.json_response({
                "success": len(successful) > 0,
                "files": uploaded_files,
                "uploaded_count": len(successful),
                "failed_count": len(failed)
            })
            
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def handle_delete_request(self, request: web.Request) -> web.Response:
        """处理删除请求"""
        try:
            data = await request.json()
            filename = data.get('filename')
            
            if not filename:
                return web.json_response({
                    "success": False,
                    "error": "缺少文件名"
                }, status=400)
            
            # 安全校验：防止目录遍历
            if '..' in filename or '/' in filename:
                return web.json_response({
                    "success": False,
                    "error": "非法文件名"
                }, status=400)
            
            # 查找文件
            daily_dir = self._get_daily_dir()
            file_path = os.path.join(daily_dir, filename)
            
            if not os.path.exists(file_path):
                return web.json_response({
                    "success": False,
                    "error": "文件不存在"
                }, status=404)
            
            # 删除文件
            os.remove(file_path)
            
            return web.json_response({
                "success": True,
                "message": "文件已删除"
            })
            
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)


# 创建应用
async def init_app():
    """初始化应用"""
    app = web.Application()
    
    # 创建上传服务
    upload_service = ImageUploadService()
    
    # 配置路由
    app.router.add_post('/api/upload', upload_service.handle_upload_request)
    app.router.add_post('/api/upload/delete', upload_service.handle_delete_request)
    
    # 静态文件服务（用于访问上传的文件）
    app.router.add_static('/uploads', upload_service.config.upload_dir)
    
    return app


# 启动服务
if __name__ == '__main__':
    app = init_app()
    web.run_app(app, host='localhost', port=8080)

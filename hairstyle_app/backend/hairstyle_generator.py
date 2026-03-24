#!/usr/bin/env python3
"""
AI 发型生成器 - 完整整合版本

功能:
- 客户上传照片
- 选择发型风格
- 调用火山引擎即梦 API 生成新发型
- 支持批量生成

使用示例:
    python hairstyle_generator.py --image photo.jpg --style 短发
    python hairstyle_generator.py --image photo.jpg --styles 短发 卷发 长发
"""

import os
import sys
import json
import time
import hashlib
import hmac
import requests
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

# 加载 .env 文件
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding='utf-8') as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value

# 导入压缩和缓存模块
from image_compressor import compress_image
from result_cache import ResultCache


class JimengClient:
    """火山引擎即梦 AI 客户端 - 图生图 (seed3l_single_ip)
    
    文档：https://www.volcengine.com/docs/86081/1804562
    端点：visual.volcengineapi.com ✅
    服务：cv ✅
    Region: cn-north-1 ✅
    
    ⚠️ 重要：根据官方文档
    - 异步 API：提交任务 → 查询结果
    - Action: CVSync2AsyncSubmitTask / CVSync2AsyncGetResult
    - Version: 2022-08-31
    - req_key: seed3l_single_ip
    """
    
    def __init__(self, access_key: str, secret_key: str, region: str = "cn-north-1"):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.host = "visual.volcengineapi.com"  # ✅ 正确的端点（根据官方文档）
        self.service = "cv"  # ✅ 正确的服务名
    
    def _sha256(self, data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def _create_authorization(self, method: str, uri: str, query: dict, body: str, timestamp: str) -> str:
        """创建 HMAC-SHA256 签名（根据官方文档）"""
        date = timestamp[:8]
        
        # 规范查询字符串（不要 URL 编码！）
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
    
    def submit_task(self, image_url: str, prompt: str, 
                    width: int = 1024, height: int = 1024,
                    strength: float = 0.6, req_key: str = "seed3l_single_ip") -> dict:
        """
        提交图生图任务（异步 API）
        
        ⚠️ 根据官方文档（2026-03-20 截图）:
        - Action: CVSync2AsyncSubmitTask
        - Version: 2022-08-31
        - image_urls: 数组格式（不是 image_url）
        - 返回 task_id，需要查询结果
        
        Args:
            image_url: 初始图片 URL（公网可访问）或 base64
            prompt: 提示词
            width: 图片宽度
            height: 图片高度
            strength: 重绘强度 (0-1)，推荐 0.4-0.6
            req_key: 模型标识，默认 seed3l_single_ip
        
        Returns:
            {"code": 10000, "data": {"task_id": "xxx"}}
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        date = timestamp[:8]
        
        # Query 参数（根据官方文档）
        query = {
            "Action": "CVSync2AsyncSubmitTask",
            "Version": "2022-08-31",
        }
        
        # Body 参数（根据官方文档 - 使用 image_urls 数组）
        body_dict = {
            "req_key": req_key,  # ✅ seed3l_single_ip
            "image_urls": [image_url],  # ✅ 数组格式（官方文档要求）
            "prompt": prompt,
            "width": width,
            "height": height,
        }
        
        if strength is not None:
            body_dict["strength"] = strength
        
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
            return result
        except Exception as e:
            return {"error": str(e), "code": -1}
    
    def query_result(self, task_id: str, req_key: str = "seed3l_single_ip") -> dict:
        """
        查询任务结果（异步 API）
        
        ⚠️ 根据官方文档:
        - Action: CVSync2AsyncGetResult
        - Version: 2022-08-31
        - 返回：data.image_urls (数组)
        
        Args:
            task_id: 任务 ID
            req_key: 模型标识
        
        Returns:
            {"code": 10000, "data": {"image_urls": [...], "status": "done"}}
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        date = timestamp[:8]
        
        # Query 参数
        query = {
            "Action": "CVSync2AsyncGetResult",
            "Version": "2022-08-31",
        }
        
        # Body 参数
        body_dict = {
            "req_key": req_key,
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
        try:
            response = requests.post(url, params=query, data=body, headers=headers, timeout=60)
            result = response.json()
            return result
        except Exception as e:
            return {"error": str(e), "code": -1}


class HairstyleGenerator:
    """发型生成器 - 整合业务逻辑 (v2 优化版)"""
    
    # 支持的发型风格 - 详细描述版
    STYLES = {
        "短发": {
            "prompt": "short bob cut hairstyle, clean and neat, professional look, above shoulder",
            "negative": "long hair, waist length, 长发"
        },
        "卷发": {
            "prompt": "curly hairstyle, wavy and voluminous, bouncy curls, textured hair",
            "negative": "straight hair, 直发"
        },
        "长发": {
            "prompt": "long straight hairstyle, elegant and smooth, flowing hair past shoulders, silky",
            "negative": "short hair, bob cut, 短发"
        },
        "直发": {
            "prompt": "straight sleek hairstyle, professional look, smooth and shiny",
            "negative": "curly hair, wavy hair, 卷发"
        },
        "马尾": {
            "prompt": "ponytail hairstyle, sporty and fresh, pulled back hair, high ponytail",
            "negative": "loose hair, down hair, 披发"
        },
        "辫子": {
            "prompt": "braided hairstyle, intricate plait, French braid, detailed braids",
            "negative": "loose hair, unstyled, 披发"
        },
        "波浪卷": {
            "prompt": "wavy curly hairstyle, beach waves, natural flowing waves, medium curls",
            "negative": "straight hair, tight curls, 直发"
        },
        "大波浪": {
            "prompt": "big wavy hairstyle, glamorous curls, voluminous waves, long flowing hair, elegant and sexy",
            "negative": "short hair, bob cut, straight hair, small waves, 短发，直发"
        },
        "中分": {
            "prompt": "middle part hairstyle, symmetrical style, center part, balanced look",
            "negative": "side part, bangs, 斜刘海"
        },
        "斜刘海": {
            "prompt": "side bangs hairstyle, asymmetrical fringe, side swept bangs",
            "negative": "middle part, no bangs, 中分"
        },
        "染发红": {
            "prompt": "red hair color, vibrant and bold, crimson red, fiery hair",
            "negative": "black hair, brown hair, 黑发"
        },
        "染现金": {
            "prompt": "blonde hair color, bright and stylish, platinum blonde, golden highlights",
            "negative": "black hair, dark hair, 黑发"
        },
        "染发棕": {
            "prompt": "brown hair color, natural and warm, chocolate brown, chestnut highlights",
            "negative": "black hair, blonde hair, 黑发"
        },
        "及腰长发": {
            "prompt": "waist-length long hair, ultra long flowing hair, silky smooth, elegant and graceful",
            "negative": "short hair, bob cut, medium hair, shoulder length, 短发，齐肩发"
        },
        "羊毛卷": {
            "prompt": "wool curly hair, tight curly coils, afro curls, voluminous and bouncy, textured",
            "negative": "straight hair, wavy hair, long straight, 直发"
        },
        # ===== 新增发型（2026-03-23）=====
        "齐肩发": {
            "prompt": "shoulder length bob hairstyle, classic and timeless, neat ends, versatile style, elegant collarbone length",
            "negative": "very long hair, waist length, super short, 及腰长发，超短发"
        },
        "梨花头": {
            "prompt": "pear blossom hairstyle, soft inward curls at ends, korean style, gentle and feminine, romantic look",
            "negative": "outward curls, straight ends, 外翘，直发尾"
        },
        "外翘发型": {
            "prompt": "outward flipped ends hairstyle, playful and cute, flirty style, modern look, bouncy tips",
            "negative": "inward curls, straight ends, 内扣，直发尾"
        },
        "丸子头": {
            "prompt": "high bun hairstyle, neat and tidy, elegant updo, summer style, clean and fresh, exposed neck",
            "negative": "loose hair, down hair, 披发，散发"
        },
        "空气刘海": {
            "prompt": "air bangs hairstyle, wispy and light bangs, korean style, soft forehead coverage, see-through fringe",
            "negative": "heavy bangs, thick bangs, no bangs, 厚刘海，无刘海"
        },
    }
    
    # 变换强度预设
    TRANSFORM_PRESETS = {
        "轻微": {"strength": 0.55, "cfg_scale": 8.0, "sample_steps": 35},
        "中等": {"strength": 0.70, "cfg_scale": 9.0, "sample_steps": 40},
        "彻底": {"strength": 0.85, "cfg_scale": 10.0, "sample_steps": 45},
    }
    
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        transform_mode: str = "中等",
        enable_cache: bool = True,
        enable_compression: bool = True,
        cache_dir: str = "./cache",
        cache_ttl_hours: int = 24,
        compression_quality: int = 85
    ):
        """
        初始化发型生成器
        
        Args:
            access_key: API 访问密钥
            secret_key: API 密钥
            transform_mode: 变换强度（轻微/中等/彻底）
            enable_cache: 是否启用缓存
            enable_compression: 是否启用图片压缩
            cache_dir: 缓存目录
            cache_ttl_hours: 缓存有效期（小时）
            compression_quality: 压缩质量（1-100）
        """
        self.client = JimengClient(access_key, secret_key)
        self.transform_mode = transform_mode
        
        # 压缩和缓存配置
        self.enable_cache = enable_cache
        self.enable_compression = enable_compression
        self.compression_quality = compression_quality
        
        # 初始化缓存
        if enable_cache:
            self.cache = ResultCache(
                cache_dir=cache_dir,
                ttl_hours=cache_ttl_hours,
                max_size_gb=2.0  # 最大 2GB
            )
            print(f"💾 缓存已启用：{cache_dir} (TTL: {cache_ttl_hours}小时)")
        else:
            self.cache = None
            print(f"⚠️  缓存已禁用")
        
        # 上传目录
        self.upload_dir = Path(__file__).parent / "uploads"
        self.upload_dir.mkdir(exist_ok=True)
        
        # 压缩目录
        if enable_compression:
            self.compressed_dir = Path(__file__).parent / "compressed"
            self.compressed_dir.mkdir(exist_ok=True)
            print(f"🗜️  压缩已启用：质量={compression_quality}")
        
        # 发型分析器（用于指定发型功能）
        self.analyzer = None
        if access_key:
            try:
                from hairstyle_analyzer import HairstyleAnalyzer
                self.analyzer = HairstyleAnalyzer(access_key)
                print(f"🎨 发型分析器已启用（支持指定发型）")
            except Exception as e:
                print(f"⚠️  发型分析器初始化失败：{e}")
    
    def upload_image(self, image_path: str) -> str:
        """
        上传图片，返回公网可访问的 URL
        
        ⚠️ 根据即梦工程师反馈：
        - 本地链接 (localhost) 无法使用
        - 必须使用公网可访问的 URL 或 base64
        
        优先级:
        1. TOS/OSS (如果配置了)
        2. base64 (默认 fallback)
        
        Args:
            image_path: 本地图片路径
            
        Returns:
            公网 URL 或 base64
        """
        # 导入上传器
        from image_uploader import quick_upload
        
        print(f"📤 上传图片：{image_path}")
        url = quick_upload(image_path)
        
        if url.startswith("data:"):
            print(f"✅ 已转换为 base64（长度：{len(url)}）")
        else:
            print(f"✅ 已上传到公网：{url[:60]}...")
        
        return url
    
    def generate(self, image_path: str, style: str, 
                 transform_mode: str = None,
                 wait: bool = True, timeout: int = 180) -> dict:
        """
        生成发型（图生图 - 角色特征保持）- 异步 API v2
        
        改进点:
        - 支持负面提示词 (negative_prompt)
        - 支持变换强度预设 (轻微/中等/彻底)
        - 更详细的发型描述
        
        Args:
            image_path: 客户照片路径
            style: 发型风格
            transform_mode: 变换强度 (轻微/中等/彻底)，默认使用初始化时的设置
            wait: 是否等待完成
            timeout: 超时时间（秒）
        
        Returns:
            生成结果
        """
        # 检查风格
        if style not in self.STYLES:
            available = ", ".join(self.STYLES.keys())
            return {
                "success": False,
                "error": f"不支持的发型：{style}",
                "available_styles": available
            }
        
        # 📦 查询缓存（如果启用）
        if self.enable_cache and self.cache:
            style_config = self.STYLES[style]
            style_prompt = style_config["prompt"]
            negative_prompt = style_config.get("negative", "")
            full_prompt = f"{style_prompt} {negative_prompt}"
            
            cache_result = self.cache.get(image_path, style, full_prompt)
            
            if cache_result['hit']:
                print(f"✅ 使用缓存结果，跳过 API 调用")
                return {
                    "success": True,
                    "cached": True,
                    "image_urls": [cache_result['image_url']],
                    "result_path": cache_result['result_path'],
                    "cache_info": {
                        'age_hours': cache_result.get('age_hours', 0),
                        'style': cache_result.get('style', style)
                    }
                }
        
        # 上传图片（自动选择 TOS/OSS/base64）
        image_url = self.upload_image(image_path)
        
        # 获取发型配置
        style_config = self.STYLES[style]
        style_prompt = style_config["prompt"]
        negative_prompt = style_config.get("negative")
        
        # 获取变换强度参数
        mode = transform_mode or self.transform_mode
        preset = self.TRANSFORM_PRESETS.get(mode, self.TRANSFORM_PRESETS["中等"])
        strength = preset["strength"]
        cfg_scale = preset["cfg_scale"]
        sample_steps = preset["sample_steps"]
        
        # 构建提示词 - 角色特征保持 + 详细发型描述
        prompt = f"保持人物脸部完全一致，只改变发型为{style}，{style_prompt}, realistic photo, high quality, professional photography, natural lighting"
        
        print(f"🎨 生成发型：{style} [{mode}模式]")
        print(f"📝 正向提示词：{prompt[:80]}...")
        if negative_prompt:
            print(f"🚫 负面提示词：{negative_prompt}")
        print(f"🔧 模型：seed3l_single_ip (图生图 - 角色特征保持)")
        print(f"⚙️  参数：strength={strength}, cfg={cfg_scale}, steps={sample_steps}")
        print(f"🌐 图片：{'base64' if image_url.startswith('data:') else '公网 URL'}")
        
        # 步骤 1: 提交任务
        print(f"📤 提交任务...")
        submit_result = self.client.submit_task(
            image_url=image_url,
            prompt=prompt,
            strength=strength,
            req_key="seed3l_single_ip"
        )
        
        # 检查提交结果（支持两种响应格式）
        # 格式 1: {'code': 10000, 'data': {...}, 'message': 'Success'}
        # 格式 2: {'ResponseMetadata': {'Error': {'Code': 'xxx', 'Message': 'xxx'}}}
        
        error_code = None
        error_message = "提交失败"
        request_id = None
        
        if submit_result and isinstance(submit_result, dict):
            # 检查格式 1（成功响应）
            if submit_result.get("code") == 10000:
                pass  # 成功，继续
            # 检查格式 2（错误响应）
            elif "ResponseMetadata" in submit_result and "Error" in submit_result["ResponseMetadata"]:
                error_meta = submit_result["ResponseMetadata"]["Error"]
                error_code = error_meta.get("CodeN", error_meta.get("Code"))
                error_message = error_meta.get("Message", "提交失败")
                request_id = submit_result["ResponseMetadata"].get("RequestId")
            # 其他错误格式
            else:
                error_code = submit_result.get("code")
                error_message = submit_result.get("message", "提交失败")
                request_id = submit_result.get("request_id")
        else:
            error_message = "提交失败（无响应）"
        
        if error_code is not None or (submit_result and not submit_result.get("code")):
            print(f"❌ API 错误：{error_message}")
            print(f"   错误代码：{error_code}")
            print(f"   Request ID: {request_id}")
            
            return {
                "success": False,
                "error": error_message,
                "code": error_code,
                "request_id": request_id
            }
        
        task_id = submit_result["data"]["task_id"]
        print(f"✅ 任务已提交：{task_id}")
        
        if not wait:
            return {
                "success": True,
                "task_id": task_id,
                "status": "submitted"
            }
        
        # 步骤 2: 轮询查询结果
        print(f"⏳ 等待生成完成...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            time.sleep(3)  # 每 3 秒查询一次
            
            query_result = self.client.query_result(task_id)
            
            # 检查查询结果
            if query_result.get("code") != 10000:
                return {
                    "success": False,
                    "error": query_result.get("message", "查询失败"),
                    "code": query_result.get("code"),
                    "task_id": task_id
                }
            
            data = query_result.get("data", {})
            status = data.get("status", "")
            
            print(f"  状态：{status}")
            
            if status == "done":
                # ✅ 完成
                image_urls = data.get("image_urls", [])
                print(f"✅ 生成完成！")
                
                # 🗜️ 压缩图片（如果启用）
                compressed_path = None
                if self.enable_compression and image_urls:
                    try:
                        # 下载临时文件
                        temp_path = self.upload_dir / f"temp_{task_id}.jpg"
                        response = requests.get(image_urls[0], timeout=30)
                        with open(temp_path, 'wb') as f:
                            f.write(response.content)
                        
                        # 压缩
                        compressed_path = self.compressed_dir / f"compressed_{task_id}.jpg"
                        _, orig_size, comp_size = compress_image(
                            str(temp_path),
                            str(compressed_path),
                            quality=self.compression_quality,
                            max_size=1024
                        )
                        
                        # 删除临时文件
                        temp_path.unlink()
                        
                        # 上传压缩后的图片到 TOS（如果需要公网 URL）
                        from image_uploader import quick_upload
                        compressed_url = quick_upload(str(compressed_path))
                        
                        print(f"🗜️  图片已压缩：{orig_size/1024:.1f}KB → {comp_size/1024:.1f}KB")
                        
                        # 使用压缩后的 URL
                        result_urls = [compressed_url]
                        
                    except Exception as e:
                        print(f"⚠️  压缩失败：{e}，使用原始图片")
                        result_urls = image_urls
                else:
                    result_urls = image_urls
                
                # 💾 保存到缓存（如果启用）
                if self.enable_cache and self.cache:
                    try:
                        style_config = self.STYLES.get(style, {})
                        full_prompt = f"{style_config.get('prompt', '')} {style_config.get('negative', '')}"
                        
                        # 如果有压缩文件，使用压缩文件路径
                        cache_path = str(compressed_path) if compressed_path and compressed_path.exists() else image_path
                        
                        self.cache.set(
                            image_path=image_path,
                            style=style,
                            prompt=full_prompt,
                            result_url=result_urls[0],
                            result_path=cache_path if compressed_path and compressed_path.exists() else image_path,
                            metadata={
                                'task_id': task_id,
                                'compressed': compressed_path is not None,
                                'model': 'seed3l_single_ip'
                            }
                        )
                    except Exception as e:
                        print(f"⚠️  缓存保存失败：{e}")
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "image_urls": result_urls,
                    "model": "seed3l_single_ip",
                    "cached": False,
                    "compressed": compressed_path is not None
                }
            elif status == "not_found":
                return {
                    "success": False,
                    "error": "任务未找到",
                    "task_id": task_id
                }
            elif status == "expired":
                return {
                    "success": False,
                    "error": "任务已过期",
                    "task_id": task_id
                }
        
        # 超时
        return {
            "success": False,
            "error": "超时",
            "task_id": task_id
        }
    
    def generate_custom_style(
        self,
        user_photo_path: str,
        reference_photo_path: str,
        wait: bool = True,
        timeout: int = 180
    ) -> dict:
        """
        生成客户指定发型（参考图同款）
        
        Args:
            user_photo_path: 用户照片路径
            reference_photo_path: 参考发型照片路径
            wait: 是否等待完成
            timeout: 超时时间（秒）
        
        Returns:
            生成结果
        """
        if not self.analyzer:
            return {
                "success": False,
                "error": "发型分析器未初始化"
            }
        
        print("\n" + "=" * 80)
        print("🎨 客户指定发型生成")
        print("=" * 80)
        
        # 1. 上传参考图到 TOS
        print("\n📤 上传参考图...")
        ref_url = self.upload_image(reference_photo_path)
        
        # 2. 分析参考图发型
        print("\n🔍 分析参考图发型...")
        analysis = self.analyzer.analyze_hairstyle(ref_url)
        
        if not analysis.get('success'):
            return {
                "success": False,
                "error": f"发型分析失败：{analysis.get('error')}"
            }
        
        print(f"✅ 发型分析完成")
        print(f"   描述：{analysis['description']}")
        
        # 3. 使用分析结果生成
        print("\n💇 开始生成指定发型...")
        
        # 上传用户照片
        user_url = self.upload_image(user_photo_path)
        
        # 调用 API 生成
        try:
            response = self.client.generate_image(
                image_url=user_url,
                prompt=analysis['prompt'],
                wait=wait,
                timeout=timeout
            )
            
            if response.get('success'):
                print("\n✅ 指定发型生成成功！")
                response['analysis'] = analysis['description']
                response['reference_url'] = ref_url
            else:
                print("\n❌ 指定发型生成失败")
            
            return response
            
        except Exception as e:
            print(f"\n❌ 生成失败：{e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": analysis['description']
            }
    
    def generate_batch(self, image_path: str, styles: List[str],
                       delay: float = 2.0) -> List[dict]:
        """批量生成多个发型（异步 API）"""
        results = []
        
        print(f"\n🚀 开始批量生成 {len(styles)} 个发型")
        print(f"🔧 模型：seed3l_single_ip (图生图 - 角色特征保持)")
        print(f"⚙️  延迟：{delay}秒（避免 API 限流）\n")
        
        for i, style in enumerate(styles, 1):
            print(f"\n[{i}/{len(styles)}] 生成：{style}")
            
            # 请求间隔（避免并发限制）
            if i > 1:
                print(f"⏳ 等待 {delay}秒...")
                time.sleep(delay)
            
            result = self.generate(image_path, style, wait=True, timeout=180)
            result["style"] = style
            results.append(result)
        
        # 统计
        success_count = sum(1 for r in results if r["success"])
        print(f"\n📊 完成：{success_count}/{len(styles)} 成功")
        
        return results


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI 发型生成器 - DreamO 图生图 3.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成单个发型
  python hairstyle_generator.py -i photo.jpg -s 短发
  
  # 批量生成
  python hairstyle_generator.py -i photo.jpg --styles 短发 卷发 长发
  
  # 列出发型
  python hairstyle_generator.py --list-styles

模型：DreamO 4.0 (图生图 3.0 - 角色特征保持)
文档：https://www.volcengine.com/docs/86081/1804562
        """
    )
    parser.add_argument("--image", "-i", required=True, help="客户照片路径")
    parser.add_argument("--style", "-s", help="单个发型风格")
    parser.add_argument("--styles", nargs="+", help="多个发型风格（批量）")
    parser.add_argument("--list-styles", action="store_true", help="列出支持的发型")
    parser.add_argument("--no-wait", action="store_true", help="不等待完成（同步 API，此参数无效）")
    
    args = parser.parse_args()
    
    # 获取 API 密钥
    access_key = os.getenv("JIMENG_ACCESS_KEY_ID", "")
    secret_key = os.getenv("JIMENG_SECRET_ACCESS_KEY", "")
    
    if not access_key or not secret_key or "待填写" in access_key:
        print("❌ 错误：请先配置 API 密钥")
        print(f"   编辑：{env_path}")
        print(f"   设置：JIMENG_ACCESS_KEY_ID 和 JIMENG_SECRET_ACCESS_KEY")
        print(f"\n📖 文档：https://www.volcengine.com/docs/86081/1804562")
        sys.exit(1)
    
    # 创建生成器
    generator = HairstyleGenerator(access_key, secret_key)
    
    # 列出风格
    if args.list_styles:
        print("支持的发型风格：")
        for style in generator.STYLES.keys():
            print(f"  - {style}")
        sys.exit(0)
    
    # 检查图片
    if not os.path.exists(args.image):
        print(f"❌ 错误：图片不存在：{args.image}")
        sys.exit(1)
    
    # 单个生成
    if args.style:
        result = generator.generate(
            args.image,
            args.style,
            wait=True  # DreamO 是同步 API
        )
        
        print("\n" + "=" * 60)
        print("生成结果：")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result["success"] and result.get("images"):
            print("\n✅ 生成成功！")
            print(f"   模型：DreamO 4.0")
            print(f"   Request ID: {result.get('request_id', 'N/A')}")
            for img in result["images"]:
                print(f"   URL: {img.get('url', 'N/A')}")
        else:
            print("\n❌ 生成失败")
            print(f"   错误码：{result.get('code', 'N/A')}")
            print(f"   Request ID: {result.get('request_id', 'N/A')}")
    
    # 批量生成
    elif args.styles:
        results = generator.generate_batch(args.image, args.styles)
        
        print("\n" + "=" * 60)
        print("批量生成结果：")
        for r in results:
            status = "✅" if r["success"] else "❌"
            print(f"{status} {r['style']}: {r.get('status', r.get('error', 'unknown'))}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
图片上传工具 - 上传到公网可访问的存储

支持:
- 火山引擎 TOS (推荐，同厂商)
- 阿里云 OSS
- 腾讯云 COS
- 或返回 base64 编码（用于测试）
"""

import os
import uuid
from pathlib import Path
from typing import Optional


class ImageUploader:
    """图片上传器 - 上传到公网存储"""
    
    def __init__(self, storage_type: str = "tos"):
        """
        初始化上传器
        
        Args:
            storage_type: 存储类型 (tos, oss, cos, base64)
        """
        self.storage_type = storage_type
        
        # 从环境变量读取配置
        self.tos_bucket = os.getenv("TOS_BUCKET", "")
        self.tos_ak = os.getenv("TOS_ACCESS_KEY", "")
        self.tos_sk = os.getenv("TOS_SECRET_KEY", "")
        
        self.oss_bucket = os.getenv("OSS_BUCKET", "")
        self.oss_ak = os.getenv("OSS_ACCESS_KEY_ID", "")
        self.oss_sk = os.getenv("OSS_ACCESS_KEY_SECRET", "")
    
    def upload(self, image_path: str) -> str:
        """
        上传图片，返回公网 URL
        
        Args:
            image_path: 本地图片路径
            
        Returns:
            公网可访问的 URL
        """
        if self.storage_type == "base64":
            # 测试模式：返回 base64
            return self._to_base64(image_path)
        
        elif self.storage_type == "tos":
            # 火山引擎 TOS
            return self._upload_to_tos(image_path)
        
        elif self.storage_type == "oss":
            # 阿里云 OSS
            return self._upload_to_oss(image_path)
        
        else:
            raise ValueError(f"不支持的存储类型：{self.storage_type}")
    
    def _to_base64(self, image_path: str) -> str:
        """转换为 base64（测试用）"""
        import base64
        
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        # 即梦 API 支持 base64 格式
        return f"data:image/jpeg;base64,{image_data}"
    
    def _upload_to_tos(self, image_path: str) -> str:
        """上传到火山引擎 TOS"""
        if not self.tos_bucket or not self.tos_ak or not self.tos_sk:
            raise ValueError(
                "TOS 配置缺失，请设置环境变量:\n"
                "  TOS_BUCKET=your-bucket\n"
                "  TOS_ACCESS_KEY=your_ak\n"
                "  TOS_SECRET_KEY=your_sk"
            )
        
        # TODO: 实现 TOS 上传
        # 使用 tos-sdk
        from tos import TosClientV2
        
        filename = f"hairstyle/{uuid.uuid4()}.jpg"
        
        try:
            from tos import TosClientV2
            client = TosClientV2(
                ak=self.tos_ak,
                sk=self.tos_sk,
                region='cn-beijing'
            )
            
            client.put_object_from_file(
                bucket=self.tos_bucket,
                key=filename,
                file_path=image_path
            )
            
            url = f"https://{self.tos_bucket}.tos-cn-beijing.volces.com/{filename}"
            print(f"✅ 已上传到 TOS: {url}")
            return url
            
        except Exception as e:
            print(f"❌ TOS 上传失败：{e}")
            # Fallback 到 base64
            print("⚠️  使用 base64 模式")
            return self._to_base64(image_path)
    
    def _upload_to_oss(self, image_path: str) -> str:
        """上传到阿里云 OSS"""
        if not self.oss_bucket or not self.oss_ak or not self.oss_sk:
            raise ValueError(
                "OSS 配置缺失，请设置环境变量:\n"
                "  OSS_BUCKET=your-bucket\n"
                "  OSS_ACCESS_KEY_ID=your_ak\n"
                "  OSS_ACCESS_KEY_SECRET=your_sk"
            )
        
        # TODO: 实现 OSS 上传
        # 使用 oss2 SDK
        import oss2
        
        filename = f"hairstyle/{uuid.uuid4()}.jpg"
        
        try:
            auth = oss2.Auth(self.oss_ak, self.oss_sk)
            bucket = oss2.Bucket(
                auth,
                f"https://oss-cn-hangzhou.aliyuncs.com",
                self.oss_bucket
            )
            
            bucket.put_object_from_file(filename, image_path)
            
            url = f"https://{self.oss_bucket}.oss-cn-hangzhou.aliyuncs.com/{filename}"
            print(f"✅ 已上传到 OSS: {url}")
            return url
            
        except Exception as e:
            print(f"❌ OSS 上传失败：{e}")
            # Fallback 到 base64
            print("⚠️  使用 base64 模式")
            return self._to_base64(image_path)


def quick_upload(image_path: str) -> str:
    """
    快速上传图片
    
    优先级:
    1. TOS (如果配置了)
    2. OSS (如果配置了)
    3. base64 (默认 fallback)
    
    Args:
        image_path: 本地图片路径
        
    Returns:
        公网 URL 或 base64
    """
    # 检查 TOS 配置
    if os.getenv("TOS_BUCKET") and os.getenv("TOS_ACCESS_KEY"):
        uploader = ImageUploader("tos")
        return uploader.upload(image_path)
    
    # 检查 OSS 配置
    elif os.getenv("OSS_BUCKET") and os.getenv("OSS_ACCESS_KEY_ID"):
        uploader = ImageUploader("oss")
        return uploader.upload(image_path)
    
    # 默认使用 base64
    else:
        print("⚠️  未配置对象存储，使用 base64 模式")
        uploader = ImageUploader("base64")
        return uploader.upload(image_path)


def delete_tos_object(tos_url: str) -> bool:
    """
    删除 TOS 上的对象
    
    Args:
        tos_url: TOS 文件 URL
        
    Returns:
        是否删除成功
    """
    try:
        from tos import TosClientV2
        
        # 提取 object key
        if tos_url.startswith("https://"):
            tos_url = tos_url[8:]
        parts = tos_url.split('/', 1)
        object_key = parts[1] if len(parts) == 2 else tos_url
        
        # 提取 bucket 和 region
        domain_part = tos_url.split('.')[0]
        bucket = domain_part
        
        region = "cn-beijing"  # 默认
        if "tos-cn-beijing" in tos_url:
            region = "cn-beijing"
        
        # 初始化客户端
        client = TosClientV2(
            ak=os.getenv("TOS_ACCESS_KEY"),
            sk=os.getenv("TOS_SECRET_KEY"),
            region=region
        )
        
        # 删除对象
        client.delete_object(bucket=bucket, key=object_key)
        print(f"✅ TOS 删除成功：{object_key}")
        return True
        
    except Exception as e:
        print(f"❌ TOS 删除失败：{e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python image_uploader.py <图片路径>")
        print("示例：python image_uploader.py photo.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"❌ 文件不存在：{image_path}")
        sys.exit(1)
    
    print(f"📤 上传图片：{image_path}")
    url = quick_upload(image_path)
    
    if url.startswith("data:"):
        print(f"✅ Base64 编码完成（长度：{len(url)}）")
        print(f"   可直接用于即梦 API")
    else:
        print(f"✅ 上传成功！")
        print(f"   URL: {url}")

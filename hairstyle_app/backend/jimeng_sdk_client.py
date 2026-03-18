#!/usr/bin/env python3
"""
火山引擎即梦 API 客户端 - 使用官方 SDK
"""
from volcengine.visual.VisualService import VisualService
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


class JimengSDKClient:
    """使用官方 SDK 的即梦客户端"""
    
    def __init__(self, ak: str, sk: str):
        self.ak = ak
        self.sk = sk
        self.visual_service = VisualService()
        self.visual_service.set_ak(ak)
        self.visual_service.set_sk(sk)
    
    def generate_image(self, prompt: str, image_url: str = None) -> dict:
        """
        生成图片
        
        Args:
            prompt: 提示词
            image_url: 参考图片 URL（可选）
            
        Returns:
            生成结果
        """
        try:
            # 构建请求参数 - 火山引擎格式
            params = {
                "req_key": "ai_inference",  # 必需参数
                "model_version": "general_v2.1",
                "prompt": prompt,
                "width": 1024,
                "height": 1024,
                "sample_steps": 25,
                "seed": -1,  # 随机种子
            }
            
            # 图生图模式
            if image_url:
                params["image_url"] = image_url
                params["strength"] = 0.6  # 保持原图程度
            
            # 调用 API
            result = self.visual_service.cv_process(params)
            
            return {
                "success": True,
                "data": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_task_result(self, task_id: str) -> dict:
        """
        获取任务结果（异步任务）
        
        Args:
            task_id: 任务 ID
            
        Returns:
            任务结果
        """
        try:
            params = {"task_id": task_id}
            result = self.visual_service.get_task_result(params)
            
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# 测试
if __name__ == "__main__":
    ak = os.getenv("JIMENG_ACCESS_KEY_ID", "")
    sk = os.getenv("JIMENG_SECRET_ACCESS_KEY", "")
    
    print(f"AK: {ak[:20]}...")
    print(f"SK: {sk[:20]}...")
    print()
    
    client = JimengSDKClient(ak, sk)
    
    # 测试文生图
    print("测试文生图...")
    result = client.generate_image("一个穿着汉服的女孩，古风，高清")
    
    if result["success"]:
        print(f"✅ 成功！")
        print(f"数据：{result['data']}")
    else:
        print(f"❌ 失败：{result['error']}")

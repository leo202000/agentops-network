#!/usr/bin/env python3
"""
发型生成器 V2 - 使用 OpenAI SDK 调用即梦 API
"""

import os
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


class HairstyleGeneratorV2:
    """发型生成器 V2 - 基于 OpenAI SDK"""
    
    # 发型库（20 种）
    HAIRSTYLES = {
        # 基础发型（15 种）
        "短发": "short pixie cut, modern and edgy, low maintenance, chic and stylish",
        "卷发": "curly hairstyle, bouncy curls, voluminous and lively, romantic and feminine",
        "长发": "long flowing hair, elegant and graceful, classic beauty, smooth and shiny",
        "直发": "straight sleek hair, smooth and shiny, modern and clean, minimalist elegance",
        "马尾": "high ponytail, sporty and energetic, clean and neat, practical and stylish",
        "辫子": "braided hairstyle, intricate braids, bohemian style, romantic and artistic",
        "波浪卷": "wavy hairstyle, soft waves, beach waves, relaxed and natural",
        "大波浪": "big wavy hairstyle, glamorous waves, red carpet style, voluminous and dramatic",
        "中分": "middle part hairstyle, symmetrical and balanced, modern and sleek",
        "斜刘海": "side swept bangs, asymmetrical style, soft and flattering",
        "染发红": "red dyed hair, vibrant and bold, eye-catching color, passionate",
        "染现金": "blonde dyed hair, bright and sunny, glamorous and fashionable",
        "染发棕": "brown dyed hair, natural and warm, versatile color, elegant",
        "及腰长发": "waist length hair, extremely long, elegant and graceful, stunning",
        "羊毛卷": "woolly curly hair, tight curls, afro style, voluminous and textured",
        # 新增发型（5 种）⭐
        "齐肩发": "shoulder length bob hairstyle, classic and timeless, neat ends, versatile",
        "梨花头": "pear blossom hairstyle, soft inward curls at ends, korean style, gentle",
        "外翘发型": "outward flipped ends hairstyle, playful and cute, flirty style",
        "丸子头": "high bun hairstyle, neat and tidy, elegant updo, summer style",
        "空气刘海": "air bangs hairstyle, wispy and light bangs, korean style, youthful",
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化生成器
        
        Args:
            api_key: 火山引擎 API Key，如果不传则从环境变量读取
        """
        self.api_key = api_key or os.environ.get("ARK_API_KEY")
        
        if not self.api_key:
            raise ValueError("请提供 API Key 或设置 ARK_API_KEY 环境变量")
        
        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=self.api_key,
        )
        
        print(f"✅ 发型生成器 V2 初始化完成")
        print(f"   支持发型：{len(self.HAIRSTYLES)} 种")
        print(f"   模型：doubao-seedream-4-5-251128")
    
    def generate(self, image_url: str, style: str, wait: bool = True) -> Dict[str, Any]:
        """
        生成发型
        
        Args:
            image_url: 用户照片 URL（公网可访问）
            style: 发型风格名称
            wait: 是否等待完成（当前 API 是同步的）
            
        Returns:
            生成结果字典
        """
        # 检查发型是否存在
        if style not in self.HAIRSTYLES:
            available = ", ".join(self.HAIRSTYLES.keys())
            return {
                "success": False,
                "error": f"不支持的发型：{style}",
                "available_styles": available
            }
        
        # 构建提示词
        style_prompt = self.HAIRSTYLES[style]
        prompt = f"保持人物脸部完全一致，只改变发型为{style}，{style_prompt}, realistic photo, high quality, professional photography, natural lighting"
        
        print(f"\n🎨 生成发型：{style}")
        print(f"📝 提示词：{prompt[:80]}...")
        print(f"🌐 图片：{image_url[:60]}...")
        
        try:
            # 调用即梦 API
            print(f"\n⏳ 正在生成...")
            
            response = self.client.images.generate(
                model="doubao-seedream-4-5-251128",
                prompt=prompt,
                size="2K",
                response_format="url",
                extra_body={
                    "image": image_url,
                    "watermark": False,
                }
            )
            
            result_url = response.data[0].url
            
            print(f"\n✅ 生成成功!")
            print(f"   结果 URL: {result_url}")
            
            return {
                "success": True,
                "image_url": result_url,
                "style": style,
                "prompt": prompt
            }
            
        except Exception as e:
            print(f"\n❌ 生成失败：{e}")
            return {
                "success": False,
                "error": str(e),
                "style": style
            }
    
    def generate_batch(self, image_url: str, styles: List[str], interval: int = 2) -> List[Dict[str, Any]]:
        """
        批量生成发型
        
        Args:
            image_url: 用户照片 URL
            styles: 发型风格列表
            interval: 请求间隔（秒），避免 API 限流
            
        Returns:
            生成结果列表
        """
        results = []
        
        for i, style in enumerate(styles):
            if i > 0:
                print(f"\n⏳ 等待 {interval} 秒...")
                time.sleep(interval)
            
            result = self.generate(image_url, style)
            results.append(result)
        
        return results
    
    def list_styles(self) -> List[str]:
        """返回所有支持的发型"""
        return list(self.HAIRSTYLES.keys())


# 测试
if __name__ == "__main__":
    # 使用官方示例图片测试
    test_image_url = "https://ark-project.tos-cn-beijing.volces.com/doc_image/seedream4_imageToimage.png"
    
    generator = HairstyleGeneratorV2()
    
    print(f"\n{'='*70}")
    print("测试发型：齐肩发")
    print(f"{'='*70}\n")
    
    result = generator.generate(test_image_url, "齐肩发")
    
    print(f"\n{'='*70}")
    print(f"测试结果：{result['success']}")
    if result.get('image_url'):
        print(f"结果 URL: {result['image_url']}")
    print(f"{'='*70}\n")

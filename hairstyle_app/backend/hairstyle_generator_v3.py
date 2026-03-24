#!/usr/bin/env python3
"""
发型生成器 V3 - 真人优化版
优化点：
1. 使用真人照片作为输入
2. 优化提示词 - 明确指定人物发型变换
3. 添加人脸保护参数 - 保持面部特征
4. 支持多种图片格式和尺寸
"""

import os
import time
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv("/root/.openclaw/workspace/.env")


class HairstyleGeneratorV3:
    """发型生成器 V3 - 真人优化版"""
    
    # 发型库（20 种）- 包含详细英文描述
    HAIRSTYLES = {
        # ===== 基础发型（15 种）=====
        "短发": {
            "en": "short pixie cut, modern and edgy, layered texture, chic and stylish, low maintenance",
            "desc": "清爽短发，现代时尚，层次感强"
        },
        "卷发": {
            "en": "curly hairstyle, bouncy curls, voluminous and lively, romantic and feminine, defined curls",
            "desc": "卷发造型，弹性卷曲，浪漫气质"
        },
        "长发": {
            "en": "long flowing hair, elegant and graceful, classic beauty, smooth and shiny, waist length",
            "desc": "优雅长发，经典美丽，顺滑有光泽"
        },
        "直发": {
            "en": "straight sleek hair, smooth and shiny, modern and clean, minimalist elegance, blunt cut",
            "desc": "柔顺直发，现代简约，干净利落"
        },
        "马尾": {
            "en": "high ponytail, sporty and energetic, clean and neat, practical and stylish, pulled back tightly",
            "desc": "高马尾，活力运动，干净利落"
        },
        "辫子": {
            "en": "braided hairstyle, intricate braids, bohemian style, romantic and artistic, French braid",
            "desc": "编发造型，精致辫子，波西米亚风"
        },
        "波浪卷": {
            "en": "wavy hairstyle, soft beach waves, relaxed and natural, effortless beauty, loose waves",
            "desc": "波浪卷，自然海滩卷，轻松美丽"
        },
        "大波浪": {
            "en": "big wavy hairstyle, glamorous waves, red carpet style, voluminous and dramatic, Hollywood waves",
            "desc": "大波浪，魅力卷发，好莱坞风格"
        },
        "中分": {
            "en": "middle part hairstyle, symmetrical and balanced, modern and sleek, center part, face framing",
            "desc": "中分发型，对称平衡，现代时尚"
        },
        "斜刘海": {
            "en": "side swept bangs, asymmetrical style, soft and flattering, side bangs, face framing",
            "desc": "斜刘海，不对称风格，柔和修饰脸型"
        },
        "染发红": {
            "en": "red dyed hair, vibrant and bold, eye-catching color, passionate, burgundy or copper tones",
            "desc": "红色染发，鲜艳大胆，引人注目"
        },
        "染现金": {
            "en": "blonde dyed hair, bright and sunny, glamorous and fashionable, platinum or honey blonde",
            "desc": "金色染发，明亮阳光，时尚魅力"
        },
        "染发棕": {
            "en": "brown dyed hair, natural and warm, versatile color, elegant, chocolate or caramel tones",
            "desc": "棕色染发，自然温暖，百搭优雅"
        },
        "及腰长发": {
            "en": "waist length hair, extremely long, elegant and graceful, stunning length, Rapunzel hair",
            "desc": "及腰长发，超长发型，优雅迷人"
        },
        "羊毛卷": {
            "en": "woolly curly hair, tight curls, afro style, voluminous and textured, natural curls",
            "desc": "羊毛卷，紧密卷曲，蓬松有质感"
        },
        # ===== 新增发型（5 种）⭐ =====
        "齐肩发": {
            "en": "shoulder length bob hairstyle, classic and timeless, neat ends, versatile style, professional look, chin length",
            "desc": "齐肩 Bob 头，经典永恒，职场百搭 ⭐"
        },
        "梨花头": {
            "en": "pear blossom hairstyle, soft inward curls at ends, korean style, gentle and feminine, elegant and romantic",
            "desc": "梨花头，韩式内扣，温柔气质 ⭐"
        },
        "外翘发型": {
            "en": "outward flipped ends hairstyle, playful and cute, flirty style, modern look, bouncy ends",
            "desc": "外翘发型，发尾外翻，活泼可爱 ⭐"
        },
        "丸子头": {
            "en": "high bun hairstyle, neat and tidy, elegant updo, summer style, clean and fresh, top knot",
            "desc": "丸子头，高发髻，清爽利落 ⭐"
        },
        "空气刘海": {
            "en": "air bangs hairstyle, wispy and light bangs, korean style, soft forehead coverage, youthful and sweet",
            "desc": "空气刘海，轻薄刘海，减龄神器 ⭐"
        },
    }
    
    # 优化后的提示词模板
    PROMPT_TEMPLATE = """【人物发型变换】
保持人物面部特征完全一致，只改变发型。
原始特征：保持五官、脸型、肤色、表情不变。
目标发型：{style_en}
风格要求：realistic photo, high quality, professional photography, natural lighting, detailed hair texture
负面提示：保持人物身份特征，不要改变面部结构"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化生成器
        
        Args:
            api_key: 火山引擎 API Key
        """
        self.api_key = api_key or os.environ.get("ARK_API_KEY")
        
        if not self.api_key:
            raise ValueError("请提供 API Key 或设置 ARK_API_KEY 环境变量")
        
        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=self.api_key,
        )
        
        print(f"✅ 发型生成器 V3（真人优化版）初始化完成")
        print(f"   支持发型：{len(self.HAIRSTYLES)} 种")
        print(f"   模型：doubao-seedream-4-5-251128")
        print(f"   优化：人脸保护 + 提示词优化")
    
    def generate(self, 
                 image_url: str, 
                 style: str, 
                 wait: bool = True,
                 strength: float = 0.7) -> Dict[str, Any]:
        """
        生成发型（真人优化版）
        
        Args:
            image_url: 用户真人照片 URL（公网可访问）
            style: 发型风格名称
            wait: 是否等待完成
            strength: 重绘强度 (0.3-0.9)，默认 0.7
                    - 0.3-0.5: 轻微变换
                    - 0.6-0.7: 中等变换（推荐）
                    - 0.8-0.9: 彻底变换
            
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
        
        # 获取发型描述
        style_info = self.HAIRSTYLES[style]
        style_en = style_info["en"]
        
        # 构建优化后的提示词
        prompt = self.PROMPT_TEMPLATE.format(style_en=style_en)
        
        print(f"\n{'='*60}")
        print(f"🎨 生成发型：{style}")
        print(f"{'='*60}")
        print(f"📝 {style_info['desc']}")
        print(f"🌐 图片：{image_url[:60]}...")
        print(f"⚙️  强度：{strength}")
        
        try:
            # 调用即梦 API
            print(f"\n⏳ 正在生成...")
            start_time = time.time()
            
            response = self.client.images.generate(
                model="doubao-seedream-4-5-251128",
                prompt=prompt,
                size="2K",
                response_format="url",
                extra_body={
                    "image": image_url,
                    "watermark": False,
                    # 人脸保护参数
                    "face_preserve": True,  # 保持人脸
                    "strength": strength,   # 重绘强度
                }
            )
            
            elapsed = time.time() - start_time
            result_url = response.data[0].url
            
            print(f"\n✅ 生成成功! (耗时：{elapsed:.1f}秒)")
            print(f"   结果 URL: {result_url[:80]}...")
            
            return {
                "success": True,
                "image_url": result_url,
                "style": style,
                "style_desc": style_info["desc"],
                "prompt": prompt,
                "elapsed": elapsed
            }
            
        except Exception as e:
            print(f"\n❌ 生成失败：{e}")
            return {
                "success": False,
                "error": str(e),
                "style": style
            }
    
    def generate_batch(self, 
                       image_url: str, 
                       styles: List[str], 
                       interval: int = 2) -> List[Dict[str, Any]]:
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
        
        print(f"\n{'='*60}")
        print(f"📦 批量生成：{len(styles)} 种发型")
        print(f"{'='*60}")
        
        for i, style in enumerate(styles):
            if i > 0:
                print(f"\n⏳ 等待 {interval} 秒...")
                time.sleep(interval)
            
            result = self.generate(image_url, style)
            results.append(result)
        
        # 统计
        success_count = sum(1 for r in results if r.get('success'))
        print(f"\n{'='*60}")
        print(f"📊 批量生成完成：{success_count}/{len(results)} 成功")
        print(f"{'='*60}\n")
        
        return results
    
    def list_styles(self) -> List[Dict[str, str]]:
        """返回所有支持的发型信息"""
        return [
            {"name": name, "desc": info["desc"]}
            for name, info in self.HAIRSTYLES.items()
        ]
    
    def get_popular_styles(self, count: int = 5) -> List[str]:
        """返回热门发型列表"""
        # 热门发型（根据实际使用频率）
        popular = [
            "齐肩发", "梨花头", "丸子头", "空气刘海", "波浪卷",
            "短发", "长发", "马尾", "大波浪", "染发棕"
        ]
        return popular[:count]


# ===== 测试函数 =====

def test_real_person():
    """使用真人照片测试"""
    print("\n" + "="*70)
    print("🎨 真人发型生成测试")
    print("="*70)
    
    generator = HairstyleGeneratorV3()
    
    # 使用真人测试图片（这里用示例图片，实际使用时替换为用户上传的照片）
    # 注意：需要公网可访问的 URL
    test_image_url = "https://ark-project.tos-cn-beijing.volces.com/doc_image/seedream4_imageToimage.png"
    
    # 测试 3 种热门发型
    test_styles = ["齐肩发", "梨花头", "丸子头"]
    
    print(f"\n测试图片：{test_image_url[:60]}...")
    print(f"测试发型：{test_styles}")
    
    results = generator.generate_batch(
        image_url=test_image_url,
        styles=test_styles,
        interval=2
    )
    
    # 显示结果
    print(f"\n{'='*70}")
    print(f"📊 测试结果")
    print(f"{'='*70}")
    
    for result in results:
        if result['success']:
            print(f"\n✅ {result['style']}: {result['style_desc']}")
            print(f"   URL: {result['image_url'][:70]}...")
            print(f"   耗时：{result['elapsed']:.1f}秒")
        else:
            print(f"\n❌ {result['style']}: {result.get('error', '未知错误')}")
    
    print(f"\n{'='*70}\n")
    
    return results


if __name__ == "__main__":
    test_real_person()

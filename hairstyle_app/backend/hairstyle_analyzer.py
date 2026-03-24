#!/usr/bin/env python3
"""
发型分析器 - 从参考图提取发型特征

功能:
- 分析客户提供的发型参考图
- 提取发型特征（长度/卷度/刘海/发色等）
- 生成 AI 绘画提示词
- 支持指定发型生成

使用示例:
    from hairstyle_analyzer import HairstyleAnalyzer
    
    analyzer = HairstyleAnalyzer(api_key)
    result = analyzer.analyze_hairstyle(reference_image_url)
    print(f"发型描述：{result['description']}")
    print(f"生成提示词：{result['prompt']}")
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from openai import OpenAI


class HairstyleAnalyzer:
    """发型分析器 - 基于视觉 AI"""
    
    def __init__(self, api_key: str):
        """
        初始化分析器
        
        Args:
            api_key: 火山引擎 API Key
        """
        self.api_key = api_key
        self.client = OpenAI(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=api_key
        )
        # 使用视觉分析模型
        self.vision_model = "doubao-vision-pro-32k"
        # 使用生成模型
        self.generation_model = "doubao-seedream-4-5-251128"
        
        print(f"🎨 发型分析器初始化完成")
        print(f"   视觉模型：{self.vision_model}")
        print(f"   生成模型：{self.generation_model}")
    
    def analyze_hairstyle(self, reference_image_url: str) -> Dict[str, Any]:
        """
        分析参考图的发型特征
        
        Args:
            reference_image_url: 参考图 URL（TOS 或公网）
        
        Returns:
            分析结果字典
        """
        try:
            print(f"\n🔍 分析发型参考图...")
            print(f"   参考图：{reference_image_url[:60]}...")
            
            # 调用视觉模型分析
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """请详细分析这张图片中的发型特征，按以下维度描述：

1. 长度：短发/齐肩/中长发/长发/及腰长发
2. 卷度：直发/微卷/波浪卷/大波浪/羊毛卷/蛋卷头
3. 刘海：无刘海/空气刘海/斜刘海/齐刘海/法式刘海
4. 发色：黑色/棕色/金色/红色/灰色/其他（具体描述）
5. 造型：披发/马尾/丸子头/编发/其他
6. 层次：齐发/层次/碎发
7. 其他特征：如外翘/内扣/蓬松/贴头等

请用中文简洁描述，100 字以内，突出主要特征。"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": reference_image_url}
                        }
                    ]
                }]
            )
            
            description = response.choices[0].message.content
            
            print(f"✅ 分析完成")
            print(f"   发型描述：{description}")
            
            # 生成提示词
            prompt = self._generate_prompt(description)
            
            # 提取关键词
            keywords = self._extract_keywords(description)
            
            return {
                'success': True,
                'description': description,
                'prompt': prompt,
                'keywords': keywords,
                'reference_url': reference_image_url
            }
            
        except Exception as e:
            print(f"❌ 分析失败：{e}")
            return {
                'success': False,
                'error': str(e),
                'description': '',
                'prompt': ''
            }
    
    def _generate_prompt(self, description: str) -> str:
        """
        根据描述生成 AI 绘画提示词
        
        Args:
            description: 发型描述
        
        Returns:
            AI 绘画提示词
        """
        # 基础模板
        base_prompt = "保持人物脸部完全一致，只改变发型为"
        
        # 质量词
        quality_tags = "realistic photo, high quality, professional photography, natural lighting, 8k, detailed hair texture"
        
        # 生成完整提示词
        prompt = f"{base_prompt}{description}, {quality_tags}"
        
        print(f"📝 生成提示词：{prompt[:80]}...")
        
        return prompt
    
    def _extract_keywords(self, description: str) -> Dict[str, str]:
        """
        提取发型关键词
        
        Args:
            description: 发型描述
        
        Returns:
            关键词字典
        """
        keywords = {
            'length': '',      # 长度
            'curl': '',        # 卷度
            'bangs': '',       # 刘海
            'color': '',       # 发色
            'style': '',       # 造型
            'texture': ''      # 质感
        }
        
        # 简单关键词匹配
        length_keywords = ['短发', '齐肩', '中长发', '长发', '及腰']
        curl_keywords = ['直发', '微卷', '波浪卷', '大波浪', '羊毛卷', '蛋卷头']
        bangs_keywords = ['无刘海', '空气刘海', '斜刘海', '齐刘海', '法式刘海']
        style_keywords = ['披发', '马尾', '丸子头', '编发']
        
        for kw in length_keywords:
            if kw in description:
                keywords['length'] = kw
                break
        
        for kw in curl_keywords:
            if kw in description:
                keywords['curl'] = kw
                break
        
        for kw in bangs_keywords:
            if kw in description:
                keywords['bangs'] = kw
                break
        
        for kw in style_keywords:
            if kw in description:
                keywords['style'] = kw
                break
        
        # 发色提取
        color_keywords = ['黑色', '棕色', '金色', '红色', '灰色', '蓝色', '粉色']
        for kw in color_keywords:
            if kw in description:
                keywords['color'] = kw
                break
        
        print(f"🏷️  提取关键词：{keywords}")
        
        return keywords
    
    def analyze_and_save(self, reference_image_path: str, save_dir: str = "./analyzed_hairstyles") -> Dict[str, Any]:
        """
        分析并保存结果
        
        Args:
            reference_image_path: 参考图本地路径
            save_dir: 保存目录
        
        Returns:
            分析结果
        """
        # 上传参考图到 TOS
        from image_uploader import quick_upload
        
        if not Path(reference_image_path).exists():
            return {'success': False, 'error': '文件不存在'}
        
        # 上传
        ref_url = quick_upload(reference_image_path)
        
        # 分析
        result = self.analyze_hairstyle(ref_url)
        
        if result['success']:
            # 保存分析结果
            save_dir = Path(save_dir)
            save_dir.mkdir(exist_ok=True)
            
            result_file = save_dir / f"analysis_{Path(reference_image_path).stem}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"💾 分析结果已保存：{result_file}")
        
        return result


# 便捷函数
def quick_analyze(reference_image_url: str, api_key: str = None) -> Dict[str, Any]:
    """快速分析发型"""
    if not api_key:
        api_key = os.getenv('ARK_API_KEY')
    
    analyzer = HairstyleAnalyzer(api_key)
    return analyzer.analyze_hairstyle(reference_image_url)


# 命令行工具
if __name__ == "__main__":
    import sys
    
    # 加载环境变量
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding='utf-8') as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
    
    if len(sys.argv) < 2:
        print("用法：python hairstyle_analyzer.py <参考图路径或 URL>")
        print("示例：python hairstyle_analyzer.py reference.jpg")
        print("      python hairstyle_analyzer.py https://example.com/photo.jpg")
        sys.exit(1)
    
    reference = sys.argv[1]
    
    analyzer = HairstyleAnalyzer(os.getenv('ARK_API_KEY'))
    
    if reference.startswith('http'):
        # URL 直接分析
        result = analyzer.analyze_hairstyle(reference)
    else:
        # 本地文件上传后分析
        result = analyzer.analyze_and_save(reference)
    
    if result.get('success'):
        print("\n" + "=" * 80)
        print("✅ 发型分析完成")
        print("=" * 80)
        print(f"描述：{result['description']}")
        print(f"\n提示词：{result['prompt']}")
        print(f"\n关键词：{result['keywords']}")
        print("=" * 80)
    else:
        print(f"\n❌ 分析失败：{result.get('error')}")

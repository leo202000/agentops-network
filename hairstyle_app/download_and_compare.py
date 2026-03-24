#!/usr/bin/env python3
"""
批量下载 TOS 发型生成结果
并制作对比图（原图 + 生成图拼接）
"""

import os
import requests
from pathlib import Path
from PIL import Image

# TOS 配置
TOS_BUCKET = 'hairfashon'
TOS_REGION = 'cn-beijing'

# 下载目录
DOWNLOAD_DIR = Path('/root/.openclaw/workspace/hairstyle_app/content_materials/downloaded')
COMPARISON_DIR = Path('/root/.openclaw/workspace/hairstyle_app/content_materials/comparisons')
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
COMPARISON_DIR.mkdir(parents=True, exist_ok=True)

# 模特照片
MODEL_PHOTOS = {
    'model1': '/root/.openclaw/media/inbound/file_60---00de3a22-c475-411b-81eb-1dfea9f831de.jpg',
    'model2': '/root/.openclaw/media/inbound/file_61---f44ca44d-4b81-43dc-8498-40c22a4f517e.jpg',
}

# 发型结果（从 TOS 获取）
HAIRSTYLE_RESULTS = [
    # 模特 2 的结果
    {'name': 'model2_short', 'url': 'https://hairfashon.tos-cn-beijing.volces.com/hairstyle/results/1774164088_result.jpg', 'style': '短发'},
    {'name': 'model2_wavy', 'url': 'https://hairfashon.tos-cn-beijing.volces.com/hairstyle/results/1774164261_result.jpg', 'style': '大波浪'},
    {'name': 'model2_curly', 'url': 'https://hairfashon.tos-cn-beijing.volces.com/hairstyle/results/1774164390_result.jpg', 'style': '羊毛卷'},
    {'name': 'model2_bangs', 'url': 'https://hairfashon.tos-cn-beijing.volces.com/hairstyle/results/1774165733_file_61---f44ca44d-4b81-43dc-8498-40c22a4f517e_result.jpg', 'style': '空气刘海'},
    {'name': 'model2_ponytail', 'url': 'https://hairfashon.tos-cn-beijing.volces.com/hairstyle/results/1774165776_file_61---f44ca44d-4b81-43dc-8498-40c22a4f517e_result.jpg', 'style': '高马尾'},
]

def download_image(url, save_path):
    """下载图片"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        print(f'✅ 下载：{save_path.name}')
        return True
    except Exception as e:
        print(f'❌ 下载失败 {save_path.name}: {e}')
        return False

def create_comparison(original_path, result_path, output_path, style_name):
    """创建对比图（左右拼接）"""
    try:
        # 打开图片
        original = Image.open(original_path)
        result = Image.open(result_path)
        
        # 统一尺寸（取较小的高度）
        min_height = min(original.height, result.height)
        aspect_ratio_orig = original.width / original.height
        aspect_ratio_result = result.width / result.height
        
        # 调整尺寸
        new_width = int(min_height * aspect_ratio_orig)
        original = original.resize((new_width, min_height), Image.Resampling.LANCZOS)
        
        new_width = int(min_height * aspect_ratio_result)
        result = result.resize((new_width, min_height), Image.Resampling.LANCZOS)
        
        # 创建拼接图
        total_width = original.width + result.width + 50  # 50px 间隔
        comparison = Image.new('RGB', (total_width, min_height), 'white')
        
        # 粘贴图片
        comparison.paste(original, (0, 0))
        comparison.paste(result, (original.width + 50, 0))
        
        # 添加文字标签（可选）
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(comparison)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # 左标签
        draw.text((10, 10), "原图", fill='black', font=font)
        # 右标签
        draw.text((original.width + 60, 10), f"{style_name}", fill='black', font=font)
        
        # 保存
        comparison.save(output_path, quality=95)
        print(f'✅ 对比图：{output_path.name}')
        
        return True
    except Exception as e:
        print(f'❌ 创建对比图失败 {output_path.name}: {e}')
        return False

def main():
    print('=' * 80)
    print('批量下载并制作对比图')
    print('=' * 80)
    
    # 1. 下载结果图片
    print('\n【1】下载发型结果图片...')
    downloaded = {}
    
    for item in HAIRSTYLE_RESULTS:
        save_path = DOWNLOAD_DIR / f"{item['name']}.jpg"
        if download_image(item['url'], save_path):
            downloaded[item['name']] = str(save_path)
    
    # 2. 创建对比图
    print('\n【2】创建对比图...')
    
    # 使用模特 2 的照片
    model2_original = MODEL_PHOTOS['model2']
    
    for item in HAIRSTYLE_RESULTS:
        if item['name'] not in downloaded:
            continue
        
        result_path = downloaded[item['name']]
        output_path = COMPARISON_DIR / f"comparison_{item['name']}.jpg"
        
        create_comparison(
            model2_original,
            result_path,
            output_path,
            item['style']
        )
    
    print('\n' + '=' * 80)
    print('完成！')
    print(f'下载目录：{DOWNLOAD_DIR}')
    print(f'对比图目录：{COMPARISON_DIR}')
    print('=' * 80)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
制作发型对比图（原图 + 生成图左右拼接）
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# 目录
ORIGINAL_DIR = Path('/root/.openclaw/media/inbound')
RESULT_DIR = Path('/root/.openclaw/workspace/hairstyle_app/content_materials/downloaded')
OUTPUT_DIR = Path('/root/.openclaw/workspace/hairstyle_app/content_materials/comparisons')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 模特原图
ORIGINALS = {
    'model1': '/root/.openclaw/media/inbound/file_60---00de3a22-c475-411b-81eb-1dfea9f831de.jpg',
    'model2': '/root/.openclaw/media/inbound/file_61---f44ca44d-4b81-43dc-8498-40c22a4f517e.jpg',
}

# 生成结果
RESULTS = {
    'model2': [
        ('short', '短发', 'model2_short.jpg'),
        ('wavy', '大波浪', 'model2_wavy.jpg'),
        ('curly', '羊毛卷', 'model2_curly.jpg'),
        ('ponytail', '高马尾', 'model2_ponytail.jpg'),
    ],
    'model1': [
        ('short', '短发', 'model1_short.jpg'),
        ('wavy', '大波浪', 'model1_wavy.jpg'),
    ]
}

def create_comparison(original_path, result_path, output_path, style_name):
    """创建对比图"""
    try:
        # 打开图片
        original = Image.open(original_path)
        result = Image.open(result_path)
        
        # 统一高度
        target_height = 800
        orig_ratio = original.width / original.height
        result_ratio = result.width / result.height
        
        new_orig_width = int(target_height * orig_ratio)
        new_result_width = int(target_height * result_ratio)
        
        original = original.resize((new_orig_width, target_height), Image.Resampling.LANCZOS)
        result = result.resize((new_result_width, target_height), Image.Resampling.LANCZOS)
        
        # 创建拼接图
        gap = 30
        total_width = new_orig_width + new_result_width + gap
        comparison = Image.new('RGB', (total_width, target_height), 'white')
        
        comparison.paste(original, (0, 0))
        comparison.paste(result, (new_orig_width + gap, 0))
        
        # 添加文字
        draw = ImageDraw.Draw(comparison)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 36)
        except:
            font = ImageFont.load_default()
        
        # 左标签
        draw.text((20, 20), "原图", fill='black', font=font)
        # 右标签
        draw.text((new_orig_width + gap + 20, 20), f"{style_name}", fill='black', font=font)
        
        # 保存
        comparison.save(output_path, quality=95, optimize=True)
        print(f'✅ {output_path.name}')
        return True
        
    except Exception as e:
        print(f'❌ {output_path.name}: {e}')
        return False

print('=' * 80)
print('制作发型对比图')
print('=' * 80)

# 模特 2
print('\n【模特 2】')
for style_key, style_name, result_file in RESULTS['model2']:
    result_path = RESULT_DIR / result_file
    if not result_path.exists():
        print(f'⏳ {style_name}: 结果图未下载')
        continue
    
    output_path = OUTPUT_DIR / f"comparison_model2_{style_key}.jpg"
    create_comparison(ORIGINALS['model2'], result_path, output_path, style_name)

# 模特 1
print('\n【模特 1】')
for style_key, style_name, result_file in RESULTS['model1']:
    result_path = RESULT_DIR / result_file
    if not result_path.exists():
        print(f'⏳ {style_name}: 结果图未下载')
        continue
    
    output_path = OUTPUT_DIR / f"comparison_model1_{style_key}.jpg"
    create_comparison(ORIGINALS['model1'], result_path, output_path, style_name)

print('\n' + '=' * 80)
print('完成！')
print(f'输出目录：{OUTPUT_DIR}')
print('=' * 80)

# 列出文件
print('\n📁 对比图列表:')
for f in sorted(OUTPUT_DIR.glob('*.jpg')):
    size = f.stat().st_size / 1024
    print(f'  {f.name} ({size:.1f} KB)')

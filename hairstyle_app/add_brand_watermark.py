#!/usr/bin/env python3
"""
给对比图添加品牌水印
品牌：智颜社 AI Beauty Lab
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# 目录
INPUT_DIR = Path('/root/.openclaw/workspace/hairstyle_app/content_materials/comparisons')
OUTPUT_DIR = Path('/root/.openclaw/workspace/hairstyle_app/content_materials/branded')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 品牌信息
BRAND_NAME = "智颜社"
BRAND_EN = "AI Beauty Lab"
SLOGAN = "用 AI，遇见更美的自己"

def add_watermark(image_path, output_path):
    """添加品牌水印"""
    try:
        # 打开图片
        img = Image.open(image_path)
        width, height = img.size
        
        # 创建绘图对象
        draw = ImageDraw.Draw(img)
        
        # 尝试加载字体
        try:
            font_cn = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 28)
            font_en = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font_cn = ImageFont.load_default()
            font_en = ImageFont.load_default()
        
        # 水印文字
        text1 = f"  {BRAND_NAME}  "
        text2 = f"  {BRAND_EN}  "
        
        # 计算文字位置（右下角）
        margin = 15
        text1_bbox = draw.textbbox((0, 0), text1, font=font_cn)
        text1_width = text1_bbox[2] - text1_bbox[0]
        text2_bbox = draw.textbbox((0, 0), text2, font=font_en)
        text2_width = text2_bbox[2] - text2_bbox[0]
        
        # 背景框
        bg_width = max(text1_width, text2_width) + 20
        bg_height = 70
        bg_x = width - bg_width - margin
        bg_y = height - bg_height - margin
        
        # 绘制半透明背景
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(
            [bg_x, bg_y, bg_x + bg_width, bg_y + bg_height],
            fill=(255, 255, 255, 200)  # 白色半透明
        )
        
        # 合并图层
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        draw = ImageDraw.Draw(img)
        
        # 绘制文字
        draw.text(
            (bg_x + 10, bg_y + 10),
            text1,
            fill='#FF6B81',  # 粉色
            font=font_cn
        )
        draw.text(
            (bg_x + 10, bg_y + 40),
            text2,
            fill='#333333',  # 深灰
            font=font_en
        )
        
        # 保存（转回 RGB）
        img.convert('RGB').save(output_path, quality=95, optimize=True)
        print(f'✅ {output_path.name}')
        return True
        
    except Exception as e:
        print(f'❌ {output_path.name}: {e}')
        return False

print('=' * 80)
print(f'添加品牌水印 - {BRAND_NAME}')
print('=' * 80)
print(f'输出目录：{OUTPUT_DIR}\n')

# 处理所有对比图
count = 0
for img_path in sorted(INPUT_DIR.glob('comparison_*.jpg')):
    output_path = OUTPUT_DIR / f"branded_{img_path.name}"
    if add_watermark(img_path, output_path):
        count += 1

print('\n' + '=' * 80)
print(f'完成！处理 {count} 张图片')
print('=' * 80)

# 列出文件
print('\n📁 带水印图片列表:')
for f in sorted(OUTPUT_DIR.glob('*.jpg')):
    size = f.stat().st_size / 1024
    print(f'  {f.name} ({size:.1f} KB)')

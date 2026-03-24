#!/usr/bin/env python3
"""
数字水印追溯系统
在上传前添加不可见水印，用于数据泄露追溯
"""

import os
from PIL import Image, ImageDraw
from pathlib import Path
import hashlib
import json
from datetime import datetime

# 水印数据库（实际应该用数据库）
WATERMARK_DB = Path('/root/.openclaw/workspace/hairstyle_app/watermark_records.json')

def create_watermark_record(user_id: str, image_path: str) -> dict:
    """
    创建水印记录
    
    Args:
        user_id: 用户 ID
        image_path: 图片路径
        
    Returns:
        水印记录
    """
    # 生成追溯信息
    timestamp = datetime.now().isoformat()
    session_id = hashlib.md5(f"{user_id}{timestamp}".encode()).hexdigest()[:16]
    
    trace_info = f"user:{user_id}|time:{timestamp}|session:{session_id}"
    
    # 生成水印哈希（用于验证）
    trace_hash = hashlib.sha256(trace_info.encode()).hexdigest()
    
    # 创建记录
    record = {
        'user_id': user_id,
        'timestamp': timestamp,
        'session_id': session_id,
        'trace_info': trace_info,
        'trace_hash': trace_hash,
        'original_image': image_path,
        'created_at': datetime.now().isoformat()
    }
    
    # 保存到数据库
    save_watermark_record(record)
    
    return record

def save_watermark_record(record: dict):
    """保存水印记录到数据库"""
    # 加载现有记录
    if WATERMARK_DB.exists():
        with open(WATERMARK_DB, 'r', encoding='utf-8') as f:
            db = json.load(f)
    else:
        db = {'records': []}
    
    # 添加新记录
    db['records'].append(record)
    
    # 保存
    with open(WATERMARK_DB, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    print(f'✅ 水印记录已保存：{record["session_id"]}')

def add_visible_watermark(image_path: str, output_path: str, text: str = "智颜社"):
    """
    添加可见水印（用于宣传图）
    
    Args:
        image_path: 原图路径
        output_path: 输出路径
        text: 水印文字
    """
    # 打开图片
    img = Image.open(image_path)
    
    # 创建绘图对象
    draw = ImageDraw.Draw(img)
    
    # 水印参数
    font_size = 36
    color = (255, 107, 129, 180)  # 粉色半透明
    position = 'bottom-right'
    
    # 计算位置
    width, height = img.size
    text_width = len(text) * font_size * 0.6
    text_height = font_size * 1.2
    
    if position == 'bottom-right':
        x = width - text_width - 20
        y = height - text_height - 20
    elif position == 'bottom-left':
        x = 20
        y = height - text_height - 20
    
    # 绘制水印
    draw.text((x, y), text, fill=color, font_size=font_size)
    
    # 保存
    img.save(output_path, quality=95)
    print(f'✅ 可见水印已添加：{output_path}')

def trace_leaked_image(leaked_image_path: str) -> dict:
    """
    追溯泄露图片（需要提取水印信息）
    
    Args:
        leaked_image_path: 泄露图片路径
        
    Returns:
        追溯结果
    """
    # TODO: 实现水印提取逻辑
    # 这里需要根据实际使用的水印算法实现
    
    print(f'⚠️  水印提取功能待实现')
    print(f'   需要使用专业水印提取工具')
    
    return {
        'success': False,
        'error': '水印提取功能待实现'
    }

if __name__ == '__main__':
    print('=' * 80)
    print('数字水印追溯系统')
    print('=' * 80)
    
    # 测试创建水印记录
    test_user_id = 'user_test_001'
    test_image = '/root/.openclaw/workspace/hairstyle_app/test_image.jpg'
    
    if Path(test_image).exists():
        print(f'\n📝 创建水印记录...')
        record = create_watermark_record(test_user_id, test_image)
        
        print(f'\n✅ 水印记录创建成功')
        print(f'   用户 ID: {record["user_id"]}')
        print(f'   Session: {record["session_id"]}')
        print(f'   Hash: {record["trace_hash"][:32]}...')
    else:
        print(f'\n⚠️  测试图片不存在：{test_image}')
    
    print('\n' + '=' * 80)
    print('水印数据库位置:', WATERMARK_DB)
    print('=' * 80)

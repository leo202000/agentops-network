#!/usr/bin/env python3
"""
图片压缩模块

功能:
- 压缩发型生成结果图片
- 保持质量的同时减小文件大小
- 支持批量压缩

使用示例:
    from image_compressor import compress_image
    
    # 压缩单张图片
    compress_image("input.jpg", "output.jpg")
    
    # 自定义参数
    compress_image("input.jpg", "output.jpg", quality=85, max_size=1024)
"""

import os
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image


def compress_image(
    input_path: str,
    output_path: str = None,
    quality: int = 85,
    max_size: int = 1024,
    format: str = "JPEG"
) -> Tuple[str, int, float]:
    """
    压缩图片
    
    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径（可选，默认覆盖原文件）
        quality: JPEG 质量 (1-100)，推荐 80-90
                 - 90-100: 几乎无损，文件较大
                 - 80-90: 平衡质量和大小（推荐）
                 - 70-80: 明显压缩，质量可接受
                 - <70:  质量损失明显
        max_size: 最大边长（像素），推荐 1024-2048
                  - 1024: 适合手机屏幕
                  - 2048: 适合高清显示
                  - 0: 不调整尺寸
        format: 输出格式（JPEG/WebP）
    
    Returns:
        (输出路径，原始大小，压缩后大小)
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"文件不存在：{input_path}")
    
    # 默认输出路径
    if output_path is None:
        output_path = input_path
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 获取原始大小
    original_size = input_path.stat().st_size
    
    # 打开图片
    img = Image.open(input_path)
    
    # 1. 调整尺寸（如果需要）
    if max_size > 0:
        width, height = img.size
        if max(width, height) > max_size:
            ratio = max_size / max(width, height)
            new_size = (int(width * ratio), int(height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            print(f"📏 调整尺寸：{width}x{height} → {new_size[0]}x{new_size[1]}")
    
    # 2. 转换为 RGB（移除 Alpha 通道，JPEG 不支持透明）
    if img.mode in ('RGBA', 'LA', 'P'):
        # 创建白色背景
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # 3. 保存为压缩格式
    save_kwargs = {
        'quality': quality,
        'optimize': True,  # 优化压缩
    }
    
    if format == "JPEG":
        save_kwargs['progressive'] = True  # 渐进式加载（用户体验更好）
    elif format == "WebP":
        save_kwargs['method'] = 6  # 最佳压缩质量
    
    # 保存
    img.save(output_path, format, **save_kwargs)
    
    # 获取压缩后大小
    compressed_size = output_path.stat().st_size
    
    # 计算压缩率
    compression_rate = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
    
    print(f"✅ 压缩完成")
    print(f"   原始大小：{original_size/1024:.1f} KB")
    print(f"   压缩后：{compressed_size/1024:.1f} KB")
    print(f"   压缩率：{compression_rate:.1f}%")
    
    return str(output_path), original_size, compressed_size


def compress_batch(
    input_dir: str,
    output_dir: str = None,
    quality: int = 85,
    max_size: int = 1024,
    extensions: tuple = ('.jpg', '.jpeg', '.png', '.webp')
) -> dict:
    """
    批量压缩图片
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录（可选，默认覆盖）
        quality: JPEG 质量
        max_size: 最大边长
        extensions: 处理的文件扩展名
    
    Returns:
        压缩统计信息
    """
    input_dir = Path(input_dir)
    
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = input_dir
    
    # 查找所有图片
    image_files = []
    for ext in extensions:
        image_files.extend(input_dir.glob(f"*{ext}"))
        image_files.extend(input_dir.glob(f"*{ext.upper()}"))
    
    if not image_files:
        print(f"⚠️  未找到图片文件：{input_dir}")
        return {'count': 0, 'original_size': 0, 'compressed_size': 0}
    
    print(f"📁 找到 {len(image_files)} 张图片")
    print("=" * 60)
    
    # 统计信息
    stats = {
        'count': 0,
        'success': 0,
        'failed': 0,
        'original_size': 0,
        'compressed_size': 0
    }
    
    # 批量压缩
    for i, img_path in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] 压缩：{img_path.name}")
        
        try:
            # 确定输出路径
            if output_dir == input_dir:
                out_path = img_path
            else:
                out_path = output_dir / img_path.name
            
            # 压缩
            _, orig_size, comp_size = compress_image(
                str(img_path),
                str(out_path),
                quality=quality,
                max_size=max_size
            )
            
            stats['count'] += 1
            stats['success'] += 1
            stats['original_size'] += orig_size
            stats['compressed_size'] += comp_size
            
        except Exception as e:
            print(f"❌ 压缩失败：{e}")
            stats['count'] += 1
            stats['failed'] += 1
    
    # 输出统计
    print("\n" + "=" * 60)
    print("📊 批量压缩统计")
    print("=" * 60)
    print(f"总数量：{stats['count']}")
    print(f"成功：{stats['success']}")
    print(f"失败：{stats['failed']}")
    print(f"原始总大小：{stats['original_size']/1024/1024:.2f} MB")
    print(f"压缩后总大小：{stats['compressed_size']/1024/1024:.2f} MB")
    
    total_savings = stats['original_size'] - stats['compressed_size']
    total_rate = (1 - stats['compressed_size'] / stats['original_size']) * 100 if stats['original_size'] > 0 else 0
    
    print(f"节省空间：{total_savings/1024/1024:.2f} MB ({total_rate:.1f}%)")
    print("=" * 60)
    
    return stats


def get_image_info(image_path: str) -> dict:
    """
    获取图片信息
    
    Args:
        image_path: 图片路径
    
    Returns:
        图片信息字典
    """
    img = Image.open(image_path)
    
    return {
        'path': image_path,
        'format': img.format,
        'mode': img.mode,
        'width': img.width,
        'height': img.height,
        'size_bytes': Path(image_path).stat().st_size,
        'size_kb': Path(image_path).stat().st_size / 1024,
        'size_mb': Path(image_path).stat().st_size / 1024 / 1024
    }


# 命令行工具
if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="图片压缩工具")
    parser.add_argument("input", help="输入图片路径或目录")
    parser.add_argument("-o", "--output", help="输出路径（可选）")
    parser.add_argument("-q", "--quality", type=int, default=85, help="JPEG 质量 (1-100)，默认 85")
    parser.add_argument("-s", "--size", type=int, default=1024, help="最大边长（像素），默认 1024")
    parser.add_argument("-f", "--format", choices=["JPEG", "WebP"], default="JPEG", help="输出格式")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if input_path.is_dir():
        # 批量压缩
        compress_batch(
            str(input_path),
            args.output,
            quality=args.quality,
            max_size=args.size
        )
    else:
        # 单张压缩
        if not input_path.exists():
            print(f"❌ 文件不存在：{input_path}")
            sys.exit(1)
        
        output_path, orig_size, comp_size = compress_image(
            str(input_path),
            args.output,
            quality=args.quality,
            max_size=args.size,
            format=args.format
        )
        
        savings = orig_size - comp_size
        rate = (1 - comp_size / orig_size) * 100 if orig_size > 0 else 0
        
        print(f"\n💾 节省：{savings/1024:.1f} KB ({rate:.1f}%)")

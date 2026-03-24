#!/usr/bin/env python3
"""
发型生成结果缓存模块

功能:
- 缓存发型生成结果，避免重复 API 调用
- 基于图片哈希 + 发型风格 + 提示词生成缓存键
- 支持 TTL（过期时间）
- 自动清理过期缓存

使用示例:
    from result_cache import ResultCache
    
    # 初始化缓存
    cache = ResultCache(cache_dir="./cache", ttl_hours=24)
    
    # 查询缓存
    result = cache.get(image_path, style, prompt)
    if result['hit']:
        print("缓存命中！")
        return result['image_url']
    
    # 未命中，调用 API 生成后缓存
    result = generate_hairstyle(image_path, style, prompt)
    cache.set(image_path, style, prompt, result['url'], result['path'])
"""

import os
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResultCache:
    """发型生成结果缓存"""
    
    def __init__(
        self,
        cache_dir: str = "./cache",
        ttl_hours: int = 24,
        max_size_gb: float = 1.0
    ):
        """
        初始化缓存
        
        Args:
            cache_dir: 缓存目录
            ttl_hours: 缓存有效期（小时），默认 24 小时
            max_size_gb: 最大缓存大小（GB），默认 1GB
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录（按日期分类）
        self.results_dir = self.cache_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
        
        self.ttl_hours = ttl_hours
        self.max_size_bytes = int(max_size_gb * 1024 * 1024 * 1024)
        
        # 缓存索引文件
        self.index_file = self.cache_dir / "cache_index.json"
        self.index = self._load_index()
        
        logger.info(f"💾 缓存初始化完成：{self.cache_dir}")
        logger.info(f"   TTL: {ttl_hours}小时")
        logger.info(f"   最大容量：{max_size_gb}GB")
    
    def _load_index(self) -> dict:
        """加载缓存索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载索引失败：{e}")
                return {}
        return {}
    
    def _save_index(self):
        """保存缓存索引"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存索引失败：{e}")
    
    def _generate_cache_key(
        self,
        image_hash: str,
        style: str,
        prompt: str = ""
    ) -> str:
        """
        生成缓存键
        
        Args:
            image_hash: 原图哈希
            style: 发型风格
            prompt: 提示词
        
        Returns:
            MD5 缓存键
        """
        key_string = f"{image_hash}:{style}:{prompt}"
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def _get_image_hash(self, image_path: str) -> str:
        """
        计算图片哈希（MD5）
        
        Args:
            image_path: 图片路径
        
        Returns:
            MD5 哈希值
        """
        hash_md5 = hashlib.md5()
        with open(image_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _get_cache_size(self) -> int:
        """获取当前缓存总大小（字节）"""
        total_size = 0
        if self.results_dir.exists():
            for path in self.results_dir.glob("*"):
                if path.is_file():
                    total_size += path.stat().st_size
        return total_size
    
    def _cleanup_if_needed(self):
        """如果缓存超限，清理最旧的缓存"""
        current_size = self._get_cache_size()
        
        if current_size > self.max_size_bytes:
            logger.warning(f"⚠️  缓存超限：{current_size/1024/1024:.1f}MB > {self.max_size_bytes/1024/1024:.1f}MB")
            
            # 按创建时间排序，删除最旧的
            sorted_entries = sorted(
                self.index.items(),
                key=lambda x: x[1].get('created_at', '')
            )
            
            for cache_key, entry in sorted_entries:
                if current_size <= self.max_size_bytes * 0.8:  # 清理到 80%
                    break
                
                self._delete_cache_entry(cache_key)
                current_size = self._get_cache_size()
    
    def get(
        self,
        image_path: str,
        style: str,
        prompt: str = ""
    ) -> Dict[str, Any]:
        """
        查询缓存
        
        Args:
            image_path: 原图路径
            style: 发型风格
            prompt: 提示词
        
        Returns:
            {'hit': True/False, 'image_url': ..., 'result_path': ...}
        """
        try:
            # 计算图片哈希
            image_hash = self._get_image_hash(image_path)
            
            # 生成缓存键
            cache_key = self._generate_cache_key(image_hash, style, prompt)
            
            # 查询索引
            if cache_key in self.index:
                cache_entry = self.index[cache_key]
                
                # 检查是否过期
                created_at = datetime.fromisoformat(cache_entry['created_at'])
                age_hours = (datetime.now() - created_at).total_seconds() / 3600
                
                if age_hours < self.ttl_hours:
                    # 检查文件是否存在
                    result_path = self.results_dir / cache_entry['result_file']
                    if result_path.exists():
                        logger.info(f"✅ 缓存命中：{cache_key[:16]}... (风格：{style})")
                        return {
                            'hit': True,
                            'cache_key': cache_key,
                            'image_url': cache_entry.get('result_url', ''),
                            'result_path': str(result_path),
                            'age_hours': age_hours,
                            'style': style
                        }
                    else:
                        logger.warning(f"⚠️  缓存文件丢失：{cache_key[:16]}...")
                        self._delete_cache_entry(cache_key)
                else:
                    logger.info(f"⏰ 缓存过期：{cache_key[:16]}... ({age_hours:.1f}小时)")
                    self._delete_cache_entry(cache_key)
            
            logger.info(f"⏳ 缓存未命中：{cache_key[:16]}... (风格：{style})")
            return {
                'hit': False,
                'cache_key': cache_key,
                'style': style
            }
            
        except FileNotFoundError:
            logger.error(f"❌ 文件不存在：{image_path}")
            return {'hit': False, 'error': 'File not found'}
        except Exception as e:
            logger.error(f"❌ 缓存查询失败：{e}")
            return {'hit': False, 'error': str(e)}
    
    def set(
        self,
        image_path: str,
        style: str,
        prompt: str,
        result_url: str,
        result_path: str,
        metadata: dict = None
    ) -> bool:
        """
        设置缓存
        
        Args:
            image_path: 原图路径
            style: 发型风格
            prompt: 提示词
            result_url: 结果 URL
            result_path: 结果文件路径
            metadata: 额外元数据
        
        Returns:
            是否成功
        """
        try:
            # 计算图片哈希
            image_hash = self._get_image_hash(image_path)
            
            # 生成缓存键
            cache_key = self._generate_cache_key(image_hash, style, prompt)
            
            # 复制结果到缓存目录
            result_file = f"{cache_key}.jpg"
            cache_path = self.results_dir / result_file
            
            # 确保目录存在
            self.results_dir.mkdir(exist_ok=True)
            
            # 复制文件
            shutil.copy2(result_path, cache_path)
            
            # 更新索引
            self.index[cache_key] = {
                'created_at': datetime.now().isoformat(),
                'style': style,
                'prompt': prompt,
                'result_file': result_file,
                'result_url': result_url,
                'original_hash': image_hash,
                'metadata': metadata or {}
            }
            
            self._save_index()
            
            # 检查并清理
            self._cleanup_if_needed()
            
            logger.info(f"💾 已缓存：{cache_key[:16]}... (风格：{style})")
            logger.info(f"   缓存路径：{cache_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 缓存保存失败：{e}")
            return False
    
    def _delete_cache_entry(self, cache_key: str):
        """删除缓存条目"""
        if cache_key in self.index:
            cache_file = self.index[cache_key].get('result_file', '')
            cache_path = self.results_dir / cache_file
            
            # 删除文件
            if cache_path.exists():
                cache_path.unlink()
            
            # 删除索引
            del self.index[cache_key]
            self._save_index()
            
            logger.debug(f"🗑️  已删除缓存：{cache_key[:16]}...")
    
    def cleanup_expired(self) -> int:
        """
        清理过期缓存
        
        Returns:
            清理的数量
        """
        expired_keys = []
        
        for cache_key, entry in self.index.items():
            created_at = datetime.fromisoformat(entry['created_at'])
            age_hours = (datetime.now() - created_at).total_seconds() / 3600
            
            if age_hours >= self.ttl_hours:
                expired_keys.append(cache_key)
        
        for cache_key in expired_keys:
            self._delete_cache_entry(cache_key)
        
        logger.info(f"🧹 清理了 {len(expired_keys)} 个过期缓存")
        return len(expired_keys)
    
    def get_stats(self) -> dict:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        total_size = self._get_cache_size()
        
        # 按风格统计
        style_counts = {}
        for entry in self.index.values():
            style = entry.get('style', 'unknown')
            style_counts[style] = style_counts.get(style, 0) + 1
        
        return {
            'total_entries': len(self.index),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / 1024 / 1024,
            'max_size_mb': self.max_size_bytes / 1024 / 1024,
            'usage_percent': (total_size / self.max_size_bytes) * 100 if self.max_size_bytes > 0 else 0,
            'style_counts': style_counts,
            'ttl_hours': self.ttl_hours,
            'cache_dir': str(self.cache_dir)
        }
    
    def clear_all(self):
        """清空所有缓存"""
        # 删除所有文件
        if self.results_dir.exists():
            for path in self.results_dir.glob("*"):
                if path.is_file():
                    path.unlink()
        
        # 清空索引
        self.index = {}
        self._save_index()
        
        logger.info("🗑️  已清空所有缓存")
    
    def list_entries(self, limit: int = 10) -> list:
        """
        列出缓存条目
        
        Args:
            limit: 最多返回数量
        
        Returns:
            缓存条目列表
        """
        entries = []
        
        for cache_key, entry in list(self.index.items())[:limit]:
            entries.append({
                'cache_key': cache_key[:16] + '...',
                'style': entry.get('style', ''),
                'created_at': entry.get('created_at', ''),
                'result_file': entry.get('result_file', ''),
                'result_url': entry.get('result_url', '')
            })
        
        return entries


# 便捷函数
def quick_cache(
    image_path: str,
    style: str,
    prompt: str,
    result_url: str,
    result_path: str,
    cache_dir: str = "./cache"
) -> bool:
    """快速缓存结果"""
    cache = ResultCache(cache_dir=cache_dir)
    return cache.set(image_path, style, prompt, result_url, result_path)


def quick_check(
    image_path: str,
    style: str,
    prompt: str = "",
    cache_dir: str = "./cache"
) -> Dict[str, Any]:
    """快速查询缓存"""
    cache = ResultCache(cache_dir=cache_dir)
    return cache.get(image_path, style, prompt)


# 命令行工具
if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="发型结果缓存管理工具")
    parser.add_argument("action", choices=["stats", "list", "clear", "cleanup"],
                       help="操作类型")
    parser.add_argument("-d", "--dir", default="./cache", help="缓存目录")
    parser.add_argument("-n", "--limit", type=int, default=10, help="显示数量")
    
    args = parser.parse_args()
    
    cache = ResultCache(cache_dir=args.dir)
    
    if args.action == "stats":
        stats = cache.get_stats()
        print("\n💾 缓存统计")
        print("=" * 60)
        print(f"缓存目录：{stats['cache_dir']}")
        print(f"条目数量：{stats['total_entries']}")
        print(f"使用空间：{stats['total_size_mb']:.1f} MB / {stats['max_size_mb']:.1f} MB")
        print(f"使用率：{stats['usage_percent']:.1f}%")
        print(f"TTL: {stats['ttl_hours']}小时")
        
        if stats['style_counts']:
            print("\n按风格统计:")
            for style, count in sorted(stats['style_counts'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {style}: {count}")
        
        print("=" * 60)
    
    elif args.action == "list":
        entries = cache.list_entries(args.limit)
        print(f"\n📋 最近缓存 ({len(entries)}条)")
        print("=" * 60)
        for entry in entries:
            print(f"风格：{entry['style']}")
            print(f"  缓存键：{entry['cache_key']}")
            print(f"  创建时间：{entry['created_at']}")
            print()
    
    elif args.action == "clear":
        confirm = input("⚠️  确认清空所有缓存？(y/N): ")
        if confirm.lower() == 'y':
            cache.clear_all()
            print("✅ 已清空缓存")
        else:
            print("❌ 已取消")
    
    elif args.action == "cleanup":
        count = cache.cleanup_expired()
        print(f"✅ 清理了 {count} 个过期缓存")

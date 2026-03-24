#!/usr/bin/env python3
"""
TOS 数据自动清理脚本

功能:
- 定期删除超过 24 小时的用户照片
- 保留生成结果（永久）
- 记录删除日志（合规审计）
"""

import os
import time
from pathlib import Path
from datetime import datetime, timedelta
from tos import TosClientV2

# 配置
TOS_BUCKET = os.getenv('TOS_BUCKET', '')
TOS_ACCESS_KEY = os.getenv('TOS_ACCESS_KEY', '')
TOS_SECRET_KEY = os.getenv('TOS_SECRET_KEY', '')
TOS_REGION = os.getenv('TOS_REGION', 'cn-beijing')

# 保留时间（小时）
RETENTION_HOURS = 24

# 日志文件
LOG_FILE = '/root/.openclaw/workspace/hairstyle_app/logs/data_cleanup.log'
Path(LOG_FILE).parent.mkdir(exist_ok=True)


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}\n"
    
    print(log_line.strip())
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_line)


def cleanup_old_files():
    """清理超过保留期的文件"""
    client = TosClientV2(
        ak=TOS_ACCESS_KEY,
        sk=TOS_SECRET_KEY,
        region=TOS_REGION
    )
    
    log("=" * 60)
    log("开始清理过期数据")
    
    deleted_count = 0
    kept_count = 0
    
    try:
        # 列出所有对象
        response = client.list_objects(bucket=TOS_BUCKET, prefix='hairstyle/')
        
        # TOS SDK 返回的是对象，不是字典
        objects = getattr(response, 'contents', [])
        if not objects:
            log("未发现文件")
            return
        
        cutoff_time = time.time() - (RETENTION_HOURS * 3600)
        
        for obj in objects:
            key = getattr(obj, 'key', '')
            last_modified = getattr(obj, 'lastModified', None)
            if last_modified is None:
                continue
            last_modified = last_modified.timestamp()
            
            # 跳过 results 目录（永久保存）
            if 'results/' in key:
                kept_count += 1
                continue
            
            # 检查是否过期
            if last_modified < cutoff_time:
                # 删除过期文件
                client.delete_object(bucket=TOS_BUCKET, key=key)
                log(f"✅ 删除：{key} (创建时间：{datetime.fromtimestamp(last_modified)})")
                deleted_count += 1
            else:
                kept_count += 1
        
        log("-" * 60)
        log(f"清理完成：删除 {deleted_count} 个文件，保留 {kept_count} 个文件")
        
    except Exception as e:
        log(f"❌ 清理失败：{e}")
        raise


def cleanup_local_temp():
    """清理本地临时文件"""
    temp_dirs = [
        Path('/tmp/hairstyle_skill'),
        Path('/tmp/hairstyle_bot'),
    ]
    
    log("\n清理本地临时文件")
    
    for temp_dir in temp_dirs:
        if temp_dir.exists():
            count = 0
            for file in temp_dir.glob('*.jpg'):
                # 删除超过 1 小时的文件
                if time.time() - file.stat().st_mtime > 3600:
                    file.unlink()
                    count += 1
            
            log(f"清理 {temp_dir}: {count} 个文件")


if __name__ == "__main__":
    log("=" * 60)
    log("TOS 数据清理任务启动")
    log("=" * 60)
    
    cleanup_old_files()
    cleanup_local_temp()
    
    log("\n所有清理任务完成")
    log("=" * 60)

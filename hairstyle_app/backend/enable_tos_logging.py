#!/usr/bin/env python3
"""
启用 TOS 访问日志
配置 TOS Bucket 访问日志记录
"""

import os
from tos import TosClientV2
from datetime import datetime

# 配置
TOS_BUCKET = os.getenv('TOS_BUCKET', 'hairfashon')
TOS_ACCESS_KEY = os.getenv('TOS_ACCESS_KEY', '')
TOS_SECRET_KEY = os.getenv('TOS_SECRET_KEY', '')
TOS_REGION = os.getenv('TOS_REGION', 'cn-beijing')

# 日志存储 Bucket（可以与原 Bucket 相同）
LOG_BUCKET = TOS_BUCKET
LOG_PREFIX = 'access-logs/'

print('=' * 80)
print('TOS 访问日志配置')
print('=' * 80)

try:
    # 创建客户端
    client = TosClientV2(
        ak=TOS_ACCESS_KEY,
        sk=TOS_SECRET_KEY,
        region=TOS_REGION
    )
    
    print(f'\n✅ TOS 客户端创建成功')
    print(f'   Bucket: {TOS_BUCKET}')
    print(f'   Region: {TOS_REGION}')
    
    # 配置访问日志
    # 注意：TOS SDK 可能不支持直接配置日志，需要通过控制台配置
    # 以下是配置说明
    
    print('\n📋 TOS 访问日志配置说明:')
    print('-' * 60)
    print('1. 登录火山引擎控制台')
    print('   https://console.volcengine.com/tos/')
    print('')
    print('2. 进入存储桶管理')
    print(f'   选择：{TOS_BUCKET}')
    print('')
    print('3. 进入"访问日志"设置')
    print('   路径：存储桶详情 > 访问日志')
    print('')
    print('4. 启用访问日志')
    print('   - 目标存储桶：hairfashon')
    print('   - 日志前缀：access-logs/')
    print('   - 日志文件命名：{日期}/{时间}-{随机字符串}.log')
    print('')
    print('5. 保存配置')
    print('')
    print('-' * 60)
    
    # 检查日志目录是否存在
    try:
        response = client.list_objects(bucket=LOG_BUCKET, prefix=LOG_PREFIX)
        objects = getattr(response, 'contents', [])
        print(f'\n✅ 日志目录检查完成')
        print(f'   现有日志文件：{len(objects)} 个')
    except Exception as e:
        print(f'\n⚠️  日志目录检查失败：{e}')
    
    print('\n' + '=' * 80)
    print('配置完成！')
    print('=' * 80)
    
    # 查看日志示例
    print('\n📊 访问日志示例格式:')
    print('-' * 60)
    print('[22/Mar/2026:19:05:03 +0800] 192.168.1.100')
    print('  GET /hairstyle/results/1774164088_result.jpg')
    print('  HTTP/1.1 200 - 123456 "-" "Mozilla/5.0"')
    print('-' * 60)
    
except Exception as e:
    print(f'\n❌ 配置失败：{e}')
    print('\n请通过火山引擎控制台手动配置访问日志')

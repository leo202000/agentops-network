#!/usr/bin/env python3
"""
批量下载 TOS 发型生成结果到本地
"""

import os
import requests
from pathlib import Path

# 下载目录
DOWNLOAD_DIR = Path('/root/.openclaw/workspace/hairstyle_app/content_materials/downloaded')
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# TOS 结果列表
RESULTS = [
    # 模特 2 的结果
    {'name': 'model2_short', 'url': 'https://hairfashon.tos-cn-beijing.volces.com/hairstyle/results/1774164088_result.jpg', 'style': '短发'},
    {'name': 'model2_wavy', 'url': 'https://hairfashon.tos-cn-beijing.volces.com/hairstyle/results/1774164261_result.jpg', 'style': '大波浪'},
    {'name': 'model2_curly', 'url': 'https://hairfashon.tos-cn-beijing.volces.com/hairstyle/results/1774164390_result.jpg', 'style': '羊毛卷'},
    {'name': 'model2_bangs', 'url': 'https://hairfashon.tos-cn-beijing.volces.com/hairstyle/results/1774165733_file_61---f44ca44d-4b81-43dc-8498-40c22a4f517e_result.jpg', 'style': '空气刘海'},
    {'name': 'model2_ponytail', 'url': 'https://hairfashon.tos-cn-beijing.volces.com/hairstyle/results/1774165776_file_61---f44ca44d-4b81-43dc-8498-40c22a4f517e_result.jpg', 'style': '高马尾'},
    # 模特 1 的结果
    {'name': 'model1_short', 'url': 'https://hairfashon.tos-cn-beijing.volces.com/hairstyle/results/1774163633_model_1_result.jpg', 'style': '短发'},
    {'name': 'model1_wavy', 'url': 'https://hairfashon.tos-cn-beijing.volces.com/hairstyle/results/1774163676_model_1_result.jpg', 'style': '大波浪'},
    {'name': 'model1_curly', 'url': 'https://hairfashon.tos-cn-beijing.volces.com/hairstyle/results/1774163836_model_1_result.jpg', 'style': '羊毛卷'},
    {'name': 'model1_bangs', 'url': 'https://hairfashon.tos-cn-beijing.volces.com/hairstyle/results/1774163967_model_1_result.jpg', 'style': '空气刘海'},
    {'name': 'model1_ponytail', 'url': 'https://hairfashon.tos-cn-beijing.volces.com/hairstyle/results/1774164026_model_1_result.jpg', 'style': '高马尾'},
]

# 模特原图
MODEL_ORIGINALS = [
    {'name': 'model1_original', 'path': '/root/.openclaw/media/inbound/file_60---00de3a22-c475-411b-81eb-1dfea9f831de.jpg'},
    {'name': 'model2_original', 'path': '/root/.openclaw/media/inbound/file_61---f44ca44d-4b81-43dc-8498-40c22a4f517e.jpg'},
]

print('=' * 80)
print('批量下载 TOS 发型生成结果')
print('=' * 80)
print(f'下载目录：{DOWNLOAD_DIR}\n')

# 下载生成结果
print('【1】下载发型生成结果...')
downloaded = []

for item in RESULTS:
    save_path = DOWNLOAD_DIR / f"{item['name']}.jpg"
    
    try:
        response = requests.get(item['url'], timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        file_size = os.path.getsize(save_path) / 1024  # KB
        print(f'✅ {item["name"]} ({item["style"]}): {file_size:.1f} KB')
        downloaded.append(item)
        
    except Exception as e:
        print(f'❌ {item["name"]} 失败：{e}')

# 复制模特原图
print('\n【2】复制模特原图...')
for model in MODEL_ORIGINALS:
    save_path = DOWNLOAD_DIR / f"{model['name']}.jpg"
    
    try:
        import shutil
        shutil.copy2(model['path'], save_path)
        file_size = os.path.getsize(save_path) / 1024
        print(f'✅ {model["name"]}: {file_size:.1f} KB')
    except Exception as e:
        print(f'❌ {model["name"]} 失败：{e}')

print('\n' + '=' * 80)
print(f'下载完成！')
print(f'成功：{len(downloaded)} 个生成结果 + 2 个原图')
print(f'目录：{DOWNLOAD_DIR}')
print('=' * 80)

# 列出所有文件
print('\n📁 文件列表:')
for f in sorted(DOWNLOAD_DIR.glob('*.jpg')):
    size = f.stat().st_size / 1024
    print(f'  {f.name} ({size:.1f} KB)')

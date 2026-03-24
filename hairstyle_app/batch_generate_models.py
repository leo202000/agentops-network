#!/usr/bin/env python3
"""
批量生成模特发型对比图
2 张模特照片 × 5 款发型 = 10 张生成图
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/hairstyle-generator')

from hairstyle_skill import HairstyleSkill
import os

skill = HairstyleSkill()

# 模特照片
model_images = [
    '/root/.openclaw/workspace/hairstyle_app/model_photos/model_1.jpg',
    '/root/.openclaw/workspace/hairstyle_app/model_photos/model_2.jpg',
]

# 5 款热门发型
styles = [
    ('短发', '短发发型，清爽利落，自然真实'),
    ('大波浪', '大波浪长发，性感迷人，自然真实'),
    ('羊毛卷', '可爱羊毛卷，复古时尚，自然真实'),
    ('空气刘海', '空气刘海，清新甜美，轻薄透气'),
    ('高马尾', '高马尾，活力青春，清爽利落'),
]

print('=' * 80)
print('批量生成模特发型对比图')
print('=' * 80)
print(f'模特照片：{len(model_images)} 张')
print(f'发型风格：{len(styles)} 款')
print(f'预计生成：{len(model_images) * len(styles)} 张图')
print()

results = []

for i, img_path in enumerate(model_images, 1):
    print(f'\n{"="*60}')
    print(f'模特 {i}: {img_path}')
    print(f'{"="*60}')
    
    if not os.path.exists(img_path):
        print(f'❌ 文件不存在：{img_path}')
        continue
    
    for style_name, style_prompt in styles:
        print(f'\n  生成：{style_name}...', end=' ', flush=True)
        
        try:
            result = skill.generate(img_path, style_name)
            
            if result['success']:
                url = result['url']
                print(f'✅')
                print(f'     URL: {url}')
                
                results.append({
                    'model': img_path,
                    'style': style_name,
                    'url': url,
                    'success': True
                })
            else:
                error = result.get('error', '未知错误')
                print(f'❌ {error}')
                results.append({
                    'model': img_path,
                    'style': style_name,
                    'error': error,
                    'success': False
                })
        
        except Exception as e:
            print(f'❌ 异常：{e}')
            results.append({
                'model': img_path,
                'style': style_name,
                'error': str(e),
                'success': False
            })

print(f'\n{"="*80}')
print('批量生成完成！')
print(f'{"="*80}')
print(f'总计：{len(results)} 个任务')
print(f'成功：{sum(1 for r in results if r["success"])} 个')
print(f'失败：{sum(1 for r in results if not r["success"])} 个')
print()

# 输出结果清单
print('📋 生成结果清单:')
print('-' * 80)
for r in results:
    status = '✅' if r['success'] else '❌'
    model_name = os.path.basename(r['model'])
    if r['success']:
        print(f'{status} {model_name} - {r["style"]}: {r["url"]}')
    else:
        print(f'{status} {model_name} - {r["style"]}: {r.get("error", "失败")}')

print()
print('💾 结果已保存到 TOS，可永久访问！')
print('=' * 80)

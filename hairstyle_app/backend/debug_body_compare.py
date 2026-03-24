#!/usr/bin/env python3
"""对比 body 内容"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hairstyle_generator import HairstyleGenerator

ak = os.getenv("JIMENG_ACCESS_KEY_ID")
sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")

hg = HairstyleGenerator(ak, sk, enable_cache=False, enable_compression=False)

# 成功请求的 body
body1_dict = {
    "req_key": "seed3l_single_ip",
    "image_urls": ["https://hairfashon.tos-cn-beijing.volces.com/hairstyle/1fd9c969-32f1-4d73-9b8b-be6ae2cf34c8.jpg"],
    "prompt": "test",
    "width": 1024,
    "height": 1024,
}
body1 = json.dumps(body1_dict, ensure_ascii=False)

# generate 方法的 body
style = "齐肩发"
style_config = hg.STYLES[style]
style_prompt = style_config["prompt"]
prompt = f"保持人物脸部完全一致，只改变发型为{style}，{style_prompt}, realistic photo, high quality, professional photography, natural lighting"
mode = hg.transform_mode
preset = hg.TRANSFORM_PRESETS.get(mode, hg.TRANSFORM_PRESETS["中等"])
strength = preset["strength"]

body2_dict = {
    "req_key": "seed3l_single_ip",
    "image_urls": ["https://hairfashon.tos-cn-beijing.volces.com/hairstyle/test.jpg"],
    "prompt": prompt,
    "width": 1024,
    "height": 1024,
    "strength": strength,
}
body2 = json.dumps(body2_dict, ensure_ascii=False)

print("Body 1 (成功):")
print(body1)
print()
print("Body 2 (generate):")
print(body2[:200] + "...")
print()
print(f"Body 1 length: {len(body1)}")
print(f"Body 2 length: {len(body2)}")
print()
print(f"strength in body2: {strength}")
print(f"prompt length: {len(prompt)}")

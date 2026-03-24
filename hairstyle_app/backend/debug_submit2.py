#!/usr/bin/env python3
"""调试 submit_task"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hairstyle_generator import HairstyleGenerator

ak = os.getenv("JIMENG_ACCESS_KEY_ID")
sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")

hg = HairstyleGenerator(ak, sk, enable_cache=False, enable_compression=False)

image_url = "https://hairfashon.tos-cn-beijing.volces.com/hairstyle/test.jpg"
prompt = "test prompt"
strength = 0.7

print("调用 submit_task...")
print(f"  image_url: {image_url}")
print(f"  prompt: {prompt}")
print(f"  strength: {strength}")

try:
    result = hg.client.submit_task(
        image_url=image_url,
        prompt=prompt,
        strength=strength,
        req_key="seed3l_single_ip"
    )
    print(f"\nResult type: {type(result)}")
    print(f"Result: {result}")
    
    if result is None:
        print("ERROR: Result is None!")
    elif isinstance(result, dict):
        print(f"Code: {result.get('code')}")
        print(f"Message: {result.get('message')}")
except Exception as e:
    print(f"\nException: {e}")
    import traceback
    traceback.print_exc()

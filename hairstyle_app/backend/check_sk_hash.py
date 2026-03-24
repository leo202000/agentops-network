#!/usr/bin/env python3
import os
import hashlib
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")
ak = os.getenv("JIMENG_ACCESS_KEY_ID")

print(f"AK: {ak}")
print(f"SK: {sk}")
print(f"SK hash: {hashlib.md5(sk.encode()).hexdigest()}")

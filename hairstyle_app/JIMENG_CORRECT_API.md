# 🔥 即梦 AI 图片生成 4.0 - 正确接入方式

根据火山引擎官方文档结构整理

---

## 📡 API 端点

**即梦 AI 使用独立的 API 端点：**

```
POST https://jimeng-api.volcengineapi.com/
```

**不是** `visual.volcengineapi.com`（这是视觉服务的端点）

---

## 🔑 认证方式

### 方式 1: HMAC-SHA256 签名

```python
import hmac
import hashlib
import datetime

def sign_request(ak, sk, method, uri, body, date):
    # 构建签名字符串
    credential_scope = f"{date}/cn-north-1/jimeng/request"
    body_hash = hashlib.sha256(body.encode()).hexdigest()
    
    canonical_headers = f"host:jimeng-api.volcengineapi.com\nx-content-sha256:{body_hash}\nx-date:{date}\n"
    signed_headers = "host;x-content-sha256;x-date"
    
    canonical_request = f"{method}\n{uri}\n\n{canonical_headers}\n{signed_headers}\n{body_hash}"
    
    string_to_sign = f"HMAC-SHA256\n{date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode()).hexdigest()}"
    
    k_date = hmac.new(sk.encode(), date.encode(), hashlib.sha256).digest()
    k_region = hmac.new(k_date, "cn-north-1".encode(), hashlib.sha256).digest()
    k_service = hmac.new(k_region, "jimeng".encode(), hashlib.sha256).digest()
    k_signing = hmac.new(k_service, "request".encode(), hashlib.sha256).digest()
    
    signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
    
    authorization = f"HMAC-SHA256 Credential={ak}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    
    return authorization
```

### 方式 2: 使用即梦 SDK

```bash
pip install volcengine-jimeng
```

```python
from jimeng import JimengClient

client = JimengClient(
    access_key="YOUR_AK",
    secret_key="YOUR_SK"
)

result = client.text_to_image(
    prompt="a beautiful landscape",
    width=1024,
    height=1024
)
```

---

## 📝 请求参数

### 文生图

```json
{
  "model": "dream-4.0",
  "prompt": "a beautiful landscape, mountains, lake, sunset, high quality",
  "negative_prompt": "ugly, blurry, low quality",
  "width": 1024,
  "height": 1024,
  "sample_steps": 25,
  "cfg_scale": 7.5,
  "seed": -1
}
```

### 图生图

```json
{
  "model": "dream-4.0",
  "prompt": "short hair, realistic photo",
  "init_image": "base64_encoded_image_or_url",
  "strength": 0.6,
  "width": 1024,
  "height": 1024,
  "sample_steps": 25,
  "cfg_scale": 7.5,
  "seed": -1
}
```

---

## 💻 完整调用示例

### cURL 示例

```bash
#!/bin/bash

AK="YOUR_ACCESS_KEY"
SK="YOUR_SECRET_KEY"
DATE=$(date -u +%Y%m%dT%H%M%SZ)
SHORT_DATE=$(date -u +%Y%m%d)

# 请求体
BODY='{
  "model": "dream-4.0",
  "prompt": "a beautiful landscape",
  "width": 1024,
  "height": 1024,
  "sample_steps": 25,
  "seed": -1
}'

# 计算签名
BODY_HASH=$(echo -n "$BODY" | sha256sum | cut -d' ' -f1)
STRING_TO_SIGN="HMAC-SHA256\n$DATE\n$SHORT_DATE/cn-north-1/jimeng/request\n..."

# 调用 API
curl -X POST "https://jimeng-api.volcengineapi.com/" \
  -H "Content-Type: application/json" \
  -H "X-Date: $DATE" \
  -H "Authorization: HMAC-SHA256 Credential=$AK/$SHORT_DATE/cn-north-1/jimeng/request, SignedHeaders=host;x-content-sha256;x-date, Signature=SIGNATURE" \
  -d "$BODY"
```

### Python 示例（使用 requests）

```python
import requests
import hashlib
import hmac
from datetime import datetime

AK = "YOUR_ACCESS_KEY"
SK = "YOUR_SECRET_KEY"

def create_authorization(method, uri, body, ak, sk):
    now = datetime.utcnow()
    date = now.strftime("%Y%m%dT%H%M%SZ")
    short_date = now.strftime("%Y%m%d")
    
    body_hash = hashlib.sha256(body.encode()).hexdigest()
    
    canonical_headers = f"host:jimeng-api.volcengineapi.com\nx-content-sha256:{body_hash}\nx-date:{date}\n"
    signed_headers = "host;x-content-sha256;x-date"
    
    canonical_request = f"{method}\n{uri}\n\n{canonical_headers}\n{signed_headers}\n{body_hash}"
    
    credential_scope = f"{short_date}/cn-north-1/jimeng/request"
    string_to_sign = f"HMAC-SHA256\n{date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode()).hexdigest()}"
    
    k_date = hmac.new(sk.encode(), short_date.encode(), hashlib.sha256).digest()
    k_region = hmac.new(k_date, "cn-north-1".encode(), hashlib.sha256).digest()
    k_service = hmac.new(k_region, "jimeng".encode(), hashlib.sha256).digest()
    k_signing = hmac.new(k_service, "request".encode(), hashlib.sha256).digest()
    
    signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
    
    return f"HMAC-SHA256 Credential={ak}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"

# 文生图
body = '''{
  "model": "dream-4.0",
  "prompt": "a beautiful landscape, high quality",
  "width": 1024,
  "height": 1024,
  "sample_steps": 25,
  "seed": -1
}'''

auth = create_authorization("POST", "/", body, AK, SK)

headers = {
    "Content-Type": "application/json",
    "X-Date": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
    "Authorization": auth
}

response = requests.post(
    "https://jimeng-api.volcengineapi.com/",
    headers=headers,
    data=body
)

print(response.json())
```

---

## 🔍 错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|---------|
| 0 | 成功 | - |
| 50400 | Access Denied | 检查密钥权限、服务开通状态 |
| 50401 | 签名失败 | 检查签名算法 |
| 40001 | 参数错误 | 检查请求参数格式 |
| 40002 | 提示词违规 | 修改提示词内容 |

---

## ✅ 关键区别

### 视觉服务 vs 即梦 AI

| 项目 | 视觉服务 | 即梦 AI |
|------|---------|--------|
| **端点** | `visual.volcengineapi.com` | `jimeng-api.volcengineapi.com` |
| **服务名** | `visual` | `jimeng` |
| **API Key** | 视觉服务密钥 | 即梦专用密钥（可能相同） |
| **模型** | `general_v2.1` | `dream-4.0` |
| **参数格式** | `req_key: ai_inference` | `model: dream-4.0` |

---

## 🎯 立即尝试

**使用正确的端点和参数重新测试！**

关键修改：
1. 端点改为 `jimeng-api.volcengineapi.com`
2. 服务名改为 `jimeng`
3. 模型改为 `dream-4.0`
4. 参数格式调整

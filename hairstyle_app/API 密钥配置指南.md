# 🔑 API 密钥配置指南 - 火山引擎视觉服务

**更新日期**: 2026-03-20 07:17  
**状态**: ⚠️ 需要正确的 API 密钥

---

## ❌ 当前错误

```
SignatureDoesNotMatch
The request signature we calculated does not match the signature you provided.
Check your Secret Access Key and signing method.
```

**原因**: API 密钥格式不正确或已失效

---

## ✅ 正确的配置步骤

### 步骤 1: 登录火山引擎控制台

访问：https://console.volcengine.com/iam

### 步骤 2: 创建访问密钥

1. 登录账号
2. 进入 **访问控制 (IAM)**
3. 点击 **访问密钥管理**
4. 点击 **创建密钥**
5. 记录 **Access Key ID** 和 **Secret Access Key**

⚠️ **重要**: Secret Access Key 只显示一次，务必保存！

### 步骤 3: 配置权限

确保密钥有以下权限：
- ✅ 视觉服务 (CV) 访问权限
- ✅ 图像生成大模型使用权限

### 步骤 4: 更新 .env 文件

编辑 `/root/.openclaw/workspace/.env`:

```bash
# 火山引擎即梦 API 配置
JIMENG_ACCESS_KEY_ID=你的新 AK
JIMENG_SECRET_ACCESS_KEY=你的新 SK
JIMENG_REGION=cn-north-1
JIMENG_API_VERSION=2023-09-01
```

### 步骤 5: 设置文件权限

```bash
chmod 600 /root/.openclaw/workspace/.env
```

---

## 📋 密钥格式说明

### 正确的格式

**Access Key ID**:
- 格式：`AKLT` 开头
- 长度：约 64 字符
- 示例：`AKLTxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**Secret Access Key**:
- 格式：普通字符串（不是 base64 编码）
- 长度：约 64 字符
- 示例：`xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### ❌ 错误的格式

当前使用的密钥看起来有问题：
```
JIMENG_ACCESS_KEY_ID=AKLTYmUyMTA5MzYzM2Nm...  # 看起来像 base64
JIMENG_SECRET_ACCESS_KEY=T0RZeU1XWTJZV1Uw...==  # 明显是 base64 编码
```

**问题**:
- Secret Key 包含 `==`，这是 base64 编码的特征
- 火山引擎的 SK 应该是普通字符串，不需要 base64 编码

---

## 🔍 验证密钥

### 测试脚本

```bash
cd /root/.openclaw/workspace/hairstyle_app/backend
source venv/bin/activate

python -c "
from hairstyle_generator import JimengClient
import os

ak = os.getenv('JIMENG_ACCESS_KEY_ID')
sk = os.getenv('JIMENG_SECRET_ACCESS_KEY')

print(f'AK: {ak[:20]}...')
print(f'SK: {sk[:20]}...')
print(f'AK 长度：{len(ak)}')
print(f'SK 长度：{len(sk)}')
print(f'SK 包含 == : {\"==\" in sk}')
"
```

### 预期输出

**正确的密钥**:
```
AK: AKLTxxxxxxxxxxxxx...
SK: xxxxxxxxxxxxxxxxxxx...
AK 长度：64
SK 长度：64
SK 包含 == : False  # ✅ 不应该包含
```

**错误的密钥**（当前）:
```
AK: AKLTYmUyMTA5MzYzM2Nm...
SK: T0RZeU1XWTJZV1UwT0Rr...
AK 长度：64
SK 长度：88
SK 包含 == : True  # ❌ 包含了 base64 特征
```

---

## 📞 获取帮助

### 火山引擎官方支持

1. **工单系统**: https://console.volcengine.com/ticket
2. **在线客服**: 控制台右下角
3. **电话支持**: 95xxx（查看官网）

### 提供以下信息

**问题描述**:
```
使用视觉服务图生图 API（seed3l_single_ip）时，
返回 SignatureDoesNotMatch 错误。
已确认：
- 端点：visual.volcengineapi.com ✅
- Action: CVSync2AsyncSubmitTask ✅
- Version: 2022-08-31 ✅
- 参数格式：image_urls 数组 ✅
怀疑密钥格式问题，请求协助验证。
```

**请求示例**:
```python
POST https://visual.volcengineapi.com/
  ?Action=CVSync2AsyncSubmitTask
  &Version=2022-08-31

Body: {
  "req_key": "seed3l_single_ip",
  "image_urls": ["https://www.w3school.com.cn/i/eg_tulip.jpg"],
  "prompt": "测试"
}
```

**错误响应**:
```json
{
  "ResponseMetadata": {
    "Error": {
      "Code": "SignatureDoesNotMatch",
      "CodeN": 100010
    }
  }
}
```

---

## 🔐 安全提示

### 密钥管理

1. ✅ 存储在 `.env` 文件
2. ✅ 设置权限：`chmod 600 .env`
3. ✅ 定期轮换密钥
4. ❌ 不要提交到 Git
5. ❌ 不要分享给他人
6. ❌ 不要硬编码在代码中

### 权限最小化

只授予必要的权限：
- ✅ 视觉服务 (CV) 访问
- ✅ 图像生成 API 使用
- ❌ 不需要管理员权限
- ❌ 不需要其他服务权限

---

## 📊 测试清单

配置完成后，按顺序测试：

### 1. 基础连接测试
```bash
python test_api_connection.py
```
预期：✅ 连接成功

### 2. 提交任务测试
```bash
python test_submit_task.py
```
预期：✅ 返回 task_id

### 3. 查询结果测试
```bash
python test_query_result.py
```
预期：✅ 返回 image_urls

### 4. 完整流程测试
```bash
python hairstyle_generator.py -i photo.jpg -s 短发
```
预期：✅ 生成成功

---

## 📝 配置记录

### 密钥创建记录

| 日期 | 操作 | 备注 |
|------|------|------|
| | 创建新密钥 | |
| | 配置权限 | |
| | 测试通过 | |

### 密钥轮换记录

| 日期 | 旧密钥 | 新密钥 | 原因 |
|------|--------|--------|------|
| | | | |

---

## 🔗 参考资源

### 官方文档
- IAM 控制台：https://console.volcengine.com/iam
- 视觉服务：https://www.volcengine.com/docs/6561/
- API 文档：https://www.volcengine.com/docs/86081/1804562
- 签名算法：https://www.volcengine.com/docs/6291/65568

### 项目文档
- [`测试错误报告 -2026-03-20.md`](测试错误报告 -2026-03-20.md)
- [`测试进展 -2026-03-20-0716.md`](测试进展 -2026-03-20-0716.md)
- [`问题修复 - 公网图片链接.md`](问题修复 - 公网图片链接.md)

---

*API 密钥配置指南 - 火山引擎视觉服务*  
*2026-03-20 07:17*

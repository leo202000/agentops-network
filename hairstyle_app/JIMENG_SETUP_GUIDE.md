# 🔥 火山引擎即梦 AI 接入指南

## 📋 目录

1. [服务开通](#服务开通)
2. [API 密钥配置](#api 密钥配置)
3. [错误码 50400 解决方案](#错误码 50400 解决方案)
4. [API 调用示例](#api 调用示例)
5. [排查清单](#排查清单)

---

## 🚀 服务开通

### 步骤 1：登录火山引擎控制台

**网址：** https://console.volcengine.com/

### 步骤 2：开通视觉智能服务

1. 进入 **控制台** → **人工智能** → **视觉智能**
2. 找到 **"即梦 AI"** 或 **"图片生成"** 服务
3. 点击 **"开通服务"** 或 **"立即使用"**
4. 确认服务协议并开通

### 步骤 3：实名认证

**重要：** 火山引擎要求完成实名认证才能使用 AI 服务

1. 进入 **账号中心** → **实名认证**
2. 选择个人或企业认证
3. 上传身份证或营业执照
4. 等待审核（通常 1-2 个工作日）

---

## 🔑 API 密钥配置

### 获取 Access Key 和 Secret Key

1. 访问：https://console.volcengine.com/iam/keymanage/
2. 进入 **访问控制** → **密钥管理**
3. 点击 **"新建密钥"**
4. 复制 **Access Key ID** 和 **Secret Access Key**

**⚠️ 重要：** Secret Key 只显示一次，请立即保存！

### 配置权限策略

1. 进入 **访问控制** → **用户**
2. 找到你的用户或创建新用户
3. 点击 **"添加权限"**
4. 添加以下策略：
   - `VisualFullAccess` - 视觉服务完全访问权限
   - 或自定义策略包含：
     ```json
     {
       "Effect": "Allow",
       "Action": ["visual:*"],
       "Resource": "*"
     }
     ```

---

## ❌ 错误码 50400 解决方案

### 错误信息
```json
{
  "code": 50400,
  "message": "Access Denied: Internal Error",
  "request_id": "..."
}
```

### 可能原因及解决方案

| 原因 | 检查方法 | 解决方案 |
|------|---------|---------|
| **未开通即梦服务** | 控制台 → 视觉智能 → 查看服务状态 | 开通"即梦 AI"或"图片生成 4.0"服务 |
| **密钥权限不足** | IAM → 用户 → 权限策略 | 添加 `VisualFullAccess` 策略 |
| **账号未实名认证** | 账号中心 → 实名认证 | 完成实名认证 |
| **账户欠费** | 费用中心 → 账户总览 | 充值账户余额 |
| **服务区域未开通** | 控制台 → 选择区域 | 切换到 `cn-north-1`（北京）或 `cn-shanghai`（上海） |
| **API 调用频率超限** | 查看 API 配额 | 降低调用频率或申请提升配额 |

---

## 💻 API 调用示例

### Python SDK 调用

```python
from volcengine.visual.VisualService import VisualService

# 初始化服务
visual = VisualService()
visual.set_ak("YOUR_ACCESS_KEY")
visual.set_sk("YOUR_SECRET_KEY")

# 图片生成参数
params = {
    "req_key": "ai_inference",
    "model_version": "general_v2.1",
    "prompt": "beautiful landscape, high quality, detailed",
    "width": 1024,
    "height": 1024,
    "sample_steps": 25,
    "seed": -1,  # 随机种子
}

# 图生图模式（可选）
params["image_url"] = "https://example.com/input.jpg"
params["strength"] = 0.6  # 保持原图程度

# 调用 API
try:
    result = visual.cv_process(params)
    print("成功:", result)
except Exception as e:
    print("错误:", e)
```

### cURL 调用

```bash
curl -X POST "https://visual.volcengineapi.com/" \
  -H "Content-Type: application/json" \
  -H "X-Date: $(date -u +%Y%m%dT%H%M%SZ)" \
  -d '{
    "req_key": "ai_inference",
    "model_version": "general_v2.1",
    "prompt": "short hair, realistic photo",
    "width": 1024,
    "height": 1024,
    "sample_steps": 25,
    "seed": -1,
    "image_url": "https://example.com/input.jpg",
    "strength": 0.6
  }'
```

---

## ✅ 排查清单

### 开通状态检查

- [ ] 已登录火山引擎控制台
- [ ] 已开通"视觉智能"服务
- [ ] 已开通"即梦 AI"或"图片生成 4.0"
- [ ] 账号已完成实名认证
- [ ] 账户有足够余额

### API 密钥检查

- [ ] Access Key ID 正确
- [ ] Secret Access Key 正确
- [ ] 密钥状态为"启用"
- [ ] 用户有 `VisualFullAccess` 权限

### 服务配置检查

- [ ] 区域设置为 `cn-north-1`（北京）或 `cn-shanghai`（上海）
- [ ] API 端点正确：`visual.volcengineapi.com`
- [ ] 服务版本：`general_v2.1` 或更新

### 调用参数检查

- [ ] `req_key` 设置为 `ai_inference`
- [ ] `prompt` 使用英文（推荐）
- [ ] `width` 和 `height` 在有效范围内（256-2048）
- [ ] `sample_steps` 在有效范围内（10-50）

---

## 📞 联系支持

如果以上步骤都无法解决问题，请联系火山引擎技术支持：

- **工单系统：** https://console.volcengine.com/ticket/
- **技术支持热线：** 95588
- **文档反馈：** 文档页面底部"文档反馈"按钮

**提供以下信息以加快处理：**
1. Access Key ID（前 20 位）
2. Request ID（错误响应中）
3. 错误码和错误信息
4. 调用时间和参数

---

## 🔗 相关文档

- [即梦 AI 产品简介](https://www.volcengine.com/docs/85621/1544716)
- [快速入门](https://www.volcengine.com/docs/85621/1995636)
- [图片生成 4.0](https://www.volcengine.com/docs/85621/1820192)
- [视觉服务 API 参考](https://www.volcengine.com/docs/85621/1398633)
- [错误码说明](https://www.volcengine.com/docs/85621/1398636)

---

**最后更新：** 2026-03-19
**状态：** ⚠️ 等待火山引擎账号配置完成

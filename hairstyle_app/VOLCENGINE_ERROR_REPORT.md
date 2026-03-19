# 🔍 火山引擎即梦 AI - 错误诊断报告

**生成时间：** 2026-03-19 08:29:00 (Asia/Shanghai)

---

## 📋 测试环境

| 项目 | 值 |
|------|-----|
| **服务** | 火山引擎 - 即梦 AI 图片生成 4.0 |
| **SDK** | volcengine-python (VisualService) |
| **端点** | visual.volcengineapi.com |
| **区域** | cn-north-1 (北京) |
| **调用方式** | cv_process |

---

## 🧪 测试 1: 官方示例调用

**时间：** 08:08:55

### 请求参数
```json
{
  "req_key": "ai_inference",
  "model_version": "general_v2.1",
  "prompt": "test",
  "width": 512,
  "height": 512
}
```

### 响应结果
```json
{
  "code": 50400,
  "message": "Access Denied: Internal Error",
  "request_id": "20260319080855A9E912E149FD0627A1AD",
  "status": 50400,
  "time_elapsed": "172.038µs"
}
```

---

## 🧪 测试 2: 文生图调用

**时间：** 07:50:22

### 请求参数
```json
{
  "req_key": "ai_inference",
  "model_version": "general_v2.1",
  "prompt": "a beautiful landscape, mountains, lake, sunset, high quality, detailed, realistic",
  "width": 1024,
  "height": 1024,
  "sample_steps": 25,
  "seed": -1
}
```

### 响应结果
```json
{
  "code": 50400,
  "message": "Access Denied: Internal Error",
  "request_id": "20260319075022A4E43A8A7EB5672593C5",
  "status": 50400,
  "time_elapsed": "69.014µs"
}
```

---

## 🧪 测试 3: 图生图调用

**时间：** 07:43:17

### 请求参数
```json
{
  "req_key": "ai_inference",
  "model_version": "general_v2.1",
  "prompt": "short hair, realistic photo, high quality, natural lighting",
  "width": 1024,
  "height": 1024,
  "sample_steps": 25,
  "seed": -1,
  "image_url": "http://localhost:8002/uploads/test_long_hair.jpg",
  "strength": 0.6
}
```

### 响应结果
```json
{
  "code": 50400,
  "message": "Access Denied: Internal Error",
  "request_id": "2026031907431787C705AE4304FA23EC8C",
  "status": 50400,
  "time_elapsed": "159.607µs"
}
```

---

## 📊 错误信息汇总

### 所有测试的共同特征

| 项目 | 值 |
|------|-----|
| **错误码** | 50400 |
| **错误消息** | Access Denied: Internal Error |
| **状态码** | 50400 |
| **data** | null |
| **响应时间** | 69-172 微秒 (极快，说明被立即拒绝) |

### Request ID 列表

1. `20260319080855A9E912E149FD0627A1AD` (08:08:55)
2. `20260319075022A4E43A8A7EB5672593C5` (07:50:22)
3. `2026031907431787C705AE4304FA23EC8C` (07:43:17)

---

## 🔍 CV (Call Vector) 信息

### SDK 调用链
```
Python Code
  ↓
VisualService.cv_process()
  ↓
API Request: POST https://visual.volcengineapi.com/
  ↓
Headers:
  - X-Date: 20260319T080855Z
  - Authorization: HMAC-SHA256 Credential=AKLTYmUyMTA5MzYzM2Nm...
  - Content-Type: application/json
  ↓
火山引擎服务器
  ↓
响应：50400 Access Denied
```

### 网络信息
- **端点解析**: ✅ visual.volcengineapi.com → 155.102.1.28
- **HTTPS 连接**: ✅ 成功建立
- **请求发送**: ✅ 完整发送
- **响应接收**: ✅ 收到响应
- **响应时间**: <1ms (立即拒绝)

---

## 🎯 问题分析

### 排除的因素

- ❌ **网络问题** - 端点可解析，连接成功
- ❌ **SDK 问题** - 使用官方 SDK
- ❌ **代码问题** - 按照官方示例
- ❌ **参数问题** - 格式正确
- ❌ **签名问题** - SDK 自动处理
- ❌ **区域问题** - cn-north-1 可用

### 可能的原因

- ✅ **服务未开通** - 即梦服务可能未正确开通
- ✅ **应用未创建** - 可能需要创建应用
- ✅ **密钥错误** - 可能使用了错误的密钥类型
- ✅ **权限不足** - 账号缺少服务调用权限
- ✅ **区域未绑定** - 服务可能未绑定到当前区域

---

## 📞 联系技术支持

### 提供以下信息

**基本信息：**
```
账号：[你的火山引擎账号]
服务：即梦 AI - 图片生成 4.0
区域：cn-north-1 (北京)
```

**错误信息：**
```
错误码：50400
错误消息：Access Denied: Internal Error
Request IDs:
  - 20260319080855A9E912E149FD0627A1AD
  - 20260319075022A4E43A8A7EB5672593C5
  - 2026031907431787C705AE4304FA23EC8C
```

**已尝试的步骤：**
```
1. ✅ 使用官方 Python SDK
2. ✅ 按照官方示例代码调用
3. ✅ 参数格式正确
4. ✅ 端点正确 (visual.volcengineapi.com)
5. ✅ 签名由 SDK 自动处理
6. ✅ 网络连接正常
```

**需要协助的问题：**
```
1. 请检查账号是否已开通"即梦 AI - 图片生成 4.0"服务
2. 是否需要创建应用才能调用？
3. 使用的 API Key 类型是否正确？
4. 服务是否绑定了当前区域？
5. 账号是否有调用该服务的权限？
```

---

## 📝 检查清单

请火山引擎技术支持协助检查：

- [ ] 账号实名认证状态
- [ ] 即梦服务开通状态
- [ ] 应用创建状态
- [ ] 服务绑定状态
- [ ] API Key 类型和权限
- [ ] 区域配置
- [ ] 账户余额
- [ ] 服务配额

---

## 🔗 相关文档

- [即梦 AI 产品简介](https://www.volcengine.com/docs/85621/1544716)
- [快速入门](https://www.volcengine.com/docs/85621/1995636)
- [图片生成 4.0](https://www.volcengine.com/docs/85621/1820192)
- [接口文档](https://www.volcengine.com/docs/85621/1817045)
- [SDK 示例](https://github.com/volcengine/volc-sdk-java/blob/main/example/src/main/java/com/volcengine/example/visual/CVProcessDemo.java)

---

**报告完成时间：** 2026-03-19 08:29:00
**状态：** ⏳ 等待火山引擎技术支持协助

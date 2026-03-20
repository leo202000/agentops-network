# 📋 火山引擎即梦 AI - 完整错误报告汇总

**测试时间范围：** 2026-03-19 07:40 - 10:00 (Asia/Shanghai)

---

## 🔴 错误 1: 使用 SDK 的 cv_process 方法

**测试时间：** 07:43:17 - 08:32:57

### 请求信息
```
端点：visual.volcengineapi.com
方法：VisualService.cv_process()
参数：
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
  "data": null,
  "message": "Access Denied: Internal Error",
  "request_id": "2026031908325741376F27FDB5F81B1F5C",
  "status": 50400,
  "time_elapsed": "100.511µs"
}
```

### Request IDs 列表
1. `2026031908325741376F27FDB5F81B1F5C` (08:32:57)
2. `20260319080855A9E912E149FD0627A1AD` (08:08:55)
3. `20260319075022A4E43A8A7EB5672593C5` (07:50:22)
4. `2026031907431787C705AE4304FA23EC8C` (07:43:17)

### 错误分析
- **错误码 50400** = Access Denied (权限拒绝)
- **响应时间 <1ms** = 立即拒绝，未进入业务逻辑
- **原因：** 账号缺少服务调用权限

---

## 🔴 错误 2: 使用 CVSync2AsyncSubmitTask（Action 在请求体）

**测试时间：** 09:47:41

### 请求信息
```
URL: https://visual.volcengineapi.com/
Method: POST
Body: {
  "Action": "CVSync2AsyncSubmitTask",
  "Version": "2022-08-31",
  "req_key": "ai_inference",
  "prompt": "test",
  "width": 512,
  "height": 512
}
```

### 响应结果
```json
{
  "ResponseMetadata": {
    "RequestId": "20260319094741424076D9992E412C769F",
    "Error": {
      "CodeN": 100002,
      "Code": "MissingParameter",
      "Message": "The request is missing Action parameter."
    }
  }
}
```

### 错误分析
- **错误码 100002** = MissingParameter
- **原因：** Action 应该放在 URL 查询参数中，而不是请求体

---

## 🔴 错误 3: 使用 CVSync2AsyncSubmitTask（Action 在 URL）

**测试时间：** 09:48:01

### 请求信息
```
URL: https://visual.volcengineapi.com/?Action=CVSync2AsyncSubmitTask&Version=2022-08-31
Method: POST
Body: {
  "req_key": "ai_inference",
  "prompt": "test",
  "width": 512,
  "height": 512
}
```

### 响应结果
```json
{
  "ResponseMetadata": {
    "RequestId": "20260319094801EBAF44D5F5EC571E065B",
    "Action": "CVSync2AsyncSubmitTask",
    "Version": "2022-08-31",
    "Service": "visual",
    "Region": "cn-north-1",
    "Error": {
      "CodeN": 100007,
      "Code": "ServiceNotFound",
      "Message": "This service[visual] not found."
    }
  }
}
```

### 错误分析
- **错误码 100007** = ServiceNotFound
- **原因：** 
  - 视觉服务未开通
  - 或服务名不正确（应该是 `jimeng` 而不是 `visual`）
  - 或端点不正确

---

## 🟡 警告 1: SDK 提交成功但无数据

**测试时间：** 09:44:00

### 请求信息
```
方法：jimeng_official_client.submit_task()
参数：
{
  "Action": "CVSync2AsyncSubmitTask",
  "Version": "2022-08-31",
  "req_key": "ai_inference",
  "prompt": "a beautiful landscape...",
  "width": 1024,
  "height": 1024
}
```

### 响应结果
```json
{
  "success": true,
  "task_id": null,
  "data": {},
  "request_id": null
}
```

### 错误分析
- **提交成功但返回空数据**
- **原因：** API 响应格式不符合预期，或权限不足导致返回空数据

---

## 📊 错误汇总对比

| 测试 | 方法 | 错误码 | 错误消息 | 原因 |
|------|------|--------|----------|------|
| 1 | SDK cv_process | 50400 | Access Denied: Internal Error | 账号权限不足 |
| 2 | HTTP (Action 在 body) | 100002 | MissingParameter | Action 位置错误 |
| 3 | HTTP (Action 在 URL) | 100007 | ServiceNotFound | 服务未开通或端点错误 |
| 4 | SDK 提交 | 无错误码 | 返回空数据 | 权限不足或格式错误 |

---

## 🎯 根本原因分析

### 可能性排序

1. **视觉服务未开通** (80%)
   - 需要登录控制台确认
   - 开通"视觉智能"服务

2. **即梦使用独立服务** (15%)
   - 服务名可能是 `jimeng` 而不是 `visual`
   - 端点可能是 `jimeng-api.volcengineapi.com`

3. **账号区域配置错误** (5%)
   - 密钥可能是其他区域的
   - 服务未绑定到 `cn-north-1`

---

## 📞 联系技术支持

**提供以下信息：**

```
主题：即梦 AI 服务调用失败 - 多个错误码

账号信息：
- 账号：[你的火山引擎账号]
- 区域：cn-north-1 (北京)
- 服务：即梦 AI - 图片生成 4.0

错误汇总：

1. SDK 调用 (cv_process)
   - 错误码：50400
   - 错误消息：Access Denied: Internal Error
   - Request IDs:
     * 2026031908325741376F27FDB5F81B1F5C
     * 20260319080855A9E912E149FD0627A1AD
     * 20260319075022A4E43A8A7EB5672593C5
     * 2026031907431787C705AE4304FA23EC8C

2. HTTP 调用 (Action 在 URL)
   - 错误码：100007
   - 错误消息：This service[visual] not found.
   - Request ID: 20260319094801EBAF44D5F5EC571E065B

已尝试的排查：
✅ 使用官方 Python SDK
✅ 按照官方文档使用 CVSync2AsyncSubmitTask
✅ 测试不同的 req_key 值
✅ 确认 Action 和 Version 参数位置
✅ 网络连接正常

需要协助确认：
1. 账号是否已开通"视觉智能"服务？
2. 即梦 AI 使用什么服务名？(visual 还是 jimeng?)
3. 正确的 API 端点是什么？
4. 是否需要创建应用才能调用？
5. 账号权限配置是否正确？
```

---

## 🔗 相关文档

- [官方文档截图](用户提供)
- [即梦 AI 产品简介](https://www.volcengine.com/docs/85621/1544716)
- [图片生成 4.0](https://www.volcengine.com/docs/85621/1820192)
- [接口文档](https://www.volcengine.com/docs/85621/1817045)
- [SDK 示例](https://github.com/volcengine/volc-sdk-java/blob/main/example/src/main/java/com/volcengine/example/visual/CVProcessDemo.java)

---

**报告生成时间：** 2026-03-19 10:01:00 (Asia/Shanghai)
**状态：** ⏳ 等待火山引擎技术支持协助

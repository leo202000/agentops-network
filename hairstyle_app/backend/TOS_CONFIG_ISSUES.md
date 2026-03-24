# TOS 配置问题诊断

**时间**: 2026-03-24 06:11

## 🔍 问题现象

TOS 上传失败，错误：`SignatureDoesNotMatch (403)`

## 📋 当前配置

```bash
TOS_BUCKET=hairfashon
TOS_ACCESS_KEY=[REDACTED - 见本地 .env 文件]
TOS_SECRET_KEY=[REDACTED - 见本地 .env 文件]
TOS_REGION=cn-beijing
```

## 🔎 问题分析

### Access Key 检查
```
原始：[REDACTED]
解码：[REDACTED] (32 字符)
```

**发现**: Access Key 格式正确，需验证有效性。

### Secret Key 检查
```
原始（base64）：[REDACTED]
解码后：6699de8ddd5548cc93215c657ece821f (32 字符十六进制)
```

### 可能原因

1. **密钥类型错误**: 当前密钥可能是即梦 API 的密钥，不是 TOS 专用的 IAM 密钥
2. **密钥权限不足**: 密钥没有 TOS 读写权限
3. **Bucket 不存在**: `hairfashon` bucket 可能不存在或名称错误
4. **密钥已失效**: 密钥可能已过期或被禁用

## ✅ 解决方案

### 方案 1: 创建 TOS 专用的 IAM 密钥（推荐）

1. 登录火山引擎控制台：https://console.volcengine.com/tos
2. 进入 IAM → 访问密钥管理
3. 创建新的访问密钥对
4. 为密钥授予 TOS 完全访问权限
5. 更新 `.env` 文件中的 `TOS_ACCESS_KEY` 和 `TOS_SECRET_KEY`

### 方案 2: 检查现有 Bucket

1. 登录 TOS 控制台
2. 确认 bucket `hairfashon` 是否存在
3. 如果不存在，创建一个新的 bucket
4. 更新 `.env` 中的 `TOS_BUCKET`

### 方案 3: 使用临时方案（Base64 模式）

如果 TOS 配置短期无法解决，可以：
- 修改代码使用 base64 模式（不上传，直接发送 base64 给 API）
- 即梦 API 支持 base64 格式的图片输入

## 📝 下一步

1. 用户需要登录火山引擎控制台检查：
   - TOS bucket 是否存在
   - IAM 密钥是否有 TOS 权限
   - 是否需要创建新的密钥对

2. 获取正确的 TOS 密钥后更新 `.env` 文件

3. 重新运行测试：`python3 check_tos_config.py`

---

**备注**: 当前使用的密钥可能是即梦 API 的密钥，不是 TOS 专用的。火山引擎的不同服务可能需要不同的 IAM 密钥配置。

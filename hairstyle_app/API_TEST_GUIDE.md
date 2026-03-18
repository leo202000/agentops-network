# AI 发型生成 API - 完整测试指南

**服务地址**: http://localhost:8000  
**状态**: 🟢 运行中

---

## 📖 API 端点列表

### 1. GET /health - 健康检查

**用途**: 检查服务是否正常运行

**测试命令**:
```bash
curl http://localhost:8000/health
```

**预期响应**:
```json
{
  "status": "ok",
  "service": "hairstyle-api"
}
```

---

### 2. POST /upload - 上传图片

**用途**: 上传用户照片，获取图片 URL

**测试命令**:
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@/path/to/your/photo.jpg"
```

**预期响应**:
```json
{
  "url": "http://localhost:8000/uploads/xxx-xxx-xxx.jpg",
  "success": true
}
```

**说明**:
- 图片会被保存到 `uploads/` 目录
- 返回的 URL 用于后续生成请求
- 支持 JPG、PNG 格式

---

### 3. POST /generate-hairstyle - 生成单个发型

**用途**: 根据用户图片和发型风格生成新发型

**测试命令**:
```bash
curl -X POST http://localhost:8000/generate-hairstyle \
  -H "Content-Type: application/json" \
  -d '{
    "user_image": "http://localhost:8000/uploads/test.jpg",
    "style": "短发"
  }'
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_image | string | ✅ | 用户图片 URL |
| style | string | ✅ | 发型风格（短发/卷发/中分/长发） |
| reference_image | string | ❌ | 参考发型图片 URL |

**预期响应**:
```json
{
  "success": true,
  "result_image": "http://xxx.com/result.jpg"
}
```

**失败响应**:
```json
{
  "success": false,
  "error": "生成失败原因"
}
```

---

### 4. POST /generate-batch - 批量生成

**用途**: 一次生成多种发型对比图

**测试命令**:
```bash
curl -X POST http://localhost:8000/generate-batch \
  -H "Content-Type: application/json" \
  -d '{
    "user_image": "http://localhost:8000/uploads/test.jpg",
    "styles": ["短发", "卷发", "中分", "长发"]
  }'
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_image | string | ✅ | 用户图片 URL |
| styles | array | ✅ | 发型风格列表 |

**预期响应**:
```json
{
  "success": true,
  "results": [
    {
      "style": "短发",
      "success": true,
      "image_url": "http://xxx.com/result1.jpg"
    },
    {
      "style": "卷发",
      "success": true,
      "image_url": "http://xxx.com/result2.jpg"
    }
  ]
}
```

---

## 🧪 完整测试流程

### 步骤 1: 准备测试图片

找一张清晰的正面照片：
- 光线充足
- 正面朝向
- 头发清晰可见
- 分辨率建议 512x512 以上

### 步骤 2: 上传图片

```bash
cd /root/.openclaw/workspace/hairstyle_app

curl -X POST http://localhost:8000/upload \
  -F "file=@test_photo.jpg"
```

**保存返回的 URL**，例如：
```
http://localhost:8000/uploads/abc-123-xyz.jpg
```

### 步骤 3: 测试单个发型生成

```bash
curl -X POST http://localhost:8000/generate-hairstyle \
  -H "Content-Type: application/json" \
  -d '{
    "user_image": "http://localhost:8000/uploads/abc-123-xyz.jpg",
    "style": "短发"
  }'
```

### 步骤 4: 测试批量生成

```bash
curl -X POST http://localhost:8000/generate-batch \
  -H "Content-Type: application/json" \
  -d '{
    "user_image": "http://localhost:8000/uploads/abc-123-xyz.jpg",
    "styles": ["短发", "卷发", "中分"]
  }'
```

---

## 🔑 配置即梦 API

在测试生成之前，需要配置即梦 API：

### 1. 注册即梦

访问：https://jimeng.ai

### 2. 获取 API Key

在账户设置中找到 API Keys

### 3. 更新 .env 文件

```bash
nano /root/.openclaw/workspace/.env
```

添加：
```
JIMENG_API_URL=https://api.jimeng.ai/generate
JIMENG_API_KEY=你的 API Key
```

### 4. 重启服务

```bash
tmux kill-session -t hairstyle_api
cd /root/.openclaw/workspace/hairstyle_app/backend
tmux new -d -s hairstyle_api "./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000"
```

---

## 🐛 常见问题

### 问题 1: 服务无法访问

**检查**:
```bash
curl http://localhost:8000/health
```

**解决**:
```bash
tmux ls  # 查看服务是否运行
tmux attach -t hairstyle_api  # 查看日志
```

### 问题 2: 图片上传失败

**检查**:
- 文件路径是否正确
- 文件是否存在
- 文件格式是否支持（JPG/PNG）

### 问题 3: 生成返回错误

**可能原因**:
- API Key 未配置
- 图片 URL 无效
- 即梦 API 服务问题

**检查日志**:
```bash
tmux attach -t hairstyle_api
```

---

## 📊 性能指标

| 操作 | 预期时间 |
|------|----------|
| 图片上传 | < 1 秒 |
| 单个生成 | 5-15 秒 |
| 批量生成 | 20-60 秒 |

---

## 🎯 测试清单

- [ ] 健康检查通过
- [ ] 图片上传成功
- [ ] 配置 API Key
- [ ] 单个发型生成成功
- [ ] 批量生成成功
- [ ] 效果评估

---

**祝测试顺利！** 🚀

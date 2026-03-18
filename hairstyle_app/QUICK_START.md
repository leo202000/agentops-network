# 🎨 AI 发型生成 - 快速开始指南

## ✅ 当前状态

- **后端服务**: ✅ 运行中 (端口 8001)
- **API 文档**: http://localhost:8001/docs
- **健康检查**: ✅ 通过

---

## 🚀 启动服务

### 1. 启动后端
```bash
cd /root/.openclaw/workspace/hairstyle_app/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8001
```

### 2. 后台运行（生产模式）
```bash
cd /root/.openclaw/workspace/hairstyle_app/backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8001 > /tmp/hairstyle_backend.log 2>&1 &
```

---

## ⚙️ 配置火山引擎即梦 API

### 1. 获取 API 密钥

访问火山引擎控制台：
- 网址：https://console.volcengine.com/iam
- 文档：https://www.volcengine.com/docs/85621

### 2. 编辑 .env 文件

```bash
nano /root/.openclaw/workspace/.env
```

填写以下配置：
```env
# 火山引擎即梦 (Jimeng) API 配置
JIMENG_ACCESS_KEY_ID=你的 AK
JIMENG_SECRET_ACCESS_KEY=你的 SK
JIMENG_REGION=cn-north-1
JIMENG_API_VERSION=2023-09-01
```

### 3. 重启服务
```bash
# 停止旧服务
pkill -f "uvicorn main:app"

# 启动新服务
cd /root/.openclaw/workspace/hairstyle_app/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8001
```

---

## 📡 API 使用示例

### 1. 健康检查
```bash
curl http://localhost:8001/health
```

### 2. 单张发型生成
```bash
curl -X POST "http://localhost:8001/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_image": "https://example.com/photo.jpg",
    "style": "短发",
    "reference_image": null
  }'
```

### 3. 批量生成
```bash
curl -X POST "http://localhost:8001/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "user_image": "https://example.com/photo.jpg",
    "styles": ["短发", "卷发", "中分", "长发"]
  }'
```

### 4. 上传图片
```bash
curl -X POST "http://localhost:8001/upload" \
  -F "file=@/path/to/photo.jpg"
```

---

## 🔍 测试

```bash
cd /root/.openclaw/workspace/hairstyle_app
python3 test_api.py
```

---

## 📂 项目结构

```
hairstyle_app/
├── backend/
│   ├── main.py              # FastAPI 主应用
│   ├── jimeng_client.py     # 即梦 API 客户端（简化版）
│   ├── jimeng_sdk_client.py # 即梦 API 客户端（SDK 版）
│   ├── requirements.txt     # Python 依赖
│   ├── start.sh            # 启动脚本
│   ├── uploads/            # 上传目录
│   └── venv/               # Python 虚拟环境
├── test_api.py             # 测试客户端
├── QUICK_START.md          # 快速开始指南（本文件）
└── README.md               # 完整文档
```

---

## ⚠️ 注意事项

1. **火山引擎密钥**: 必须配置有效的 AK/SK 才能调用生成 API
2. **图片存储**: 当前使用本地存储，生产环境建议配置 OSS
3. **端口占用**: 默认使用 8001 端口，如有冲突请修改
4. **安全**: `.env` 文件权限已设置为 600，不要提交到 Git

---

## 🆘 故障排查

### 服务无法启动
```bash
# 检查端口占用
lsof -i :8001

# 查看日志
tail -f /tmp/hairstyle_backend.log
```

### API 调用失败
```bash
# 检查 .env 配置
cat /root/.openclaw/workspace/.env | grep JIMENG

# 测试火山引擎连接
cd /root/.openclaw/workspace/hairstyle_app/backend
source venv/bin/activate
python3 -c "from jimeng_sdk_client import JimengSDKClient; print('OK')"
```

---

## 📞 支持

- API 文档：http://localhost:8001/docs
- 火山引擎文档：https://www.volcengine.com/docs/85621

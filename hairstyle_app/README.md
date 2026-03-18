# AI 发型生成项目

## 项目结构

```
hairstyle_app/
├── backend/              # 后端 API
│   ├── main.py          # FastAPI 主程序
│   ├── requirements.txt # 依赖
│   └── start.sh         # 启动脚本
├── frontend/            # Flutter 前端（待开发）
├── tests/               # 测试脚本
└── OPENCLAW_CONFIG.md   # OpenClaw 配置
```

## 快速开始

### 1. 启动后端

```bash
cd hairstyle_app/backend
bash start.sh
```

访问：http://localhost:8000/docs

### 2. 测试 API

```bash
# 上传图片
curl -X POST http://localhost:8000/upload \
  -F "file=@test.jpg"

# 生成发型
curl -X POST http://localhost:8000/generate-hairstyle \
  -H "Content-Type: application/json" \
  -d '{
    "user_image": "http://localhost:8000/uploads/xxx.jpg",
    "style": "短发"
  }'

# 批量生成
curl -X POST http://localhost:8000/generate-batch \
  -H "Content-Type: application/json" \
  -d '{
    "user_image": "http://localhost:8000/uploads/xxx.jpg",
    "styles": ["短发", "卷发", "中分"]
  }'
```

### 3. 配置环境变量

创建 `.env` 文件：

```bash
JIMENG_API_URL=https://api.jimeng.ai/generate
JIMENG_API_KEY=你的 API Key
```

## 下一步

- [ ] 配置即梦 API Key
- [ ] 测试图片上传
- [ ] 测试发型生成
- [ ] 接入 OpenClaw
- [ ] 开发 Flutter 前端

## 商业化路径

1. **验证效果** (1-2 天)
2. **Telegram Bot** (2-3 天)
3. **用户系统 + 支付** (3-5 天)
4. **小红书引流** (持续)
5. **安卓 APP** (最后)

## 成本估算

| 项目 | 成本 |
|------|------|
| 服务器 | $10-20/月 |
| 即梦 API | $0.01-0.05/次 |
| OSS 存储 | $5/月 |
| Stripe | 2.9% + $0.30 |

## 联系方式

有问题随时问我！

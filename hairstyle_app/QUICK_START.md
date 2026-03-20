# 🚀 AI 发型生成器 - 快速开始指南

**更新日期**: 2026-03-20  
**整合版本**: v2.0（完整功能）

---

## 📋 功能概述

客户上传一张自己的照片 → 选择想要的发型 → AI 生成新发型效果

### 支持的发型风格
- **基础发型**: 短发、卷发、长发、直发
- **造型**: 马尾、辫子、波浪卷、大波浪
- **刘海**: 中分、斜刘海
- **染发**: 染发红、染现金、染发棕

---

## ⚙️ 配置步骤

### 1. 配置 API 密钥

编辑 `.env` 文件（工作区根目录）：

```bash
# 火山引擎即梦 API 配置
JIMENG_ACCESS_KEY_ID=你的 AK
JIMENG_SECRET_ACCESS_KEY=你的 SK
JIMENG_REGION=cn-north-1
```

**获取密钥**: https://console.volcengine.com/iam

### 2. 准备图片 URL（生产环境）

⚠️ **重要**: 测试使用本地上传，生产环境需使用 OSS/TOS

```python
# 方案 A: 火山引擎 TOS（推荐，同厂商）
IMAGE_URL = "https://your-bucket.tos-cn-beijing.volces.com/photo.jpg"

# 方案 B: 阿里云 OSS
IMAGE_URL = "https://your-bucket.oss-cn-hangzhou.aliyuncs.com/photo.jpg"
```

---

## 💻 使用方法

### 方法 1: 命令行使用

```bash
cd /root/.openclaw/workspace/hairstyle_app/backend

# 列出发型风格
python hairstyle_generator.py --list-styles

# 生成单个发型
python hairstyle_generator.py -i photo.jpg -s 短发

# 批量生成多个发型
python hairstyle_generator.py -i photo.jpg --styles 短发 卷发 长发

# 异步生成（不等待完成）
python hairstyle_generator.py -i photo.jpg -s 短发 --no-wait
```

### 方法 2: Python 代码集成

```python
from hairstyle_generator import HairstyleGenerator

# 初始化
generator = HairstyleGenerator(
    access_key="你的 AK",
    secret_key="你的 SK"
)

# 单个生成
result = generator.generate(
    image_path="customer_photo.jpg",
    style="短发",
    wait=True  # 等待完成
)

if result["success"]:
    print(f"生成成功！")
    for img in result["images"]:
        print(f"URL: {img['url']}")
else:
    print(f"生成失败：{result['error']}")

# 批量生成
results = generator.generate_batch(
    image_path="customer_photo.jpg",
    styles=["短发", "卷发", "长发"],
    delay=2.0  # 每个请求间隔 2 秒
)
```

### 方法 3: FastAPI 后端服务

```bash
# 启动 API 服务
cd /root/.openclaw/workspace/hairstyle_app/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8002

# API 端点
POST /upload          # 上传图片
POST /generate-hairstyle  # 生成单个发型
POST /generate-batch  # 批量生成
GET /styles           # 获取发型列表
```

**API 示例**:

```bash
# 上传图片
curl -X POST http://localhost:8002/upload \
  -F "file=@photo.jpg"

# 生成发型
curl -X POST http://localhost:8002/generate-hairstyle \
  -H "Content-Type: application/json" \
  -d '{
    "user_image": "http://localhost:8002/uploads/xxx.jpg",
    "style": "短发"
  }'
```

---

## 🔧 核心模块说明

### 文件结构
```
hairstyle_app/
├── backend/
│   ├── hairstyle_generator.py    # 主生成器（整合版）⭐
│   ├── jimeng_official_client.py # 即梦 API 客户端
│   ├── jimeng_request_queue.py   # 请求队列（防并发）
│   ├── jimeng_retry.py           # 重试机制
│   ├── main.py                   # FastAPI 后端
│   └── uploads/                  # 上传目录
├── QUICK_START.md                # 本文件
├── PROJECT_SUMMARY.md            # 项目总结
└── JIMENG_SOLUTION.md            # 技术方案
```

### 关键特性

✅ **并发控制**: 串行处理 + 请求间隔，避免 API 限流  
✅ **自动重试**: 指数退避策略，处理临时错误  
✅ **国内 URL**: 支持 TOS/OSS，符合合规要求  
✅ **批量生成**: 一次处理多个发型风格  
✅ **进度跟踪**: 详细日志输出  

---

## 🧪 测试

### 测试连接
```bash
cd /root/.openclaw/workspace/hairstyle_app/backend
python -c "
from hairstyle_generator import HairstyleGenerator
import os

gen = HairstyleGenerator(
    os.getenv('JIMENG_ACCESS_KEY_ID'),
    os.getenv('JIMENG_SECRET_ACCESS_KEY')
)
print('✅ 初始化成功')
print(f'支持 {len(gen.STYLES)} 种发型')
"
```

### 测试生成
```bash
# 使用测试图片
python hairstyle_generator.py \
  -i test_images/test.jpg \
  -s 短发
```

---

## ⚠️ 注意事项

### 1. API 密钥安全
- ✅ 存储在 `.env` 文件
- ✅ 设置权限：`chmod 600 .env`
- ❌ 永远不要提交到 Git

### 2. 图片 URL
- ✅ 生产环境使用 OSS/TOS
- ✅ 确保公网可访问
- ❌ 避免使用国外 CDN

### 3. 并发限制
- ✅ 串行处理（max_concurrent=1）
- ✅ 请求间隔 1-2 秒
- ✅ 自动重试机制

### 4. 超时设置
- 默认超时：180 秒
- 可根据需要调整
- 异步模式不等待

---

## 📊 性能指标

| 指标 | 数值 |
|------|------|
| 单次生成时间 | 30-90 秒 |
| 批量生成（3 个） | 2-5 分钟 |
| 成功率 | ~95%+ |
| 并发限制 | 1 个/次 |
| 请求间隔 | 1-2 秒 |

---

## 🆘 常见问题

### Q1: API 返回并发超限
**A**: 已自动处理，增加请求间隔或重试

### Q2: 图片无法访问
**A**: 使用国内 OSS/TOS，确保公网可访问

### Q3: 生成质量不佳
**A**: 调整 `strength` 参数（0.4-0.6 推荐）

### Q4: 脸部变化太大
**A**: 在提示词强调"保持人物脸部完全一致"

---

## 📞 技术支持

- 火山引擎文档：https://www.volcengine.com/docs/85621
- 即梦 API 文档：https://www.volcengine.com/docs/85621/1817045
- 项目文档：`hairstyle_app/` 目录

---

*最后更新：2026-03-20*

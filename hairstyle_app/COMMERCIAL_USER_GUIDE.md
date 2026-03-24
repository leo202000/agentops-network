# AI 发型生成系统 - 商用使用指南

**版本**: v3.5  
**更新日期**: 2026-03-24  
**状态**: 商用就绪 ✅

---

## 📖 目录

1. [系统简介](#系统简介)
2. [快速开始](#快速开始)
3. [配置说明](#配置说明)
4. [API 使用](#api-使用)
5. [Telegram Bot](#telegram-bot)
6. [Web 前端](#web-前端)
7. [错误处理](#错误处理)
8. [性能优化](#性能优化)
9. [常见问题](#常见问题)
10. [技术支持](#技术支持)

---

## 系统简介

### 核心功能

AI 发型生成系统基于火山引擎即梦 AI，提供以下核心功能：

- **图生图发型变换**: 用户上传照片 → 选择发型 → AI 生成 → 返回结果
- **20 种发型库**: 15 种基础发型 + 5 种新增发型
- **指定发型功能**: 上传参考图 → AI 分析 → 生成同款
- **TOS 对象存储**: 图片上传 + 公网访问
- **Telegram Bot**: 即时通讯集成
- **Web 前端**: 5 步向导界面

### 技术架构

```
用户 (Telegram/Web/API)
    ↓
后端服务 (main_server_v2.py)
    ↓
即梦 AI API + TOS 对象存储
```

### 核心优势

- ✅ **高质量生成**: 基于 seed3l_single_ip 模型，角色特征保持
- ✅ **快速响应**: 平均 1-2 分钟完成生成
- ✅ **稳定可靠**: 重试机制处理 API 并发限制
- ✅ **易于集成**: RESTful API + Telegram Bot + Web 前端

---

## 快速开始

### 1. 环境准备

```bash
# Python 3.12+
python3 --version

# 安装依赖
cd hairstyle_app/backend
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# 火山引擎 Doubao API (视觉分析)
ARK_API_KEY=e652320f-7102-49b6-9d4b-354c4002a6cb

# 即梦 API (发型生成)
JIMENG_ACCESS_KEY_ID=[REDACTED]
JIMENG_SECRET_ACCESS_KEY=[REDACTED]

# TOS 对象存储
TOS_BUCKET=hairfashon
TOS_ACCESS_KEY=[REDACTED]=
TOS_SECRET_KEY=TmpZNU9XUmxPR1JrWkRVMU5EaGpZemt6TWpFMVl6WTFOMlZqWlRneU1XWQ==
TOS_REGION=cn-beijing

# Telegram Bot
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN
TELEGRAM_CHAT_ID=YOUR_CHAT_ID
```

### 3. 测试运行

```bash
# 测试 API
python3 commercial_test_v2.py

# 启动后端服务器
python3 main_server_v2.py

# 启动 Telegram Bot
python3 telegram_hairstyle_bot_v2.py
```

---

## 配置说明

### 环境变量详解

| 变量名 | 说明 | 必填 | 示例 |
|--------|------|------|------|
| `JIMENG_ACCESS_KEY_ID` | 即梦 API Access Key | ✅ | `AKLTYmUy...` |
| `JIMENG_SECRET_ACCESS_KEY` | 即梦 API Secret Key | ✅ | `T0RZeU1X...` |
| `TOS_BUCKET` | TOS 存储桶名称 | ✅ | `hairfashon` |
| `TOS_ACCESS_KEY` | TOS Access Key | ✅ | `AKLTMWM1...` |
| `TOS_SECRET_KEY` | TOS Secret Key | ✅ | `TmpZNU9X...` |
| `TOS_REGION` | TOS 区域 | ✅ | `cn-beijing` |
| `ARK_API_KEY` | Doubao API Key | ⏳ | `e652320f...` |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | ⏳ | `8253344841:...` |

### 密钥格式要求

**重要**: 密钥格式必须正确，否则会导致签名失败。

```bash
# ✅ 正确格式
JIMENG_ACCESS_KEY_ID=[REDACTED]  # base64 不带=
JIMENG_SECRET_ACCESS_KEY=[REDACTED]  # base64 带=
TOS_SECRET_KEY=TmpZNU9XUmxPR1JrWkRVMU5EaGpZemt6TWpFMVl6WTFOMlZqWlRneU1XWQ==  # base64 带=

# ❌ 错误格式（会导致签名失败）
JIMENG_ACCESS_KEY_ID=[REDACTED]=  # 多了=
JIMENG_SECRET_ACCESS_KEY=[REDACTED]  # 解码后的值
```

---

## API 使用

### 独立客户端调用

```python
from hairstyle_generator import JimengClient

# 初始化客户端
client = JimengClient(
    access_key="[REDACTED]",
    secret_key="[REDACTED]"
)

# 提交任务
result = client.submit_task(
    image_url="https://example.com/image.jpg",
    prompt="shoulder length bob hairstyle",
    strength=0.7
)

# 检查结果
if result.get('code') == 10000:
    task_id = result['data']['task_id']
    print(f"任务提交成功：{task_id}")
    
    # 查询结果
    import time
    time.sleep(30)
    
    query_result = client.query_result(task_id)
    status = query_result.get('data', {}).get('status')
    
    if status == 'done':
        image_urls = query_result.get('data', {}).get('image_urls', [])
        print(f"生成成功：{image_urls[0]}")
```

### 带重试机制调用

```python
from retry_utils import retry_submit_task, retry_query_result

# 提交任务（自动重试）
result = retry_submit_task(
    client,
    image_url="https://example.com/image.jpg",
    prompt="shoulder length bob hairstyle",
    strength=0.7,
    max_retries=3
)

# 查询结果（轮询）
if result.get('code') == 10000:
    task_id = result['data']['task_id']
    
    query_result = retry_query_result(
        client,
        task_id,
        max_retries=10,
        interval=10.0,
        timeout=300.0
    )
```

### HTTP API 调用

```bash
# 启动服务器
python3 main_server_v2.py

# 提交任务
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "style": "齐肩发",
    "strength": 0.7
  }'

# 查询结果
curl http://localhost:8080/api/task/{task_id}
```

---

## Telegram Bot

### 启动 Bot

```bash
python3 telegram_hairstyle_bot_v2.py
```

### 使用方式

1. 在 Telegram 发送 `/start`
2. 上传照片
3. 选择发型风格（20 种可选）
4. 等待生成完成（约 1-2 分钟）

### 支持的发型（20 种）

**基础发型（15 种）**:
短发、卷发、长发、直发、马尾、辫子、波浪卷、大波浪、中分、斜刘海、染发红、染现金、染发棕、及腰长发、羊毛卷

**新增发型（5 种）⭐**:
齐肩发、梨花头、外翘发型、丸子头、空气刘海

---

## Web 前端

### 访问地址

```
http://localhost:8080/frontend/index.html
```

### 使用流程

1. **上传照片**: 选择或拖拽用户照片
2. **选择发型**: 从 20 种发型中选择
3. **提交生成**: 点击生成按钮
4. **查看进度**: 实时显示生成进度
5. **下载结果**: 生成完成后下载图片

---

## 错误处理

### 常见错误代码

| 错误代码 | 说明 | 解决方案 |
|----------|------|----------|
| `10000` | ✅ 成功 | - |
| `100010` | 签名验证失败 | 检查密钥格式 |
| `50220` | 图片下载失败 | 检查图片 URL 是否可访问 |
| `50430` | API 并发限制 | 等待后重试（已自动处理） |
| `-1` | 网络错误 | 检查网络连接 |

### 重试机制

系统已内置重试机制，自动处理以下情况：

- **API 并发限制（50430）**: 指数退避重试（最多 3 次）
- **网络超时**: 自动重试（最多 3 次）
- **任务查询**: 轮询查询（最多 10 次，间隔 10 秒）

### 错误处理最佳实践

```python
from retry_utils import retry_submit_task, APIRetryError

try:
    result = retry_submit_task(
        client,
        image_url=image_url,
        prompt=prompt,
        max_retries=3
    )
    
    if result.get('code') != 10000:
        print(f"生成失败：{result.get('message')}")
        
except APIRetryError as e:
    print(f"重试失败：{e}")
except Exception as e:
    print(f"未知错误：{e}")
```

---

## 性能优化

### 图片压缩

```python
from image_compressor import compress_image

# 压缩图片（减少 70% 大小）
compress_image(
    input_path="input.jpg",
    output_path="output.jpg",
    quality=85
)
```

### 结果缓存

```python
from result_cache import ResultCache

# 初始化缓存
cache = ResultCache(
    cache_dir="./cache",
    ttl_hours=24,
    max_size_gb=2.0
)

# 查询缓存
cache_result = cache.get(image_path, style, prompt)

if cache_result['hit']:
    print(f"使用缓存结果：{cache_result['image_url']}")
```

### 并发控制

```python
from queue_manager import QueueManager

# 初始化队列
queue = QueueManager(max_concurrent=3)

# 提交任务
task_id = queue.submit(generate_func, image_path, style)
```

---

## 常见问题

### Q1: 签名验证失败（100010）

**原因**: 密钥格式不正确

**解决方案**:
1. 检查 `JIMENG_ACCESS_KEY_ID` 是否不带末尾 `=`
2. 检查 `JIMENG_SECRET_ACCESS_KEY` 是否带 `=`
3. 确保使用 base64 编码的密钥

### Q2: API 并发限制（50430）

**原因**: 短时间内请求过多

**解决方案**:
1. 系统已自动重试（最多 3 次）
2. 降低并发请求数量
3. 添加请求间隔（1-2 秒）

### Q3: 图片下载失败（50220）

**原因**: 图片 URL 不可访问

**解决方案**:
1. 确保图片 URL 是公网可访问的
2. 使用 TOS 对象存储上传图片
3. 检查 TOS Bucket 的 ACL 设置为公共读

### Q4: 任务超时

**原因**: 生成时间超过预期

**解决方案**:
1. 增加查询超时时间（默认 300 秒）
2. 增加查询次数（默认 10 次）
3. 检查 API 服务状态

---

## 技术支持

### 文档资源

- **项目架构**: `PROJECT_ARCHITECTURE_AND_TODO.md`
- **API 测试**: `API_TEST_GUIDE.md`
- **配置指南**: `对象存储配置指南.md`
- **错误报告**: `ALL_ERROR_REPORTS.md`

### 联系方式

- **GitHub**: leo202000/agentops-network
- **文档**: /root/.openclaw/workspace/hairstyle_app/

### 更新日志

**v3.5** (2026-03-24):
- ✅ 新增 5 种发型（齐肩发、梨花头、外翘发型、丸子头、空气刘海）
- ✅ 使用独立 JimengClient（避免签名问题）
- ✅ 添加重试机制（处理 API 并发限制）
- ✅ TOS 对象存储集成
- ✅ 商用测试验证通过

---

**最后更新**: 2026-03-24 07:05  
**文档状态**: 商用就绪 ✅

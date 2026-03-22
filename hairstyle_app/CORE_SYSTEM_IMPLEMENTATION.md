# 核心任务系统实施文档

基于即梦平台 100% 完整分析经验

---

## 📋 实施完成

### 1. 任务状态机 ✅

**文件**: `backend/task_manager.py`

**核心功能**:
- 5 状态流转 (WAITING → QUEUING → PROCESSING → COMPLETED → CONFIRMED/FAILED)
- 任务实体管理
- 用户任务关联
- 监听器机制

**状态流转图**:
```
WAITING (10)
   ↓
QUEUING (30)
   ↓
PROCESSING (42)
   ↓
COMPLETED (45) ──→ 用户确认 ──→ CONFIRMED (20)
   ↓
FAILED (50) ──→ 重试 ──→ WAITING (10)
```

**使用方法**:
```python
from task_manager import TaskManager, TaskStateMachine, TaskStatus

# 创建管理器
tm = TaskManager()
sm = TaskStateMachine(tm)

# 创建任务
task = tm.create_task(
    user_id="user_123",
    photos=["photo1.jpg"],
    hairstyle_choice="大波浪",
    description="自然蓬松的大波浪"
)

# 状态转换
sm.transition(task.id, TaskStatus.QUEUING)
sm.transition(task.id, TaskStatus.PROCESSING)
sm.transition(task.id, TaskStatus.COMPLETED, result_image_url="...")
sm.transition(task.id, TaskStatus.CONFIRMED)
```

---

### 2. WebSocket Racing 模式 ✅

**文件**: `backend/websocket_racing.py`

**核心功能**:
- WebSocket 优先连接
- HTTP 轮询降级 (10 秒超时)
- Racing 模式 (同时启动，任一成功即可)
- 实时通知客户端

**工作流程**:
```
1. 同时启动 WebSocket 和 HTTP 轮询
2. 设置 10 秒超时定时器
3. 如果 WebSocket 先连接成功 → 使用 WebSocket
4. 如果 WebSocket 超时 → 降级到 HTTP 轮询
5. 任务完成/失败 → 停止所有连接
```

**使用方法**:
```python
from websocket_racing import TaskPollingManager

async def on_update(data):
    print(f"任务更新：{data}")

manager = TaskPollingManager(
    task_id="task_123",
    ws_url="ws://localhost:8081/ws/task/task_123",
    http_url="http://localhost:8080/api/task/task_123/status",
    on_update=on_update,
    timeout=10000,  # 10 秒超时
    polling_interval=3000  # 3 秒轮询
)

await manager.start()
```

---

### 3. 即梦 API 集成 ✅

**文件**: `backend/jimeng_integration.py`

**核心功能**:
- 即梦 API 签名认证
- 异步任务提交
- 轮询查询结果
- 自动提示词构建

**使用方法**:
```python
from jimeng_integration import JimengAPI, JimengTaskProcessor

# 创建 API 客户端
api = JimengAPI(access_key, secret_key)

# 创建处理器
processor = JimengTaskProcessor(api, task_manager, racing_server)
await processor.start()

# 处理任务
await processor.process_task(task)
```

**提示词模板**:
```python
# 正向提示词
"将图片中的长发修改为自然蓬松的大波浪发型，
保持人物面部和服装不变，realistic photo, high quality"

# 负面提示词
"short hair, bob cut, straight hair, 短发，直发"
```

---

### 4. 主服务器整合 ✅

**文件**: `backend/main_server.py`

**核心功能**:
- RESTful API
- WebSocket 实时通信
- 任务队列管理
- 即梦 API 集成

**API 端点**:
```
POST   /api/task/create           # 创建任务
GET    /api/task/{task_id}        # 获取任务状态
POST   /api/task/{task_id}/confirm # 确认任务
GET    /api/user/{user_id}/tasks  # 获取用户任务列表
WS     ws://localhost:8081/ws/task/{task_id}  # WebSocket 实时通知
```

**启动服务器**:
```bash
python backend/main_server.py
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install aiohttp websockets
```

### 2. 配置环境变量

```bash
export JIMENG_ACCESS_KEY_ID="your_access_key"
export JIMENG_SECRET_ACCESS_KEY="your_secret_key"
```

### 3. 启动服务器

```bash
cd /root/.openclaw/workspace/hairstyle_app/backend
python main_server.py
```

### 4. 测试 API

```bash
# 创建任务
curl -X POST http://localhost:8080/api/task/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "photos": ["https://example.com/photo.jpg"],
    "hairstyle_choice": "大波浪",
    "description": "自然蓬松的大波浪发型"
  }'

# 获取任务状态
curl http://localhost:8080/api/task/{task_id}

# 确认任务
curl -X POST http://localhost:8080/api/task/{task_id}/confirm
```

---

## 📊 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    客户端                                 │
│  (上传照片 + 选择发型 + 实时进度 + 确认)                   │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP + WebSocket
                   ↓
┌─────────────────────────────────────────────────────────┐
│                  主服务器 (8080 端口)                      │
│  ┌─────────────────────────────────────────────┐        │
│  │ RESTful API                                 │        │
│  │ - /api/task/create                          │        │
│  │ - /api/task/{id}                            │        │
│  │ - /api/task/{id}/confirm                    │        │
│  │ - /api/user/{id}/tasks                      │        │
│  └─────────────────────────────────────────────┘        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│              任务管理器 + Racing 服务器                    │
│  ┌─────────────────┐    ┌─────────────────────┐        │
│  │ TaskManager     │    │ RacingServer (8081) │        │
│  │ - 任务状态机     │    │ - WebSocket         │        │
│  │ - 用户任务       │    │ - HTTP 轮询          │        │
│  │ - 监听器        │    │ - 实时通知          │        │
│  └─────────────────┘    └─────────────────────┘        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│              即梦任务处理器                               │
│  ┌─────────────────────────────────────────────┐        │
│  │ JimengTaskProcessor                         │        │
│  │ - 提交任务到即梦 API                         │        │
│  │ - 轮询查询结果                               │        │
│  │ - 更新任务状态                               │        │
│  └─────────────────────────────────────────────┘        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│              即梦 AI API                                 │
│  ┌─────────────────────────────────────────────┐        │
│  │ visual.volcengineapi.com                    │        │
│  │ - CVSync2AsyncSubmitTask                    │        │
│  │ - CVSync2AsyncGetResult                     │        │
│  └─────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 核心优势

| 特性 | 即梦经验 | 您的项目 |
|------|---------|---------|
| **任务状态** | 5 状态流转 | ✅ 完整实现 |
| **实时通信** | WebSocket Racing | ✅ 10 秒降级 |
| **用户确认** | confirm_status | ✅ 预览确认 |
| **队列管理** | priority+queueIdx | ✅ 优先级队列 |
| **API 集成** | 签名认证 | ✅ 完整实现 |

---

## 📝 下一步

### 阶段 1: 核心功能 ✅ 完成
- [x] 任务状态机
- [x] WebSocket Racing 模式
- [x] 即梦 API 集成
- [x] 主服务器整合

### 阶段 2: 用户界面 (待实施)
- [ ] 照片上传组件
- [ ] 发型选择界面
- [ ] 进度显示组件
- [ ] 预览确认弹窗

### 阶段 3: 优化完善 (待实施)
- [ ] 队列管理优化
- [ ] 发型模板系统
- [ ] 性能优化
- [ ] 埋点监控

---

## 🔧 测试命令

```bash
# 测试任务管理器
python backend/task_manager.py

# 测试 WebSocket Racing
python backend/websocket_racing.py

# 测试即梦 API 集成
python backend/jimeng_integration.py

# 启动完整服务器
python backend/main_server.py
```

---

**核心任务系统实施完成！** 🎉

需要继续实施**用户界面**还是先**测试核心功能**？

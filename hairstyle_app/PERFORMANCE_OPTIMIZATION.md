# 性能优化方案

解决上下文过大和阻塞问题

---

## 🎯 问题诊断

### 日志分析

```
⚠️ 上下文使用 179% → 清理 408 条消息
🔹 健康监控重启 → 检测到阻塞
✅ WebSocket 正常 → 1005 关闭后重连成功
```

### 根本原因

| 问题 | 原因 | 影响 |
|------|------|------|
| 上下文过大 | 消息未清理，历史堆积 | 内存溢出，处理慢 |
| 阻塞 | 同步调用阻塞事件循环 | 健康监控重启 |
| 日志冗余 | 重复日志，无抑制 | 磁盘占用，性能下降 |

---

## 🔧 优化方案

### 1. 日志优化

#### 紧凑格式
```python
# 优化前
[2026-03-21 17:41:23] INFO - 系统启动成功
[2026-03-21 17:41:24] INFO - 心跳检查正常
[2026-03-21 17:41:24] INFO - 心跳检查正常  # 重复！

# 优化后
[17:41:23] I 系统启动
[17:41:24] I 心跳检查
# 重复消息被抑制
```

#### 日志抑制
```python
from logger_config import log_with_suppression

# 相同消息 5 秒内只记录一次
log_with_suppression(logger, logging.INFO, "heartbeat", "心跳检查")
```

### 2. 上下文压缩

#### 智能压缩策略
```
消息数 < 10: 不压缩
消息数 10-50: 轻度压缩（保留最近 5 条）
消息数 > 50: 深度压缩（摘要 + 保留最近 10 条）
```

#### 压缩效果
```
原始大小：50,000 bytes
压缩后：8,000 bytes
压缩率：84%
```

### 3. 性能监控

#### 实时监控指标
| 指标 | 阈值 | 告警 |
|------|------|------|
| 内存 | 512 MB | ⚠️ |
| CPU | 80% | ⚠️ |
| 上下文 | 1000 条 | ⚠️ |
| 队列 | 100 个 | ⚠️ |

#### 自动恢复
```
检测到阻塞 → 自动重启 → 恢复服务
上下文过大 → 自动压缩 → 释放内存
```

---

## 🚀 实施步骤

### 步骤 1: 集成日志优化

```python
from logger_config import setup_logger, log_with_suppression

# 创建紧凑日志器
logger = setup_logger("app", compact=True)

# 使用抑制日志
log_with_suppression(logger, logging.INFO, "key", "消息")
```

### 步骤 2: 集成上下文管理

```python
from context_compressor import SmartContextManager

# 创建管理器
manager = SmartContextManager(max_messages=100)

# 添加消息
manager.add_message({"role": "user", "content": "你好"})

# 获取压缩后的上下文
context = manager.get_context()
```

### 步骤 3: 集成性能监控

```python
from performance_monitor import PerformanceMonitor

# 创建监控器
monitor = PerformanceMonitor()

# 注册告警回调
async def on_alert(message, metrics):
    print(f"🚨 {message}")

monitor.on_alert(on_alert)

# 开始监控
await monitor.start_monitoring(interval=5.0)
```

---

## 📊 预期效果

### 优化前
```
上下文：179% (408 条消息)
内存：高
阻塞：是
重启：是
```

### 优化后
```
上下文：< 50% (< 100 条消息)
内存：正常
阻塞：否
重启：否
```

---

## 🎯 关键文件

| 文件 | 功能 |
|------|------|
| `logger_config.py` | 紧凑日志 + 抑制 |
| `context_compressor.py` | 上下文压缩 |
| `performance_monitor.py` | 性能监控 |

---

**性能优化方案完成！** 🎉

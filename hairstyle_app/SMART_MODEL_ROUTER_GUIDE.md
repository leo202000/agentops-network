# 智能模型路由器使用指南

彻底解决请求超时和中断问题

---

## 🎯 核心功能

### 1. 自动切换模型
```
请求超时 → 自动切换到更快的模型
模型故障 → 自动降级到备用模型
连续失败 → 自动标记为不健康，暂停使用
```

### 2. 智能负载均衡
```
按权重分配请求
优先使用快速模型
分散请求压力
```

### 3. 健康检查
```
每 60 秒检查一次
自动恢复健康模型
实时监控状态
```

---

## 📊 模型梯队

### 第一梯队（快速响应）⚡
| 模型 | 超时 | 权重 | 适用场景 |
|------|------|------|---------|
| qwen3-coder-next | 20s | 1.5 | 简单任务、快速响应 |
| glm-4.7 | 25s | 1.3 | 日常对话、文本生成 |

### 第二梯队（平衡性能）⚖️
| 模型 | 超时 | 权重 | 适用场景 |
|------|------|------|---------|
| qwen3.5-plus | 30s | 1.0 | 全能任务、视觉理解 |
| kimi-k2.5 | 30s | 1.0 | 深度思考、视觉理解 |
| MiniMax-M2.5 | 30s | 1.0 | 平衡性能 |

### 第三梯队（深度思考）🧠
| 模型 | 超时 | 权重 | 适用场景 |
|------|------|------|---------|
| qwen3-max-2026-01-23 | 45s | 0.5 | 复杂任务、深度分析 |
| qwen3-coder-plus | 40s | 0.5 | 代码生成 |
| glm-5 | 45s | 0.5 | 深度思考 |

---

## 🚀 使用方法

### 1. 初始化

```python
from smart_model_router import SmartModelRouter

# 创建路由器
router = SmartModelRouter()
await router.initialize()

print(f"当前模型：{router.current_model_id}")
```

### 2. 执行请求

```python
# 简单请求（自动选择最佳模型）
response = await router.execute("你好")

# 指定模型
response = await router.execute(
    "你的提示词",
    model_id="qwen3.5-plus"
)

# 带参数
response = await router.execute(
    "你的提示词",
    max_tokens=2048,
    temperature=0.7
)
```

### 3. 查看状态

```python
# 获取状态报告
report = router.get_status_report()

# 打印状态
router.print_status()
```

### 4. 处理异常

```python
try:
    response = await router.execute("你的提示词")
except Exception as e:
    print(f"所有模型请求失败：{e}")
    # 可以添加降级逻辑
```

---

## 🔧 自动切换逻辑

### 场景 1: 请求超时

```
1. 使用 qwen3-coder-next (20s 超时)
2. 超时 → 自动切换到 glm-4.7
3. 再超时 → 切换到 qwen3.5-plus
4. 最多重试 3 次
```

### 场景 2: 模型连续失败

```
1. 模型失败 1 次 → 警告
2. 模型失败 2 次 → 降低权重
3. 模型失败 3 次 → 标记为 UNHEALTHY
4. 60 秒后尝试恢复
```

### 场景 3: 性能下降

```
1. 响应时间 > 80% 超时阈值
2. 标记为 DEGRADED
3. 降低权重，减少请求
4. 性能恢复后自动恢复
```

---

## 📈 状态说明

### 健康状态

| 状态 | 说明 | 动作 |
|------|------|------|
| ✅ HEALTHY | 健康 | 正常接收请求 |
| ⚠️ DEGRADED | 降级 | 减少请求分配 |
| ❌ UNHEALTHY | 不健康 | 暂停使用 |
| 🔄 RECOVERING | 恢复中 | 测试中 |

### 统计信息

| 指标 | 说明 |
|------|------|
| success_rate | 成功率 |
| avg_response_time | 平均响应时间 |
| total_requests | 总请求数 |
| timeout_requests | 超时次数 |
| consecutive_failures | 连续失败次数 |

---

## 💡 最佳实践

### 1. 根据任务选择模型

```python
# 简单任务 - 使用快速模型
response = await router.execute(
    "简单问题",
    model_id="qwen3-coder-next"
)

# 复杂任务 - 使用深度思考模型
response = await router.execute(
    "复杂分析问题",
    model_id="qwen3-max-2026-01-23"
)

# 视觉任务 - 使用支持视觉的模型
response = await router.execute(
    "分析这张图片",
    model_id="qwen3.5-plus"  # 或 kimi-k2.5
)
```

### 2. 设置合理的超时

```python
# 根据任务复杂度设置
router.models["qwen3-coder-next"].timeout = 15  # 简单任务
router.models["qwen3.5-plus"].timeout = 30      # 普通任务
router.models["qwen3-max-2026-01-23"].timeout = 60  # 复杂任务
```

### 3. 调整权重

```python
# 偏好某个模型
router.models["kimi-k2.5"].weight = 2.0

# 减少某个模型的使用
router.models["glm-5"].weight = 0.3
```

### 4. 监控和告警

```python
async def monitor_models():
    while True:
        report = router.get_status_report()
        
        for model_id, stats in report['models'].items():
            # 成功率低于 80%
            if stats['success_rate'] < 80:
                print(f"⚠️ {model_id} 成功率低：{stats['success_rate']}%")
            
            # 平均响应时间过长
            if stats['avg_response_time'] > 30:
                print(f"⚠️ {model_id} 响应慢：{stats['avg_response_time']}s")
        
        await asyncio.sleep(60)
```

---

## 🔍 故障排查

### 问题 1: 所有模型都超时

**原因**: 网络问题或 API 故障

**解决**:
1. 检查网络连接
2. 检查 API Key 是否有效
3. 增加超时时间
4. 减少并发请求

### 问题 2: 频繁切换模型

**原因**: 模型性能不稳定

**解决**:
1. 增加超时时间
2. 降低快速模型权重
3. 添加更多备用模型

### 问题 3: 某个模型一直失败

**原因**: 模型故障或限流

**解决**:
1. 检查模型状态
2. 暂时降低权重
3. 等待恢复

---

## 📊 监控面板

### 实时状态

```python
# 获取实时状态
status = router.get_status_report()

print(f"当前模型：{status['current_model']}")
print()

for model_id, stats in status['models'].items():
    print(f"{model_id}:")
    print(f"  健康：{stats['health']}")
    print(f"  成功率：{stats['success_rate']}%")
    print(f"  响应：{stats['avg_response_time']}s")
    print()
```

### 历史记录

```python
# 记录历史数据
history = []

async def record_history():
    while True:
        report = router.get_status_report()
        history.append({
            "time": time.time(),
            "report": report
        })
        await asyncio.sleep(60)
```

---

## 🎯 实施步骤

### 阶段 1: 基础功能 ✅

- [x] 模型路由器
- [x] 自动切换
- [x] 健康检查

### 阶段 2: 集成测试 ⏳

- [ ] API 集成
- [ ] 负载均衡测试
- [ ] 故障恢复测试

### 阶段 3: 生产部署 📅

- [ ] 监控告警
- [ ] 性能优化
- [ ] 文档完善

---

## 📝 测试命令

```bash
# 测试路由器
python backend/smart_model_router.py

# 查看状态
curl http://localhost:8080/api/models/status

# 测试切换
curl -X POST http://localhost:8080/api/test/switch
```

---

**智能模型路由器完成！** 🎉

彻底解决请求超时和中断问题！

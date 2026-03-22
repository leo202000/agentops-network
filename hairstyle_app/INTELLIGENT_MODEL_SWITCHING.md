# 智能模型自动切换方案

解决请求超时和中断问题

---

## 🎯 核心功能

### 1. 自动切换模型
```
请求超时 → 自动切换到更快的模型
模型故障 → 自动降级到备用模型
```

### 2. 健康检查
```
每 60 秒检查一次模型状态
监控响应时间和成功率
自动标记不健康模型
```

### 3. 负载均衡
```
按优先级分配请求
分散请求压力
避免单点故障
```

---

## 📊 可用模型列表

### 千问系列
| 模型 | 优先级 | 超时 | 能力 |
|------|--------|------|------|
| qwen3.5-plus | 1 | 30s | 文本生成、深度思考、视觉理解 |
| qwen3-max-2026-01-23 | 2 | 40s | 文本生成、深度思考 |
| qwen3-coder-next | 1 | 25s | 文本生成（快速） |
| qwen3-coder-plus | 2 | 30s | 文本生成 |

### 智谱系列
| 模型 | 优先级 | 超时 | 能力 |
|------|--------|------|------|
| glm-5 | 1 | 30s | 文本生成、深度思考 |
| glm-4.7 | 2 | 30s | 文本生成、深度思考 |

### Kimi 系列
| 模型 | 优先级 | 超时 | 能力 |
|------|--------|------|------|
| kimi-k2.5 | 1 | 30s | 文本生成、深度思考、视觉理解 |

### MiniMax 系列
| 模型 | 优先级 | 超时 | 能力 |
|------|--------|------|------|
| MiniMax-M2.5 | 2 | 30s | 文本生成、深度思考 |

---

## 🚀 使用方法

### 1. 初始化模型管理器

```python
from model_manager import ModelManager

# 创建管理器
manager = ModelManager()
await manager.initialize()
```

### 2. 选择最佳模型

```python
# 默认选择
model = await manager.select_model("default")
print(f"选中模型：{model.name}")

# 代码任务（优先 coding 模型）
model = await manager.select_model("code")
```

### 3. 执行请求（自动重试和切换）

```python
try:
    response = await manager.execute_request(
        model_id=model.id,
        prompt="你的提示词",
        max_tokens=2048
    )
except Exception as e:
    print(f"请求失败：{e}")
```

### 4. 查看模型状态

```python
report = manager.get_model_status_report()
for model_id, stats in report.items():
    print(f"{model_id}:")
    print(f"  状态：{stats['status']}")
    print(f"  平均响应：{stats['avg_response_time']}s")
    print(f"  成功率：{stats['success_rate']}%")
```

---

## 🔧 自动切换逻辑

### 场景 1: 请求超时

```
1. 请求 qwen3.5-plus 超时
2. 自动切换到 qwen3-coder-next（更快）
3. 如果还超时，切换到 glm-5
4. 最多重试 3 次
```

### 场景 2: 模型故障

```
1. 模型连续失败 3 次
2. 标记为 UNHEALTHY
3. 自动跳过该模型
4. 选择下一个可用模型
```

### 场景 3: 性能下降

```
1. 响应时间 > 80% 超时阈值
2. 标记为 DEGRADED
3. 降低优先级
4. 减少请求分配
```

---

## 📊 健康检查机制

### 检查指标

| 指标 | 阈值 | 动作 |
|------|------|------|
| 响应时间 | > 80% 超时 | 标记 DEGRADED |
| 连续失败 | >= 3 次 | 标记 UNHEALTHY |
| 成功率 | < 50% | 标记 DEGRADED |

### 检查频率

- **健康检查**: 每 60 秒
- **统计更新**: 每次请求后
- **状态恢复**: 下次健康检查

---

## 💡 最佳实践

### 1. 设置合理的超时时间

```python
# 根据任务类型设置
model.timeout = 30  # 普通任务
model.timeout = 60  # 复杂任务
model.timeout = 10  # 简单任务
```

### 2. 调整优先级

```python
# 优先使用快速模型
qwen3-coder-next.priority = 1
glm-5.priority = 1

# 备用模型
qwen3-max.priority = 3
```

### 3. 监控和告警

```python
# 定期检查模型状态
async def monitor_models():
    while True:
        report = manager.get_model_status_report()
        
        for model_id, stats in report.items():
            if stats['status'] == 'unhealthy':
                print(f"⚠️  模型 {model_id} 不健康！")
            
            if stats['success_rate'] < 80:
                print(f"⚠️  模型 {model_id} 成功率低！")
        
        await asyncio.sleep(60)
```

---

## 🔍 故障排查

### 问题 1: 所有模型都不可用

**原因**: 网络问题或 API 故障

**解决**:
1. 检查网络连接
2. 检查 API Key 是否有效
3. 查看模型状态报告

### 问题 2: 频繁切换模型

**原因**: 模型性能不稳定

**解决**:
1. 增加超时时间
2. 降低优先级
3. 添加更多备用模型

### 问题 3: 响应时间过长

**原因**: 模型负载高

**解决**:
1. 切换到更快的模型
2. 减少 max_tokens
3. 简化提示词

---

## 📈 性能优化建议

### 1. 使用快速模型处理简单任务

```python
# 简单任务
model = await manager.select_model("default")

# 复杂任务
model = await manager.select_model("code")
```

### 2. 批量请求分散到不同模型

```python
models = manager.get_available_models()

for i, prompt in enumerate(prompts):
    model = models[i % len(models)]  # 轮询
    response = await manager.execute_request(
        model_id=model.id,
        prompt=prompt
    )
```

### 3. 缓存常用响应

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_response(prompt_hash):
    # 缓存逻辑
    pass
```

---

## 🎯 实施步骤

### 阶段 1: 基础功能 ✅

- [x] 模型管理器
- [x] 健康检查
- [x] 自动切换

### 阶段 2: 优化完善 ⏳

- [ ] API 集成
- [ ] 负载均衡
- [ ] 监控告警

### 阶段 3: 高级功能 📅

- [ ] 智能预测
- [ ] 自适应调整
- [ ] 性能分析

---

## 📝 测试命令

```bash
# 测试模型管理器
python backend/model_manager.py

# 查看模型状态
curl http://localhost:8080/api/models/status

# 测试自动切换
curl -X POST http://localhost:8080/api/test/switch
```

---

**智能模型自动切换方案完成！** 🎉

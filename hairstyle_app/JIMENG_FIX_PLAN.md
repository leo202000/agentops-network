# 📋 即梦 API 问题修复计划

**日期**: 2026-03-20  
**技能**: writing-plans  
**基于**: systematic-debugging 分析报告

---

## 🎯 目标

解决即梦 API 的两个问题：
1. ❌ 国外域名不符合要求 → 更换为国内可访问 URL
2. ❌ API 并发超限 → 实施请求队列和重试机制

---

## 📦 任务分解

### 任务 1：准备国内图片 URL（P0 - 高优先级）

**验收标准**：
- [ ] URL 国内可访问
- [ ] API 接受 URL
- [ ] 图片格式正确（JPG/PNG）
- [ ] 图片大小合适（<5MB）

**实施步骤**：

#### 1.1 选择图片存储方案
**选项 A**: 火山引擎 TOS（推荐）
- 优点：同厂商，兼容性最好
- 缺点：需要创建 Bucket

**选项 B**: 阿里云 OSS
- 优点：稳定可靠
- 缺点：跨厂商

**选项 C**: 临时测试 URL
- 优点：快速
- 缺点：不适合生产

**决定**: 使用临时测试 URL 快速验证，后续迁移到 TOS

#### 1.2 准备测试图片
```bash
# 下载测试图片到本地
curl -o test_image.jpg https://example.com/image.jpg

# 或使用现有图片
cp /path/to/image.jpg /root/.openclaw/workspace/hairstyle_app/test_images/
```

#### 1.3 上传到临时图床
**推荐**: 使用国内免费图床
- https://sm.ms/
- https://imgtu.com/
- 或其他稳定图床

#### 1.4 验证 URL
```bash
# 测试国内可访问性
curl -I https://new-url.com/image.jpg

# 测试响应时间
curl -w "@curl-format.txt" -o /dev/null -s https://new-url.com/image.jpg
```

**预计时间**: 30 分钟

---

### 任务 2：实现请求队列（P1 - 中优先级）

**验收标准**：
- [ ] 请求串行化处理
- [ ] 无并发超限错误
- [ ] 处理速度可接受
- [ ] 代码可维护

**实施步骤**：

#### 2.1 分析当前并发逻辑
**文件**: `/root/.openclaw/workspace/hairstyle_app/backend/jimeng_official_client.py`

**检查点**：
- 当前并发数
- 请求发送位置
- 错误处理逻辑

#### 2.2 实现请求队列类
```python
# 文件：jimeng_request_queue.py

import asyncio
import time
from typing import Optional, Dict, Any

class JimengRequestQueue:
    """即梦 API 请求队列 - 串行化处理"""
    
    def __init__(self, max_concurrent: int = 1, delay_between_requests: float = 0.5):
        self.max_concurrent = max_concurrent
        self.delay = delay_between_requests
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    async def submit_task(self, client, image_url: str, prompt: str) -> Dict[str, Any]:
        """提交任务（带队列控制）"""
        async with self._semaphore:
            try:
                # 提交任务
                result = await client.submit_task(image_url, prompt)
                
                # 延迟避免并发
                await asyncio.sleep(self.delay)
                
                return {
                    "status": "success",
                    "result": result
                }
            
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e)
                }
    
    async def process_batch(self, client, tasks: list) -> list:
        """批量处理任务"""
        results = []
        
        for task in tasks:
            result = await self.submit_task(
                client,
                task["image_url"],
                task["prompt"]
            )
            results.append(result)
        
        return results
```

#### 2.3 集成到现有客户端
**文件**: `/root/.openclaw/workspace/hairstyle_app/backend/jimeng_official_client.py`

**修改点**：
```python
# 添加导入
from jimeng_request_queue import JimengRequestQueue

# 初始化队列
self.request_queue = JimengRequestQueue(
    max_concurrent=1,  # 串行
    delay_between_requests=0.5  # 500ms 延迟
)

# 修改提交方法
async def submit_with_queue(self, image_url: str, prompt: str):
    return await self.request_queue.submit_task(self, image_url, prompt)
```

**预计时间**: 45 分钟

---

### 任务 3：实现重试机制（P1 - 中优先级）

**验收标准**：
- [ ] 自动重试并发超限错误
- [ ] 指数退避策略
- [ ] 最大重试次数限制
- [ ] 重试日志记录

**实施步骤**：

#### 3.1 实现重试装饰器
```python
# 文件：jimeng_retry.py

import asyncio
import time
from functools import wraps

def retry_on_concurrent_limit(max_retries: int = 3, base_delay: float = 1.0):
    """并发超限时自动重试"""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = await func(*args, **kwargs)
                    
                    # 检查是否是并发错误
                    if isinstance(result, dict) and "concurrent limit" in str(result.get("error", "")).lower():
                        if attempt < max_retries:
                            # 指数退避
                            delay = base_delay * (2 ** attempt)
                            print(f"⚠️ 并发超限，{delay}秒后重试（第{attempt+1}次）")
                            await asyncio.sleep(delay)
                            continue
                        else:
                            return {
                                "status": "error",
                                "error": "达到最大重试次数",
                                "original_error": result
                            }
                    
                    return result
                
                except Exception as e:
                    last_error = e
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        print(f"❌ 错误：{e}，{delay}秒后重试（第{attempt+1}次）")
                        await asyncio.sleep(delay)
                    else:
                        raise
            
            return {
                "status": "error",
                "error": str(last_error) if last_error else "未知错误"
            }
        
        return wrapper
    return decorator
```

#### 3.2 应用到提交方法
```python
# 修改 jimeng_official_client.py

from jimeng_retry import retry_on_concurrent_limit

class JimengOfficialClient:
    
    @retry_on_concurrent_limit(max_retries=3, base_delay=2.0)
    async def submit_task(self, image_url: str, prompt: str):
        """提交任务（带重试）"""
        # 原有实现
        pass
```

**预计时间**: 30 分钟

---

### 任务 4：集成测试（P1 - 中优先级）

**验收标准**：
- [ ] 使用国内 URL 测试
- [ ] 无并发错误
- [ ] 任务成功完成
- [ ] 性能可接受

**实施步骤**：

#### 4.1 更新测试脚本
**文件**: `/root/.openclaw/workspace/hairstyle_app/backend/test_jimeng.py`

```python
# 更新测试 URL
TEST_IMAGE_URL = "https://国内图床.com/test.jpg"  # 替换

# 测试并发控制
async def test_concurrent_control():
    client = JimengOfficialClient()
    
    # 批量提交（应该串行处理）
    tasks = [
        {"image_url": TEST_IMAGE_URL, "prompt": "发型 1"},
        {"image_url": TEST_IMAGE_URL, "prompt": "发型 2"},
        {"image_url": TEST_IMAGE_URL, "prompt": "发型 3"},
    ]
    
    results = await client.request_queue.process_batch(client, tasks)
    
    # 验证结果
    assert all(r["status"] == "success" for r in results)
    print("✅ 并发控制测试通过")
```

#### 4.2 执行测试
```bash
cd /root/.openclaw/workspace/hairstyle_app/backend
python test_jimeng.py
```

#### 4.3 验证结果
- 检查日志
- 确认无并发错误
- 确认 URL 被接受
- 检查生成质量

**预计时间**: 30 分钟

---

## 📊 时间估算

| 任务 | 优先级 | 预计时间 |
|------|--------|---------|
| 任务 1：准备国内 URL | P0 | 30 分钟 |
| 任务 2：实现请求队列 | P1 | 45 分钟 |
| 任务 3：实现重试机制 | P1 | 30 分钟 |
| 任务 4：集成测试 | P1 | 30 分钟 |
| **总计** | - | **2 小时 15 分钟** |

---

## 🎯 执行顺序

```
1. 任务 1（P0）→ 准备国内 URL
   ↓
2. 任务 2（P1）→ 实现请求队列
   ↓
3. 任务 3（P1）→ 实现重试机制
   ↓
4. 任务 4（P1）→ 集成测试
   ↓
5. 验证 → 回复客户
```

---

## ✅ 完成检查清单

### 功能验证
- [ ] 国内 URL 被 API 接受
- [ ] 无并发超限错误
- [ ] 任务成功完成
- [ ] 生成质量正常

### 代码质量
- [ ] 代码审查通过
- [ ] 错误处理完整
- [ ] 日志记录清晰
- [ ] 文档更新

### 交付准备
- [ ] 测试通过
- [ ] 性能可接受
- [ ] 准备回复客户
- [ ] 准备部署

---

## 🔄 风险和缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 国内 URL 不可用 | 低 | 高 | 准备多个备选 |
| 并发限制更严格 | 中 | 中 | 增加延迟时间 |
| 重试次数过多 | 低 | 低 | 限制最大重试 |

---

## 📝 下一步

使用 **executing-plans** 技能开始执行任务

---

*计划由 writing-plans skill 生成*

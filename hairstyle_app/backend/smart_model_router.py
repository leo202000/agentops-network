#!/usr/bin/env python3
"""
智能模型路由器
自动切换 + 健康检查 + 负载均衡
彻底解决请求超时和中断问题
"""
import asyncio
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import hashlib


class ModelHealth(Enum):
    """模型健康状态"""
    HEALTHY = "healthy"       # 健康 - 正常接收请求
    DEGRADED = "degraded"     # 降级 - 减少请求
    UNHEALTHY = "unhealthy"   # 不健康 - 暂停使用
    RECOVERING = "recovering" # 恢复中 - 测试中


@dataclass
class ModelStats:
    """模型统计"""
    total_requests: int = 0
    success_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    avg_response_time: float = 0.0
    last_error_time: float = 0
    last_success_time: float = 0
    consecutive_failures: int = 0
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 100.0
        return (self.success_requests / self.total_requests) * 100


@dataclass
class ModelConfig:
    """模型配置"""
    id: str
    name: str
    provider: str
    tier: int = 1  # 1=快速，2=平衡，3=深度
    capabilities: List[str] = field(default_factory=list)
    max_tokens: int = 4096
    timeout: int = 30  # 秒
    health: ModelHealth = ModelHealth.HEALTHY
    stats: ModelStats = field(default_factory=ModelStats)
    weight: float = 1.0  # 负载均衡权重
    last_switch_time: float = 0  # 上次切换时间


class SmartModelRouter:
    """智能模型路由器"""
    
    def __init__(self):
        # 初始化模型列表（根据用户提供的模型）
        self.models: Dict[str, ModelConfig] = {
            # 第一梯队 - 快速响应
            "qwen3-coder-next": ModelConfig(
                id="qwen3-coder-next",
                name="通义千问 Coder Next",
                provider="千问",
                tier=1,
                capabilities=["文本生成"],
                timeout=20,
                weight=1.5
            ),
            "glm-4.7": ModelConfig(
                id="glm-4.7",
                name="智谱 GLM-4.7",
                provider="智谱",
                tier=1,
                capabilities=["文本生成", "深度思考"],
                timeout=25,
                weight=1.3
            ),
            
            # 第二梯队 - 平衡性能
            "qwen3.5-plus": ModelConfig(
                id="qwen3.5-plus",
                name="通义千问 3.5 Plus",
                provider="千问",
                tier=2,
                capabilities=["文本生成", "深度思考", "视觉理解"],
                timeout=30,
                weight=1.0
            ),
            "kimi-k2.5": ModelConfig(
                id="kimi-k2.5",
                name="Kimi K2.5",
                provider="Kimi",
                tier=2,
                capabilities=["文本生成", "深度思考", "视觉理解"],
                timeout=30,
                weight=1.0
            ),
            "MiniMax-M2.5": ModelConfig(
                id="MiniMax-M2.5",
                name="MiniMax M2.5",
                provider="MiniMax",
                tier=2,
                capabilities=["文本生成", "深度思考"],
                timeout=30,
                weight=1.0
            ),
            
            # 第三梯队 - 深度思考
            "qwen3-max-2026-01-23": ModelConfig(
                id="qwen3-max-2026-01-23",
                name="通义千问 3 Max",
                provider="千问",
                tier=3,
                capabilities=["文本生成", "深度思考"],
                timeout=45,
                weight=0.5
            ),
            "qwen3-coder-plus": ModelConfig(
                id="qwen3-coder-plus",
                name="通义千问 Coder Plus",
                provider="千问",
                tier=3,
                capabilities=["文本生成"],
                timeout=40,
                weight=0.5
            ),
            "glm-5": ModelConfig(
                id="glm-5",
                name="智谱 GLM-5",
                provider="智谱",
                tier=3,
                capabilities=["文本生成", "深度思考"],
                timeout=45,
                weight=0.5
            ),
        }
        
        self.current_model_id: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.switch_cooldown = 10  # 切换冷却时间（秒）
        self.health_check_interval = 60  # 健康检查间隔
        
        # 回调函数
        self.on_model_switch: Optional[Callable] = None
    
    async def initialize(self):
        """初始化"""
        self.session = aiohttp.ClientSession()
        asyncio.create_task(self._health_check_loop())
        
        # 选择初始模型
        self.current_model_id = await self._select_best_model()
        print(f"✅ 初始模型：{self.models[self.current_model_id].name}")
    
    async def close(self):
        """关闭"""
        if self.session:
            await self.session.close()
    
    def get_available_models(self, tier: Optional[int] = None) -> List[ModelConfig]:
        """获取可用模型"""
        available = [
            m for m in self.models.values()
            if m.health in [ModelHealth.HEALTHY, ModelHealth.DEGRADED, ModelHealth.RECOVERING]
        ]
        
        if tier is not None:
            available = [m for m in available if m.tier == tier]
        
        # 按权重排序
        return sorted(available, key=lambda m: m.weight, reverse=True)
    
    async def _select_best_model(self, task_type: str = "default") -> str:
        """选择最佳模型"""
        available = self.get_available_models()
        
        if not available:
            # 如果所有模型都不可用，选择超时最长的
            all_models = list(self.models.values())
            return max(all_models, key=lambda m: m.timeout).id
        
        # 根据任务类型选择
        if task_type == "code":
            for model in available:
                if "coder" in model.id.lower():
                    return model.id
        
        # 默认选择权重最高的
        return available[0].id
    
    async def execute(self, prompt: str, **kwargs) -> Any:
        """
        执行请求（带自动重试和切换）
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数（model_id, max_tokens, temperature 等）
        
        Returns:
            模型响应
        """
        model_id = kwargs.pop('model_id', None) or self.current_model_id
        max_retries = 3
        last_error = None
        tried_models = set()
        
        for attempt in range(max_retries):
            try:
                # 检查模型是否可用
                model = self.models.get(model_id)
                if not model or model.health == ModelHealth.UNHEALTHY:
                    model_id = await self._select_next_model(tried_models)
                    model = self.models[model_id]
                    tried_models.add(model_id)
                
                print(f"🤖 使用模型：{model.name} (尝试 {attempt + 1}/{max_retries})")
                
                # 执行请求
                start_time = time.time()
                response = await self._call_model_api(model_id, prompt, **kwargs)
                response_time = time.time() - start_time
                
                # 更新统计
                self._update_stats(model, response_time, True)
                
                # 更新当前模型
                self.current_model_id = model_id
                
                return response
                
            except asyncio.TimeoutError as e:
                last_error = e
                print(f"⏰ 模型 {model_id} 请求超时")
                self._update_stats(self.models[model_id], 0, False, timeout=True)
                
                # 超时立即切换到更快的模型
                model_id = await self._switch_to_faster_model(model_id)
                
            except aiohttp.ClientError as e:
                last_error = e
                print(f"🌐 网络错误：{e}")
                self._update_stats(self.models[model_id], 0, False)
                
                # 切换到下一个模型
                model_id = await self._select_next_model(tried_models)
                
            except Exception as e:
                last_error = e
                print(f"❌ 请求失败：{e}")
                self._update_stats(self.models[model_id], 0, False)
                
                # 切换到下一个模型
                model_id = await self._select_next_model(tried_models)
        
        # 所有重试失败
        raise Exception(f"所有模型请求失败：{last_error}")
    
    async def _call_model_api(self, model_id: str, prompt: str, **kwargs) -> Any:
        """调用模型 API"""
        model = self.models[model_id]
        timeout = aiohttp.ClientTimeout(total=model.timeout)
        
        # TODO: 根据实际 API 实现
        # 这里是示例代码
        async with self.session.post(
            f"https://api.example.com/v1/chat/completions",
            json={
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}],
                **kwargs
            },
            timeout=timeout
        ) as response:
            if response.status != 200:
                raise Exception(f"API 错误：{response.status}")
            
            return await response.json()
    
    async def _switch_to_faster_model(self, current_model_id: str) -> str:
        """切换到更快的模型"""
        current_model = self.models[current_model_id]
        
        # 优先选择同一梯队的更快模型
        same_tier = [
            m for m in self.get_available_models(tier=current_model.tier)
            if m.id != current_model_id and m.timeout < current_model.timeout
        ]
        
        if same_tier:
            next_model = min(same_tier, key=lambda m: m.timeout)
            print(f"🔄 切换到同梯队更快模型：{next_model.name}")
            return next_model.id
        
        # 选择上一梯队
        if current_model.tier > 1:
            faster_tier = self.get_available_models(tier=current_model.tier - 1)
            if faster_tier:
                next_model = faster_tier[0]
                print(f"⬆️ 切换到上一梯队：{next_model.name}")
                return next_model.id
        
        # 选择任意可用模型
        available = self.get_available_models()
        if available:
            next_model = available[0]
            print(f"🔀 切换到可用模型：{next_model.name}")
            return next_model.id
        
        # 没有可用模型，返回当前
        return current_model_id
    
    async def _select_next_model(self, tried_models: set) -> str:
        """选择下一个模型"""
        available = self.get_available_models()
        
        # 排除已尝试的
        available = [m for m in available if m.id not in tried_models]
        
        if available:
            # 按权重选择
            next_model = max(available, key=lambda m: m.weight)
            print(f"🔀 选择下一个模型：{next_model.name}")
            return next_model.id
        
        # 所有模型都尝试过了，重置并重新选择
        tried_models.clear()
        return await self._select_best_model()
    
    def _update_stats(self, model: ModelConfig, response_time: float, success: bool, timeout: bool = False):
        """更新模型统计"""
        stats = model.stats
        stats.total_requests += 1
        
        if success:
            stats.success_requests += 1
            stats.consecutive_failures = 0
            stats.last_success_time = time.time()
            
            # 更新平均响应时间（滑动平均）
            stats.avg_response_time = (
                stats.avg_response_time * 0.8 + response_time * 0.2
            )
            
            # 更新健康状态
            if stats.avg_response_time > model.timeout * 0.8:
                model.health = ModelHealth.DEGRADED
            else:
                model.health = ModelHealth.HEALTHY
        else:
            stats.failed_requests += 1
            stats.last_error_time = time.time()
            stats.consecutive_failures += 1
            
            if timeout:
                stats.timeout_requests += 1
            
            # 连续失败 3 次标记为不健康
            if stats.consecutive_failures >= 3:
                model.health = ModelHealth.UNHEALTHY
                print(f"⚠️  模型 {model.name} 标记为不健康")
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while True:
            await asyncio.sleep(self.health_check_interval)
            
            for model in self.models.values():
                # 恢复不健康模型
                if model.health == ModelHealth.UNHEALTHY:
                    # 距离上次失败超过 5 分钟，尝试恢复
                    if time.time() - model.stats.last_error_time > 300:
                        model.health = ModelHealth.RECOVERING
                        print(f"🔄 模型 {model.name} 进入恢复状态")
                
                # 恢复中的模型，如果成功率高则恢复健康
                elif model.health == ModelHealth.RECOVERING:
                    if model.stats.success_rate > 80:
                        model.health = ModelHealth.HEALTHY
                        print(f"✅ 模型 {model.name} 恢复健康")
    
    def get_status_report(self) -> Dict[str, Any]:
        """获取状态报告"""
        return {
            "current_model": self.models[self.current_model_id].name if self.current_model_id else None,
            "models": {
                model.id: {
                    "name": model.name,
                    "provider": model.provider,
                    "tier": model.tier,
                    "health": model.health.value,
                    "success_rate": round(model.stats.success_rate, 2),
                    "avg_response_time": round(model.stats.avg_response_time, 2),
                    "total_requests": model.stats.total_requests,
                    "timeout_requests": model.stats.timeout_requests,
                    "weight": model.weight
                }
                for model in self.models.values()
            }
        }
    
    def print_status(self):
        """打印状态"""
        report = self.get_status_report()
        
        print("\n" + "="*60)
        print("📊 模型状态报告")
        print("="*60)
        print(f"当前模型：{report['current_model']}")
        print()
        
        for model_id, stats in report['models'].items():
            health_icon = {
                "healthy": "✅",
                "degraded": "⚠️",
                "unhealthy": "❌",
                "recovering": "🔄"
            }[stats['health']]
            
            print(f"{health_icon} {stats['name']} ({stats['provider']})")
            print(f"   梯队：T{stats['tier']} | 成功率：{stats['success_rate']}%")
            print(f"   平均响应：{stats['avg_response_time']}s")
            print(f"   请求数：{stats['total_requests']} | 超时：{stats['timeout_requests']}")
            print()


# 测试
if __name__ == "__main__":
    async def test():
        router = SmartModelRouter()
        await router.initialize()
        
        # 打印状态
        router.print_status()
        
        # 模拟请求
        try:
            response = await router.execute("你好")
            print(f"响应：{response}")
        except Exception as e:
            print(f"请求失败：{e}")
        
        await router.close()
    
    asyncio.run(test())


if __name__ == "__main__":
    import asyncio
    asyncio.run(test())

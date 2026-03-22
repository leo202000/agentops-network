#!/usr/bin/env python3
"""
智能模型路由器 v2
专为 4 个可用模型设计
彻底解决请求超时和中断问题
"""
import asyncio
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import aiohttp


class ModelHealth(Enum):
    """模型健康状态"""
    HEALTHY = "healthy"       # 健康
    DEGRADED = "degraded"     # 降级
    UNHEALTHY = "unhealthy"   # 不健康
    RECOVERING = "recovering" # 恢复中


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
    capabilities: List[str] = field(default_factory=list)
    timeout: int = 30  # 秒
    priority: int = 1  # 优先级（1=最高）
    health: ModelHealth = ModelHealth.HEALTHY
    stats: ModelStats = field(default_factory=ModelStats)
    cooldown_until: float = 0  # 冷却时间
    is_vision_model: bool = False  # 是否支持视觉


class SmartModelRouter:
    """智能模型路由器（4 模型专用版）"""
    
    def __init__(self):
        # 最优搭配：3 模型（全能 + 快速 + 极速）
        self.models: Dict[str, ModelConfig] = {
            # 主力模型：全能稳定
            "qwen3.5-plus": ModelConfig(
                id="qwen3.5-plus",
                name="通义千问 3.5 Plus",
                capabilities=["文本生成", "深度思考", "图片理解"],
                timeout=30,
                priority=1,  # 主力
                is_vision_model=True
            ),
            
            # 备用模型：快速响应
            "kimi-k2.5": ModelConfig(
                id="kimi-k2.5",
                name="Kimi K2.5",
                capabilities=["文本生成", "深度思考", "图片理解"],
                timeout=25,
                priority=2,  # 备用
                is_vision_model=True
            ),
            
            # 兜底模型：极速响应
            "MiniMax-M2.5": ModelConfig(
                id="MiniMax-M2.5",
                name="MiniMax M2.5",
                capabilities=["文本生成"],
                timeout=20,
                priority=3,  # 兜底
                is_vision_model=False
            ),
        }
        
        self.current_model_id: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.switch_cooldown = 5  # 切换冷却时间（秒）
        self.health_check_interval = 60  # 健康检查间隔
        
        # 回调
        self.on_model_switch: Optional[Callable] = None
    
    async def initialize(self):
        """初始化"""
        self.session = aiohttp.ClientSession()
        asyncio.create_task(self._health_check_loop())
        
        # 选择初始模型
        self.current_model_id = "MiniMax-M2.5"  # 默认文本模型
        print(f"✅ 路由器初始化完成，当前模型：{self.models[self.current_model_id].name}")
    
    async def close(self):
        """关闭"""
        if self.session:
            await self.session.close()
    
    def _get_available_models(self, has_image: bool = False) -> List[ModelConfig]:
        """获取可用模型"""
        available = [
            m for m in self.models.values()
            if m.health in [ModelHealth.HEALTHY, ModelHealth.DEGRADED, ModelHealth.RECOVERING]
        ]
        
        # 根据任务类型筛选
        if has_image:
            # 视觉任务：只使用支持图片的模型
            available = [m for m in available if m.is_vision_model]
            print(f"🖼️ 视觉任务，可用模型：{[m.name for m in available]}")
        else:
            # 文本任务：优先文本模型
            text_models = [m for m in available if not m.is_vision_model]
            if text_models:
                available = text_models
                print(f"📝 文本任务，可用模型：{[m.name for m in available]}")
        
        # 按优先级排序
        return sorted(available, key=lambda m: m.priority)
    
    def _select_best_model(self, has_image: bool = False) -> str:
        """选择最佳模型"""
        available = self._get_available_models(has_image)
        
        if not available:
            # 没有可用模型，使用当前模型
            return self.current_model_id
        
        # 选择优先级最高的
        return available[0].id
    
    async def execute(self, prompt: str, image_url: Optional[str] = None, **kwargs) -> Any:
        """
        执行请求（带自动重试和切换）
        
        Args:
            prompt: 提示词
            image_url: 图片 URL（可选）
            **kwargs: 其他参数
        
        Returns:
            模型响应
        """
        has_image = image_url is not None
        max_retries = 3
        last_error = None
        tried_models = set()
        
        for attempt in range(max_retries):
            try:
                # 选择模型
                if attempt == 0:
                    model_id = self._select_best_model(has_image)
                else:
                    model_id = self._select_next_model(tried_models, has_image)
                
                model = self.models[model_id]
                
                # 检查冷却时间
                if time.time() < model.cooldown_until:
                    wait_time = model.cooldown_until - time.time()
                    print(f"⏳ 模型 {model.name} 冷却中，等待 {wait_time:.1f}秒")
                    await asyncio.sleep(wait_time)
                
                print(f"🤖 使用模型：{model.name} (尝试 {attempt + 1}/{max_retries})")
                
                # 执行请求
                start_time = time.time()
                response = await self._call_model_api(model_id, prompt, image_url, **kwargs)
                response_time = time.time() - start_time
                
                # 更新统计
                self._update_stats(model, response_time, True)
                
                # 更新当前模型
                self.current_model_id = model_id
                
                # 通知切换
                if self.on_model_switch:
                    self.on_model_switch(model_id)
                
                return response
                
            except asyncio.TimeoutError as e:
                last_error = e
                print(f"⏰ 模型 {model_id} 请求超时")
                self._update_stats(self.models[model_id], 0, False, timeout=True)
                
                # 超时立即切换
                tried_models.add(model_id)
                model.cooldown_until = time.time() + self.switch_cooldown
                
            except aiohttp.ClientError as e:
                last_error = e
                print(f"🌐 网络错误：{e}")
                self._update_stats(self.models[model_id], 0, False)
                tried_models.add(model_id)
                model.cooldown_until = time.time() + self.switch_cooldown
                
            except Exception as e:
                last_error = e
                print(f"❌ 请求失败：{e}")
                self._update_stats(self.models[model_id], 0, False)
                tried_models.add(model_id)
                model.cooldown_until = time.time() + self.switch_cooldown
        
        # 所有重试失败
        raise Exception(f"所有模型请求失败：{last_error}")
    
    async def _call_model_api(self, model_id: str, prompt: str, image_url: Optional[str], **kwargs) -> Any:
        """调用模型 API"""
        model = self.models[model_id]
        timeout = aiohttp.ClientTimeout(total=model.timeout)
        
        # TODO: 根据实际 API 实现
        # 这里是示例代码
        if image_url:
            # 视觉任务
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ]
        else:
            # 文本任务
            messages = [
                {"role": "user", "content": prompt}
            ]
        
        async with self.session.post(
            f"https://api.example.com/v1/chat/completions",
            json={
                "model": model_id,
                "messages": messages,
                **kwargs
            },
            timeout=timeout
        ) as response:
            if response.status != 200:
                raise Exception(f"API 错误：{response.status}")
            
            return await response.json()
    
    def _select_next_model(self, tried_models: set, has_image: bool) -> str:
        """选择下一个模型"""
        available = self._get_available_models(has_image)
        
        # 排除已尝试的
        available = [m for m in available if m.id not in tried_models]
        
        if available:
            # 选择优先级最高的
            next_model = available[0]
            print(f"🔀 切换到模型：{next_model.name}")
            return next_model.id
        
        # 所有模型都尝试过了，重置并重新选择
        tried_models.clear()
        return self._select_best_model(has_image)
    
    def _update_stats(self, model: ModelConfig, response_time: float, success: bool, timeout: bool = False):
        """更新模型统计"""
        stats = model.stats
        stats.total_requests += 1
        
        if success:
            stats.success_requests += 1
            stats.consecutive_failures = 0
            stats.last_success_time = time.time()
            
            # 更新平均响应时间
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
                    if time.time() - model.stats.last_error_time > 300:
                        model.health = ModelHealth.RECOVERING
                        print(f"🔄 模型 {model.name} 进入恢复状态")
                
                # 恢复中的模型
                elif model.health == ModelHealth.RECOVERING:
                    if model.stats.success_rate > 80:
                        model.health = ModelHealth.HEALTHY
                        print(f"✅ 模型 {model.name} 恢复健康")
    
    def get_status_report(self) -> Dict[str, Any]:
        """获取状态报告"""
        return {
            "current_model": {
                "id": self.current_model_id,
                "name": self.models[self.current_model_id].name if self.current_model_id else None
            },
            "models": {
                model.id: {
                    "name": model.name,
                    "capabilities": model.capabilities,
                    "is_vision_model": model.is_vision_model,
                    "health": model.health.value,
                    "priority": model.priority,
                    "success_rate": round(model.stats.success_rate, 2),
                    "avg_response_time": round(model.stats.avg_response_time, 2),
                    "total_requests": model.stats.total_requests,
                    "timeout_requests": model.stats.timeout_requests
                }
                for model in self.models.values()
            }
        }
    
    def print_status(self):
        """打印状态"""
        report = self.get_status_report()
        
        print("\n" + "="*70)
        print("📊 模型状态报告")
        print("="*70)
        print(f"当前模型：{report['current_model']['name']}")
        print()
        
        print("🖼️ 视觉模型:")
        for model_id, stats in report['models'].items():
            if stats['is_vision_model']:
                self._print_model_stats(model_id, stats)
        
        print("\n📝 文本模型:")
        for model_id, stats in report['models'].items():
            if not stats['is_vision_model']:
                self._print_model_stats(model_id, stats)
        
        print()
    
    def _print_model_stats(self, model_id: str, stats: Dict):
        """打印模型状态"""
        health_icon = {
            "healthy": "✅",
            "degraded": "⚠️",
            "unhealthy": "❌",
            "recovering": "🔄"
        }[stats['health']]
        
        print(f"  {health_icon} {stats['name']} (优先级：{stats['priority']})")
        print(f"     状态：{stats['health']} | 成功率：{stats['success_rate']}%")
        print(f"     响应：{stats['avg_response_time']}s | 请求：{stats['total_requests']} | 超时：{stats['timeout_requests']}")


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

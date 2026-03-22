#!/usr/bin/env python3
"""
智能模型管理器
自动切换模型 + 健康检查 + 负载均衡
"""
import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import aiohttp


class ModelStatus(Enum):
    """模型状态"""
    HEALTHY = "healthy"      # 健康
    DEGRADED = "degraded"    # 性能下降
    UNHEALTHY = "unhealthy"  # 不健康
    OFFLINE = "offline"      # 离线


@dataclass
class ModelConfig:
    """模型配置"""
    id: str
    name: str
    provider: str
    max_tokens: int = 4096
    timeout: int = 30  # 秒
    priority: int = 1  # 优先级（数字越小优先级越高）
    status: ModelStatus = ModelStatus.HEALTHY
    consecutive_failures: int = 0
    last_check_time: float = 0
    avg_response_time: float = 0
    request_count: int = 0
    success_count: int = 0


class ModelManager:
    """智能模型管理器"""
    
    def __init__(self):
        # 可用模型列表（根据用户提供的模型配置）
        self.models: Dict[str, ModelConfig] = {
            # 千问系列
            "qwen3.5-plus": ModelConfig(
                id="qwen3.5-plus",
                name="通义千问 3.5 Plus",
                provider="千问",
                priority=1,
                timeout=30
            ),
            "qwen3-max-2026-01-23": ModelConfig(
                id="qwen3-max-2026-01-23",
                name="通义千问 3 Max",
                provider="千问",
                priority=2,
                timeout=40
            ),
            "qwen3-coder-next": ModelConfig(
                id="qwen3-coder-next",
                name="通义千问 Coder Next",
                provider="千问",
                priority=1,
                timeout=25
            ),
            "qwen3-coder-plus": ModelConfig(
                id="qwen3-coder-plus",
                name="通义千问 Coder Plus",
                provider="千问",
                priority=2,
                timeout=30
            ),
            
            # 智谱系列
            "glm-5": ModelConfig(
                id="glm-5",
                name="智谱 GLM-5",
                provider="智谱",
                priority=1,
                timeout=30
            ),
            "glm-4.7": ModelConfig(
                id="glm-4.7",
                name="智谱 GLM-4.7",
                provider="智谱",
                priority=2,
                timeout=30
            ),
            
            # Kimi 系列
            "kimi-k2.5": ModelConfig(
                id="kimi-k2.5",
                name="Kimi K2.5",
                provider="Kimi",
                priority=1,
                timeout=30
            ),
            
            # MiniMax 系列
            "MiniMax-M2.5": ModelConfig(
                id="MiniMax-M2.5",
                name="MiniMax M2.5",
                provider="MiniMax",
                priority=2,
                timeout=30
            ),
        }
        
        self.current_model_id: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.health_check_interval = 60  # 60 秒健康检查
    
    async def initialize(self):
        """初始化"""
        self.session = aiohttp.ClientSession()
        asyncio.create_task(self._health_check_loop())
    
    async def close(self):
        """关闭"""
        if self.session:
            await self.session.close()
    
    def get_available_models(self) -> List[ModelConfig]:
        """获取可用模型（按优先级排序）"""
        available = [
            m for m in self.models.values()
            if m.status in [ModelStatus.HEALTHY, ModelStatus.DEGRADED]
        ]
        return sorted(available, key=lambda m: m.priority)
    
    async def select_model(self, task_type: str = "default") -> ModelConfig:
        """
        选择最佳模型
        
        Args:
            task_type: 任务类型 (default/code/creative)
        
        Returns:
            选中的模型配置
        """
        available_models = self.get_available_models()
        
        if not available_models:
            raise Exception("没有可用的模型")
        
        # 根据任务类型选择
        if task_type == "code":
            # 优先选择 coding 模型
            for model in available_models:
                if "coder" in model.id.lower():
                    return model
        
        # 默认选择优先级最高的
        return available_models[0]
    
    async def execute_request(self, model_id: str, prompt: str, **kwargs) -> Any:
        """
        执行请求（带自动重试和切换）
        
        Args:
            model_id: 模型 ID
            prompt: 提示词
            **kwargs: 其他参数
        
        Returns:
            模型响应
        """
        model = self.models.get(model_id)
        if not model:
            raise Exception(f"模型不存在：{model_id}")
        
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                # 执行请求
                response = await self._call_model_api(model_id, prompt, **kwargs)
                
                # 记录响应时间
                response_time = time.time() - start_time
                self._update_model_stats(model, response_time, True)
                
                return response
                
            except asyncio.TimeoutError as e:
                last_error = e
                print(f"⏰ 模型 {model_id} 请求超时 ({attempt + 1}/{max_retries})")
                self._update_model_stats(model, 0, False)
                
                # 超时后自动切换到更快的模型
                if attempt < max_retries - 1:
                    model = await self._switch_to_faster_model(model)
                    print(f"🔄 切换到模型：{model.id}")
                
            except Exception as e:
                last_error = e
                print(f"❌ 模型 {model_id} 请求失败：{e} ({attempt + 1}/{max_retries})")
                self._update_model_stats(model, 0, False)
        
        # 所有重试失败
        raise Exception(f"所有模型请求失败：{last_error}")
    
    async def _call_model_api(self, model_id: str, prompt: str, **kwargs) -> Any:
        """调用模型 API（具体实现根据 API 提供商）"""
        # TODO: 实现具体的 API 调用逻辑
        # 这里根据不同模型的 API 接口调用
        
        model = self.models[model_id]
        timeout = aiohttp.ClientTimeout(total=model.timeout)
        
        # 示例：调用 API
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
                raise Exception(f"API 返回错误：{response.status}")
            
            return await response.json()
    
    async def _switch_to_faster_model(self, current_model: ModelConfig) -> ModelConfig:
        """切换到更快的模型"""
        available = self.get_available_models()
        
        # 找到比当前模型更快的
        faster_models = [
            m for m in available
            if m.priority < current_model.priority or m.timeout < current_model.timeout
        ]
        
        if faster_models:
            return faster_models[0]
        
        # 如果没有更快的，返回第一个可用的
        return available[0] if available else current_model
    
    def _update_model_stats(self, model: ModelConfig, response_time: float, success: bool):
        """更新模型统计"""
        model.request_count += 1
        
        if success:
            model.success_count += 1
            model.consecutive_failures = 0
            
            # 更新平均响应时间（滑动平均）
            model.avg_response_time = (
                model.avg_response_time * 0.9 + response_time * 0.1
            )
            
            # 更新状态
            if model.avg_response_time > model.timeout * 0.8:
                model.status = ModelStatus.DEGRADED
            else:
                model.status = ModelStatus.HEALTHY
        else:
            model.consecutive_failures += 1
            
            # 连续失败 3 次标记为不健康
            if model.consecutive_failures >= 3:
                model.status = ModelStatus.UNHEALTHY
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while True:
            await asyncio.sleep(self.health_check_interval)
            
            for model in self.models.values():
                if model.status == ModelStatus.OFFLINE:
                    continue
                
                # 简单健康检查：检查响应时间
                if model.avg_response_time > model.timeout:
                    model.status = ModelStatus.DEGRADED
                else:
                    model.status = ModelStatus.HEALTHY
    
    def get_model_status_report(self) -> Dict[str, Any]:
        """获取模型状态报告"""
        return {
            model.id: {
                "name": model.name,
                "status": model.status.value,
                "avg_response_time": round(model.avg_response_time, 2),
                "success_rate": round(
                    model.success_count / model.request_count * 100, 2
                ) if model.request_count > 0 else 100,
                "request_count": model.request_count
            }
            for model in self.models.values()
        }


# 测试
if __name__ == "__main__":
    async def test():
        manager = ModelManager()
        await manager.initialize()
        
        # 获取可用模型
        available = manager.get_available_models()
        print(f"可用模型：{len(available)}")
        for model in available:
            print(f"  - {model.name} (优先级：{model.priority})")
        
        # 选择模型
        selected = await manager.select_model("default")
        print(f"\n选中模型：{selected.name}")
        
        await manager.close()
    
    asyncio.run(test())


if __name__ == "__main__":
    import asyncio
    asyncio.run(test())

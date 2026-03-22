#!/usr/bin/env python3
"""
性能监控器
监控上下文使用、内存、响应时间
防止阻塞和上下文溢出
"""
import asyncio
import time
import psutil
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from collections import deque


@dataclass
class PerformanceMetrics:
    """性能指标"""
    timestamp: float = field(default_factory=time.time)
    memory_mb: float = 0.0
    cpu_percent: float = 0.0
    context_size: int = 0
    response_time_ms: float = 0.0
    queue_size: int = 0
    active_tasks: int = 0


class PerformanceMonitor:
    """性能监控器"""
    
    # 阈值配置
    MEMORY_THRESHOLD_MB = 512  # 内存阈值
    CPU_THRESHOLD_PERCENT = 80  # CPU 阈值
    CONTEXT_THRESHOLD = 1000  # 上下文消息数阈值
    RESPONSE_TIME_THRESHOLD_MS = 5000  # 响应时间阈值
    QUEUE_THRESHOLD = 100  # 队列大小阈值
    
    def __init__(self, max_history: int = 100):
        self.process = psutil.Process(os.getpid())
        self.metrics_history: deque = deque(maxlen=max_history)
        self.alert_callbacks: list = []
        self.monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
    
    async def start_monitoring(self, interval: float = 5.0):
        """开始监控"""
        self.monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop(interval))
        print(f"✅ 性能监控已启动（间隔：{interval}s）")
    
    async def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        print("⏹️ 性能监控已停止")
    
    async def _monitor_loop(self, interval: float):
        """监控循环"""
        while self.monitoring:
            try:
                metrics = await self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # 检查阈值
                await self._check_thresholds(metrics)
                
                await asyncio.sleep(interval)
            except Exception as e:
                print(f"监控错误：{e}")
                await asyncio.sleep(interval)
    
    async def _collect_metrics(self) -> PerformanceMetrics:
        """收集指标"""
        metrics = PerformanceMetrics()
        
        # 内存使用
        memory_info = self.process.memory_info()
        metrics.memory_mb = memory_info.rss / 1024 / 1024
        
        # CPU 使用
        metrics.cpu_percent = self.process.cpu_percent()
        
        # 上下文大小（估算）
        # 这里需要根据实际情况获取
        metrics.context_size = len(self.metrics_history)
        
        # 队列大小（估算）
        metrics.queue_size = len(asyncio.all_tasks())
        
        return metrics
    
    async def _check_thresholds(self, metrics: PerformanceMetrics):
        """检查阈值"""
        alerts = []
        
        if metrics.memory_mb > self.MEMORY_THRESHOLD_MB:
            alerts.append(f"内存使用过高：{metrics.memory_mb:.1f}MB")
        
        if metrics.cpu_percent > self.CPU_THRESHOLD_PERCENT:
            alerts.append(f"CPU 使用过高：{metrics.cpu_percent:.1f}%")
        
        if metrics.context_size > self.CONTEXT_THRESHOLD:
            alerts.append(f"上下文过大：{metrics.context_size} 条")
        
        if metrics.queue_size > self.QUEUE_THRESHOLD:
            alerts.append(f"队列堆积：{metrics.queue_size} 个任务")
        
        # 触发告警
        for alert in alerts:
            await self._trigger_alert(alert, metrics)
    
    async def _trigger_alert(self, message: str, metrics: PerformanceMetrics):
        """触发告警"""
        print(f"⚠️ 性能告警：{message}")
        
        for callback in self.alert_callbacks:
            try:
                await callback(message, metrics)
            except Exception as e:
                print(f"告警回调错误：{e}")
    
    def on_alert(self, callback):
        """注册告警回调"""
        self.alert_callbacks.append(callback)
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """获取当前指标"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None
    
    def get_average_metrics(self, last_n: int = 10) -> Dict[str, float]:
        """获取平均指标"""
        if not self.metrics_history:
            return {}
        
        recent = list(self.metrics_history)[-last_n:]
        
        return {
            "avg_memory_mb": sum(m.memory_mb for m in recent) / len(recent),
            "avg_cpu_percent": sum(m.cpu_percent for m in recent) / len(recent),
            "avg_queue_size": sum(m.queue_size for m in recent) / len(recent),
        }
    
    def print_status(self):
        """打印状态"""
        metrics = self.get_current_metrics()
        if not metrics:
            print("暂无性能数据")
            return
        
        avg = self.get_average_metrics()
        
        print("\n" + "="*50)
        print("📊 性能监控报告")
        print("="*50)
        print(f"当前内存：{metrics.memory_mb:.1f}MB")
        print(f"当前 CPU：{metrics.cpu_percent:.1f}%")
        print(f"队列大小：{metrics.queue_size}")
        print(f"历史记录：{len(self.metrics_history)} 条")
        print("-"*50)
        print(f"平均内存：{avg.get('avg_memory_mb', 0):.1f}MB")
        print(f"平均 CPU：{avg.get('avg_cpu_percent', 0):.1f}%")
        print("="*50)


class ContextManager:
    """上下文管理器 - 防止上下文溢出"""
    
    def __init__(self, max_context_size: int = 500, max_message_age: float = 3600):
        self.max_context_size = max_context_size
        self.max_message_age = max_message_age
        self.messages: deque = deque(maxlen=max_context_size)
        self.message_timestamps: deque = deque(maxlen=max_context_size)
    
    def add_message(self, message: Any):
        """添加消息"""
        now = time.time()
        
        # 清理过期消息
        self._cleanup_expired(now)
        
        # 添加新消息
        self.messages.append(message)
        self.message_timestamps.append(now)
    
    def _cleanup_expired(self, now: float):
        """清理过期消息"""
        while self.message_timestamps:
            if now - self.message_timestamps[0] > self.max_message_age:
                self.messages.popleft()
                self.message_timestamps.popleft()
            else:
                break
    
    def get_context(self) -> list:
        """获取当前上下文"""
        return list(self.messages)
    
    def clear(self):
        """清空上下文"""
        self.messages.clear()
        self.message_timestamps.clear()
    
    @property
    def size(self) -> int:
        """获取上下文大小"""
        return len(self.messages)


# 使用示例
if __name__ == "__main__":
    async def test():
        # 创建监控器
        monitor = PerformanceMonitor()
        
        # 注册告警回调
        async def on_alert(message, metrics):
            print(f"🚨 收到告警：{message}")
        
        monitor.on_alert(on_alert)
        
        # 开始监控
        await monitor.start_monitoring(interval=2.0)
        
        # 运行一段时间
        await asyncio.sleep(10)
        
        # 打印状态
        monitor.print_status()
        
        # 停止监控
        await monitor.stop_monitoring()
    
    asyncio.run(test())

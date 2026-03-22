#!/usr/bin/env python3
"""
埋点监控系统
用户行为分析 + 性能监控
"""
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict
import asyncio
import aiofiles


@dataclass
class Event:
    """埋点事件"""
    event_type: str
    user_id: Optional[str]
    task_id: Optional[str]
    timestamp: float = field(default_factory=time.time)
    properties: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None


@dataclass
class PerformanceMetric:
    """性能指标"""
    metric_type: str
    value: float
    timestamp: float = field(default_factory=time.time)
    task_id: Optional[str] = None
    user_id: Optional[str] = None


class Analytics:
    """埋点分析系统"""
    
    def __init__(self, batch_size: int = 100, flush_interval: float = 30.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        self.events: List[Event] = []
        self.metrics: List[PerformanceMetric] = []
        
        self._lock = asyncio.Lock()
        self._flush_task: Optional[asyncio.Task] = None
        self._running = False
        
        # 实时统计
        self.stats = defaultdict(lambda: defaultdict(int))
    
    async def start(self):
        """启动埋点系统"""
        self._running = True
        self._flush_task = asyncio.create_task(self._flush_loop())
        print("✅ 埋点系统已启动")
    
    async def stop(self):
        """停止埋点系统"""
        self._running = False
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        # 最后刷新
        await self._flush_data()
        print("⏹️ 埋点系统已停止")
    
    async def track_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        task_id: Optional[str] = None,
        properties: Optional[Dict] = None,
        session_id: Optional[str] = None
    ):
        """
        追踪事件
        
        Args:
            event_type: 事件类型 (如: upload_photo, select_hairstyle, submit_task)
            user_id: 用户 ID
            task_id: 任务 ID
            properties: 事件属性
            session_id: 会话 ID
        """
        event = Event(
            event_type=event_type,
            user_id=user_id,
            task_id=task_id,
            properties=properties or {},
            session_id=session_id
        )
        
        async with self._lock:
            self.events.append(event)
            self.stats['events'][event_type] += 1
        
        # 检查是否需要立即刷新
        if len(self.events) >= self.batch_size:
            asyncio.create_task(self._flush_data())
    
    async def track_metric(
        self,
        metric_type: str,
        value: float,
        task_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """
        追踪性能指标
        
        Args:
            metric_type: 指标类型 (如: api_response_time, task_duration)
            value: 指标值
            task_id: 任务 ID
            user_id: 用户 ID
        """
        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            task_id=task_id,
            user_id=user_id
        )
        
        async with self._lock:
            self.metrics.append(metric)
    
    async def _flush_loop(self):
        """定时刷新循环"""
        while self._running:
            await asyncio.sleep(self.flush_interval)
            await self._flush_data()
    
    async def _flush_data(self):
        """刷新数据到存储"""
        async with self._lock:
            events_to_flush = self.events.copy()
            metrics_to_flush = self.metrics.copy()
            
            self.events = []
            self.metrics = []
        
        # 保存事件
        if events_to_flush:
            await self._save_events(events_to_flush)
        
        # 保存指标
        if metrics_to_flush:
            await self._save_metrics(metrics_to_flush)
    
    async def _save_events(self, events: List[Event]):
        """保存事件到文件"""
        try:
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"analytics/events_{date_str}.jsonl"
            
            # 确保目录存在
            import os
            os.makedirs("analytics", exist_ok=True)
            
            # 追加写入
            async with aiofiles.open(filename, 'a') as f:
                for event in events:
                    line = json.dumps(asdict(event), ensure_ascii=False)
                    await f.write(line + '\n')
            
            print(f"💾 已保存 {len(events)} 个事件")
            
        except Exception as e:
            print(f"保存事件失败：{e}")
    
    async def _save_metrics(self, metrics: List[PerformanceMetric]):
        """保存指标到文件"""
        try:
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"analytics/metrics_{date_str}.jsonl"
            
            import os
            os.makedirs("analytics", exist_ok=True)
            
            async with aiofiles.open(filename, 'a') as f:
                for metric in metrics:
                    line = json.dumps(asdict(metric), ensure_ascii=False)
                    await f.write(line + '\n')
            
            print(f"💾 已保存 {len(metrics)} 个指标")
            
        except Exception as e:
            print(f"保存指标失败：{e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取实时统计"""
        return {
            "events": dict(self.stats['events']),
            "pending_events": len(self.events),
            "pending_metrics": len(self.metrics)
        }
    
    def print_stats(self):
        """打印统计"""
        stats = self.get_stats()
        
        print("\n" + "=" * 50)
        print("📊 埋点统计")
        print("=" * 50)
        print(f"事件统计：")
        for event_type, count in stats['events'].items():
            print(f"  {event_type}: {count}")
        print(f"\n待处理事件：{stats['pending_events']}")
        print(f"待处理指标：{stats['pending_metrics']}")
        print("=" * 50)


class PerformanceMonitor:
    """性能监控器（装饰器模式）"""
    
    def __init__(self, analytics: Analytics):
        self.analytics = analytics
    
    def monitor(self, metric_type: str):
        """监控装饰器"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    success = True
                    return result
                except Exception as e:
                    success = False
                    raise e
                finally:
                    duration = time.time() - start_time
                    
                    # 记录性能指标
                    await self.analytics.track_metric(
                        metric_type=f"{metric_type}_duration",
                        value=duration
                    )
                    
                    # 记录成功/失败
                    await self.analytics.track_event(
                        event_type=f"{metric_type}_{'success' if success else 'fail'}",
                        properties={"duration": duration}
                    )
            
            return wrapper
        return decorator


# 使用示例
if __name__ == "__main__":
    async def test():
        # 创建埋点系统
        analytics = Analytics(batch_size=10, flush_interval=5.0)
        await analytics.start()
        
        # 追踪事件
        await analytics.track_event(
            event_type="upload_photo",
            user_id="user_123",
            properties={"file_count": 3, "total_size": 5242880}
        )
        
        await analytics.track_event(
            event_type="select_hairstyle",
            user_id="user_123",
            properties={"hairstyle": "big_waves"}
        )
        
        await analytics.track_event(
            event_type="submit_task",
            user_id="user_123",
            task_id="task_456"
        )
        
        # 追踪性能指标
        await analytics.track_metric("api_response_time", 0.5)
        await analytics.track_metric("task_duration", 30.0, task_id="task_456")
        
        # 打印统计
        analytics.print_stats()
        
        # 等待刷新
        await asyncio.sleep(6)
        
        # 停止
        await analytics.stop()
    
    asyncio.run(test())

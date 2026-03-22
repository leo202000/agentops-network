#!/usr/bin/env python3
"""
队列管理优化
优先级队列 + 并发控制
"""
import asyncio
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import heapq


class TaskPriority(Enum):
    """任务优先级"""
    URGENT = 0    # 紧急
    HIGH = 1      # 高
    NORMAL = 2    # 普通
    LOW = 3       # 低


@dataclass
class QueueTask:
    """队列任务"""
    task_id: str
    user_id: str
    priority: TaskPriority
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # 用于优先级队列比较
    def __lt__(self, other):
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.created_at < other.created_at


class QueueManager:
    """队列管理器"""
    
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.task_queue: List[QueueTask] = []
        self.running_tasks: Dict[str, QueueTask] = {}
        self.completed_tasks: Dict[str, QueueTask] = {}
        self.failed_tasks: Dict[str, QueueTask] = {}
        
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._process_task: Optional[asyncio.Task] = None
        self._running = False
        
        # 回调函数
        self.on_task_start: Optional[Callable] = None
        self.on_task_complete: Optional[Callable] = None
        self.on_task_fail: Optional[Callable] = None
    
    async def start(self):
        """启动队列处理器"""
        self._running = True
        self._process_task = asyncio.create_task(self._process_loop())
        print(f"✅ 队列管理器已启动（最大并发：{self.max_concurrent}）")
    
    async def stop(self):
        """停止队列处理器"""
        self._running = False
        if self._process_task:
            self._process_task.cancel()
            try:
                await self._process_task
            except asyncio.CancelledError:
                pass
        print("⏹️ 队列管理器已停止")
    
    async def submit_task(
        self,
        task_id: str,
        user_id: str,
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> QueueTask:
        """
        提交任务到队列
        
        Args:
            task_id: 任务 ID
            user_id: 用户 ID
            priority: 优先级
        
        Returns:
            队列任务
        """
        task = QueueTask(
            task_id=task_id,
            user_id=user_id,
            priority=priority
        )
        
        async with self._lock:
            heapq.heappush(self.task_queue, task)
        
        print(f"📥 任务 {task_id} 已加入队列（优先级：{priority.name}）")
        return task
    
    async def _process_loop(self):
        """队列处理循环"""
        while self._running:
            try:
                # 获取下一个任务
                task = await self._get_next_task()
                if not task:
                    await asyncio.sleep(0.1)
                    continue
                
                # 使用信号量控制并发
                async with self._semaphore:
                    await self._execute_task(task)
                    
            except Exception as e:
                print(f"队列处理错误：{e}")
                await asyncio.sleep(1)
    
    async def _get_next_task(self) -> Optional[QueueTask]:
        """获取下一个任务"""
        async with self._lock:
            if not self.task_queue:
                return None
            return heapq.heappop(self.task_queue)
    
    async def _execute_task(self, task: QueueTask):
        """执行任务"""
        task.started_at = time.time()
        
        async with self._lock:
            self.running_tasks[task.task_id] = task
        
        print(f"▶️ 开始执行任务 {task.task_id}")
        
        try:
            # 触发开始回调
            if self.on_task_start:
                await self.on_task_start(task)
            
            # 模拟任务执行（实际应调用即梦 API）
            await asyncio.sleep(2)  # 模拟处理时间
            
            # 任务完成
            task.completed_at = time.time()
            
            async with self._lock:
                del self.running_tasks[task.task_id]
                self.completed_tasks[task.task_id] = task
            
            print(f"✅ 任务 {task.task_id} 完成")
            
            # 触发完成回调
            if self.on_task_complete:
                await self.on_task_complete(task)
                
        except Exception as e:
            print(f"❌ 任务 {task.task_id} 失败：{e}")
            await self._handle_task_failure(task, e)
    
    async def _handle_task_failure(self, task: QueueTask, error: Exception):
        """处理任务失败"""
        task.retry_count += 1
        
        if task.retry_count < task.max_retries:
            # 重新加入队列
            print(f"🔄 任务 {task.task_id} 重试（{task.retry_count}/{task.max_retries}）")
            async with self._lock:
                heapq.heappush(self.task_queue, task)
        else:
            # 标记为失败
            task.completed_at = time.time()
            
            async with self._lock:
                if task.task_id in self.running_tasks:
                    del self.running_tasks[task.task_id]
                self.failed_tasks[task.task_id] = task
            
            print(f"❌ 任务 {task.task_id} 最终失败")
            
            # 触发失败回调
            if self.on_task_fail:
                await self.on_task_fail(task, error)
    
    def get_queue_position(self, task_id: str) -> Optional[int]:
        """获取任务在队列中的位置"""
        for i, task in enumerate(self.task_queue):
            if task.task_id == task_id:
                return i + 1
        return None
    
    def get_estimated_wait_time(self, task_id: str) -> Optional[float]:
        """获取预计等待时间（秒）"""
        position = self.get_queue_position(task_id)
        if position is None:
            return None
        
        # 估算：每个任务平均 30 秒，考虑并发
        avg_task_time = 30
        concurrent_factor = max(1, self.max_concurrent - len(self.running_tasks))
        
        return (position / concurrent_factor) * avg_task_time
    
    def get_stats(self) -> Dict:
        """获取队列统计"""
        return {
            "queued": len(self.task_queue),
            "running": len(self.running_tasks),
            "completed": len(self.completed_tasks),
            "failed": len(self.failed_tasks),
            "max_concurrent": self.max_concurrent
        }
    
    def print_status(self):
        """打印状态"""
        stats = self.get_stats()
        
        print("\n" + "=" * 50)
        print("📊 队列状态")
        print("=" * 50)
        print(f"等待中：{stats['queued']}")
        print(f"运行中：{stats['running']}")
        print(f"已完成：{stats['completed']}")
        print(f"失败：{stats['failed']}")
        print(f"最大并发：{stats['max_concurrent']}")
        print("=" * 50)


# 使用示例
if __name__ == "__main__":
    async def test():
        # 创建队列管理器
        queue = QueueManager(max_concurrent=2)
        
        # 设置回调
        async def on_start(task):
            print(f"🚀 任务 {task.task_id} 开始")
        
        async def on_complete(task):
            print(f"🎉 任务 {task.task_id} 完成")
        
        async def on_fail(task, error):
            print(f"💥 任务 {task.task_id} 失败：{error}")
        
        queue.on_task_start = on_start
        queue.on_task_complete = on_complete
        queue.on_task_fail = on_fail
        
        # 启动队列
        await queue.start()
        
        # 提交任务
        await queue.submit_task("task_1", "user_1", TaskPriority.HIGH)
        await queue.submit_task("task_2", "user_2", TaskPriority.NORMAL)
        await queue.submit_task("task_3", "user_3", TaskPriority.URGENT)
        await queue.submit_task("task_4", "user_4", TaskPriority.LOW)
        
        # 打印状态
        queue.print_status()
        
        # 等待任务完成
        await asyncio.sleep(10)
        
        # 打印最终状态
        queue.print_status()
        
        # 停止队列
        await queue.stop()
    
    asyncio.run(test())

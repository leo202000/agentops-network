#!/usr/bin/env python3
"""
Agent 超时优化器
提供任务拆分、异步处理、超时监控等功能
"""

import os
import sys
import json
import time
import signal
from datetime import datetime
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class TaskCheckpoint:
    """任务检查点"""
    task_id: str
    status: str  # pending, running, completed, failed
    progress: float  # 0.0 - 1.0
    data: Dict[str, Any]
    timestamp: float
    sub_tasks_completed: int
    sub_tasks_total: int


class TaskSplitter:
    """任务拆分器 - 将大任务拆分为多个子任务"""
    
    def __init__(self, max_subtask_time: int = 120):
        """
        Args:
            max_subtask_time: 每个子任务最大执行时间（秒），默认2分钟
        """
        self.max_subtask_time = max_subtask_time
        self.checkpoints_dir = Path("/tmp/agent_checkpoints")
        self.checkpoints_dir.mkdir(exist_ok=True)
    
    def split_task(self, task_name: str, items: List[Any], 
                   processor: Callable[[Any], Any]) -> Dict[str, Any]:
        """
        将列表任务拆分为多个子任务
        
        Args:
            task_name: 任务名称
            items: 要处理的列表
            processor: 处理函数
        
        Returns:
            处理结果
        """
        total = len(items)
        results = []
        checkpoint = self._load_checkpoint(task_name)
        
        start_idx = checkpoint.sub_tasks_completed if checkpoint else 0
        
        print(f"🔄 任务拆分: {task_name}")
        print(f"   总项目数: {total}")
        print(f"   起始位置: {start_idx}")
        
        for i in range(start_idx, total):
            item = items[i]
            subtask_start = time.time()
            
            try:
                print(f"\n📦 子任务 {i+1}/{total} (预计 {self.max_subtask_time}s 内完成)")
                result = processor(item)
                results.append(result)
                
                # 保存 checkpoint
                self._save_checkpoint(task_name, TaskCheckpoint(
                    task_id=f"{task_name}_{i}",
                    status="running",
                    progress=(i + 1) / total,
                    data={"results": results},
                    timestamp=time.time(),
                    sub_tasks_completed=i + 1,
                    sub_tasks_total=total
                ))
                
                subtask_time = time.time() - subtask_start
                print(f"   ✅ 完成 ({subtask_time:.1f}s)")
                
                # 如果子任务耗时过长，警告
                if subtask_time > self.max_subtask_time:
                    print(f"   ⚠️ 警告: 子任务耗时 {subtask_time:.1f}s，超过阈值 {self.max_subtask_time}s")
                
            except Exception as e:
                print(f"   ❌ 失败: {e}")
                # 保存失败状态
                self._save_checkpoint(task_name, TaskCheckpoint(
                    task_id=f"{task_name}_{i}",
                    status="failed",
                    progress=i / total,
                    data={"results": results, "error": str(e)},
                    timestamp=time.time(),
                    sub_tasks_completed=i,
                    sub_tasks_total=total
                ))
                raise
        
        # 标记完成
        self._save_checkpoint(task_name, TaskCheckpoint(
            task_id=task_name,
            status="completed",
            progress=1.0,
            data={"results": results},
            timestamp=time.time(),
            sub_tasks_completed=total,
            sub_tasks_total=total
        ))
        
        return {
            "task_name": task_name,
            "total_items": total,
            "completed": len(results),
            "results": results
        }
    
    def _save_checkpoint(self, task_name: str, checkpoint: TaskCheckpoint):
        """保存检查点"""
        checkpoint_file = self.checkpoints_dir / f"{task_name}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(asdict(checkpoint), f, indent=2)
    
    def _load_checkpoint(self, task_name: str) -> Optional[TaskCheckpoint]:
        """加载检查点"""
        checkpoint_file = self.checkpoints_dir / f"{task_name}.json"
        if checkpoint_file.exists():
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)
                return TaskCheckpoint(**data)
        return None
    
    def clear_checkpoint(self, task_name: str):
        """清除检查点"""
        checkpoint_file = self.checkpoints_dir / f"{task_name}.json"
        if checkpoint_file.exists():
            checkpoint_file.unlink()


class TimeoutManager:
    """超时管理器"""
    
    def __init__(self, soft_timeout: int = 300, hard_timeout: int = 600):
        """
        Args:
            soft_timeout: 软超时时间（秒），默认5分钟
            hard_timeout: 硬超时时间（秒），默认10分钟
        """
        self.soft_timeout = soft_timeout
        self.hard_timeout = hard_timeout
        self.start_time = None
        self.alarm_set = False
    
    def start(self):
        """开始计时"""
        self.start_time = time.time()
        
        # 设置硬超时信号
        def timeout_handler(signum, frame):
            raise TimeoutError(f"任务执行超过硬超时 {self.hard_timeout} 秒")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.hard_timeout)
        self.alarm_set = True
        
        print(f"⏱️ 超时管理器启动")
        print(f"   软超时: {self.soft_timeout}s")
        print(f"   硬超时: {self.hard_timeout}s")
    
    def check_timeout(self) -> Dict[str, Any]:
        """检查超时状态"""
        if not self.start_time:
            return {"status": "not_started"}
        
        elapsed = time.time() - self.start_time
        
        status = {
            "elapsed": elapsed,
            "soft_timeout": self.soft_timeout,
            "hard_timeout": self.hard_timeout,
            "remaining_soft": max(0, self.soft_timeout - elapsed),
            "remaining_hard": max(0, self.hard_timeout - elapsed),
        }
        
        if elapsed > self.hard_timeout:
            status["status"] = "hard_timeout"
            status["message"] = f"已超过硬超时 {self.hard_timeout}s"
        elif elapsed > self.soft_timeout:
            status["status"] = "soft_timeout"
            status["message"] = f"已超过软超时 {self.soft_timeout}s，建议拆分任务"
        else:
            status["status"] = "normal"
            status["message"] = f"正常执行中 ({elapsed:.1f}s / {self.soft_timeout}s)"
        
        return status
    
    def stop(self):
        """停止计时"""
        if self.alarm_set:
            signal.alarm(0)
            self.alarm_set = False
        
        if self.start_time:
            elapsed = time.time() - self.start_time
            print(f"⏱️ 任务完成，总耗时: {elapsed:.1f}s")


class AgentOptimizer:
    """Agent 优化器主类"""
    
    def __init__(self):
        self.task_splitter = TaskSplitter()
        self.timeout_manager = TimeoutManager()
        self.stats = {
            "tasks_total": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_timeout": 0,
            "avg_time": 0.0
        }
    
    def run_with_split(self, task_name: str, items: List[Any], 
                       processor: Callable[[Any], Any]) -> Dict[str, Any]:
        """
        使用任务拆分运行
        
        Args:
            task_name: 任务名称
            items: 要处理的列表
            processor: 处理函数
        
        Returns:
            处理结果
        """
        self.stats["tasks_total"] += 1
        
        try:
            # 启动超时管理
            self.timeout_manager.start()
            
            # 执行拆分任务
            result = self.task_splitter.split_task(task_name, items, processor)
            
            self.stats["tasks_completed"] += 1
            self.timeout_manager.stop()
            
            return result
            
        except TimeoutError as e:
            self.stats["tasks_timeout"] += 1
            self.timeout_manager.stop()
            print(f"⏰ 任务超时: {e}")
            raise
            
        except Exception as e:
            self.stats["tasks_failed"] += 1
            self.timeout_manager.stop()
            print(f"❌ 任务失败: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Agent 优化器测试")
    print("=" * 60)
    
    optimizer = AgentOptimizer()
    
    # 测试任务拆分
    def process_item(item):
        import time
        time.sleep(0.3)  # 模拟处理时间
        return f"Processed: {item}"
    
    items = [f"item_{i}" for i in range(5)]
    
    try:
        result = optimizer.run_with_split("demo_task", items, process_item)
        print(f"\n✅ 任务完成!")
        print(f"   处理项目: {result['completed']}/{result['total_items']}")
        
        # 显示统计
        stats = optimizer.get_stats()
        print(f"\n📊 统计:")
        print(f"   总任务: {stats['tasks_total']}")
        print(f"   已完成: {stats['tasks_completed']}")
        print(f"   失败: {stats['tasks_failed']}")
        print(f"   超时: {stats['tasks_timeout']}")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    
    print("\n" + "=" * 60)
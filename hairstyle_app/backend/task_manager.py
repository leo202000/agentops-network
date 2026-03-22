#!/usr/bin/env python3
"""
任务状态管理系统
基于即梦平台经验：5 状态流转 + 确认机制
"""
import asyncio
import json
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any, Callable
import uuid


class TaskStatus(Enum):
    """任务状态枚举"""
    WAITING = 10        # 等待中
    QUEUING = 30        # 排队中
    PROCESSING = 42     # 处理中 (AI 生成中)
    COMPLETED = 45      # 生成完成 (等待用户确认)
    CONFIRMED = 20      # 用户已确认 (完全完成)
    FAILED = 50         # 失败


class Task:
    """任务实体"""
    def __init__(self, user_id: str, photos: list, hairstyle_choice: str, description: str = ""):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.photos = photos  # 照片列表
        self.hairstyle_choice = hairstyle_choice  # 发型选择
        self.description = description  # 自定义描述
        self.status = TaskStatus.WAITING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # 即梦 API 相关
        self.jimeng_task_id = None
        self.jimeng_submit_id = None
        self.confirm_status = 1  # 1 待确认，2 已确认
        
        # 队列信息
        self.priority = 5
        self.queue_idx = 0
        self.queue_length = 1
        self.estimated_wait_time = 0
        
        # 结果
        self.result_image_url = None
        self.error_message = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status.value,
            'status_name': self.status.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'jimeng_task_id': self.jimeng_task_id,
            'confirm_status': self.confirm_status,
            'queue_idx': self.queue_idx,
            'estimated_wait_time': self.estimated_wait_time,
            'result_image_url': self.result_image_url,
            'error_message': self.error_message
        }
    
    def update_status(self, status: TaskStatus):
        """更新状态"""
        self.status = status
        self.updated_at = datetime.now()


class TaskManager:
    """任务管理器"""
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.user_tasks: Dict[str, list] = {}  # user_id -> [task_ids]
        self.listeners: Dict[str, list] = {}  # task_id -> [callbacks]
    
    def create_task(self, user_id: str, photos: list, hairstyle_choice: str, description: str = "") -> Task:
        """创建任务"""
        task = Task(user_id, photos, hairstyle_choice, description)
        self.tasks[task.id] = task
        
        if user_id not in self.user_tasks:
            self.user_tasks[user_id] = []
        self.user_tasks[user_id].append(task.id)
        
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: TaskStatus, **kwargs):
        """更新任务状态"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        task.update_status(status)
        
        # 更新其他属性
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        # 通知监听者
        self._notify_listeners(task)
        
        return True
    
    def add_listener(self, task_id: str, callback: Callable):
        """添加监听器"""
        if task_id not in self.listeners:
            self.listeners[task_id] = []
        self.listeners[task_id].append(callback)
    
    def _notify_listeners(self, task: Task):
        """通知监听者"""
        if task.id in self.listeners:
            for callback in self.listeners[task.id]:
                try:
                    callback(task.to_dict())
                except Exception as e:
                    print(f"Listener error: {e}")
    
    def get_user_tasks(self, user_id: str) -> list:
        """获取用户的所有任务"""
        task_ids = self.user_tasks.get(user_id, [])
        return [self.tasks[tid] for tid in task_ids if tid in self.tasks]
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        to_remove = []
        for task_id, task in self.tasks.items():
            if task.created_at < cutoff:
                to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.tasks[task_id]
        
        return len(to_remove)


class TaskStateMachine:
    """任务状态机"""
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
    
    def transition(self, task_id: str, new_status: TaskStatus, **kwargs) -> bool:
        """状态转换"""
        task = self.task_manager.get_task(task_id)
        if not task:
            return False
        
        # 验证状态转换是否合法
        if not self._is_valid_transition(task.status, new_status):
            print(f"Invalid transition: {task.status} -> {new_status}")
            return False
        
        # 执行状态转换
        return self.task_manager.update_task_status(task_id, new_status, **kwargs)
    
    def _is_valid_transition(self, from_status: TaskStatus, to_status: TaskStatus) -> bool:
        """验证状态转换是否合法"""
        valid_transitions = {
            TaskStatus.WAITING: [TaskStatus.QUEUING, TaskStatus.FAILED],
            TaskStatus.QUEUING: [TaskStatus.PROCESSING, TaskStatus.FAILED],
            TaskStatus.PROCESSING: [TaskStatus.COMPLETED, TaskStatus.FAILED],
            TaskStatus.COMPLETED: [TaskStatus.CONFIRMED, TaskStatus.PROCESSING],  # 可以重新生成
            TaskStatus.CONFIRMED: [],  # 终态
            TaskStatus.FAILED: [TaskStatus.WAITING]  # 可以重试
        }
        
        return to_status in valid_transitions.get(from_status, [])


# 测试
if __name__ == "__main__":
    # 创建任务管理器
    tm = TaskManager()
    sm = TaskStateMachine(tm)
    
    # 创建任务
    task = tm.create_task(
        user_id="user_123",
        photos=["photo1.jpg", "photo2.jpg"],
        hairstyle_choice="大波浪",
        description="自然蓬松的大波浪发型"
    )
    
    print(f"创建任务：{task.id}")
    print(f"初始状态：{task.status.name}")
    
    # 状态转换
    sm.transition(task.id, TaskStatus.QUEUING)
    print(f"状态转换：{task.status.name}")
    
    sm.transition(task.id, TaskStatus.PROCESSING)
    print(f"状态转换：{task.status.name}")
    
    sm.transition(task.id, TaskStatus.COMPLETED, result_image_url="https://example.com/result.jpg")
    print(f"状态转换：{task.status.name}")
    print(f"结果图片：{task.result_image_url}")
    
    # 用户确认
    confirm = input("确认使用？(y/n): ")
    if confirm.lower() == 'y':
        sm.transition(task.id, TaskStatus.CONFIRMED)
        print(f"最终状态：{task.status.name}")
    else:
        sm.transition(task.id, TaskStatus.PROCESSING)  # 重新生成
        print(f"重新生成：{task.status.name}")

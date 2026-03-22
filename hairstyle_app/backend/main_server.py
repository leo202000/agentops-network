#!/usr/bin/env python3
"""
发型生成主服务器
整合任务管理 + WebSocket Racing + 即梦 API
"""
import asyncio
import json
import os
from pathlib import Path
from aiohttp import web

from task_manager import TaskManager, TaskStateMachine, TaskStatus
from websocket_racing import RacingServer
from jimeng_integration import JimengAPI, JimengTaskProcessor


class HairstyleServer:
    """发型生成服务器"""
    
    def __init__(self):
        self.task_manager = TaskManager()
        self.state_machine = TaskStateMachine(self.task_manager)
        self.racing_server = RacingServer(self.task_manager)
        
        # 即梦 API
        access_key = os.getenv("JIMENG_ACCESS_KEY_ID")
        secret_key = os.getenv("JIMENG_SECRET_ACCESS_KEY")
        self.jimeng_api = JimengAPI(access_key, secret_key)
        self.processor = None
        
        # Web 应用
        self.app = web.Application()
        self._setup_routes()
    
    def _setup_routes(self):
        """设置路由"""
        self.app.router.add_post('/api/task/create', self.create_task_handler)
        self.app.router.add_get('/api/task/{task_id}', self.get_task_handler)
        self.app.router.add_post('/api/task/{task_id}/confirm', self.confirm_task_handler)
        self.app.router.add_get('/api/user/{user_id}/tasks', self.get_user_tasks_handler)
    
    async def create_task_handler(self, request: web.Request) -> web.Response:
        """创建任务"""
        try:
            data = await request.json()
            
            user_id = data.get('user_id')
            photos = data.get('photos', [])
            hairstyle_choice = data.get('hairstyle_choice')
            description = data.get('description', '')
            
            if not user_id or not photos or not hairstyle_choice:
                return web.json_response({
                    'error': 'Missing required fields'
                }, status=400)
            
            # 创建任务
            task = self.task_manager.create_task(
                user_id=user_id,
                photos=photos,
                hairstyle_choice=hairstyle_choice,
                description=description
            )
            
            # 启动任务处理
            asyncio.create_task(self.processor.process_task(task))
            
            return web.json_response({
                'task_id': task.id,
                'status': task.status.value,
                'status_name': task.status.name
            })
            
        except Exception as e:
            return web.json_response({
                'error': str(e)
            }, status=500)
    
    async def get_task_handler(self, request: web.Request) -> web.Response:
        """获取任务状态"""
        task_id = request.match_info['task_id']
        task = self.task_manager.get_task(task_id)
        
        if not task:
            return web.json_response({'error': 'Task not found'}, status=404)
        
        return web.json_response(task.to_dict())
    
    async def confirm_task_handler(self, request: web.Request) -> web.Response:
        """确认任务"""
        task_id = request.match_info['task_id']
        task = self.task_manager.get_task(task_id)
        
        if not task:
            return web.json_response({'error': 'Task not found'}, status=404)
        
        if task.status != TaskStatus.COMPLETED:
            return web.json_response({
                'error': 'Task not in COMPLETED status'
            }, status=400)
        
        # 更新为已确认
        self.state_machine.transition(task_id, TaskStatus.CONFIRMED)
        
        return web.json_response({
            'success': True,
            'status': 'CONFIRMED'
        })
    
    async def get_user_tasks_handler(self, request: web.Request) -> web.Response:
        """获取用户任务列表"""
        user_id = request.match_info['user_id']
        tasks = self.task_manager.get_user_tasks(user_id)
        
        return web.json_response({
            'tasks': [task.to_dict() for task in tasks]
        })
    
    async def start(self, host: str = '0.0.0.0', port: int = 8080):
        """启动服务器"""
        # 启动即梦处理器
        self.processor = JimengTaskProcessor(self.jimeng_api, self.task_manager, self.racing_server)
        await self.processor.start()
        
        # 启动 Racing 服务器
        await self.racing_server.start(host, port + 1)  # WebSocket 端口
        
        # 启动 Web 服务器
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        print(f"发型生成服务器启动：http://{host}:{port}")
        print(f"WebSocket 服务器：ws://{host}:{port + 1}")
    
    async def stop(self):
        """停止服务器"""
        if self.processor:
            await self.processor.stop()


# 主程序
if __name__ == "__main__":
    server = HairstyleServer()
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        asyncio.run(server.stop())
        print("\n服务器已停止")

#!/usr/bin/env python3
"""
发型生成主服务器 v2
整合所有模块：任务管理 + WebSocket + 即梦 API + 上传 + 模板 + 队列 + 埋点
"""
import asyncio
import json
import os
from pathlib import Path
from aiohttp import web
import aiohttp_cors

# 导入所有模块
from task_manager import TaskManager, TaskStateMachine, TaskStatus
from websocket_racing import RacingServer
from jimeng_integration import JimengAPI, JimengTaskProcessor
from image_upload_service import ImageUploadService
from hairstyle_templates import HairstyleTemplateManager
from queue_manager import QueueManager, TaskPriority
from analytics import Analytics, PerformanceMonitor


class HairstyleServerV2:
    """发型生成服务器 v2"""
    
    def __init__(self):
        # 核心组件
        self.task_manager = TaskManager()
        self.state_machine = TaskStateMachine(self.task_manager)
        self.racing_server = RacingServer(self.task_manager)
        
        # 新增模块
        self.upload_service = ImageUploadService()
        self.template_manager = HairstyleTemplateManager()
        self.queue_manager = QueueManager(max_concurrent=3)
        self.analytics = Analytics(batch_size=100, flush_interval=30.0)
        self.performance_monitor = PerformanceMonitor(self.analytics)
        
        # 即梦 API
        access_key = os.getenv("JIMENG_ACCESS_KEY_ID")
        secret_key = os.getenv("JIMENG_SECRET_ACCESS_KEY")
        self.jimeng_api = JimengAPI(access_key, secret_key)
        self.processor = None
        
        # Web 应用
        self.app = web.Application()
        self._setup_routes()
        self._setup_cors()
        
        # 设置队列回调
        self._setup_queue_callbacks()
    
    def _setup_routes(self):
        """设置路由"""
        # 任务 API
        self.app.router.add_post('/api/task/create', self.create_task_handler)
        self.app.router.add_get('/api/task/{task_id}', self.get_task_handler)
        self.app.router.add_post('/api/task/{task_id}/confirm', self.confirm_task_handler)
        self.app.router.add_get('/api/user/{user_id}/tasks', self.get_user_tasks_handler)
        
        # 上传 API
        self.app.router.add_post('/api/upload', self.upload_service.handle_upload_request)
        self.app.router.add_post('/api/upload/delete', self.upload_service.handle_delete_request)
        self.app.router.add_static('/uploads', self.upload_service.config.upload_dir)
        
        # 模板 API
        self.app.router.add_get('/api/templates', self.get_templates_handler)
        self.app.router.add_get('/api/templates/{template_id}', self.get_template_handler)
        self.app.router.add_post('/api/templates/{template_id}/prompt', self.generate_prompt_handler)
        
        # 队列 API
        self.app.router.add_get('/api/queue/status', self.get_queue_status_handler)
        self.app.router.add_get('/api/queue/position/{task_id}', self.get_queue_position_handler)
        
        # 统计 API
        self.app.router.add_get('/api/analytics/stats', self.get_analytics_stats_handler)
    
    def _setup_cors(self):
        """设置 CORS"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # 为所有路由添加 CORS
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    def _setup_queue_callbacks(self):
        """设置队列回调"""
        async def on_task_start(task):
            await self.analytics.track_event(
                event_type="task_start",
                task_id=task.task_id,
                user_id=task.user_id
            )
            # 更新任务状态
            self.state_machine.transition(task.task_id, TaskStatus.PROCESSING)
        
        async def on_task_complete(task):
            await self.analytics.track_event(
                event_type="task_complete",
                task_id=task.task_id,
                user_id=task.user_id,
                properties={"duration": task.completed_at - task.started_at}
            )
            # 更新任务状态
            self.state_machine.transition(task.task_id, TaskStatus.COMPLETED)
        
        async def on_task_fail(task, error):
            await self.analytics.track_event(
                event_type="task_fail",
                task_id=task.task_id,
                user_id=task.user_id,
                properties={"error": str(error), "retry_count": task.retry_count}
            )
            # 更新任务状态
            self.state_machine.transition(task.task_id, TaskStatus.FAILED)
        
        self.queue_manager.on_task_start = on_task_start
        self.queue_manager.on_task_complete = on_task_complete
        self.queue_manager.on_task_fail = on_task_fail
    
    # ========== 任务 API ==========
    
    async def create_task_handler(self, request: web.Request) -> web.Response:
        """创建任务"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            data = await request.json()
            
            user_id = data.get('user_id')
            photos = data.get('photos', [])
            hairstyle_choice = data.get('hairstyle_choice')
            description = data.get('description', '')
            priority = data.get('priority', 'NORMAL')

            if not user_id or not photos or not hairstyle_choice:
                return web.json_response({
                    'success': False,
                    'error': '缺少必要参数'
                }, status=400)

            # 创建任务
            task = self.task_manager.create_task(
                user_id=user_id,
                photos=photos,
                hairstyle_choice=hairstyle_choice,
                description=description
            )
            
            # 提交到队列
            priority_enum = getattr(TaskPriority, priority, TaskPriority.NORMAL)
            await self.queue_manager.submit_task(task.id, user_id, priority_enum)
            
            # 埋点
            await self.analytics.track_event(
                event_type="task_create",
                user_id=user_id,
                task_id=task.id,
                properties={
                    "hairstyle_choice": hairstyle_choice,
                    "photo_count": len(photos),
                    "priority": priority
                }
            )
            
            # 性能监控
            duration = asyncio.get_event_loop().time() - start_time
            await self.analytics.track_metric("api_create_task_duration", duration)
            
            return web.json_response({
                'success': True,
                'task': task.to_dict()
            })
            
        except Exception as e:
            await self.analytics.track_event(
                event_type="task_create_fail",
                properties={"error": str(e)}
            )
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def get_task_handler(self, request: web.Request) -> web.Response:
        """获取任务状态"""
        task_id = request.match_info['task_id']
        task = self.task_manager.get_task(task_id)
        
        if not task:
            return web.json_response({
                'success': False,
                'error': '任务不存在'
            }, status=404)
        
        # 添加队列信息
        response = task.to_dict()
        position = self.queue_manager.get_queue_position(task_id)
        if position:
            response['queue_position'] = position
            response['estimated_wait'] = self.queue_manager.get_estimated_wait_time(task_id)
        
        return web.json_response({
            'success': True,
            'task': response
        })
    
    async def confirm_task_handler(self, request: web.Request) -> web.Response:
        """确认任务"""
        task_id = request.match_info['task_id']
        task = self.task_manager.get_task(task_id)
        
        if not task:
            return web.json_response({
                'success': False,
                'error': '任务不存在'
            }, status=404)
        
        if task.status != TaskStatus.COMPLETED:
            return web.json_response({
                'success': False,
                'error': '任务未完成'
            }, status=400)
        
        # 更新为已确认
        self.state_machine.transition(task_id, TaskStatus.CONFIRMED)
        
        # 埋点
        await self.analytics.track_event(
            event_type="task_confirm",
            task_id=task_id,
            user_id=task.user_id
        )
        
        return web.json_response({
            'success': True,
            'status': 'CONFIRMED'
        })
    
    async def get_user_tasks_handler(self, request: web.Request) -> web.Response:
        """获取用户任务列表"""
        user_id = request.match_info['user_id']
        tasks = self.task_manager.get_user_tasks(user_id)
        
        return web.json_response({
            'success': True,
            'tasks': [task.to_dict() for task in tasks]
        })
    
    # ========== 模板 API ==========
    
    async def get_templates_handler(self, request: web.Request) -> web.Response:
        """获取所有模板"""
        templates = self.template_manager.get_all_templates()
        
        return web.json_response({
            'success': True,
            'templates': [
                self.template_manager.get_template_info(t.id)
                for t in templates
            ]
        })
    
    async def get_template_handler(self, request: web.Request) -> web.Response:
        """获取单个模板"""
        template_id = request.match_info['template_id']
        template_info = self.template_manager.get_template_info(template_id)
        
        if not template_info:
            return web.json_response({
                'success': False,
                'error': '模板不存在'
            }, status=404)
        
        return web.json_response({
            'success': True,
            'template': template_info
        })
    
    async def generate_prompt_handler(self, request: web.Request) -> web.Response:
        """生成提示词"""
        template_id = request.match_info['template_id']
        
        try:
            data = await request.json()
            custom_description = data.get('custom_description', '')
            
            result = self.template_manager.generate_prompt(template_id, custom_description)
            
            if 'error' in result:
                return web.json_response({
                    'success': False,
                    'error': result['error']
                }, status=400)
            
            return web.json_response({
                'success': True,
                'prompt': result
            })
            
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    # ========== 队列 API ==========
    
    async def get_queue_status_handler(self, request: web.Request) -> web.Response:
        """获取队列状态"""
        stats = self.queue_manager.get_stats()
        
        return web.json_response({
            'success': True,
            'queue': stats
        })
    
    async def get_queue_position_handler(self, request: web.Request) -> web.Response:
        """获取任务在队列中的位置"""
        task_id = request.match_info['task_id']
        
        position = self.queue_manager.get_queue_position(task_id)
        if position is None:
            return web.json_response({
                'success': False,
                'error': '任务不在队列中'
            }, status=404)
        
        estimated_wait = self.queue_manager.get_estimated_wait_time(task_id)
        
        return web.json_response({
            'success': True,
            'position': position,
            'estimated_wait': estimated_wait
        })
    
    # ========== 统计 API ==========
    
    async def get_analytics_stats_handler(self, request: web.Request) -> web.Response:
        """获取埋点统计"""
        stats = self.analytics.get_stats()
        
        return web.json_response({
            'success': True,
            'stats': stats
        })
    
    # ========== 启动/停止 ==========
    
    async def start(self, host: str = '0.0.0.0', port: int = 8080):
        """启动服务器"""
        # 启动埋点系统
        await self.analytics.start()
        
        # 启动队列管理器
        await self.queue_manager.start()
        
        # 启动即梦处理器
        self.processor = JimengTaskProcessor(self.jimeng_api, self.task_manager, self.racing_server)
        await self.processor.start()
        
        # 启动 Racing 服务器
        await self.racing_server.start(host, port + 1)
        
        # 启动 Web 服务器
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        print(f"🚀 发型生成服务器 v2 启动")
        print(f"   HTTP API: http://{host}:{port}")
        print(f"   WebSocket: ws://{host}:{port + 1}")
        print(f"   前端访问: http://{host}:{port}/frontend/index.html")
    
    async def stop(self):
        """停止服务器"""
        print("\n⏹️ 正在停止服务器...")
        
        if self.processor:
            await self.processor.stop()
        
        await self.queue_manager.stop()
        await self.analytics.stop()
        
        print("✅ 服务器已停止")


# 主程序
if __name__ == "__main__":
    server = HairstyleServerV2()
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        asyncio.run(server.stop())

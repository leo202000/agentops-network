#!/usr/bin/env python3
"""
WebSocket Racing 模式实时通信
基于即梦平台经验：WebSocket 优先 + HTTP 轮询降级 + 10 秒超时
"""
import asyncio
import json
import time
from typing import Optional, Callable, Dict, Any
from enum import Enum
import websockets
from aiohttp import web


class ConnectionState(Enum):
    """连接状态"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    POLLING = "polling"  # 降级到轮询
    DISCONNECTED = "disconnected"


class TaskPollingManager:
    """
    任务轮询管理器 - Racing 模式
    WebSocket 优先 + HTTP 轮询降级 + 10 秒超时
    """
    
    def __init__(self, task_id: str, ws_url: str, http_url: str, 
                 on_update: Callable[[Dict[str, Any]], None],
                 timeout: int = 10000,
                 polling_interval: int = 3000):
        self.task_id = task_id
        self.ws_url = ws_url
        self.http_url = http_url
        self.on_update = on_update
        self.timeout = timeout  # WebSocket 超时 (毫秒)
        self.polling_interval = polling_interval  # 轮询间隔 (毫秒)
        
        self.state = ConnectionState.CONNECTING
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.polling_task: Optional[asyncio.Task] = None
        self.timeout_timer: Optional[asyncio.TimerHandle] = None
        self.running = True
    
    async def start(self):
        """启动 Racing 模式"""
        print(f"[{self.task_id}] 启动 Racing 模式")
        
        # 同时启动 WebSocket 和 HTTP 轮询
        ws_task = asyncio.create_task(self._connect_websocket())
        polling_task = asyncio.create_task(self._start_polling())
        
        # 设置 WebSocket 超时定时器
        self.timeout_timer = asyncio.get_event_loop().call_later(
            self.timeout / 1000,
            self._on_websocket_timeout
        )
        
        # 等待任一连接成功
        done, pending = await asyncio.wait(
            [ws_task, polling_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # 清理未完成的
        for task in pending:
            task.cancel()
        
        print(f"[{self.task_id}] Racing 模式完成，状态：{self.state.value}")
    
    async def _connect_websocket(self):
        """连接 WebSocket"""
        try:
            print(f"[{self.task_id}] 尝试连接 WebSocket...")
            async with websockets.connect(self.ws_url) as websocket:
                self.websocket = websocket
                self.state = ConnectionState.CONNECTED
                
                # 取消超时定时器
                if self.timeout_timer:
                    self.timeout_timer.cancel()
                
                print(f"[{self.task_id}] WebSocket 连接成功")
                
                # 监听消息
                async for message in websocket:
                    data = json.loads(message)
                    print(f"[{self.task_id}] WebSocket 消息：{data}")
                    await self._handle_message(data)
                    
        except Exception as e:
            print(f"[{self.task_id}] WebSocket 错误：{e}")
            self.state = ConnectionState.DISCONNECTED
    
    def _on_websocket_timeout(self):
        """WebSocket 超时回调"""
        if self.state == ConnectionState.CONNECTING:
            print(f"[{self.task_id}] WebSocket 超时 (10000ms)，触发降级到轮询")
            self.state = ConnectionState.POLLING
    
    async def _start_polling(self):
        """HTTP 轮询"""
        print(f"[{self.task_id}] 启动 HTTP 轮询")
        
        while self.running:
            try:
                status = await self._fetch_task_status()
                print(f"[{self.task_id}] 轮询结果：{status}")
                
                await self._handle_message(status)
                
                # 如果任务完成或失败，停止轮询
                if status.get('status') in [20, 50]:
                    print(f"[{self.task_id}] 任务完成/失败，停止轮询")
                    break
                
            except Exception as e:
                print(f"[{self.task_id}] 轮询错误：{e}")
            
            await asyncio.sleep(self.polling_interval / 1000)
    
    async def _fetch_task_status(self) -> Dict[str, Any]:
        """获取任务状态"""
        # 这里应该调用实际的任务状态 API
        # 示例代码
        return {
            'task_id': self.task_id,
            'status': 42,  # 处理中
            'queue_idx': 0,
            'queue_length': 1
        }
    
    async def _handle_message(self, data: Dict[str, Any]):
        """处理消息"""
        if self.on_update:
            await self.on_update(data)
    
    def stop(self):
        """停止"""
        self.running = False
        
        if self.websocket:
            asyncio.create_task(self.websocket.close())
        
        if self.timeout_timer:
            self.timeout_timer.cancel()


class RacingServer:
    """Racing 模式服务器"""
    
    def __init__(self, task_manager):
        self.task_manager = task_manager
        self.app = web.Application()
        self.app.router.add_get('/ws/task/{task_id}', self.websocket_handler)
        self.app.router.add_get('/api/task/{task_id}/status', self.status_handler)
        self.ws_clients: Dict[str, set] = {}  # task_id -> {websocket, ...}
    
    async def websocket_handler(self, request: web.Request) -> web.WebSocketResponse:
        """WebSocket 处理器"""
        task_id = request.match_info['task_id']
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # 添加到客户端列表
        if task_id not in self.ws_clients:
            self.ws_clients[task_id] = set()
        self.ws_clients[task_id].add(ws)
        
        print(f"[{task_id}] WebSocket 客户端连接")
        
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    print(f"[{task_id}] 收到消息：{data}")
                elif msg.type == web.WSMsgType.ERROR:
                    print(f"[{task_id}] WebSocket 错误：{ws.exception()}")
        finally:
            self.ws_clients[task_id].discard(ws)
            print(f"[{task_id}] WebSocket 客户端断开")
        
        return ws
    
    async def status_handler(self, request: web.Request) -> web.Response:
        """HTTP 轮询状态处理器"""
        task_id = request.match_info['task_id']
        task = self.task_manager.get_task(task_id)
        
        if not task:
            return web.json_response({'error': 'Task not found'}, status=404)
        
        return web.json_response(task.to_dict())
    
    async def notify_clients(self, task_id: str, data: Dict[str, Any]):
        """通知所有 WebSocket 客户端"""
        if task_id in self.ws_clients:
            message = json.dumps(data)
            for ws in self.ws_clients[task_id]:
                try:
                    await ws.send_str(message)
                except Exception as e:
                    print(f"[{task_id}] 发送消息失败：{e}")
    
    async def start(self, host: str = '0.0.0.0', port: int = 8080):
        """启动服务器"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        print(f"Racing 服务器启动：http://{host}:{port}")


# 测试
if __name__ == "__main__":
    from task_manager import TaskManager, TaskStateMachine, TaskStatus
    
    # 创建任务管理器
    tm = TaskManager()
    sm = TaskStateMachine(tm)
    
    # 创建测试任务
    task = tm.create_task(
        user_id="user_123",
        photos=["photo1.jpg"],
        hairstyle_choice="大波浪"
    )
    
    print(f"测试任务：{task.id}")
    
    # 创建 Racing 服务器
    server = RacingServer(tm)
    
    # 模拟任务状态更新
    async def simulate_task_progress():
        await asyncio.sleep(2)
        sm.transition(task.id, TaskStatus.QUEUING, queue_idx=0, queue_length=1)
        await server.notify_clients(task.id, task.to_dict())
        
        await asyncio.sleep(5)
        sm.transition(task.id, TaskStatus.PROCESSING)
        await server.notify_clients(task.id, task.to_dict())
        
        await asyncio.sleep(10)
        sm.transition(task.id, TaskStatus.COMPLETED, result_image_url="https://example.com/result.jpg")
        await server.notify_clients(task.id, task.to_dict())
    
    # 启动服务器
    async def main():
        await server.start()
        await simulate_task_progress()
        
        # 保持运行
        await asyncio.sleep(30)
    
    asyncio.run(main())

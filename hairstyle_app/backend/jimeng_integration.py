#!/usr/bin/env python3
"""
即梦 AI API 集成
基于即梦平台完整分析经验
"""
import asyncio
import json
import time
import hashlib
import hmac
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Callable
import aiohttp


class JimengAPI:
    """即梦 AI API 客户端"""
    
    def __init__(self, access_key: str, secret_key: str, region: str = "cn-north-1"):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.host = "visual.volcengineapi.com"
        self.service = "cv"
    
    def _sha256(self, data: str) -> str:
        """计算 SHA256"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def _sign(self, method: str, path: str, query: dict, body: str, timestamp: str) -> str:
        """生成 HMAC-SHA256 签名"""
        date = timestamp[:8]
        
        # 规范查询字符串
        canonical_query = "&".join([f"{k}={v}" for k, v in sorted(query.items())])
        
        # 规范请求头
        body_hash = self._sha256(body)
        canonical_headers = f"host:{self.host}\nx-content-sha256:{body_hash}\nx-date:{timestamp}\n"
        signed_headers = "host;x-content-sha256;x-date"
        
        # 规范请求
        canonical_request = f"{method}\n{path}\n{canonical_query}\n{canonical_headers}\n{signed_headers}\n{body_hash}"
        
        # 签名字符串
        credential_scope = f"{date}/{self.region}/{self.service}/request"
        string_to_sign = f"HMAC-SHA256\n{timestamp}\n{credential_scope}\n{self._sha256(canonical_request)}"
        
        # 计算签名
        k_date = hmac.new(self.secret_key.encode(), date.encode(), hashlib.sha256).digest()
        k_region = hmac.new(k_date, self.region.encode(), hashlib.sha256).digest()
        k_service = hmac.new(k_region, self.service.encode(), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
        
        signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
        return signature
    
    async def submit_task(self, session: aiohttp.ClientSession, 
                         image_url: str, prompt: str,
                         strength: float = 0.75,
                         cfg_scale: float = 9.0,
                         sample_steps: int = 40,
                         negative_prompt: str = None) -> Dict[str, Any]:
        """提交任务"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        
        # Query 参数
        query = {
            "Action": "CVSync2AsyncSubmitTask",
            "Version": "2022-08-31",
        }
        
        # 请求体
        body_dict = {
            "req_key": "seed3l_single_ip",
            "image_urls": [image_url],
            "prompt": prompt,
            "width": 1024,
            "height": 1024,
            "strength": strength,
        }
        
        if negative_prompt:
            body_dict["negative_prompt"] = negative_prompt
        
        body = json.dumps(body_dict, ensure_ascii=False)
        signature = self._sign("POST", "/", query, body, timestamp)
        
        headers = {
            "Content-Type": "application/json",
            "X-Date": timestamp,
            "X-Content-Sha256": self._sha256(body),
            "Authorization": f"HMAC-SHA256 Credential={self.access_key}/{timestamp[:8]}/{self.region}/{self.service}/request, SignedHeaders=host;x-content-sha256;x-date, Signature={signature}"
        }
        
        url = f"https://{self.host}/"
        
        async with session.post(url, params=query, data=body, headers=headers) as response:
            result = await response.json()
            return result
    
    async def query_result(self, session: aiohttp.ClientSession, task_id: str) -> Dict[str, Any]:
        """查询结果"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        
        query = {
            "Action": "CVSync2AsyncGetResult",
            "Version": "2022-08-31",
        }
        
        body = json.dumps({
            "req_key": "seed3l_single_ip",
            "task_id": task_id,
        }, ensure_ascii=False)
        
        signature = self._sign("POST", "/", query, body, timestamp)
        
        headers = {
            "Content-Type": "application/json",
            "X-Date": timestamp,
            "X-Content-Sha256": self._sha256(body),
            "Authorization": f"HMAC-SHA256 Credential={self.access_key}/{timestamp[:8]}/{self.region}/{self.service}/request, SignedHeaders=host;x-content-sha256;x-date, Signature={signature}"
        }
        
        url = f"https://{self.host}/"
        
        async with session.post(url, params=query, data=body, headers=headers) as response:
            result = await response.json()
            return result


class JimengTaskProcessor:
    """即梦任务处理器"""
    
    def __init__(self, api: JimengAPI, task_manager, racing_server):
        self.api = api
        self.task_manager = task_manager
        self.racing_server = racing_server
        self.session = None
    
    async def start(self):
        """启动"""
        self.session = aiohttp.ClientSession()
    
    async def stop(self):
        """停止"""
        if self.session:
            await self.session.close()
    
    async def process_task(self, task):
        """处理任务"""
        from task_manager import TaskStatus
        
        try:
            # 1. 更新状态为排队中
            self.task_manager.update_task_status(
                task.id, TaskStatus.QUEUING,
                queue_idx=0, queue_length=1
            )
            await self.racing_server.notify_clients(task.id, task.to_dict())
            
            # 2. 准备提示词
            prompt = self._build_prompt(task.hairstyle_choice, task.description)
            negative_prompt = self._build_negative_prompt(task.hairstyle_choice)
            
            # 3. 提交到即梦 API
            print(f"[{task.id}] 提交到即梦 API...")
            result = await self.api.submit_task(
                self.session,
                image_url=task.photos[0],  # 使用第一张照片
                prompt=prompt,
                negative_prompt=negative_prompt
            )
            
            if result.get('code') != 10000:
                raise Exception(f"提交失败：{result.get('message')}")
            
            task.jimeng_task_id = result['data']['task_id']
            print(f"[{task.id}] 即梦任务 ID: {task.jimeng_task_id}")
            
            # 4. 更新状态为处理中
            self.task_manager.update_task_status(task.id, TaskStatus.PROCESSING)
            await self.racing_server.notify_clients(task.id, task.to_dict())
            
            # 5. 轮询查询结果
            while True:
                await asyncio.sleep(5)  # 5 秒轮询一次
                
                query_result = await self.api.query_result(self.session, task.jimeng_task_id)
                
                if query_result.get('code') != 10000:
                    raise Exception(f"查询失败：{query_result.get('message')}")
                
                data = query_result.get('data', {})
                status = data.get('status', '')
                
                print(f"[{task.id}] 即梦状态：{status}")
                
                if status == 'done':
                    # 生成完成
                    image_urls = data.get('image_urls', [])
                    if image_urls:
                        self.task_manager.update_task_status(
                            task.id, TaskStatus.COMPLETED,
                            result_image_url=image_urls[0]
                        )
                        await self.racing_server.notify_clients(task.id, task.to_dict())
                        print(f"[{task.id}] 生成完成：{image_urls[0]}")
                        break
                elif status in ['not_found', 'expired', 'failed']:
                    raise Exception(f"任务失败：{status}")
            
        except Exception as e:
            print(f"[{task.id}] 错误：{e}")
            self.task_manager.update_task_status(
                task.id, TaskStatus.FAILED,
                error_message=str(e)
            )
            await self.racing_server.notify_clients(task.id, task.to_dict())
    
    def _build_prompt(self, hairstyle_choice: str, description: str) -> str:
        """构建提示词"""
        base_prompts = {
            '大波浪': '将图片中的长发修改为自然蓬松的大波浪发型',
            '羊毛卷': '将图片中的长发修改为卷度明显的羊毛卷发型',
            '短发': '将图片中的发型修改为清爽利落的短发',
            '长发': '将图片中的发型修改为柔顺的长直发',
        }
        
        base = base_prompts.get(hairstyle_choice, f'将图片中的发型修改为{hairstyle_choice}')
        desc = f'，{description}' if description else ''
        
        return f'{base}{desc}，保持人物面部和服装不变，realistic photo, high quality'
    
    def _build_negative_prompt(self, hairstyle_choice: str) -> str:
        """构建负面提示词"""
        negative_prompts = {
            '大波浪': 'short hair, bob cut, straight hair, 短发，直发',
            '羊毛卷': 'straight hair, long straight, 直发',
            '短发': 'long hair, waist length, 长发',
            '长发': 'short hair, bob cut, 短发',
        }
        
        return negative_prompts.get(hairstyle_choice, '')


# 测试
if __name__ == "__main__":
    from task_manager import TaskManager, TaskStateMachine
    
    async def main():
        # 创建组件
        api = JimengAPI("test_access_key", "test_secret_key")
        tm = TaskManager()
        from websocket_racing import RacingServer
        rs = RacingServer(tm)
        
        processor = JimengTaskProcessor(api, tm, rs)
        await processor.start()
        
        # 创建测试任务
        task = tm.create_task(
            user_id="user_123",
            photos=["https://example.com/photo.jpg"],
            hairstyle_choice="大波浪",
            description="自然蓬松的大波浪发型"
        )
        
        # 处理任务
        await processor.process_task(task)
        
        await processor.stop()
    
    asyncio.run(main())

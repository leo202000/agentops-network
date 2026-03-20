"""
即梦 API 请求队列 - 串行化处理，避免并发超限
"""

import asyncio
import time
from typing import Optional, Dict, Any, List


class JimengRequestQueue:
    """即梦 API 请求队列管理器
    
    特性:
    - 串行化处理（避免并发超限）
    - 可配置延迟
    - 批量处理支持
    """
    
    def __init__(
        self,
        max_concurrent: int = 1,
        delay_between_requests: float = 1.0,
        delay: float = None  # 兼容旧参数
    ):
        # 兼容 delay 参数
        if delay is not None:
            self.delay = delay
        else:
            self.delay = delay_between_requests
        """
        初始化请求队列
        
        Args:
            max_concurrent: 最大并发数（默认 1，串行）
            delay_between_requests: 请求间隔（秒）
        """
        self.max_concurrent = max_concurrent
        self.delay = delay_between_requests
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._request_count = 0
        self._last_request_time = 0
    
    async def submit_task(
        self,
        client,
        image_url: str,
        prompt: str,
        req_key: str = "high_aes_general_v20_L"
    ) -> Dict[str, Any]:
        """
        提交单个任务（带队列控制）
        
        Args:
            client: JimengOfficialClient 实例
            image_url: 图片 URL
            prompt: 提示词
            req_key: 模型标识
        
        Returns:
            提交结果
        """
        async with self._semaphore:
            try:
                # 等待延迟
                if self._last_request_time > 0:
                    elapsed = time.time() - self._last_request_time
                    if elapsed < self.delay:
                        await asyncio.sleep(self.delay - elapsed)
                
                # 提交任务
                print(f"📤 提交任务 #{self._request_count + 1}: {prompt[:30]}...")
                
                result = await client.submit_task(
                    image_url=image_url,
                    prompt=prompt,
                    req_key=req_key
                )
                
                # 更新状态
                self._request_count += 1
                self._last_request_time = time.time()
                
                print(f"✅ 任务 #{self._request_count} 提交成功")
                
                return {
                    "status": "success",
                    "task_id": result.get("task_id"),
                    "request_num": self._request_count,
                    "result": result
                }
            
            except Exception as e:
                print(f"❌ 任务提交失败：{e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "request_num": self._request_count + 1
                }
    
    async def process_batch(
        self,
        client,
        tasks: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        批量处理任务
        
        Args:
            client: JimengOfficialClient 实例
            tasks: 任务列表 [{"image_url": "...", "prompt": "..."}, ...]
        
        Returns:
            结果列表
        """
        print(f"\n🚀 开始批量处理 {len(tasks)} 个任务")
        print(f"⚙️  配置：并发={self.max_concurrent}, 延迟={self.delay}秒\n")
        
        results = []
        
        for i, task in enumerate(tasks, 1):
            print(f"\n[{i}/{len(tasks)}] 处理任务 {i}")
            
            result = await self.submit_task(
                client,
                task.get("image_url"),
                task.get("prompt", "发型设计"),
                task.get("req_key", "high_aes_general_v20_L")
            )
            
            results.append(result)
        
        # 统计结果
        success_count = sum(1 for r in results if r["status"] == "success")
        print(f"\n📊 批量处理完成：{success_count}/{len(tasks)} 成功")
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_requests": self._request_count,
            "max_concurrent": self.max_concurrent,
            "delay_between_requests": self.delay
        }

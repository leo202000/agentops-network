#!/usr/bin/env python3
"""
重试机制工具模块

功能:
- 处理 API 并发限制（50430）
- 指数退避策略
- 最大重试次数控制
- 请求超时处理

使用示例:
    from retry_utils import retry_on_limit
    
    @retry_on_limit(max_retries=3, initial_delay=1)
    def api_call():
        return client.submit_task(...)
"""

import time
import random
from typing import Callable, Any, Optional
from functools import wraps


class APIRetryError(Exception):
    """API 重试异常"""
    pass


def retry_on_limit(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    exponential_base: float = 2.0,
    jitter: bool = True
) -> Callable:
    """
    重试装饰器（处理 API 并发限制）
    
    Args:
        max_retries: 最大重试次数
        initial_delay: 初始延迟（秒）
        max_delay: 最大延迟（秒）
        exponential_base: 指数退避基数
        jitter: 是否添加随机抖动
        
    Returns:
        装饰后的函数
        
    使用示例:
        @retry_on_limit(max_retries=3)
        def submit_task():
            return client.submit_task(...)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # 检查是否成功
                    if isinstance(result, dict):
                        code = result.get('code')
                        
                        # 成功
                        if code == 10000:
                            return result
                        
                        # API 并发限制（50430）
                        elif code == 50430 and attempt < max_retries:
                            delay = calculate_delay(
                                attempt,
                                initial_delay,
                                max_delay,
                                exponential_base,
                                jitter
                            )
                            print(f"⏳ API 并发限制，等待 {delay:.1f} 秒后重试... (尝试 {attempt + 1}/{max_retries})")
                            time.sleep(delay)
                            continue
                        
                        # 其他错误
                        else:
                            return result
                    
                    # 非字典结果，直接返回
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        delay = calculate_delay(
                            attempt,
                            initial_delay,
                            max_delay,
                            exponential_base,
                            jitter
                        )
                        print(f"⏳ 请求失败：{e}，等待 {delay:.1f} 秒后重试... (尝试 {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                    else:
                        raise APIRetryError(f"Max retries exceeded. Last error: {e}")
            
            # 不应该到达这里
            if last_exception:
                raise last_exception
            return None
        
        return wrapper
    return decorator


def calculate_delay(
    attempt: int,
    initial_delay: float,
    max_delay: float,
    exponential_base: float,
    jitter: bool
) -> float:
    """
    计算重试延迟（指数退避 + 随机抖动）
    
    Args:
        attempt: 当前尝试次数（从 0 开始）
        initial_delay: 初始延迟
        max_delay: 最大延迟
        exponential_base: 指数基数
        jitter: 是否添加随机抖动
        
    Returns:
        延迟时间（秒）
    """
    # 指数退避
    delay = initial_delay * (exponential_base ** attempt)
    
    # 限制最大延迟
    delay = min(delay, max_delay)
    
    # 添加随机抖动（避免多个请求同时重试）
    if jitter:
        jitter_value = random.uniform(0, 0.1 * delay)
        delay += jitter_value
    
    return delay


def retry_submit_task(
    client,
    image_url: str,
    prompt: str,
    strength: float = 0.7,
    max_retries: int = 3,
    **kwargs
) -> dict:
    """
    重试提交任务（函数版本）
    
    Args:
        client: JimengClient 实例
        image_url: 图片 URL
        prompt: 提示词
        strength: 重绘强度
        max_retries: 最大重试次数
        **kwargs: 其他参数
        
    Returns:
        提交结果
    """
    last_result = None
    
    for attempt in range(max_retries):
        result = client.submit_task(
            image_url=image_url,
            prompt=prompt,
            strength=strength,
            **kwargs
        )
        
        last_result = result
        
        # 检查是否成功
        if result.get('code') == 10000:
            return result
        
        # 检查是否并发限制
        elif result.get('code') == 50430 and attempt < max_retries - 1:
            delay = calculate_delay(attempt, 1.0, 10.0, 2.0, True)
            print(f"⏳ API 并发限制，等待 {delay:.1f} 秒后重试... (尝试 {attempt + 1}/{max_retries})")
            time.sleep(delay)
            continue
        
        # 其他错误，直接返回
        else:
            return result
    
    return last_result


def retry_query_result(
    client,
    task_id: str,
    target_status: str = 'done',
    max_retries: int = 10,
    interval: float = 10.0,
    timeout: float = 300.0
) -> dict:
    """
    重试查询结果（轮询）
    
    Args:
        client: JimengClient 实例
        task_id: 任务 ID
        target_status: 目标状态（done/failed/error）
        max_retries: 最大重试次数
        interval: 查询间隔（秒）
        timeout: 超时时间（秒）
        
    Returns:
        查询结果
    """
    import time
    
    start_time = time.time()
    
    for i in range(max_retries):
        # 检查是否超时
        if time.time() - start_time > timeout:
            return {
                'code': -1,
                'message': f'Timeout after {timeout}s',
                'data': {'status': 'timeout'}
            }
        
        result = client.query_result(task_id)
        status = result.get('data', {}).get('status', 'unknown')
        
        # 检查是否达到目标状态
        if status == target_status:
            return result
        elif status in ['failed', 'error']:
            return result
        
        # 等待后重试
        if i < max_retries - 1:
            print(f"⏳ 状态：{status}，等待 {interval} 秒... (查询 {i + 1}/{max_retries})")
            time.sleep(interval)
    
    return {
        'code': -1,
        'message': f'Max retries ({max_retries}) exceeded',
        'data': {'status': 'timeout'}
    }


# 测试
if __name__ == "__main__":
    print("重试机制工具模块")
    print("="*50)
    
    # 测试延迟计算
    print("\n延迟计算测试:")
    for i in range(5):
        delay = calculate_delay(i, 1.0, 10.0, 2.0, True)
        print(f"  尝试 {i}: {delay:.2f} 秒")
    
    print("\n✅ 模块加载成功")

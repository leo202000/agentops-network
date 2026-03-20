"""
即梦 API 重试机制 - 自动处理并发超限错误
"""

import asyncio
import time
from functools import wraps
from typing import Dict, Any, Callable


def retry_on_concurrent_limit(
    max_retries: int = 3,
    base_delay: float = 2.0,
    max_delay: float = 30.0
):
    """
    并发超限时自动重试装饰器
    
    特性:
    - 指数退避策略
    - 最大重试次数限制
    - 最大延迟限制
    
    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟（秒）
        max_delay: 最大延迟（秒）
    
    Returns:
        装饰器函数
    """
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Dict[str, Any]:
            last_error = None
            last_result = None
            
            for attempt in range(max_retries + 1):
                try:
                    # 执行函数
                    result = await func(*args, **kwargs)
                    last_result = result
                    
                    # 检查是否是并发超限错误
                    error_msg = str(result.get("error", "")).lower() if isinstance(result, dict) else ""
                    
                    if "concurrent limit" in error_msg or "api concurrent limit" in error_msg:
                        if attempt < max_retries:
                            # 计算延迟时间（指数退避）
                            delay = min(base_delay * (2 ** attempt), max_delay)
                            
                            print(f"⚠️  并发超限，{delay:.1f}秒后重试（第{attempt + 1}/{max_retries}次）")
                            await asyncio.sleep(delay)
                            continue
                        else:
                            print(f"❌ 达到最大重试次数 ({max_retries})")
                            return {
                                "status": "error",
                                "error": "达到最大重试次数，API 并发限制",
                                "original_error": result,
                                "retries": max_retries
                            }
                    
                    # 非并发错误，直接返回
                    return result
                
                except Exception as e:
                    last_error = e
                    error_str = str(e).lower()
                    
                    # 检查是否是并发相关异常
                    is_concurrent_error = (
                        "concurrent limit" in error_str or
                        "api concurrent limit" in error_str or
                        "too many requests" in error_str or
                        "rate limit" in error_str
                    )
                    
                    if is_concurrent_error and attempt < max_retries:
                        # 指数退避
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        print(f"❌ 错误：{e}")
                        print(f"⚠️  {delay:.1f}秒后重试（第{attempt + 1}/{max_retries}次）")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        # 非并发错误或达到最大重试
                        print(f"❌ 错误：{e}")
                        break
            
            # 返回最终结果
            if last_error:
                return {
                    "status": "error",
                    "error": str(last_error),
                    "retries": attempt
                }
            
            return last_result if last_result else {
                "status": "error",
                "error": "未知错误"
            }
        
        return wrapper
    return decorator


class RetryConfig:
    """重试配置类"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 2.0,
        max_delay: float = 30.0,
        retry_on_errors: list = None
    ):
        """
        初始化重试配置
        
        Args:
            max_retries: 最大重试次数
            base_delay: 基础延迟（秒）
            max_delay: 最大延迟（秒）
            retry_on_errors: 需要重试的错误列表
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retry_on_errors = retry_on_errors or [
            "concurrent limit",
            "api concurrent limit",
            "too many requests",
            "rate limit"
        ]
    
    def should_retry(self, error_message: str) -> bool:
        """判断是否应该重试"""
        error_lower = error_message.lower()
        return any(keyword in error_lower for keyword in self.retry_on_errors)
    
    def get_delay(self, attempt: int) -> float:
        """计算延迟时间（指数退避）"""
        return min(self.base_delay * (2 ** attempt), self.max_delay)

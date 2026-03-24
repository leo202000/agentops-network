#!/usr/bin/env python3
"""
错误处理工具模块

功能:
- 统一异常类定义
- 错误代码映射
- 用户友好的错误消息
- 错误日志记录

使用示例:
    from error_handler import handle_error, APIError
    
    try:
        result = client.submit_task(...)
    except APIError as e:
        handle_error(e)
"""

import logging
from enum import Enum
from typing import Optional, Dict, Any


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('error_handler')


class ErrorCode(Enum):
    """错误代码枚举"""
    # 成功
    SUCCESS = 10000
    
    # 客户端错误（4xxxx）
    INVALID_REQUEST = 40000
    INVALID_IMAGE_URL = 40001
    INVALID_STYLE = 40002
    INVALID_PARAMETERS = 40003
    
    # API 错误（5xxxx）
    API_ERROR = 50000
    API_SIGNATURE_ERROR = 50001
    API_RATE_LIMIT = 50002
    API_TIMEOUT = 50003
    API_SERVICE_UNAVAILABLE = 50004
    
    # 存储错误（6xxxx）
    STORAGE_ERROR = 60000
    STORAGE_UPLOAD_FAILED = 60001
    STORAGE_DOWNLOAD_FAILED = 60002
    STORAGE_PERMISSION_DENIED = 60003
    
    # 生成错误（7xxxx）
    GENERATION_ERROR = 70000
    GENERATION_FAILED = 70001
    GENERATION_TIMEOUT = 70002
    GENERATION_QUALITY_LOW = 70003
    
    # 系统错误（8xxxx）
    SYSTEM_ERROR = 80000
    SYSTEM_INTERNAL_ERROR = 80001
    SYSTEM_NETWORK_ERROR = 80002
    SYSTEM_RESOURCE_EXHAUSTED = 80003


class HairstyleError(Exception):
    """发型系统基础异常类"""
    
    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.SYSTEM_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'success': False,
            'error': {
                'code': self.code.value,
                'message': self.message,
                'details': self.details
            }
        }


class APIError(HairstyleError):
    """API 相关异常"""
    pass


class SignatureError(APIError):
    """签名验证失败"""
    pass


class RateLimitError(APIError):
    """API 并发限制"""
    pass


class TimeoutError(HairstyleError):
    """超时异常"""
    pass


class StorageError(HairstyleError):
    """存储相关异常"""
    pass


class GenerationError(HairstyleError):
    """生成相关异常"""
    pass


# 错误代码映射（API 响应代码 -> 内部错误代码）
ERROR_CODE_MAP = {
    10000: ErrorCode.SUCCESS,
    100010: ErrorCode.API_SIGNATURE_ERROR,
    50220: ErrorCode.STORAGE_DOWNLOAD_FAILED,
    50430: ErrorCode.API_RATE_LIMIT,
}

# 错误消息映射
ERROR_MESSAGE_MAP = {
    ErrorCode.SUCCESS: "操作成功",
    ErrorCode.INVALID_REQUEST: "请求参数无效",
    ErrorCode.INVALID_IMAGE_URL: "图片 URL 不可访问",
    ErrorCode.INVALID_STYLE: "不支持的发型风格",
    ErrorCode.INVALID_PARAMETERS: "参数配置错误",
    ErrorCode.API_ERROR: "API 调用失败",
    ErrorCode.API_SIGNATURE_ERROR: "签名验证失败，请检查密钥配置",
    ErrorCode.API_RATE_LIMIT: "API 并发限制，请稍后重试",
    ErrorCode.API_TIMEOUT: "API 请求超时",
    ErrorCode.API_SERVICE_UNAVAILABLE: "API 服务不可用",
    ErrorCode.STORAGE_ERROR: "存储操作失败",
    ErrorCode.STORAGE_UPLOAD_FAILED: "图片上传失败",
    ErrorCode.STORAGE_DOWNLOAD_FAILED: "图片下载失败",
    ErrorCode.STORAGE_PERMISSION_DENIED: "存储权限不足",
    ErrorCode.GENERATION_ERROR: "发型生成失败",
    ErrorCode.GENERATION_FAILED: "生成任务失败",
    ErrorCode.GENERATION_TIMEOUT: "生成任务超时",
    ErrorCode.GENERATION_QUALITY_LOW: "生成质量过低",
    ErrorCode.SYSTEM_ERROR: "系统错误",
    ErrorCode.SYSTEM_INTERNAL_ERROR: "系统内部错误",
    ErrorCode.SYSTEM_NETWORK_ERROR: "网络连接错误",
    ErrorCode.SYSTEM_RESOURCE_EXHAUSTED: "系统资源耗尽",
}


def get_error_message(code: ErrorCode) -> str:
    """获取错误消息"""
    return ERROR_MESSAGE_MAP.get(code, f"未知错误 (code={code.value})")


def map_api_error(api_code: int, api_message: str = "") -> ErrorCode:
    """映射 API 错误代码"""
    return ERROR_CODE_MAP.get(api_code, ErrorCode.API_ERROR)


def handle_api_response(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理 API 响应，转换为统一格式
    
    Args:
        result: API 原始响应
        
    Returns:
        统一格式的结果
    """
    code = result.get('code')
    
    # 成功
    if code == 10000:
        return {
            'success': True,
            'data': result.get('data', {}),
            'request_id': result.get('request_id')
        }
    
    # 错误
    error_code = map_api_error(code, result.get('message', ''))
    error_message = result.get('message', get_error_message(error_code))
    
    # 记录错误日志
    logger.error(f"API 错误：code={code}, message={error_message}, request_id={result.get('request_id')}")
    
    return {
        'success': False,
        'error': {
            'code': error_code.value,
            'message': error_message,
            'api_code': code,
            'request_id': result.get('request_id')
        }
    }


def handle_error(error: Exception, context: str = "") -> Dict[str, Any]:
    """
    处理异常，转换为统一格式
    
    Args:
        error: 异常对象
        context: 错误上下文
        
    Returns:
        统一格式的错误响应
    """
    # 已知的 HairstyleError
    if isinstance(error, HairstyleError):
        logger.error(f"{context}: {error.message} (code={error.code.value})")
        return error.to_dict()
    
    # API 响应错误
    if isinstance(error, dict) and 'code' in error:
        return handle_api_response(error)
    
    # 其他异常
    logger.exception(f"{context}: {str(error)}")
    
    return {
        'success': False,
        'error': {
            'code': ErrorCode.SYSTEM_ERROR.value,
            'message': f"系统错误：{str(error)}",
            'type': type(error).__name__
        }
    }


def validate_image_url(url: str) -> bool:
    """验证图片 URL"""
    if not url:
        return False
    
    # 检查是否是有效的 URL
    if not (url.startswith('http://') or url.startswith('https://')):
        return False
    
    # 检查是否是常见的图片格式
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
    url_lower = url.lower()
    
    if not any(url_lower.endswith(ext) for ext in valid_extensions):
        logger.warning(f"图片 URL 可能无效：{url}")
    
    return True


def validate_style(style: str, available_styles: list) -> bool:
    """验证发型风格"""
    return style in available_styles


def create_error_response(
    code: ErrorCode,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """创建错误响应"""
    return {
        'success': False,
        'error': {
            'code': code.value,
            'message': message or get_error_message(code),
            'details': details or {}
        }
    }


# 测试
if __name__ == "__main__":
    print("错误处理工具模块")
    print("="*50)
    
    # 测试错误代码映射
    print("\n错误代码映射测试:")
    test_codes = [10000, 100010, 50220, 50430, 99999]
    for code in test_codes:
        error_code = map_api_error(code)
        print(f"  {code} -> {error_code.name} ({error_code.value})")
    
    # 测试错误消息
    print("\n错误消息测试:")
    for code in [ErrorCode.SUCCESS, ErrorCode.API_SIGNATURE_ERROR, ErrorCode.API_RATE_LIMIT]:
        print(f"  {code.name}: {get_error_message(code)}")
    
    # 测试 URL 验证
    print("\nURL 验证测试:")
    test_urls = [
        "https://example.com/image.jpg",
        "https://example.com/image.png",
        "https://example.com/image.gif",
        "not_a_url",
        "ftp://example.com/image.jpg"
    ]
    for url in test_urls:
        valid = validate_image_url(url)
        print(f"  {'✅' if valid else '❌'} {url}")
    
    print("\n✅ 模块加载成功")

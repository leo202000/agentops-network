#!/usr/bin/env python3
"""
日志配置优化
减少冗余日志，提高性能
"""
import logging
import sys
from typing import Optional


class CompactFormatter(logging.Formatter):
    """紧凑格式 - 减少日志大小"""
    
    def format(self, record):
        # 简化时间格式
        record.asctime = self.formatTime(record, "%H:%M:%S")
        
        # 简化级别名称
        level_short = {
            'DEBUG': 'D',
            'INFO': 'I',
            'WARNING': 'W',
            'ERROR': 'E',
            'CRITICAL': 'C'
        }.get(record.levelname, record.levelname[:1])
        record.levelshort = level_short
        
        return f"[{record.asctime}] {record.levelshort} {record.message}"


def setup_logger(name: str, level: int = logging.INFO, compact: bool = True) -> logging.Logger:
    """
    设置优化后的日志器
    
    Args:
        name: 日志器名称
        level: 日志级别
        compact: 是否使用紧凑格式
    
    Returns:
        配置好的日志器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 创建处理器
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # 设置格式
    if compact:
        formatter = CompactFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # 避免重复日志
    logger.propagate = False
    
    return logger


class LogSuppressor:
    """日志抑制器 - 减少重复日志"""
    
    def __init__(self, cooldown_seconds: float = 5.0):
        self.cooldown = cooldown_seconds
        self.last_log_time: dict = {}
        self.last_log_message: dict = {}
    
    def should_log(self, key: str, message: str) -> bool:
        """检查是否应该记录日志"""
        now = time.time()
        
        # 检查冷却时间
        if key in self.last_log_time:
            if now - self.last_log_time[key] < self.cooldown:
                # 检查消息是否相同
                if self.last_log_message.get(key) == message:
                    return False  # 相同消息在冷却期内，不记录
        
        # 更新记录
        self.last_log_time[key] = now
        self.last_log_message[key] = message
        return True


# 全局日志抑制器
_log_suppressor = LogSuppressor()


def log_with_suppression(logger: logging.Logger, level: int, key: str, message: str):
    """带抑制的日志记录"""
    if _log_suppressor.should_log(key, message):
        logger.log(level, message)


# 使用示例
if __name__ == "__main__":
    import time
    
    # 创建紧凑日志器
    logger = setup_logger("test", compact=True)
    
    # 测试紧凑格式
    logger.info("系统启动")
    logger.warning("连接超时")
    logger.error("请求失败")
    
    # 测试日志抑制
    for i in range(10):
        log_with_suppression(logger, logging.INFO, "heartbeat", "心跳检查")
        time.sleep(0.5)

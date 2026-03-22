#!/usr/bin/env python3
"""
上下文压缩器
减少消息上下文大小，防止溢出
"""
import json
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CompressedMessage:
    """压缩后的消息"""
    hash: str
    timestamp: float
    summary: str
    full_content: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "h": self.hash[:8],  # 短哈希
            "t": int(self.timestamp),
            "s": self.summary[:100]  # 限制摘要长度
        }


class ContextCompressor:
    """上下文压缩器"""
    
    def __init__(self, max_summary_length: int = 200):
        self.max_summary_length = max_summary_length
        self.compression_stats = {
            "original_size": 0,
            "compressed_size": 0,
            "compression_ratio": 0.0
        }
    
    def compress_message(self, message: Dict[str, Any]) -> CompressedMessage:
        """压缩单条消息"""
        # 生成哈希
        content_str = json.dumps(message, ensure_ascii=False, sort_keys=True)
        msg_hash = hashlib.md5(content_str.encode()).hexdigest()
        
        # 生成摘要
        summary = self._generate_summary(message)
        
        # 获取时间戳
        timestamp = message.get("timestamp", 0)
        
        compressed = CompressedMessage(
            hash=msg_hash,
            timestamp=timestamp,
            summary=summary
        )
        
        # 更新统计
        self.compression_stats["original_size"] += len(content_str)
        compressed_str = json.dumps(compressed.to_dict())
        self.compression_stats["compressed_size"] += len(compressed_str)
        
        return compressed
    
    def _generate_summary(self, message: Dict[str, Any]) -> str:
        """生成消息摘要"""
        parts = []
        
        # 角色
        if "role" in message:
            parts.append(f"[{message['role']}]")
        
        # 内容摘要
        if "content" in message:
            content = message["content"]
            if isinstance(content, str):
                # 限制长度
                if len(content) > self.max_summary_length:
                    content = content[:self.max_summary_length] + "..."
                parts.append(content)
            elif isinstance(content, list):
                # 多模态内容
                parts.append(f"[{len(content)} parts]")
        
        # 工具调用
        if "tool_calls" in message:
            parts.append(f"[tool_calls: {len(message['tool_calls'])}]")
        
        return " ".join(parts)
    
    def compress_context(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """压缩整个上下文"""
        if len(messages) <= 10:
            # 消息少，不压缩
            return messages
        
        compressed = []
        
        # 保留最近 5 条完整消息
        recent_messages = messages[-5:]
        
        # 压缩前面的消息
        old_messages = messages[:-5]
        
        if old_messages:
            # 生成摘要
            summary = self._generate_batch_summary(old_messages)
            compressed.append({
                "role": "system",
                "content": f"[历史消息摘要] {summary}",
                "compressed": True,
                "original_count": len(old_messages)
            })
        
        # 添加最近的消息
        compressed.extend(recent_messages)
        
        return compressed
    
    def _generate_batch_summary(self, messages: List[Dict[str, Any]]) -> str:
        """生成批量摘要"""
        roles = {}
        for msg in messages:
            role = msg.get("role", "unknown")
            roles[role] = roles.get(role, 0) + 1
        
        summary_parts = []
        for role, count in sorted(roles.items()):
            summary_parts.append(f"{role}:{count}")
        
        return f"共 {len(messages)} 条消息 ({', '.join(summary_parts)})"
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """获取压缩统计"""
        if self.compression_stats["original_size"] > 0:
            ratio = (1 - self.compression_stats["compressed_size"] / self.compression_stats["original_size"]) * 100
            self.compression_stats["compression_ratio"] = ratio
        
        return self.compression_stats
    
    def print_stats(self):
        """打印统计"""
        stats = self.get_compression_stats()
        print("\n" + "="*50)
        print("📦 上下文压缩统计")
        print("="*50)
        print(f"原始大小：{stats['original_size']} bytes")
        print(f"压缩后：{stats['compressed_size']} bytes")
        print(f"压缩率：{stats['compression_ratio']:.1f}%")
        print("="*50)


# 智能上下文管理器
class SmartContextManager:
    """智能上下文管理器 - 自动压缩和清理"""
    
    def __init__(self, max_messages: int = 100, compress_threshold: int = 50):
        self.max_messages = max_messages
        self.compress_threshold = compress_threshold
        self.messages: List[Dict[str, Any]] = []
        self.compressor = ContextCompressor()
    
    def add_message(self, message: Dict[str, Any]):
        """添加消息"""
        self.messages.append(message)
        
        # 检查是否需要压缩
        if len(self.messages) > self.compress_threshold:
            self._compress_if_needed()
        
        # 限制最大消息数
        if len(self.messages) > self.max_messages:
            # 保留最近的消息
            self.messages = self.messages[-self.max_messages:]
    
    def _compress_if_needed(self):
        """需要时压缩"""
        # 压缩前半部分消息
        mid = len(self.messages) // 2
        old_messages = self.messages[:mid]
        recent_messages = self.messages[mid:]
        
        # 生成摘要
        summary = self.compressor._generate_batch_summary(old_messages)
        compressed_msg = {
            "role": "system",
            "content": f"[历史消息摘要] {summary}",
            "compressed": True,
            "original_count": len(old_messages)
        }
        
        # 替换
        self.messages = [compressed_msg] + recent_messages
    
    def get_context(self) -> List[Dict[str, Any]]:
        """获取上下文"""
        return self.messages
    
    def clear(self):
        """清空"""
        self.messages = []
    
    @property
    def size(self) -> int:
        """获取大小"""
        return len(self.messages)
    
    def estimate_tokens(self) -> int:
        """估算 token 数（粗略估计）"""
        total_chars = sum(
            len(json.dumps(msg, ensure_ascii=False))
            for msg in self.messages
        )
        # 假设平均 4 个字符 1 个 token
        return total_chars // 4


# 使用示例
if __name__ == "__main__":
    # 创建管理器
    manager = SmartContextManager(max_messages=100, compress_threshold=50)
    
    # 添加消息
    for i in range(60):
        manager.add_message({
            "role": "user" if i % 2 == 0 else "assistant",
            "content": f"这是第 {i+1} 条消息，内容比较长..." * 10,
            "timestamp": 1700000000 + i
        })
    
    # 打印状态
    print(f"消息数：{manager.size}")
    print(f"估算 tokens：{manager.estimate_tokens()}")
    
    # 打印压缩统计
    manager.compressor.print_stats()

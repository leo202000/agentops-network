#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentOps Network - 不可变审计日志系统
用于记录所有关键操作，支持区块链存证
"""

import json
import hashlib
import hmac
from datetime import datetime
from pathlib import Path
import base64


class AuditLogger:
    """不可变审计日志记录器"""
    
    def __init__(self, log_path="audit_logs/audit_log.jsonl", secret_key=None):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化哈希链
        self.previous_hash = self.get_last_hash()
        
        # HMAC 密钥 (用于防篡改)
        if secret_key is None:
            secret_key = self.load_or_generate_secret()
        self.secret_key = secret_key.encode() if isinstance(secret_key, str) else secret_key
        
        # 内存缓冲区
        self.buffer = []
        self.buffer_size = 10  # 缓冲 10 条后写入
    
    def load_or_generate_secret(self):
        """加载或生成 HMAC 密钥"""
        secret_path = self.log_path.parent / ".audit_secret"
        
        if secret_path.exists():
            with open(secret_path, 'r') as f:
                return f.read().strip()
        else:
            # 生成随机密钥
            import secrets
            secret = secrets.token_hex(32)
            with open(secret_path, 'w') as f:
                f.write(secret)
            # 设置权限为 600 (仅所有者可读写)
            secret_path.chmod(0o600)
            return secret
    
    def get_last_hash(self):
        """获取最后一条记录的哈希"""
        if not self.log_path.exists():
            return "genesis"  # 创世哈希
        
        try:
            with open(self.log_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    return last_entry.get('hash', 'genesis')
        except Exception:
            pass
        
        return "genesis"
    
    def create_entry(self, action, details, result="success", metadata=None):
        """创建审计日志条目"""
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        entry = {
            'timestamp': timestamp,
            'action': action,
            'details': details,
            'result': result,
            'previous_hash': self.previous_hash,
            'metadata': metadata or {}
        }
        
        # 计算当前条目的哈希
        entry_hash = self.calculate_hash(entry)
        entry['hash'] = entry_hash
        
        # 计算 HMAC 签名
        entry['signature'] = self.sign_entry(entry)
        
        return entry
    
    def calculate_hash(self, entry):
        """计算条目哈希 (不包含 hash 和 signature 字段)"""
        # 创建不含 hash 和 signature 的副本
        entry_copy = {k: v for k, v in entry.items() if k not in ['hash', 'signature']}
        
        # 序列化并计算哈希
        entry_bytes = json.dumps(entry_copy, sort_keys=True).encode('utf-8')
        return hashlib.sha256(entry_bytes).hexdigest()
    
    def sign_entry(self, entry):
        """使用 HMAC 签名条目"""
        entry_copy = {k: v for k, v in entry.items() if k not in ['signature']}
        entry_bytes = json.dumps(entry_copy, sort_keys=True).encode('utf-8')
        
        signature = hmac.new(
            self.secret_key,
            entry_bytes,
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    def verify_entry(self, entry):
        """验证条目完整性"""
        # 验证哈希
        expected_hash = self.calculate_hash(entry)
        if entry.get('hash') != expected_hash:
            return False, "Hash mismatch"
        
        # 验证 HMAC 签名
        expected_sig = self.sign_entry(entry)
        if not hmac.compare_digest(entry.get('signature', ''), expected_sig):
            return False, "Signature mismatch"
        
        return True, "Valid"
    
    def verify_chain(self):
        """验证整个哈希链的完整性"""
        if not self.log_path.exists():
            return True, "No log file"
        
        previous_hash = "genesis"
        line_num = 0
        
        with open(self.log_path, 'r') as f:
            for line in f:
                line_num += 1
                try:
                    entry = json.loads(line.strip())
                    
                    # 验证 previous_hash
                    if entry.get('previous_hash') != previous_hash:
                        return False, f"Chain broken at line {line_num}"
                    
                    # 验证条目
                    valid, msg = self.verify_entry(entry)
                    if not valid:
                        return False, f"Invalid entry at line {line_num}: {msg}"
                    
                    previous_hash = entry['hash']
                    
                except json.JSONDecodeError:
                    return False, f"Invalid JSON at line {line_num}"
        
        return True, f"Verified {line_num} entries"
    
    def log(self, action, details, result="success", metadata=None, flush=True):
        """记录审计日志"""
        entry = self.create_entry(action, details, result, metadata)
        self.buffer.append(entry)
        self.previous_hash = entry['hash']
        
        # 如果缓冲区满了或强制刷新，写入文件
        if flush or len(self.buffer) >= self.buffer_size:
            self.flush()
        
        return entry
    
    def flush(self):
        """将缓冲区写入文件"""
        if not self.buffer:
            return
        
        with open(self.log_path, 'a') as f:
            for entry in self.buffer:
                f.write(json.dumps(entry) + '\n')
        
        self.buffer = []
    
    def get_entries(self, limit=10, action_filter=None):
        """获取审计日志条目"""
        if not self.log_path.exists():
            return []
        
        entries = []
        with open(self.log_path, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if action_filter is None or entry.get('action') == action_filter:
                        entries.append(entry)
                except json.JSONDecodeError:
                    continue
        
        # 返回最新的 limit 条
        return entries[-limit:] if limit else entries
    
    def get_statistics(self):
        """获取审计统计信息"""
        if not self.log_path.exists():
            return {"total_entries": 0}
        
        stats = {
            "total_entries": 0,
            "actions": {},
            "results": {"success": 0, "failure": 0, "other": 0},
            "first_entry": None,
            "last_entry": None
        }
        
        with open(self.log_path, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    stats["total_entries"] += 1
                    
                    # 统计 action
                    action = entry.get('action', 'unknown')
                    stats["actions"][action] = stats["actions"].get(action, 0) + 1
                    
                    # 统计 result
                    result = entry.get('result', 'other')
                    if result in stats["results"]:
                        stats["results"][result] += 1
                    else:
                        stats["results"]["other"] += 1
                    
                    # 记录时间范围
                    timestamp = entry.get('timestamp')
                    if timestamp:
                        if stats["first_entry"] is None:
                            stats["first_entry"] = timestamp
                        stats["last_entry"] = timestamp
                    
                except json.JSONDecodeError:
                    continue
        
        return stats
    
    def export_for_blockchain(self, batch_size=100):
        """导出用于区块链存证的数据"""
        entries = self.get_entries(limit=batch_size)
        
        if not entries:
            return None
        
        # 计算 Merkle Root (简化版：所有哈希的哈希)
        all_hashes = [entry['hash'] for entry in entries]
        combined = ''.join(all_hashes)
        merkle_root = hashlib.sha256(combined.encode()).hexdigest()
        
        return {
            'entries_count': len(entries),
            'first_timestamp': entries[0]['timestamp'],
            'last_timestamp': entries[-1]['timestamp'],
            'merkle_root': merkle_root,
            'first_hash': entries[0]['hash'],
            'last_hash': entries[-1]['hash'],
            'entries': entries  # 完整条目用于验证
        }
    
    def print_status(self):
        """打印审计日志状态"""
        stats = self.get_statistics()
        valid, msg = self.verify_chain()
        
        print("=" * 70)
        print("📋 审计日志状态")
        print("=" * 70)
        print(f"文件：{self.log_path}")
        print(f"完整性：{'✅ 验证通过' if valid else '❌ 验证失败'} - {msg}")
        print(f"\n统计信息:")
        print(f"  总条目数：{stats['total_entries']}")
        print(f"  时间范围：{stats['first_entry']} ~ {stats['last_entry']}")
        print(f"\n操作分布:")
        for action, count in sorted(stats['actions'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {action}: {count}")
        print(f"\n结果分布:")
        print(f"  成功：{stats['results']['success']}")
        print(f"  失败：{stats['results']['failure']}")
        print(f"  其他：{stats['results']['other']}")
        print("=" * 70)


# 预定义的操作类型
class AuditActions:
    """审计操作类型"""
    MINING_START = "mining.start"
    MINING_COMPLETE = "mining.complete"
    MINING_ERROR = "mining.error"
    
    PAYMENT_INITIATE = "payment.initiate"
    PAYMENT_COMPLETE = "payment.complete"
    PAYMENT_ERROR = "payment.error"
    
    SKILL_EXECUTE = "skill.execute"
    SKILL_ERROR = "skill.error"
    
    CONFIG_CHANGE = "config.change"
    SECURITY_ALERT = "security.alert"
    
    SERVICE_START = "service.start"
    SERVICE_STOP = "service.stop"
    SERVICE_ERROR = "service.error"


def main():
    """主函数 - 演示用法"""
    logger = AuditLogger()
    
    print("🔐 审计日志系统演示\n")
    
    # 记录一些示例日志
    print("📝 记录示例操作...")
    
    logger.log(
        AuditActions.MINING_START,
        "AgentCoin mining started",
        metadata={"agent_id": "34506", "problem_number": 459}
    )
    
    logger.log(
        AuditActions.MINING_COMPLETE,
        "Problem solved successfully",
        metadata={"answer": "238153514", "time_taken": 4.5}
    )
    
    logger.log(
        AuditActions.SERVICE_START,
        "Server monitor service started",
        metadata={"version": "1.0.0"}
    )
    
    logger.log(
        AuditActions.CONFIG_CHANGE,
        "Mining interval updated",
        metadata={"old_value": 300, "new_value": 240}
    )
    
    logger.flush()
    
    # 打印状态
    logger.print_status()
    
    # 验证链条
    print("\n🔗 验证哈希链...")
    valid, msg = logger.verify_chain()
    print(f"结果：{'✅ 通过' if valid else '❌ 失败'} - {msg}")
    
    # 导出区块链存证
    print("\n⛓️  导出区块链存证数据...")
    blockchain_data = logger.export_for_blockchain()
    if blockchain_data:
        print(f"Merkle Root: {blockchain_data['merkle_root'][:16]}...")
        print(f"条目数：{blockchain_data['entries_count']}")
    
    print("\n💡 提示:")
    print(f"  - 日志文件：{logger.log_path}")
    print(f"  - HMAC 密钥：{logger.log_path.parent}/.audit_secret (权限 600)")
    print(f"  - 使用 'logger.log(action, details)' 记录新操作")


if __name__ == "__main__":
    main()

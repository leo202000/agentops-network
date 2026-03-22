#!/usr/bin/env python3
"""
Telegram 消息安全发送工具
解决：message is too long (4096 字符限制)
"""

# Telegram 单条消息最大长度
MAX_LEN = 3500  # 留 596 字符余量

def safe_reply(text):
    """
    将长消息分割成多条短消息
    
    Args:
        text (str): 原始消息文本
        
    Returns:
        list[str]: 分割后的消息列表
    """
    if not text:
        return []
    
    if len(text) <= MAX_LEN:
        return [text]
    
    # 按段落分割，保持可读性
    paragraphs = text.split('\n\n')
    messages = []
    current_msg = ""
    
    for para in paragraphs:
        # 如果单个段落就超长，强制按字符分割
        if len(para) > MAX_LEN:
            # 先发送当前累积的消息
            if current_msg:
                messages.append(current_msg)
                current_msg = ""
            
            # 按 MAX_LEN 分割长段落
            for i in range(0, len(para), MAX_LEN):
                messages.append(para[i:i+MAX_LEN])
        # 如果当前消息 + 新段落不超长，追加
        elif len(current_msg) + len(para) + 2 <= MAX_LEN:
            if current_msg:
                current_msg += '\n\n' + para
            else:
                current_msg = para
        # 否则发送当前消息，开始新消息
        else:
            messages.append(current_msg)
            current_msg = para
    
    # 添加最后一条消息
    if current_msg:
        messages.append(current_msg)
    
    return messages


def test_safe_reply():
    """测试分片功能"""
    # 测试 1: 短消息
    short = "Hello, World!"
    result = safe_reply(short)
    assert len(result) == 1
    assert result[0] == short
    print("✅ 测试 1 通过：短消息")
    
    # 测试 2: 超长消息
    long = "A" * 8000
    result = safe_reply(long)
    assert len(result) == 3  # 8000 / 3500 ≈ 2.28 → 3 条
    assert all(len(msg) <= MAX_LEN for msg in result)
    print("✅ 测试 2 通过：超长消息分割")
    
    # 测试 3: 带段落的长消息
    paragraph = "\n\n".join(["段落" + str(i) * 100 for i in range(50)])
    result = safe_reply(paragraph)
    assert all(len(msg) <= MAX_LEN for msg in result)
    print("✅ 测试 3 通过：段落消息分割")
    
    print("\n🎉 所有测试通过！")


if __name__ == "__main__":
    test_safe_reply()
    
    # 示例用法
    print("\n📝 使用示例:")
    print("""
from utils.safe_reply import safe_reply

# 生成长回复
response = "..."  # AI 生成的长消息

# 分割发送
for msg in safe_reply(response):
    send_message(msg)  # 调用 Telegram API 发送
    """)

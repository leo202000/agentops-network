#!/usr/bin/env python3
"""
即梦 API 配置诊断工具

检查即梦 API 的密钥配置和连接问题
"""

import os
import sys
import base64
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def test_1_env_config():
    """测试 1: 环境变量配置"""
    print_header("测试 1: 环境变量配置")
    
    config = {
        "JIMENG_ACCESS_KEY_ID": os.getenv("JIMENG_ACCESS_KEY_ID", ""),
        "JIMENG_SECRET_ACCESS_KEY": os.getenv("JIMENG_SECRET_ACCESS_KEY", ""),
        "ARK_API_KEY": os.getenv("ARK_API_KEY", ""),
    }
    
    all_ok = True
    for key, value in config.items():
        if value:
            masked = f"{value[:20]}...{value[-10:]}" if len(value) > 30 else value
            print(f"✅ {key}: {masked}")
            
            # 检查是否是 base64 编码
            if '=' in value or value.startswith('AKLT'):
                print(f"   格式：base64 编码 ✅")
            else:
                print(f"   格式：原始值 ⚠️")
        else:
            print(f"❌ {key}: 未配置")
            all_ok = False
    
    return all_ok

def test_2_key_decode():
    """测试 2: 密钥解码测试"""
    print_header("测试 2: 密钥解码测试")
    
    ak = os.getenv("JIMENG_ACCESS_KEY_ID", "")
    sk = os.getenv("JIMENG_SECRET_ACCESS_KEY", "")
    
    try:
        # 尝试解码 Access Key
        if ak:
            ak_decoded = base64.b64decode(ak).decode('utf-8', errors='ignore')
            print(f"Access Key:")
            print(f"   编码：{ak[:40]}...")
            print(f"   解码：{ak_decoded[:40]}...")
            print(f"   长度：{len(ak_decoded)} 字符")
        
        # 尝试解码 Secret Key
        if sk:
            sk_decoded = base64.b64decode(sk).decode('utf-8', errors='ignore')
            print(f"\nSecret Key:")
            print(f"   编码：{sk[:40]}...")
            print(f"   解码：{sk_decoded[:40]}...")
            print(f"   长度：{len(sk_decoded)} 字符")
        
        return True
    except Exception as e:
        print(f"❌ 解码失败：{e}")
        return False

def test_3_client_init():
    """测试 3: 客户端初始化"""
    print_header("测试 3: 客户端初始化")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from hairstyle_generator import JimengClient
        
        ak = os.getenv("JIMENG_ACCESS_KEY_ID")
        sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")
        
        if not ak or not sk:
            print(f"❌ 密钥未配置")
            return False
        
        print(f"   Access Key: {ak[:30]}...")
        print(f"   Secret Key: {sk[:30]}...")
        print(f"   Region: cn-north-1")
        
        client = JimengClient(ak, sk)
        
        print(f"✅ 客户端初始化成功")
        print(f"   Host: {client.host}")
        print(f"   Service: {client.service}")
        print(f"   Region: {client.region}")
        
        return True, client
    except Exception as e:
        print(f"❌ 初始化失败：{e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_4_api_signature():
    """测试 4: API 签名测试"""
    print_header("测试 4: API 签名测试")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from hairstyle_generator import JimengClient
        import json
        
        ak = os.getenv("JIMENG_ACCESS_KEY_ID")
        sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")
        
        client = JimengClient(ak, sk)
        
        # 测试签名生成
        method = "POST"
        path = "/"
        query = {"Action": "SubmitInferenceTask", "Version": "2023-09-01"}
        body = json.dumps({"model_version": "general_v2.1", "prompt": "test"})
        
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        
        signature = client._sign(method, path, query, body, timestamp)
        
        print(f"✅ 签名生成成功")
        print(f"   签名：{signature[:60]}...")
        print(f"   长度：{len(signature)} 字符")
        
        # 检查 Access Key 格式
        auth_header = f"HMAC-SHA256 Credential={client.access_key}/"
        print(f"\n   Authorization 头：{auth_header[:60]}...")
        
        return True
    except Exception as e:
        print(f"❌ 签名失败：{e}")
        import traceback
        traceback.print_exc()
        return False

def test_5_api_call():
    """测试 5: API 调用测试"""
    print_header("测试 5: API 调用测试（简化版）")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from hairstyle_generator import JimengClient
        import requests
        
        ak = os.getenv("JIMENG_ACCESS_KEY_ID")
        sk = os.getenv("JIMENG_SECRET_ACCESS_KEY")
        
        client = JimengClient(ak, sk)
        
        # 测试端点连通性
        url = f"https://{client.host}"
        print(f"   测试端点：{url}")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"   响应状态码：{response.status_code}")
            print(f"   ✅ 端点可访问")
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️ 端点访问受限：{e}")
        
        # 尝试提交一个真实任务
        print(f"\n   尝试提交 API 任务...")
        
        result = client.generate_image(
            prompt="test hairstyle",
            image_url="https://hairfashon.tos-cn-beijing.volces.com/hairstyle/test.jpg"
        )
        
        if result:
            print(f"✅ API 调用成功")
            print(f"   结果：{result}")
            return True
        else:
            print(f"❌ API 调用失败")
            return False
            
    except Exception as e:
        print(f"❌ API 调用失败：{e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print_header("🔍 即梦 API 配置诊断工具")
    print(f"   时间：2026-03-24")
    
    results = []
    
    # 测试 1: 环境变量
    results.append(("环境变量", test_1_env_config()))
    
    # 测试 2: 密钥解码
    results.append(("密钥解码", test_2_key_decode()))
    
    # 测试 3: 客户端初始化
    init_result, client = test_3_client_init()
    results.append(("客户端初始化", init_result))
    
    if init_result:
        # 测试 4: API 签名
        results.append(("API 签名", test_4_api_signature()))
        
        # 测试 5: API 调用
        results.append(("API 调用", test_5_api_call()))
    
    # 总结
    print_header("📊 诊断结果总结")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {name}")
    
    print(f"\n   总计：{passed}/{total} 通过")
    
    if passed == total:
        print(f"\n🎉 即梦 API 配置正常！")
        return 0
    else:
        print(f"\n⚠️  发现问题")
        
        # 给出建议
        print(f"\n💡 建议:")
        print(f"   1. 检查密钥格式（可能需要 base64 编码）")
        print(f"   2. 确认密钥有即梦 API 权限")
        print(f"   3. 检查 API 端点配置")
        print(f"   4. 登录火山引擎控制台验证密钥状态")
        print(f"   5. 对比 private 目录的成功配置")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())

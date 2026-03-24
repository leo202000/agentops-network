#!/usr/bin/env python3
"""
TOS 配置诊断工具

检查火山引擎 TOS 配置和连接问题
"""

import os
import sys
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
        "TOS_BUCKET": os.getenv("TOS_BUCKET", ""),
        "TOS_ACCESS_KEY": os.getenv("TOS_ACCESS_KEY", ""),
        "TOS_SECRET_KEY": os.getenv("TOS_SECRET_KEY", ""),
        "TOS_REGION": os.getenv("TOS_REGION", ""),
    }
    
    all_ok = True
    for key, value in config.items():
        if value:
            if "KEY" in key:
                # 密钥只显示前后缀
                masked = f"{value[:20]}...{value[-10:]}" if len(value) > 30 else value
                print(f"✅ {key}: {masked}")
            else:
                print(f"✅ {key}: {value}")
        else:
            print(f"❌ {key}: 未配置")
            all_ok = False
    
    return all_ok

def test_2_sdk_import():
    """测试 2: SDK 导入"""
    print_header("测试 2: TOS SDK 导入")
    
    try:
        from tos import TosClientV2
        print(f"✅ TOS SDK 导入成功")
        return True
    except ImportError as e:
        print(f"❌ SDK 导入失败：{e}")
        print(f"   请安装：pip install tos")
        return False

def test_3_client_init():
    """测试 3: 客户端初始化"""
    print_header("测试 3: TOS 客户端初始化")
    
    try:
        from tos import TosClientV2
        
        ak = os.getenv("TOS_ACCESS_KEY")
        sk = os.getenv("TOS_SECRET_KEY")
        region = os.getenv("TOS_REGION", "cn-beijing")
        
        if not ak or not sk:
            print(f"❌ 密钥未配置")
            return False
        
        print(f"   Access Key: {ak[:20]}...{ak[-10:]}")
        print(f"   Secret Key: {sk[:20]}...{sk[-10:]}")
        print(f"   Region: {region}")
        
        client = TosClientV2(
            ak=ak,
            sk=sk,
            region=region
        )
        
        print(f"✅ 客户端初始化成功")
        return True, client
        
    except Exception as e:
        print(f"❌ 客户端初始化失败：{e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_4_bucket_exists():
    """测试 4: Bucket 存在性检查"""
    print_header("测试 4: Bucket 存在性检查")
    
    try:
        from tos import TosClientV2
        from tos.exceptions import TosServerError
        
        ak = os.getenv("TOS_ACCESS_KEY")
        sk = os.getenv("TOS_SECRET_KEY")
        region = os.getenv("TOS_REGION", "cn-beijing")
        bucket = os.getenv("TOS_BUCKET")
        
        if not bucket:
            print(f"❌ Bucket 未配置")
            return False
        
        client = TosClientV2(ak=ak, sk=sk, region=region)
        
        print(f"   检查 Bucket: {bucket}")
        print(f"   Region: {region}")
        
        # 尝试列出 bucket 中的对象
        try:
            resp = client.list_objects(bucket=bucket, max_keys=1)
            print(f"✅ Bucket 存在且可访问")
            
            if resp.contents:
                print(f"   对象数量：{len(resp.contents)}+")
                print(f"   示例对象：{resp.contents[0].key}")
            else:
                print(f"   Bucket 为空")
            
            return True
        except TosServerError as e:
            if e.status_code == 403:
                print(f"❌ 访问被拒绝 (403) - 密钥权限不足")
            elif e.status_code == 404:
                print(f"❌ Bucket 不存在 (404)")
            else:
                print(f"❌ 服务器错误 ({e.status_code}): {e}")
            return False
        except Exception as e:
            print(f"❌ 错误：{e}")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False

def test_5_upload_test():
    """测试 5: 上传测试"""
    print_header("测试 5: 上传测试")
    
    try:
        from tos import TosClientV2
        from tos.exceptions import TosServerError
        import io
        
        ak = os.getenv("TOS_ACCESS_KEY")
        sk = os.getenv("TOS_SECRET_KEY")
        region = os.getenv("TOS_REGION", "cn-beijing")
        bucket = os.getenv("TOS_BUCKET")
        
        if not all([ak, sk, bucket]):
            print(f"❌ 配置不完整")
            return False
        
        client = TosClientV2(ak=ak, sk=sk, region=region)
        
        # 测试上传一个小文件
        test_key = "test/tos_connection_test.txt"
        test_content = b"TOS connection test - 2026-03-24"
        
        print(f"   上传测试文件：{test_key}")
        print(f"   Bucket: {bucket}")
        
        try:
            client.put_object(
                bucket=bucket,
                key=test_key,
                content=test_content
            )
            print(f"✅ 上传成功")
            
            # 尝试删除测试文件
            try:
                client.delete_object(bucket=bucket, key=test_key)
                print(f"   已清理测试文件")
            except:
                pass
            
            return True
            
        except TosServerError as e:
            if e.status_code == 403:
                print(f"❌ 签名验证失败 (403)")
                print(f"   错误代码：{e.code}")
                print(f"   错误信息：{e.message}")
                print(f"\n   可能原因:")
                print(f"   1. Secret Key 格式错误（可能是 base64 编码 vs 解码）")
                print(f"   2. 密钥权限不足")
                print(f"   3. 密钥已失效")
            elif e.status_code == 404:
                print(f"❌ Bucket 不存在 (404)")
            else:
                print(f"❌ 服务器错误 ({e.status_code}): {e.message}")
            return False
        except Exception as e:
            print(f"❌ 上传失败：{e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        return False

def main():
    print_header("🔍 TOS 配置诊断工具")
    print(f"   时间：2026-03-24")
    
    results = []
    
    # 测试 1: 环境变量
    results.append(("环境变量", test_1_env_config()))
    
    # 测试 2: SDK 导入
    results.append(("SDK 导入", test_2_sdk_import()))
    
    # 测试 3: 客户端初始化
    init_result, client = test_3_client_init()
    results.append(("客户端初始化", init_result))
    
    if not init_result:
        print("\n⚠️  客户端初始化失败，跳过后续测试")
    else:
        # 测试 4: Bucket 存在性
        results.append(("Bucket 检查", test_4_bucket_exists()))
        
        # 测试 5: 上传测试
        results.append(("上传测试", test_5_upload_test()))
    
    # 总结
    print_header("📊 诊断结果总结")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {name}")
    
    print(f"\n   总计：{passed}/{total} 通过")
    
    if passed == total:
        print(f"\n🎉 TOS 配置正常！")
        return 0
    else:
        print(f"\n⚠️  发现问题，请检查配置")
        
        # 给出建议
        print(f"\n💡 建议:")
        print(f"   1. 登录火山引擎控制台：https://console.volcengine.com/tos")
        print(f"   2. 检查 Bucket '{os.getenv('TOS_BUCKET', 'N/A')}' 是否存在")
        print(f"   3. 检查 IAM 访问密钥是否正确")
        print(f"   4. 确认密钥有 TOS 读写权限")
        print(f"   5. Secret Key 可能需要重新生成")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())

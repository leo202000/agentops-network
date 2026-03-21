#!/usr/bin/env python3
"""
发型变换 v2 快速测试

一键测试改进效果，对比优化前后的差异。

使用方法:
    python quick_test_v2.py
"""
import os
import sys
import json
from pathlib import Path

# 加载 .env 文件
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding='utf-8') as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value

# 导入生成器
sys.path.insert(0, str(Path(__file__).parent / "backend"))
from hairstyle_generator import HairstyleGenerator


def main():
    print("=" * 80)
    print("发型变换 v2 快速测试")
    print("=" * 80)
    
    # 获取 API 密钥
    access_key = os.getenv("JIMENG_ACCESS_KEY_ID", "")
    secret_key = os.getenv("JIMENG_SECRET_ACCESS_KEY", "")
    
    if not access_key or "待填写" in access_key:
        print("\n❌ 错误：请先配置 API 密钥")
        print(f"   编辑：{env_path}")
        print(f"   设置：JIMENG_ACCESS_KEY_ID 和 JIMENG_SECRET_ACCESS_KEY")
        sys.exit(1)
    
    # 查找测试图片
    uploads_dir = Path(__file__).parent / "backend" / "uploads"
    test_images = list(uploads_dir.glob("*.jpg")) + list(uploads_dir.glob("*.png"))
    
    if not test_images:
        print("\n❌ 错误：未找到测试图片")
        print(f"   请将图片放入：{uploads_dir}")
        sys.exit(1)
    
    # 使用第一张图片
    test_image = test_images[0]
    print(f"\n📷 使用测试图片：{test_image.name}")
    
    # 支持的发型
    styles = ["大波浪", "及腰长发", "羊毛卷", "卷发"]
    
    print(f"\n📋 可用发型：{', '.join(styles)}")
    print(f"\n💡 提示：可以使用 --style 指定发型，--mode 指定强度")
    print(f"   例如：python quick_test_v2.py --style 大波浪 --mode 彻底")
    
    # 创建生成器（默认中等强度）
    generator = HairstyleGenerator(access_key, secret_key, transform_mode="中等")
    
    print("\n" + "=" * 80)
    print("开始测试：大波浪 [中等强度]")
    print("=" * 80)
    
    # 测试大波浪
    result = generator.generate(
        image_path=str(test_image),
        style="大波浪",
        wait=True,
        timeout=180
    )
    
    # 输出结果
    print("\n" + "=" * 80)
    print("测试结果：")
    print("=" * 80)
    
    if result["success"]:
        print("\n✅ 生成成功！")
        print(f"   任务 ID: {result.get('task_id', 'N/A')}")
        if result.get("image_urls"):
            print(f"   生成图片：{len(result['image_urls'])} 张")
            for i, url in enumerate(result["image_urls"], 1):
                if url.startswith("http"):
                    print(f"   [{i}] {url}")
                else:
                    print(f"   [{i}] base64 (长度：{len(url)})")
        
        # 保存结果
        output_file = Path(__file__).parent / "test_result.json"
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 结果已保存到：{output_file}")
        
    else:
        print("\n❌ 生成失败")
        print(f"   错误：{result.get('error', 'Unknown')}")
        if result.get("code"):
            print(f"   错误码：{result.get('code')}")
    
    print("\n" + "=" * 80)
    print("下一步建议：")
    print("=" * 80)
    print("""
1. 查看生成效果：
   - 如果效果满意，可以尝试其他发型
   - 如果变化不够，使用 --mode 彻底 再次测试

2. 对比测试不同强度：
   python quick_test_v2.py --style 及腰长发 --mode 轻微
   python quick_test_v2.py --style 及腰长发 --mode 中等
   python quick_test_v2.py --style 及腰长发 --mode 彻底

3. 查看详细文档：
   cat 发型变换优化指南-v2.md

4. 运行完整测试：
   python backend/test_hair_transform_v2.py -i {test_image} -s 大波浪 --compare
    """)


if __name__ == "__main__":
    # 简单参数解析
    style = "大波浪"
    mode = "中等"
    
    if "--style" in sys.argv:
        idx = sys.argv.index("--style")
        if idx + 1 < len(sys.argv):
            style = sys.argv[idx + 1]
    
    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            mode = sys.argv[idx + 1]
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print("使用方法:")
        print("  python quick_test_v2.py [--style 发型] [--mode 强度]")
        print("\n选项:")
        print("  --style 发型名称 (默认：大波浪)")
        print("  --mode 强度：轻微/中等/彻底 (默认：中等)")
        print("  --help 显示帮助")
        sys.exit(0)
    
    main()

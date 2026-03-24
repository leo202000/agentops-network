# 发型生成系统 - 快速参考卡

**版本**: V3.0 | **更新**: 2026-03-24 | **状态**: ✅ 生产就绪

---

## 🔑 核心配置

```bash
# API
ARK_API_KEY=e652320f-7102-49b6-9d4b-354c4002a6cb
model="doubao-seedream-4-5-251128"

# TOS
TOS_BUCKET=hairfashon
TOS_ACCESS_KEY=[REDACTED]
TOS_SECRET_KEY=TmpZNU9XUmxPR1JrWkRVMU5EaGpZemt6TWpFMVl6WTFOMlZqWlRneU1XWQ==
TOS_REGION=cn-beijing

# Telegram
TELEGRAM_BOT_TOKEN=[REDACTED]
TELEGRAM_CHAT_ID=6598565346
```

---

## 🚀 快速使用

```python
from hairstyle_generator_v3 import HairstyleGeneratorV3

generator = HairstyleGeneratorV3()

result = generator.generate(
    image_url="https://example.com/photo.jpg",
    style="齐肩发",
    strength=0.7
)

print(f"✅ {result['image_url']}")
```

---

## 🎨 热门发型 TOP 5

1. **齐肩发** - shoulder length bob, classic
2. **梨花头** - pear blossom hairstyle, korean
3. **丸子头** - high bun hairstyle, elegant
4. **波浪卷** - wavy hairstyle, beach waves
5. **空气刘海** - air bangs hairstyle, youthful

---

## ⚙️ 关键参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| strength | 0.7 | 重绘强度 (0.3-0.9) |
| face_preserve | True | 人脸保护 |
| interval | 2 秒 | 请求间隔 |
| timeout | 120 秒 | 超时时间 |

---

## 📊 性能指标

- **单次生成**: 10-20 秒
- **成功率**: 100%
- **图片大小**: 500-600KB
- **分辨率**: 2K

---

## 📁 重要文件

| 文件 | 说明 |
|------|------|
| `hairstyle_generator_v3.py` | 核心生成器 |
| `test_complete_flow.py` | 完整流程测试 |
| `send_results_to_telegram.py` | Telegram 发送 |
| `PROJECT_COMPLETE_DOCUMENTATION.md` | 完整文档 |

---

## 🔧 常见命令

```bash
# 运行完整测试
python3 test_complete_flow.py

# 发送结果到 Telegram
python3 send_results_to_telegram.py

# 测试热门发型
python3 test_popular_styles.py
```

---

## ⚠️ 注意事项

1. ✅ 请求间隔≥2 秒
2. ✅ 图片 URL 必须公网可访问
3. ✅ strength 推荐 0.7
4. ✅ face_preserve 必须 True
5. ✅ 批量≤10 种发型

---

## 📞 快速排障

| 问题 | 解决 |
|------|------|
| 生成失败 | 检查图片 URL |
| 人脸变形 | strength 降到 0.5 |
| API 限流 | 间隔增加到 3-5 秒 |
| TOS 失败 | 检查密钥配置 |

---

**完整文档**: `PROJECT_COMPLETE_DOCUMENTATION.md`  
**优化指南**: `OPTIMIZATION_GUIDE_V3.md`

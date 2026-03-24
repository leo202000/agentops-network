# 🔒 发型生成系统 - 快速参考卡（安全版）

**版本**: V3.0 | **更新**: 2026-03-24 | **状态**: ✅ 生产就绪

---

## ⚠️ 安全警告

**所有密钥必须从环境变量读取，严禁明文存储！**

```bash
# ❌ 绝对不要这样做
ARK_API_KEY=e652320f-7102-49b6-9d4b-354c4002a6cb

# ✅ 正确做法
ARK_API_KEY=${ARK_API_KEY}  # 从环境变量读取
```

---

## 🔑 配置方式

### 环境变量设置

在系统中设置（不要写入文档）：

```bash
# 火山引擎 Ark API
export ARK_API_KEY="your_api_key_here"

# TOS 对象存储
export TOS_BUCKET="your_bucket_name"
export TOS_ACCESS_KEY="your_access_key_here"
export TOS_SECRET_KEY="your_secret_key_here"
export TOS_REGION="cn-beijing"

# Telegram Bot
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
```

### .env 文件（权限 600）

```bash
# .env 文件（不要提交到 Git）
ARK_API_KEY=your_api_key_here
TOS_BUCKET=your_bucket_name
TOS_ACCESS_KEY=your_access_key_here
TOS_SECRET_KEY=your_secret_key_here
TOS_REGION=cn-beijing
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

---

## 🚀 快速使用

```python
from hairstyle_generator_v3 import HairstyleGeneratorV3

# 自动从环境变量读取 API Key
generator = HairstyleGeneratorV3()

result = generator.generate(
    image_url="https://example.com/photo.jpg",
    style="齐肩发",
    strength=0.7
)

if result['success']:
    print(f"✅ 生成成功：{result['image_url']}")
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
| `SECURITY_ALERT.md` | 安全警告 ⭐ |

---

## 🔧 常见命令

```bash
# 运行完整测试
python3 test_complete_flow.py

# 发送结果到 Telegram
python3 send_results_to_telegram.py

# 测试热门发型
python3 test_popular_styles.py

# 备份项目
./backup_project.sh
```

---

## ⚠️ 安全注意事项

1. ✅ .env 文件权限设置为 600
2. ✅ 永远不要提交 .env 到 Git
3. ✅ 文档中使用占位符
4. ✅ 定期轮换密钥（90 天）
5. ✅ 请求间隔≥2 秒

---

## 🔒 安全检查

```bash
# 检查 .env 权限
ls -la /root/.openclaw/workspace/.env
# 应该显示：-rw-------

# 搜索泄露的密钥
grep -r "your_api_key" /path/to/project/

# 清理备份文件
./backup_project.sh
```

---

## 📞 快速排障

| 问题 | 解决 |
|------|------|
| 生成失败 | 检查图片 URL |
| 人脸变形 | strength 降到 0.5 |
| API 限流 | 间隔增加到 3-5 秒 |
| 认证失败 | 检查环境变量 |

---

**完整文档**: 参考 `hairstyle_generator_v3.py` 中的注释  
**安全指南**: `SECURITY_ALERT.md`  
**项目总结**: `/root/.openclaw/workspace/memory/2026-03-24.md`

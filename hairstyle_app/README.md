# 🎨 AI 发型生成系统

**版本**: v2.2 (公网图片链接修复)  
**状态**: ✅ 已完成，可投入使用  
**最后更新**: 2026-03-20  
**模型**: seed3l_single_ip (图生图 - 角色特征保持)

---

## 🚀 快速开始

### 1️⃣ 准备照片
```bash
cp customer_photo.jpg /root/.openclaw/workspace/hairstyle_app/backend/uploads/
```

### 2️⃣ 生成发型
```bash
cd /root/.openclaw/workspace/hairstyle_app/backend
source venv/bin/activate

# 单个发型
python hairstyle_generator.py -i uploads/photo.jpg -s 短发

# 批量生成（推荐）
python hairstyle_generator.py -i uploads/photo.jpg --styles 短发 卷发 长发
```

### 3️⃣ 查看结果
```
✅ 生成成功！
图片 URL: https://xxx.volces.com/generated.jpg
```

---

## 📋 支持的发型（13 种）

| 类别 | 发型 |
|------|------|
| **基础** | 短发、卷发、长发、直发 |
| **造型** | 马尾、辫子、波浪卷、大波浪 |
| **刘海** | 中分、斜刘海 |
| **染发** | 染发红、染现金、染发棕 |

---

### 📁 重要文件

#### 🌟 核心文件
- [`hairstyle_generator.py`](backend/hairstyle_generator.py) - 主程序（DreamO 3.0）
- [`test_hairstyle_generator.py`](backend/test_hairstyle_generator.py) - 测试脚本

#### 📖 文档
- [`问题修复 - 公网图片链接.md`](问题修复 - 公网图片链接.md) - ⭐ 最新修复
- [`配置说明 - 公网图片存储.md`](配置说明 - 公网图片存储.md) - ⭐ 配置指南
- [`完整使用指南.md`](完整使用指南.md) - 详细使用指南
- [`API 更新说明-DreamO 图生图 3.0.md`](API 更新说明-DreamO 图生图 3.0.md) - API 更新
- [`QUICK_START.md`](QUICK_START.md) - 快速开始

#### ⚙️ 配置
- `/root/.openclaw/workspace/.env` - API 密钥（已配置）

---

## ✅ 测试结果

```
📊 测试套件 - 4/4 通过 (100%)

✅ API 配置检查
✅ 客户端初始化
✅ 生成器初始化
✅ 发型列表
```

---

## 🔧 技术细节

### API 配置
- **端点**: `jimeng-api.volcengineapi.com`
- **服务**: `jimeng`
- **模型**: `seed3l_single_ip` (图生图 - 角色特征保持)
- **类型**: 同步 API（即时返回）

### ⚠️ 重要提示
根据即梦工程师反馈：
- ❌ 本地链接 (localhost) 无法使用
- ✅ 必须使用公网 URL 或 base64
- ✅ 系统会自动处理图片上传

### 特性
- ✅ 角色特征保持
- ✅ 保持脸部完全一致
- ✅ 自动图片上传（TOS/OSS/base64）
- ✅ 公网可访问
- ✅ 自动并发控制

### 使用方式

#### 方式 1: 命令行（推荐）
```bash
python hairstyle_generator.py -i photo.jpg -s 短发
```

#### 方式 2: Python 代码
```python
from hairstyle_generator import HairstyleGenerator
import os

generator = HairstyleGenerator(
    os.getenv("JIMENG_ACCESS_KEY_ID"),
    os.getenv("JIMENG_SECRET_ACCESS_KEY")
)

result = generator.generate("photo.jpg", "短发")
```

#### 方式 3: API 服务
```bash
uvicorn main:app --host 0.0.0.0 --port 8002
```

---

## ⚠️ 注意事项

1. **API 密钥**: 已配置在 `.env` 文件，不要分享
2. **图片存储**: 生产环境使用 OSS/TOS（国内 CDN）
3. **并发控制**: 已自动处理，批量生成时设置 delay=2.0

---

## 🆘 帮助

### 列出发型
```bash
python hairstyle_generator.py --list-styles
```

### 查看帮助
```bash
python hairstyle_generator.py --help
```

### 运行测试
```bash
python test_hairstyle_generator.py
```

---

## 📞 技术支持

- **完整文档**: [`完整使用指南.md`](完整使用指南.md)
- **API 更新**: [`API 更新说明-DreamO 图生图 3.0.md`](API 更新说明-DreamO 图生图 3.0.md) ⭐
- **官方文档**: https://www.volcengine.com/docs/86081/1804562
- **项目总结**: [`项目交付总结.md`](项目交付总结.md)

---

*AI 发型生成系统 v2.2 - 让发型设计更简单*

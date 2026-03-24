# 智颜社 - 隐私保护配置开关

**版本**: 1.0  
**更新日期**: 2026-03-23

---

## 🎛️ 隐私保护模式切换

### 当前模式：基础方案 + 立即删除选项 ✅

**配置位置**: `hairstyle_skill_v2.py`

**参数**: `immediate_delete`

| 值 | 说明 | 适用场景 |
|------|------|---------|
| `True` | 生成完成后立即删除原图 | 正式环境（推荐）⭐ |
| `False` | 24 小时后自动删除 | 调试环境/测试 |

---

## 🔧 切换方法

### 方法 1: 代码中设置（推荐）

**文件**: `hairstyle_skill_v2.py`

**修改位置**: `handle_message()` 函数

```python
# 第 234 行左右
def handle_message(message_text: str, image_path: Optional[str] = None, immediate_delete: bool = True) -> dict:
    """
    处理消息
    
    Args:
        message_text: 用户消息文本
        image_path: 图片路径（如果有）
        immediate_delete: 是否立即删除原图（默认 True，隐私保护）
    """
```

**修改为**：
```python
# 正式环境（立即删除）
immediate_delete: bool = True

# 调试环境（24 小时后删除）
immediate_delete: bool = False
```

---

### 方法 2: 环境变量控制

**文件**: `.env`

**添加配置**：
```bash
# 隐私保护配置
# True: 立即删除原图
# False: 24 小时后自动删除
IMMEDIATE_DELETE_ORIGINAL=True
```

**修改代码**：
```python
# 在 HairstyleSkill.__init__() 中添加
self.immediate_delete = os.getenv('IMMEDIATE_DELETE_ORIGINAL', 'True').lower() == 'true'

# 在 generate() 方法中使用
def generate(self, image_path: str, style: str, immediate_delete: bool = None) -> dict:
    # 如果未指定，使用环境变量配置
    if immediate_delete is None:
        immediate_delete = self.immediate_delete
```

---

### 方法 3: 配置文件控制

**文件**: `privacy_config.json`

**内容**：
```json
{
  "immediate_delete": true,
  "delete_delay_hours": 0,
  "enable_watermark": true,
  "enable_encryption": false
}
```

**说明**：
- `immediate_delete`: 是否立即删除
- `delete_delay_hours`: 延迟删除时间（小时）
- `enable_watermark`: 是否启用数字水印
- `enable_encryption`: 是否启用加密存储

---

## 📊 模式对比

| 特性 | 立即删除模式 | 24 小时删除模式 |
|------|------------|---------------|
| 原图保留时间 | 0 小时 | 24 小时 |
| 隐私保护等级 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 调试便利性 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 客户信任度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 推荐场景 | 正式环境 | 测试环境 |

---

## 🎯 推荐使用策略

### 开发测试阶段

```bash
# .env 配置
IMMEDIATE_DELETE_ORIGINAL=False

# 优点
✅ 可以反复测试原图
✅ 方便调试问题
✅ 保留测试数据
```

### 正式运营阶段

```bash
# .env 配置
IMMEDIATE_DELETE_ORIGINAL=True

# 优点
✅ 最高隐私保护
✅ 符合法规要求
✅ 提升客户信任
```

---

## 📝 切换记录

| 日期 | 模式 | 操作人 | 说明 |
|------|------|--------|------|
| 2026-03-23 | 立即删除 | [姓名] | 正式运营开始 |
| - | - | - | - |

---

## ⚠️ 注意事项

### 立即删除模式

**注意事项**：
- ⚠️ 原图删除后无法恢复
- ⚠️ 测试前请备份重要图片
- ⚠️ 确保生成成功后再删除

**建议**：
- ✅ 先在测试环境验证
- ✅ 保留测试图片用于调试
- ✅ 正式环境使用立即删除

---

### 24 小时删除模式

**注意事项**：
- ⚠️ 原图保留 24 小时
- ⚠️ 需要确保自动删除脚本正常运行
- ⚠️ 定期检查 TOS 存储空间

**建议**：
- ✅ 仅用于测试环境
- ✅ 测试完成后手动清理
- ✅ 不要用于正式客户数据

---

## 🔍 验证方法

### 检查当前模式

```bash
# 查看环境变量
cat /root/.openclaw/workspace/.env | grep IMMEDIATE_DELETE

# 查看代码配置
grep "immediate_delete" /root/.openclaw/workspace/skills/hairstyle-generator/hairstyle_skill_v2.py
```

### 测试删除功能

```bash
# 测试立即删除
cd /root/.openclaw/workspace/skills/hairstyle-generator
source /root/.openclaw/workspace/hairstyle_app/backend/venv/bin/activate
python3 hairstyle_skill_v2.py /path/to/test.jpg 短发 true

# 测试 24 小时删除
python3 hairstyle_skill_v2.py /path/to/test.jpg 短发 false
```

---

## 📞 故障排查

### 问题 1: 原图未删除

**检查步骤**：
1. 检查 `immediate_delete` 参数是否为 `True`
2. 检查文件权限是否允许删除
3. 检查是否有其他进程占用文件

**解决方法**：
```bash
# 手动删除
rm /path/to/original_image.jpg

# 检查权限
ls -la /path/to/original_image.jpg
```

### 问题 2: 删除脚本报错

**检查步骤**：
1. 查看错误日志
2. 检查 TOS 连接是否正常
3. 检查环境变量配置

**解决方法**：
```bash
# 查看日志
tail -f /var/log/hairstyle_cleanup.log

# 测试 TOS 连接
python3 -c "from tos import TosClientV2; print('OK')"
```

---

*最后更新：2026-03-23*

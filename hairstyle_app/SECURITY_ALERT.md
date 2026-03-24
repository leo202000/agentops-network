# 🔒 安全警告 - API 密钥管理

**时间**: 2026-03-24  
**级别**: ⚠️ **重要**

---

## 🚨 安全原则

**永远不要在代码或文档中明文存储密钥！**

```bash
# ❌ 绝对不要这样做
ARK_API_KEY=your_actual_key_here

# ✅ 正确做法
ARK_API_KEY=${ARK_API_KEY}  # 从环境变量读取
```

---

## ⚡ 密钥管理最佳实践

### 1. 使用环境变量

```bash
# 在系统中设置
export ARK_API_KEY="your_key_here"
export TOS_ACCESS_KEY="your_key_here"
export TOS_SECRET_KEY="your_secret_here"
```

### 2. .env 文件（权限 600）

```bash
# .env 文件（不要提交到 Git）
ARK_API_KEY=your_api_key_here
TOS_ACCESS_KEY=your_access_key_here
TOS_SECRET_KEY=your_secret_here
```

### 3. 文档中使用占位符

```markdown
### API 配置

```bash
ARK_API_KEY=your_api_key_here  # 从环境变量读取
model="doubao-seedream-4-5-251128"
```
```

---

## 🔒 安全检查清单

- [ ] ✅ .env 文件权限设置为 600
- [ ] ✅ 使用环境变量读取密钥
- [ ] ✅ 文档中使用占位符
- [ ] ✅ .gitignore 包含 .env
- [ ] ✅ 定期轮换密钥（90 天）

---

## 📞 如怀疑密钥泄露

1. 立即轮换所有密钥
2. 检查访问日志
3. 更新所有使用该密钥的系统

---

**安全级别**: 🔴 重要  
**最后更新**: 2026-03-24

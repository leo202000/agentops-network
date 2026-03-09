# 🔐 安全策略 - 敏感信息处理

**最后更新**: 2026-03-10  
**状态**: ✅ 已实施

---

## 核心原则

**用完即弃，不保存到本地文件**

---

## 🚫 禁止保存的敏感信息

| 类型 | 示例 | 处理方式 |
|------|------|---------|
| API Keys | `sk-xxxx`, `nvapi-xxxx` | 临时提供，用完删除 |
| 私钥 | `0x...` (64 字符) | 永远不要保存 |
| 助记词 | 12/24 单词短语 | 永远不要保存 |
| 密码 | 任何密码 | 使用密码管理器 |
| 访问令牌 | JWT, Bearer Token | 会话结束后清除 |

---

## ✅ 可以保存的信息

| 类型 | 示例 | 说明 |
|------|------|------|
| 公钥 | `/mWVX...` | 公开信息 |
| 钱包地址 | `0x694a...0e1a` | 公开链上地址 |
| 交易哈希 | `0xc68e...f479` | 公开链上数据 |
| API 端点 | `https://api.example.com` | 公开配置 |

---

## 📁 文件权限规范

```bash
# .env 文件 - 仅所有者可读写
chmod 600 .env

# 敏感脚本 - 仅所有者可执行
chmod 700 script.py

# 普通文档 - 正常权限
chmod 644 README.md
```

---

## 🔧 正确使用方法

### 临时使用 API Keys

```bash
# ❌ 错误：写入 .env 文件长期保存
echo "API_KEY=sk-xxxx" >> .env

# ✅ 正确：临时环境变量
export API_KEY="sk-xxxx"
python script.py
unset API_KEY

# ✅ 正确：使用时创建，用完删除
cp .env.example .env.local
# 编辑 .env.local 填入真实密钥
python script.py
rm .env.local  # 用完立即删除
```

### 使用系统密钥管理

```bash
# macOS Keychain
security add-generic-password -s "myapp" -a "api_key" -w "sk-xxxx"
security find-generic-password -s "myapp" -a "api_key" -w

# Linux (pass)
pass insert myapp/api_key
pass myapp/api_key
```

---

## 📋 检查清单

### 每次会话结束前

- [ ] 删除临时 .env.local 文件
- [ ] 清除 shell 历史中的敏感命令
- [ ] 确认没有新创建的敏感文件
- [ ] 检查 git status 确保无敏感文件暂存

### 定期检查

- [ ] 审查 memory/ 目录中的敏感信息
- [ ] 轮换已使用的 API Keys
- [ ] 更新 .env.example 模板
- [ ] 检查 .gitignore 是否完整

---

## 🗂️ 相关文件

| 文件 | 用途 | 权限 |
|------|------|------|
| `.env` | 临时敏感信息 | 600 |
| `.env.example` | 模板（无真实值） | 644 |
| `SECURITY.md` | 本文件 - 安全策略 | 644 |
| `.gitignore` | Git 忽略规则 | 644 |

---

## ⚠️ 历史脱敏记录

**2026-03-10**: Memory 目录脱敏完成
- 11 个文件，18 处敏感信息
- 备份位置：`memory/backup/`
- 详见：`memory/DESANITIZATION_REPORT.md`

---

## 🆘 应急处理

### 如果意外保存了敏感信息

1. **立即删除**敏感文件
2. **轮换**已泄露的密钥
3. **检查 git 历史**是否已提交
4. **更新** `.gitignore` 防止再次发生
5. **记录**教训到 `memory/YYYY-MM-DD.md`

```bash
# 从 git 历史中彻底删除敏感文件
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/sensitive/file' \
  --prune-empty --tag-name-filter cat -- --all
```

---

*安全是持续的过程，不是一次性的任务。*

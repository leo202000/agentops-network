# 🚀 Skill Vetting - 快速参考卡片

**打印此卡片，审查技能时快速查阅**

---

## ⚡ 5 分钟快速审查

```bash
# 1. 下载技能
git clone <skill-repo> ./review
cd ./review

# 2. 运行自动检查
./scripts/skill-security-check.sh

# 3. 手动检查关键点
grep -r "eval\|exec\|spawn" --include="*.js" .
grep -r "api_key\|secret\|password" --include="*.js" .
grep -r "fetch\|axios" --include="*.js" .

# 4. 检查依赖
cat package.json | grep -A 20 '"dependencies"'
npm audit

# 5. 查看文档
cat SKILL.md
```

---

## 🚩 危险信号（发现即拒绝）

| 信号 | 命令检查 | 风险 |
|------|---------|------|
| 硬编码密钥 | `grep -r "sk-[a-zA-Z0-9]" .` | 🔴 高 |
| 动态代码执行 | `grep -r "eval(" .` | 🔴 高 |
| 无限制 exec | `grep -r "exec(" .` | 🔴 高 |
| 隐藏网络请求 | `grep -r "fetch.*http" .` | 🔴 高 |
| 路径遍历 | `grep -r "fs.*userInput" .` | 🔴 高 |

---

## ✅ 安全信号（越多越好）

| 信号 | 检查方式 |
|------|---------|
| 使用环境变量 | `grep "process.env" .` |
| 输入验证 | 代码中有 validation 函数 |
| 错误处理 | try/catch 块完整 |
| 权限声明 | SKILL.md 清晰列出 |
| 测试用例 | tests/ 目录存在 |
| 类型定义 | .d.ts 或 TypeScript |

---

## 📊 决策树

```
技能来源可信？
├─ 否 → ❌ 拒绝
└─ 是 ↓
代码无危险信号？
├─ 否 → ❌ 拒绝（或修复后重新审查）
└─ 是 ↓
权限合理？
├─ 否 → ⚠️ 限制权限后批准
└─ 是 ↓
沙箱测试通过？
├─ 否 → ❌ 拒绝
└─ 是 → ✅ 批准安装
```

---

## 🎯 权限风险速查

| 权限 | 风险 | 建议 |
|------|------|------|
| exec | 🔴 | 默认禁用，除非必要 |
| writeFile | 🟡 | 限制到 ./workspace/* |
| readFile | 🟡 | 限制到 ./workspace/* |
| fetch | 🟡 | 白名单域名 |
| browser | 🟡 | 限制 URL |
| message | 🟢 | 需用户授权 |
| web_search | 🟢 | 安全 |
| tts | 🟢 | 安全 |

---

## 📝 审查记录模板

```
技能：___________ 日期：___________
作者：___________ 来源：___________

快速检查:
[ ] 无 eval/exec
[ ] 无硬编码密钥
[ ] 网络请求可信
[ ] 文件访问安全

决策：[ ] ✅ 批准  [ ] ⚠️ 限制  [ ] ❌ 拒绝

备注：_______________________
```

---

## 🆘 应急命令

```bash
# 禁用技能
openclaw skills disable <skill-name>

# 删除技能
openclaw skills remove <skill-name>

# 查看审计日志
openclaw audit log --since "1h"

# 检查技能状态
openclaw skills info <skill-name>
```

---

**完整指南**: `SKILL_VETTING_GUIDE.md`  
**检查脚本**: `scripts/skill-security-check.sh`

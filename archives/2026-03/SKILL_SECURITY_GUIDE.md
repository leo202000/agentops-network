# 🔐 技能安全学习与安装指南

**版本**: 1.0  
**最后更新**: 2026-03-10  
**适用**: OpenClaw 技能学习/安装前安全检查

---

## ⚠️ 核心原则

**先安全升级，再学习安装**

1. 永远不要直接安装未经验证的技能
2. 始终在隔离环境中测试新技能
3. 审查代码后再授予权限
4. 使用最小权限原则

---

## 📋 安装前检查清单

### 阶段 1: 环境准备

```bash
# 1. 检查 OpenClaw 版本
openclaw --version

# 2. 更新到最新版本
npm update -g openclaw

# 3. 检查安全配置
openclaw config list
```

### 阶段 2: 技能来源验证

| 检查项 | 方法 | 标准 |
|--------|------|------|
| 来源可信度 | ClawHub 官方/社区推荐 | ✅ 优先 |
| 作者信誉 | 查看作者历史技能 | ⭐ 3+ 好评 |
| 下载量 | `clawhub skills show <skill>` | 📊 100+ |
| 更新时间 | 最近 6 个月内 | 📅 活跃维护 |
| 安全审计 | ClawGuard 扫描报告 | ✅ 通过 |

### 阶段 3: 代码审查

```bash
# 1. 获取技能源码（不安装）
git clone https://github.com/author/skill-name.git
cd skill-name

# 2. 检查关键文件
ls -la
cat SKILL.md          # 技能描述
cat package.json      # 依赖检查
cat index.js          # 主逻辑

# 3. 扫描敏感操作
grep -r "exec\|spawn\|writeFile\|readFile\|fetch" .
grep -r "private_key\|api_key\|secret\|password" .

# 4. 检查网络请求
grep -r "http://\|https://" .

# 5. 检查文件系统访问
grep -r "fs\." .
```

### 阶段 4: 权限审查

**危险权限**（需要特别谨慎）：

| 权限 | 风险 | 建议 |
|------|------|------|
| `exec` | 执行系统命令 | ❌ 拒绝，除非必要 |
| `writeFile` | 写入文件 | ⚠️ 限制路径 |
| `readFile` | 读取文件 | ⚠️ 限制路径 |
| `fetch` | 网络请求 | ⚠️ 检查域名 |
| `browser` | 浏览器控制 | ⚠️ 明确用途 |

**安全权限**（相对安全）：

- `web_search` - 搜索 API
- `tts` - 语音合成
- `message` - 消息发送（需授权）

---

## 🔍 ClawGuard 安全检查

### 什么是 ClawGuard？

ClawGuard 是 OpenClaw 的供应链攻击防护系统：

- ✅ 技能签名验证
- ✅ 权限清单审查
- ✅ 模式检查（pattern checks）
- ✅ Docker 沙箱隔离

### 使用 ClawGuard 扫描

```bash
# 扫描技能目录
openclaw security scan ./skill-name

# 验证技能签名
openclaw security verify <skill-name>

# 检查权限清单
openclaw security audit <skill-name>
```

---

## 🧪 沙箱测试

### 创建测试环境

```bash
# 1. 创建隔离会话
openclaw sessions spawn --runtime=subagent --mode=run \
  --task "test skill: <skill-name>" \
  --label "skill-test"

# 2. 在沙箱中运行技能
# 观察行为，检查是否有异常操作

# 3. 检查日志
openclaw sessions history --session "skill-test"
```

### 测试检查点

- [ ] 技能是否按描述工作？
- [ ] 是否有未声明的网络请求？
- [ ] 是否尝试访问未授权的文件？
- [ ] 是否有异常的系统调用？
- [ ] 资源使用是否合理（CPU/内存）？

---

## 📁 技能目录结构审查

### 标准结构

```
skill-name/
├── SKILL.md              # 技能描述（必需）
├── package.json          # 依赖声明（必需）
├── index.js             # 主入口（必需）
├── README.md            # 使用说明
├── tests/               # 测试用例（推荐）
└── assets/              # 资源文件（可选）
```

### 危险信号 🚩

- ❌ 缺少 `SKILL.md`
- ❌ `package.json` 包含不明依赖
- ❌ 代码混淆/压缩
- ❌ 硬编码的 API Keys
- ❌ 动态代码执行（`eval()`）
- ❌ 隐藏的网络请求

---

## 🔐 安装后的安全措施

### 1. 权限限制

```json
// openclaw.json
{
  "skills": {
    "skill-name": {
      "enabled": true,
      "permissions": {
        "exec": false,
        "writeFile": ["./workspace/*"],
        "readFile": ["./workspace/*"],
        "fetch": ["api.trusted-domain.com"]
      }
    }
  }
}
```

### 2. 监控行为

```bash
# 启用审计日志
openclaw audit enable

# 查看技能活动
openclaw audit log --skill "skill-name"
```

### 3. 定期审查

```bash
# 每周检查已安装技能
openclaw skills list --verbose

# 更新技能
openclaw skills update <skill-name>

# 移除不用的技能
openclaw skills remove <skill-name>
```

---

## 📚 推荐的安全技能学习路径

### 初级（安全基础）

1. **weather** - 天气查询（只读 API）
2. **tts** - 语音合成（无敏感权限）
3. **web_search** - 网络搜索（只读）

### 中级（有限权限）

1. **message** - 消息发送（需授权）
2. **browser** - 浏览器控制（沙箱）
3. **memory** - 记忆管理（本地文件）

### 高级（需要审查）

1. **exec** - 系统命令执行
2. **nodes** - 设备控制
3. **canvas** - UI 自动化

---

## 🆘 应急处理

### 发现恶意技能

```bash
# 1. 立即禁用
openclaw skills disable <skill-name>

# 2. 删除技能
openclaw skills remove <skill-name>

# 3. 检查影响
openclaw audit log --since "1h"

# 4. 报告问题
# 在 ClawHub 或 GitHub 上报
```

### 恢复步骤

1. 停止所有会话
2. 删除可疑技能
3. 审查审计日志
4. 更改可能泄露的密钥
5. 恢复备份（如有必要）

---

## 📋 快速检查清单

安装技能前快速确认：

- [ ] OpenClaw 已更新到最新版本
- [ ] 技能来源可信（ClawHub 官方/社区推荐）
- [ ] 代码已审查（无危险操作）
- [ ] 权限已限制（最小权限原则）
- [ ] 沙箱测试通过
- [ ] 审计日志已启用

---

## 🔗 相关资源

- [OpenClaw 安全文档](https://docs.openclaw.ai/security)
- [ClawHub 技能市场](https://clawhub.ai)
- [ClawGuard 安全工具](https://docs.openclaw.ai/tools/clawguard)
- [技能开发指南](https://docs.openclaw.ai/skills)

---

**安全提示**: 如有疑问，先询问或在小环境中测试！

*最后审查：2026-03-10*

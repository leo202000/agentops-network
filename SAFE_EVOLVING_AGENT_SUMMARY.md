# 🌱 Safe Evolving Agent - 安全进化代理系统

**发布日期**: 2026-03-10  
**版本**: 1.0.0  
**状态**: ✅ 已安装并可用

---

## 🎯 设计理念

传统的"自进化"技能存在安全隐患：
- ❌ 自动修改核心配置文件（AGENTS.md 等）
- ❌ 行为可能随时间漂移
- ❌ 用户不知道发生了什么变化
- ❌ 难以回滚

我们的**安全进化**方案：
- ✅ **只读模式** - 不修改任何现有文件
- ✅ **独立存储** - 所有经验存 `.evolution/` 目录
- ✅ **显式审批** - 所有晋升需要用户确认
- ✅ **完全透明** - 所有变更可追溯、可回滚

---

## 📊 对比分析

| 特性 | 传统自进化 | Safe Evolving Agent |
|------|-----------|---------------------|
| 修改核心文件 | ✅ 自动 | ❌ 需审批 |
| 经验存储 | 直接写入 | 独立目录 |
| 透明度 | 低 | 高（完整日志） |
| 回滚能力 | 困难 | 简单（备份） |
| 用户控制 | 弱 | 强（显式审批） |
| 行为漂移风险 | 高 | 低（只追加） |
| 安全性 | 🟡 中 | 🟢 高 |

---

## 🚀 快速使用

### 1. 记录观察

```bash
cd /root/.openclaw/workspace/skills/safe-evolving-agent

# 记录错误
./scripts/record-observation.sh error platform "MBC20 响应超时 (>5s)"

# 记录用户纠正
./scripts/record-observation.sh correction workflow "用户纠正：git push 前应该先 pull"

# 记录改进建议
./scripts/record-observation.sh improvement tools "并行检查平台可提速 3 倍"
```

### 2. 生成提案

当同一模式出现≥3 次：

```bash
./scripts/generate-proposal.sh "MBC20" 3
```

### 3. 审批提案

```bash
# 查看待审批
ls .evolution/proposals/pending/

# 批准
./scripts/approve-proposal.sh PROP-20260310-*

# 拒绝
./scripts/reject-proposal.sh PROP-20260310-* "需要更多测试"
```

### 4. 查看统计

```bash
./scripts/evolution-stats.sh weekly
```

---

## 📁 目录结构

```
skills/safe-evolving-agent/
├── SKILL.md                 # 完整技能文档 (11KB)
├── README.md                # 快速开始指南 (4KB)
├── templates/
│   ├── observation.md       # 观察记录模板
│   └── proposal.md          # 提案模板
├── scripts/
│   ├── record-observation.sh    # 记录观察
│   ├── generate-proposal.sh     # 生成提案
│   ├── approve-proposal.sh      # 批准提案
│   ├── reject-proposal.sh       # 拒绝提案
│   └── evolution-stats.sh       # 查看统计
└── .evolution/
    ├── observations/        # 观察记录
    │   ├── errors/
    │   ├── corrections/
    │   ├── improvements/
    │   └── review/
    ├── proposals/
    │   ├── pending/
    │   ├── approved/
    │   └── rejected/
    ├── changelog.jsonl      # 操作日志
    └── stats.json           # 统计数据
```

---

## 🔄 工作流程

```
观察 → 记录 → 聚合 → 提案 → 审批 → 应用
  ↓                              ↓
存储到.evolution/            仅批准后
                              ↓
                         备份 + 追加 + 日志
```

### 阶段说明

1. **观察** (自动)
   - 检测错误、纠正、改进
   - 不执行任何修改

2. **记录** (自动)
   - 写入 `.evolution/observations/`
   - 记录到 changelog.jsonl

3. **聚合** (定期)
   - 检查重复模式
   - ≥3 次 → 生成提案

4. **提案** (自动)
   - 生成 `.evolution/proposals/pending/`
   - 等待用户审批

5. **审批** (用户)
   - 批准 → 应用变更
   - 拒绝 → 记录原因

6. **应用** (仅批准后)
   - 创建备份
   - 追加到目标文件
   - Git 提交
   - 记录日志

---

## 🛡️ 安全护栏

### 1. 只读原则

**永不修改**:
- ❌ SOUL.md（核心人格）
- ❌ 其他技能的 SKILL.md
- ❌ 系统配置文件

**可以建议**:
- ✅ AGENTS.md（工作流）
- ✅ TOOLS.md（工具使用）
- ✅ 用户明确授权的文件

### 2. 追加原则

- ✅ **追加** - 在文件末尾添加
- ❌ **不修改** - 不删除现有内容
- ❌ **不覆盖** - 不替换已有规则

### 3. 透明原则

所有操作记录到：
```jsonl
.evolution/changelog.jsonl
{"ts":"2026-03-10T14:30:00+08:00","action":"observe","type":"error","id":"OBS-001"}
{"ts":"2026-03-10T15:00:00+08:00","action":"propose","id":"PROP-001"}
{"ts":"2026-03-11T09:00:00+08:00","action":"approve","id":"PROP-001"}
{"ts":"2026-03-11T09:01:00+08:00","action":"apply","id":"PROP-001","file":"AGENTS.md"}
```

### 4. 回滚原则

随时回滚：
```bash
# 查看备份
ls -la AGENTS.md.backup.*

# 回滚
cp AGENTS.md.backup.20260310141500 AGENTS.md
```

---

## 📋 触发条件

### 类型 1: 错误观察

**触发**: 命令/操作失败

**示例**:
```bash
./scripts/record-observation.sh error platform "MBC20 响应超时"
```

### 类型 2: 用户纠正

**触发**: 用户说"不对"、"错了"、"应该是"

**示例**:
```bash
./scripts/record-observation.sh correction workflow "用户纠正：先 pull 再 push"
```

### 类型 3: 改进建议

**触发**: 发现更好的做法

**示例**:
```bash
./scripts/record-observation.sh improvement tools "并行检查可提速"
```

### 类型 4: 任务回顾

**触发**: 任务完成后

**示例**:
```bash
./scripts/record-observation.sh review project "Skill Vetting 耗时 45 分钟，踩坑 3 个"
```

---

## 📊 监控指标

### 每日检查

```bash
# 新增观察
find .evolution/observations/ -mtime -1 | wc -l

# 待审批提案
ls .evolution/proposals/pending/ | wc -l
```

### 每周检查

```bash
./scripts/evolution-stats.sh weekly
```

**输出示例**:
```
📊 安全进化统计
================
周期：weekly

📝 观察记录:
------------
总数：15

按类型分布:
  7 error
  5 correction
  2 improvement
  1 review

📋 提案状态:
------------
待审批：2
已批准：3
已拒绝：1
总计：6
批准率：50%

📈 最近变更:
------------
{"action":"approve","id":"PROP-003","ts":"2026-03-10T14:30:00"}
{"action":"propose","id":"PROP-003","ts":"2026-03-10T12:00:00"}

💡 洞察:
------
最常见的观察类型：error
⚠️  有待审批提案：2 个
存储空间：1.2MB
```

---

## 🆘 应急处理

### 发现问题提案

```bash
# 1. 查看提案
cat .evolution/proposals/approved/PROP-*.md

# 2. 找到备份
ls -la AGENTS.md.backup.*

# 3. 回滚
cp AGENTS.md.backup.20260310141500 AGENTS.md

# 4. 标记重新审查
mv .evolution/proposals/approved/PROP-*.md .evolution/proposals/rejected/
echo "原因：需要重新审查" >> .evolution/proposals/rejected/PROP-*.md
```

---

## 🎯 使用场景

### 场景 1: 平台监控优化

**Day 1-3**: 观察 MBC20 超时
```bash
./scripts/record-observation.sh error platform "MBC20 超时 5.2s"
./scripts/record-observation.sh error platform "MBC20 超时 6.1s"
./scripts/record-observation.sh error platform "MBC20 超时 5.8s"
```

**Day 4**: 生成提案
```bash
./scripts/generate-proposal.sh "MBC20" 3
```

**Day 5**: 审批并应用
```bash
./scripts/approve-proposal.sh PROP-20260310-*
```

**结果**: 增加超时重试机制

---

### 场景 2: Git 工作流改进

**观察**:
```bash
./scripts/record-observation.sh error workflow "git push 失败，未先 pull"
./scripts/record-observation.sh error workflow "git push 冲突"
./scripts/record-observation.sh error workflow "git push 失败"
```

**提案**: 自动 pre-push 检查

**审批**: ❌ 拒绝（风险高）

**结果**: 提案移动到 rejected/，记录原因

---

## 🔗 相关资源

- [完整文档](./SKILL.md)
- [快速开始](./README.md)
- [观察模板](./templates/observation.md)
- [提案模板](./templates/proposal.md)
- [GitHub 提交](https://github.com/leo202000/agentops-network/commit/51d4337)

---

## 📈 项目状态

- ✅ 技能文档完成
- ✅ 脚本开发完成
- ✅ 目录结构创建
- ✅ 已提交到 GitHub
- ✅ 可立即使用

---

**创建者**: AgentOps Network  
**创建日期**: 2026-03-10  
**License**: MIT

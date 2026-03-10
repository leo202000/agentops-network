# Safe Evolving Agent - 安全进化代理

**版本**: 1.0.0  
**作者**: AgentOps Network  
**创建日期**: 2026-03-10  
**安全等级**: 🟢 高（只读模式 + 显式审批）

---

## 🎯 核心理念

**"进化，但不失控"**

传统自进化技能的问题：
- ❌ 自动修改核心配置文件（AGENTS.md 等）
- ❌ 行为可能随时间漂移
- ❌ 用户不知道发生了什么变化

我们的解决方案：
- ✅ **只读模式** - 不修改任何现有文件
- ✅ **独立存储** - 所有经验存 `.evolution/` 目录
- ✅ **显式审批** - 晋升需要用户确认
- ✅ **完全透明** - 所有变更可追溯、可回滚

---

## 📊 系统架构

```
.evolution/
├── observations/       # 原始观察记录
│   ├── errors/        # 错误观察
│   ├── corrections/   # 用户纠正
│   └── improvements/  # 改进建议
├── proposals/         # 晋升提案（待审批）
│   ├── pending/       # 等待审批
│   ├── approved/      # 已批准
│   └── rejected/      # 已拒绝
├── changelog.jsonl    # 操作日志
└── stats.json         # 统计数据
```

---

## 🔄 工作流程

### 阶段 1: 观察（自动）

**触发条件**:
1. 操作失败/报错
2. 用户纠正（"不对"、"应该是"）
3. 发现更好的做法
4. 任务完成回顾

**行动**:
```markdown
# 写入 .evolution/observations/<category>/<timestamp>.md

## 观察记录

**类型**: error | correction | improvement | review  
**时间**: 2026-03-10 14:30  
**上下文**: 执行了什么操作  
**问题**: 发生了什么错误/纠正  
**建议**: 可能的改进方案  
**信心**: low | medium | high  
```

**关键**: 只记录，不执行任何修改！

---

### 阶段 2: 聚合（定期）

**每周执行**:
```bash
# 检查重复模式
grep -r "关键词" .evolution/observations/

# 统计频率
# 同一问题出现 ≥3 次 → 生成提案
```

**生成提案**:
```markdown
# .evolution/proposals/pending/PROP-20260310-001.md

## 晋升提案

**提案 ID**: PROP-20260310-001  
**类型**: workflow | tool | behavior  
**来源观察**: 
- OBS-20260308-001
- OBS-20260309-003
- OBS-20260310-001

## 建议变更

**目标文件**: AGENTS.md  
**目标章节**: ## 工作流  
**建议内容**: 
```markdown
### 批量处理任务
- 每个任务独立 spawn 子会话
- 任务间不共享状态
- 失败任务自动重试 3 次
```

## 理由

重复出现 3 次，证明此模式有效。

## 审批

- [ ] 待审批
- [ ] 已批准（日期：___）
- [ ] 已拒绝（原因：___）
```

---

### 阶段 3: 审批（用户决定）

**用户收到通知**:
```
📋 新的进化提案待审批

提案 ID: PROP-20260310-001
类型：工作流改进
来源：3 次观察
建议：批量处理任务时每任务独立 spawn

查看：.evolution/proposals/pending/PROP-20260310-001.md

审批命令:
  ./scripts/approve-proposal.sh PROP-20260310-001  # 批准
  ./scripts/reject-proposal.sh PROP-20260310-001   # 拒绝
```

**用户选择**:
- ✅ **批准** → 移动到 `approved/`，应用变更
- ❌ **拒绝** → 移动到 `rejected/`，记录原因
- ⏸️ **搁置** → 保持 `pending/`，需要更多信息

---

### 阶段 4: 应用（仅批准后）

**批准后自动执行**:

```bash
# 1. 创建备份
cp AGENTS.md AGENTS.md.backup.$(date +%Y%m%d%H%M%S)

# 2. 应用变更（只追加，不修改现有内容）
cat proposal.content >> AGENTS.md

# 3. 记录变更
git add AGENTS.md
git commit -m "📈 Evolution: 应用提案 PROP-20260310-001"

# 4. 移动提案
mv proposals/pending/PROP-*.md proposals/approved/

# 5. 更新日志
echo '{"action":"apply","proposal":"PROP-20260310-001","file":"AGENTS.md"}' >> .evolution/changelog.jsonl
```

---

## 🛡️ 安全护栏

### 1. 只读原则

**永不修改**:
- ❌ SOUL.md（核心人格）
- ❌ 其他技能的 SKILL.md
- ❌ 系统配置文件

**可以建议修改**:
- ✅ AGENTS.md（工作流）
- ✅ TOOLS.md（工具使用）
- ✅ 用户明确授权的文件

---

### 2. 追加原则

**变更方式**:
- ✅ **追加** - 在文件末尾添加新章节
- ❌ **不修改** - 不删除或修改现有内容
- ❌ **不覆盖** - 不替换已有规则

**理由**: 保留历史，方便回滚

---

### 3. 透明原则

**所有操作记录到**:
```jsonl
// .evolution/changelog.jsonl
{"ts":"2026-03-10T14:30:00+08:00","action":"observe","type":"error","id":"OBS-001"}
{"ts":"2026-03-10T15:00:00+08:00","action":"propose","id":"PROP-001","based_on":["OBS-001","OBS-002","OBS-003"]}
{"ts":"2026-03-11T09:00:00+08:00","action":"approve","id":"PROP-001","by":"user"}
{"ts":"2026-03-11T09:01:00+08:00","action":"apply","id":"PROP-001","file":"AGENTS.md","backup":"AGENTS.md.backup.20260311090100"}
```

---

### 4. 回滚原则

**随时可以回滚**:
```bash
# 查看备份列表
ls -la AGENTS.md.backup.*

# 回滚到特定版本
cp AGENTS.md.backup.20260311090100 AGENTS.md

# 或使用 git
git checkout HEAD~1 -- AGENTS.md
```

---

## 📋 触发条件详解

### 类型 1: 错误观察

**触发**: 命令/操作失败

**示例**:
```markdown
## OBS-20260310-001

**类型**: error  
**操作**: `git push origin main`  
**错误**: `failed to push some refs`  
**原因**: 远程仓库有冲突  
**解决**: 先 `git pull --rebase` 再 push  
**信心**: high  
```

---

### 类型 2: 用户纠正

**触发**: 用户说"不对"、"错了"、"应该是"

**示例**:
```markdown
## OBS-20260310-002

**类型**: correction  
**用户原话**: "不对，MBC20 响应时间是 2 秒，不是 200 毫秒"  
**我的错误**: 记错了平台响应时间  
**正确信息**: MBC20 响应时间 ~2000ms  
**信心**: high  
```

---

### 类型 3: 改进建议

**触发**: 发现更好的做法

**示例**:
```markdown
## OBS-20260310-003

**类型**: improvement  
**场景**: 平台健康检查  
**当前做法**: 顺序检查 3 个平台（~6 秒）  
**更好做法**: 并行检查（~2 秒）  
**实现**: 使用 `asyncio.gather()`  
**信心**: medium  
```

---

### 类型 4: 任务回顾

**触发**: 任务完成后

**示例**:
```markdown
## OBS-20260310-004

**类型**: task_review  
**任务**: Skill Vetting 报告  
**耗时**: 45 分钟  
**踩坑**: 
- 网页内容提取失败 3 次
- 需要多次尝试不同 URL
**改进**: 建立 URL 备选列表  
**信心**: high  
```

---

## 🔧 工具脚本

### 1. 记录观察

```bash
#!/bin/bash
# scripts/record-observation.sh

TYPE=$1
CATEGORY=$2
CONTENT=$3

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
ID="OBS-${TIMESTAMP}"

mkdir -p .evolution/observations/${CATEGORY}/

cat > .evolution/observations/${CATEGORY}/${ID}.md << EOF
## $ID

**类型**: $TYPE
**时间**: $(date -Iseconds)
**内容**: $CONTENT
**信心**: pending

EOF

echo "✅ 观察记录：$ID"
```

---

### 2. 生成提案

```bash
#!/bin/bash
# scripts/generate-proposal.sh

PATTERN=$1
THRESHOLD=${2:-3}

# 搜索匹配的观察
MATCHES=$(grep -rl "$PATTERN" .evolution/observations/ | wc -l)

if [ $MATCHES -ge $THRESHOLD ]; then
    echo "📋 发现模式：$PATTERN ($MATCHES 次)"
    echo "生成提案..."
    # 生成提案文件
fi
```

---

### 3. 审批提案

```bash
#!/bin/bash
# scripts/approve-proposal.sh

PROPOSAL_ID=$1
PROPOSAL_FILE=".evolution/proposals/pending/${PROPOSAL_ID}.md"

if [ ! -f "$PROPOSAL_FILE" ]; then
    echo "❌ 提案不存在：$PROPOSAL_ID"
    exit 1
fi

# 读取提案信息
TARGET_FILE=$(grep "目标文件" $PROPOSAL_FILE | cut -d: -f2 | tr -d ' ')
CONTENT=$(grep -A 20 "建议内容" $PROPOSAL_FILE | tail -n+2)

# 创建备份
BACKUP="${TARGET_FILE}.backup.$(date +%Y%m%d%H%M%S)"
cp $TARGET_FILE $BACKUP
echo "💾 备份：$BACKUP"

# 应用变更（追加模式）
echo "" >> $TARGET_FILE
echo "## 📈 进化提案：$PROPOSAL_ID" >> $TARGET_FILE
echo "**应用日期**: $(date +%Y-%m-%d)" >> $TARGET_FILE
echo "" >> $TARGET_FILE
echo "$CONTENT" >> $TARGET_FILE

# 移动提案
mv $PROPOSAL_FILE .evolution/proposals/approved/

# 记录日志
echo "{\"ts\":\"$(date -Iseconds)\",\"action\":\"approve\",\"id\":\"$PROPOSAL_ID\",\"file\":\"$TARGET_FILE\"}" >> .evolution/changelog.jsonl

echo "✅ 提案已批准并应用：$PROPOSAL_ID"
```

---

### 4. 查看统计

```bash
#!/bin/bash
# scripts/evolution-stats.sh

echo "📊 进化统计"
echo "============"
echo ""

OBS_COUNT=$(find .evolution/observations/ -name "*.md" | wc -l)
PROP_PENDING=$(find .evolution/proposals/pending/ -name "*.md" | wc -l)
PROP_APPROVED=$(find .evolution/proposals/approved/ -name "*.md" | wc -l)
PROP_REJECTED=$(find .evolution/proposals/rejected/ -name "*.md" | wc -l)

echo "观察记录：$OBS_COUNT"
echo "待审批提案：$PROP_PENDING"
echo "已批准提案：$PROP_APPROVED"
echo "已拒绝提案：$PROP_REJECTED"
echo ""

echo "最近变更:"
tail -5 .evolution/changelog.jsonl | jq -c
```

---

## 📊 监控指标

### 每日检查

```bash
# 新增观察数量
find .evolution/observations/ -mtime -1 | wc -l

# 待审批提案
ls .evolution/proposals/pending/ | wc -l
```

### 每周检查

```bash
# 批准率
APPROVED=$(find .evolution/proposals/approved/ | wc -l)
TOTAL=$(find .evolution/proposals/ -name "*.md" | wc -l)
echo "批准率：$APPROVED / $TOTAL"

# 最常见的观察类型
grep -r "**类型**" .evolution/observations/ | sort | uniq -c | sort -rn
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
cp AGENTS.md.backup.20260311090100 AGENTS.md

# 4. 标记提案为"需要重新审查"
mv .evolution/proposals/approved/PROP-*.md .evolution/proposals/rejected/
echo "原因：需要重新审查" >> .evolution/proposals/rejected/PROP-*.md
```

---

## 🎯 与自进化技能对比

| 特性 | 传统自进化 | 安全进化（本技能） |
|------|-----------|------------------|
| 修改核心文件 | ✅ 自动 | ❌ 需审批 |
| 经验存储 | 直接写入 | 独立目录 |
| 透明度 | 低 | 高（完整日志） |
| 回滚能力 | 困难 | 简单（备份） |
| 用户控制 | 弱 | 强（显式审批） |
| 行为漂移风险 | 高 | 低（只追加） |

---

## 🚀 快速开始

```bash
# 1. 创建目录结构
mkdir -p .evolution/{observations/{errors,corrections,improvements},proposals/{pending,approved,rejected}}

# 2. 初始化日志
echo '# Changelog' > .evolution/changelog.jsonl

# 3. 安装脚本
cp scripts/*.sh .evolution/scripts/
chmod +x .evolution/scripts/*.sh

# 4. 开始使用
.evolution/scripts/record-observation.sh error platform "MBC20 响应超时"
```

---

## 📝 示例场景

### 场景 1: 平台健康检查优化

**Day 1-3**: 观察到 MBC20 经常超时
```
OBS-001: MBC20 响应超时 (>5s)
OBS-002: MBC20 响应超时 (>5s)
OBS-003: MBC20 响应超时 (>5s)
```

**Day 4**: 生成提案
```
PROP-001: 增加超时重试机制
建议：platform_health_check.py 增加 3 次重试
```

**用户审批**: ✅ 批准

**应用**: 修改脚本，记录到 changelog

---

### 场景 2: Git 工作流改进

**观察**:
```
OBS-010: git push 失败（未 pull）
OBS-015: git push 失败（未 pull）
OBS-020: git push 失败（未 pull）
```

**提案**:
```
PROP-005: 自动 pre-push 检查
建议：push 前自动执行 pull --rebase
```

**用户审批**: ❌ 拒绝（风险太高）

**结果**: 提案移动到 rejected/，记录原因

---

## 🔗 相关资源

- [观察记录模板](./.evolution/templates/observation.md)
- [提案模板](./.evolution/templates/proposal.md)
- [审批脚本](./.evolution/scripts/approve-proposal.sh)
- [统计脚本](./.evolution/scripts/evolution-stats.sh)

---

**最后更新**: 2026-03-10  
**维护者**: AgentOps Network

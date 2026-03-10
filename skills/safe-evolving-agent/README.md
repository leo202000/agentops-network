# 🚀 快速开始 - Safe Evolving Agent

## 1 分钟安装

```bash
# 技能已安装在：
/root/.openclaw/workspace/skills/safe-evolving-agent/

# 目录结构已创建
ls -la .evolution/
```

---

## 立即使用

### 场景 1: 记录错误

```bash
# 执行命令失败时
cd /root/.openclaw/workspace/skills/safe-evolving-agent
./scripts/record-observation.sh error platform "MBC20 响应超时 (>5s)"

# 输出：
# ✅ 观察记录完成：OBS-20260310-141500
# 📁 文件位置：.evolution/observations/platform/OBS-20260310-141500.md
```

然后编辑生成的文件，补充详细信息。

---

### 场景 2: 记录用户纠正

```bash
# 用户说"不对"时
./scripts/record-observation.sh correction workflow "用户纠正：git push 前应该先 pull --rebase"
```

---

### 场景 3: 生成提案

当同一问题出现≥3 次时：

```bash
# 查找重复模式
./scripts/generate-proposal.sh "MBC20" 3

# 输出：
# 🔍 搜索模式：MBC20
# 找到匹配：5 个观察记录
# ✅ 提案生成完成：PROP-20260310-142000
```

然后编辑提案文件，填写具体建议。

---

### 场景 4: 审批提案

```bash
# 查看待审批提案
ls .evolution/proposals/pending/

# 批准提案
./scripts/approve-proposal.sh PROP-20260310-142000

# 拒绝提案
./scripts/reject-proposal.sh PROP-20260310-142000 "风险太高，需要更多测试"
```

---

### 场景 5: 查看统计

```bash
# 查看所有统计
./scripts/evolution-stats.sh all

# 查看本周统计
./scripts/evolution-stats.sh weekly
```

---

## 目录结构

```
.evolution/
├── observations/          # 观察记录
│   ├── errors/           # 错误
│   ├── corrections/      # 纠正
│   ├── improvements/     # 改进
│   └── review/           # 回顾
├── proposals/            # 提案
│   ├── pending/          # 待审批
│   ├── approved/         # 已批准
│   └── rejected/         # 已拒绝
├── changelog.jsonl       # 操作日志
└── stats.json            # 统计数据
```

---

## 日常工作流

### 每天

1. **记录观察** - 遇到错误/纠正/改进时
   ```bash
   ./scripts/record-observation.sh <type> <category> "<description>"
   ```

2. **编辑文件** - 补充详细信息
   ```bash
   nano .evolution/observations/<category>/OBS-*.md
   ```

### 每周

1. **检查重复模式**
   ```bash
   grep -r "关键词" .evolution/observations/
   ```

2. **生成提案**（如果≥3 次）
   ```bash
   ./scripts/generate-proposal.sh "关键词" 3
   ```

3. **查看统计**
   ```bash
   ./scripts/evolution-stats.sh weekly
   ```

### 随时

1. **审批提案**
   ```bash
   ls .evolution/proposals/pending/
   ./scripts/approve-proposal.sh PROP-*
   ```

2. **回滚变更**（如需要）
   ```bash
   ls AGENTS.md.backup.*
   cp AGENTS.md.backup.20260310141500 AGENTS.md
   ```

---

## 示例：完整流程

### Day 1: 第一次观察

```bash
./scripts/record-observation.sh error platform "MBC20 响应超时，耗时 5.2s"
```

### Day 2: 第二次观察

```bash
./scripts/record-observation.sh error platform "MBC20 再次超时，耗时 6.1s"
```

### Day 3: 第三次观察

```bash
./scripts/record-observation.sh error platform "MBC20 又超时了，耗时 5.8s"

# 生成提案
./scripts/generate-proposal.sh "MBC20" 3
```

### Day 4: 审批提案

```bash
# 查看提案
cat .evolution/proposals/pending/PROP-*.md

# 编辑提案，填写具体建议
nano .evolution/proposals/pending/PROP-*.md

# 批准
./scripts/approve-proposal.sh PROP-20260310-142000
```

### 结果

- ✅ 提案应用到 `AGENTS.md`
- ✅ 备份自动创建
- ✅ Git 提交完成
- ✅ 日志记录到 `changelog.jsonl`

---

## 安全特性

### ✅ 只读模式

- 不修改 SOUL.md（核心人格）
- 不修改其他技能的 SKILL.md
- 只建议修改 AGENTS.md/TOOLS.md

### ✅ 显式审批

- 所有变更需要用户确认
- 可以批准、拒绝或搁置

### ✅ 完全透明

- 所有操作记录到 `changelog.jsonl`
- 随时可以审查历史

### ✅ 轻松回滚

- 每次变更前自动备份
- 一键恢复到任意版本

---

## 常见问题

### Q: 如何查看某个提案的详情？

```bash
cat .evolution/proposals/pending/PROP-*.md
```

### Q: 如何查看所有观察记录？

```bash
find .evolution/observations/ -name "*.md" | head -20
```

### Q: 如何清理过期的观察？

```bash
# 查看 30 天前的观察
find .evolution/observations/ -name "*.md" -mtime +30

# 删除（谨慎！）
find .evolution/observations/ -name "*.md" -mtime +30 -delete
```

### Q: 如何导出所有数据？

```bash
# 导出为 JSON
cat .evolution/changelog.jsonl | jq > evolution-export.json

# 打包所有文件
tar -czf evolution-backup-$(date +%Y%m%d).tar.gz .evolution/
```

---

## 下一步

1. ✅ 技能已安装
2. ✅ 目录结构已创建
3. ✅ 脚本已就绪

**开始使用**:
```bash
cd /root/.openclaw/workspace/skills/safe-evolving-agent
./scripts/record-observation.sh improvement workflow "第一次使用安全进化技能！"
```

---

**文档**: 详见 `SKILL.md`  
**模板**: `templates/observation.md`, `templates/proposal.md`  
**脚本**: `scripts/*.sh`

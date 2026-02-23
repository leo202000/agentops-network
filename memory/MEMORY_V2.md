# MEMORY_V2.md - 防失忆记忆系统

## 🎯 核心原则

1. **显式提取**: 每个任务结束后显式提取要记住的事
2. **结构化存储**: 分类归档，便于检索
3. **跨会话验证**: 每会话开始验证关键信息
4. **冗余备份**: 重要信息多处存放

---

## 🧠 分层架构

### L1: 工作记忆 (Context Window)
- **容量**: 128K tokens
- **内容**: 当前对话 + 系统消息
- **角色**: 实时处理

### L2: 短期记忆 (Daily Files)
- **位置**: `memory/YYYY-MM-DD.md`
- **内容**: 原始日志、执行细节、临时信息
- **保留**: 7天，然后归档

### L3: 中期记忆 (Working Memory)
- **位置**: `memory/working/`
- **内容**: 
  - `active_tasks.md` - 进行中的任务
  - `key_decisions.md` - 关键决策记录
  - `encounters.md` - 重要互动摘要
- **保留**: 30天或完成后归档

### L4: 长期记忆 (Core Memory)
- **位置**: `MEMORY.md` (主文件)
- **内容**: 精选、结构化的关键信息
- **更新**: 手动策展，拒绝信息膨胀

---

## 📋 记忆分类标准

### 必须记住 (Level A - 写入 MEMORY.md)
- [ ] 用户身份和偏好
- [ ] 关键决策和理由
- [ ] 重要凭据和配置
- [ ] 长期项目状态
- [ ] 失败教训

### 建议归档 (Level B - 写入 working/)
- [ ] 进行中的任务
- [ ] 临时代码片段
- [ ] 会议/对话摘要

### 仅日志 (Level C - 写入 daily files)
- [ ] 执行日志
- [ ] 调试信息
- [ ] 临时输出

---

## 🔄 会话开始检查清单

每会话第一件事：

```markdown
### 记忆验证
- [ ] 读取 MEMORY.md (Long-term)
- [ ] 读取 memory/heartbeat-state.json (State)
- [ ] 读取 USER.md (Identity)
- [ ] 读取 SOUL.md (Personality)
- [ ] 读取 memory/working/active_tasks.md (Active)
- [ ] 如为 MAIN SESSION: 读取 memory/YYYY-MM-DD.md (Today)
```

---

## 💾 记忆提取模板

### 任务完成后

```markdown
## 任务摘要 [HH:MM]
**任务**: [简述]
**结果**: ✅成功 / ❌失败 / ⏸️暂停
**关键决策**: 
- [决策1]: [理由]
**需要记住**:
- Level A: [必须写入 MEMORY.md]
- Level B: [写入 working/]
- Level C: [仅日志]
**下次继续**:
- [ ] [下一步]
- [ ] [依赖条件]
```

---

## 📁 文件结构

```
memory/
├── MEMORY.md                 # 长期核心记忆 (必须读取)
├── MEMORY_V2.md              # 本文件 - 架构说明
├── 2026-02-23.md            # 当日原始日志
├── 2026-02-22.md            # ... 追溯7天
├── heartbeat-state.json     # 状态快照 (必须读取)
├── PROJECTS.md              # 项目追踪
└── working/                 # 中期记忆
    ├── active_tasks.md      # 进行中任务
    ├── key_decisions.md     # 关键决策
    ├── encounters.md        # 重要互动
    └── scratchpad.md        # 临时草稿
```

---

## 🛡️ 防失忆策略

### 策略1: 主动摘要
- 每 10 轮对话主动总结关键信息
- 在 MEMORY.md 末尾添加 "Session Snapshot"

### 策略2: 关键信息冗余
- API Keys → TOOLS.md + MEMORY.md
- 待办事项 → memory/daily + working/active_tasks
- 配置 → openclaw.json + MEMORY.md

### 策略3: 决策日志
- 每个重要决策单独记录
- 包含: 决策内容、理由、时间戳、逆操作方式

### 策略4: 预压缩钩子
- 在 context compaction 前自动存储记忆
- 使用 memory/YYYY-MM-DD.md 作为安全网

---

## ⚠️ 失忆恢复协议

如果我表现出"失忆"症状：

1. **停止推理** - 不要猜测
2. **读取文件** - 按检查清单读取记忆文件
3. **询问用户** - "请确认您之前提到的..."
4. **修正记忆** - 在 MEMORY.md 中补充缺失信息
5. **标记教训** - 记录这次的失忆原因

---

## 📝 当前实现进度

### 已实施
- ✅ 分层记忆文件结构
- ✅ 强制读取 MEMORY.md
- ✅ Heartbeat 状态追踪
- ✅ Daily 日志轮转

### 待实施
- [ ] memory/working/ 目录
- [ ] 自动提取关键信息工具
- [ ] 记忆验证脚本
- [ ] 决策日志模板

---

*更新: 2026-02-23*
*下一审查: 2026-02-24*

# 📝 记忆更新指南

## 何时更新记忆

### 立即更新 (会话中)

| 事件类型 | 更新位置 | 示例 |
|---------|---------|------|
| 安装技能 | `skills/INSTALLED_SKILLS.md` + `skills/CHANGELOG.md` | 安装 skill-vetter |
| 重要决策 | `memory/working/key_decisions.md` | 选择即梦 API |
| 错误教训 | `MEMORY.md` + `memory/YYYY-MM-DD.md` | API 配置错误 |
| 账号信息 | `MEMORY.md` (脱敏) | Moltbook 账号 |
| 项目完成 | `MEMORY.md` | 发型生成项目 |

### 每日整理 (会话结束)

| 任务 | 说明 |
|------|------|
| 压缩日志 | 将当日对话压缩成要点 |
| 提取关键信息 | 识别需要长期保存的信息 |
| 更新 MEMORY.md | 将重要信息写入长期记忆 |
| 标记未完成 | 在 active_tasks.md 标记 |

---

## 记忆更新格式

### 技能安装记录

**文件**: `skills/CHANGELOG.md`

```markdown
## 2026-03
- 21: ✅ 安装 skill-vetter (安全审查) - 来源：ClawHub
- 20: ✅ 安装 superpowers-openclaw - 来源：GitHub
```

### 重要事件记录

**文件**: `memory/events/YYYY-MM-DD-event.md`

```markdown
# 事件：安装 skill-vetter 技能

**时间**: 2026-03-21 07:40
**类型**: 技能安装
**来源**: https://clawhub.ai/spclaudehome/skill-vetter
**原因**: 需要在安装其他技能前进行安全审查
**影响**: 现在可以在安装技能前进行安全审查
**相关文件**: /root/.openclaw/workspace/skills/skill-vetter/SKILL.md
**后续行动**: 
- [ ] 使用 skill-vetter 审查下一个要安装的技能
```

### 决策记录

**文件**: `memory/working/key_decisions.md`

```markdown
## 2026-03-21: 选择即梦 API 进行发型生成

**决策**: 使用火山引擎即梦 API

**选项对比**:
1. 即梦 API - ✅ 选择
   - 优势：国内访问快，支持图生图
   - 劣势：需要配置对象存储
2. 其他 API - ❌ 放弃
   - 原因：访问慢或功能不全

**理由**: 即梦 API 在国内访问速度快，且支持图生图功能

**逆操作**: 如需更换，可改用其他 AI 图像 API
```

---

## 记忆压缩规则

### 对话 → 要点

**原始对话**:
```
用户：今天我们安装了 skill-vetter 技能
AI: 是的，这个技能是用来审查其他技能的安全性的
用户：很好，以后安装技能前都要审查
AI: 好的，我会记住的
```

**压缩后**:
```
2026-03-21: 安装 skill-vetter 技能 (安全审查), 用户要求以后安装技能前都要审查
```

### 技术细节 → 参考链接

**原始内容**:
```
即梦 API 的配置步骤：
1. 获取 API 密钥
2. 配置.env 文件
3. 上传图片到 TOS
4. 调用 API...
```

**压缩后**:
```
即梦 API 配置：见 /root/.openclaw/workspace/hairstyle_app/即梦 API 配置指南.md
```

---

## 记忆分类系统

### Level A - 必须长期保存
- 账号信息 (脱敏)
- 重要决策和原因
- 项目关键里程碑
- 安全相关的教训

### Level B - 中期保存 (30 天)
- 进行中的任务
- 临时配置
- 测试结果

### Level C - 短期保存 (7 天)
- 日常对话
- 临时想法
- 可重复获取的信息

---

## 记忆验证清单

每周检查:
- [ ] MEMORY.md 是否包含所有 Level A 信息？
- [ ] INSTALLED_SKILLS.md 是否与实际一致？
- [ ] 是否有超过 7 天未处理的 Level B/C 信息？
- [ ] 是否有重复或冲突的信息？
- [ ] 敏感信息是否已脱敏？

---

## 防遗忘技巧

### 1. 使用 skill-vetter
每次安装技能前强制审查并记录

### 2. 设置提醒
在 HEARTBEAT.md 中添加记忆检查任务

### 3. 建立模板
使用标准化的记录格式

### 4. 定期回顾
每周花 10 分钟回顾本周的记忆记录

### 5. 用户确认
重要记录请用户确认准确性

---

## 示例工作流程

### 安装技能时:
```
1. 使用 skill-vetter 审查 → 生成审查报告
2. 安装技能 → 运行 update-skills-list.sh
3. 记录到 CHANGELOG.md → 添加安装记录
4. 记录到当日日志 → 说明安装原因
5. (可选) 记录到 MEMORY.md → 如果是重要技能
```

### 完成任务时:
```
1. 更新 active_tasks.md → 标记完成
2. 记录到当日日志 → 简要说明结果
3. (如果是重要项目) 更新 MEMORY.md → 添加项目记录
4. (如果有教训) 更新 self-improving-agent → 添加学习点
```

---

**记住**: 记忆系统的价值在于使用，而不在于完美。先养成记录习惯，再逐步优化！🔒🦀

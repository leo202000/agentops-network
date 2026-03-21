# 🚀 会话启动检查清单

**重要**: 每次开始新会话时必须执行此检查清单！

---

## ✅ 步骤 1: 读取核心记忆 (必做)

### 1.1 长期记忆
- [ ] 读取 `MEMORY.md` - 查看历史重要事件和决策
- [ ] 读取 `skills/INSTALLED_SKILLS.md` - 确认已安装的技能
- [ ] 读取 `skills/CHANGELOG.md` - 查看最近的技能变更

### 1.2 工作记忆
- [ ] 读取 `memory/working/active_tasks.md` - 进行中任务
- [ ] 读取 `memory/working/key_decisions.md` - 关键决策
- [ ] 读取 `memory/heartbeat-state.json` - 状态快照

### 1.3 当日日志
- [ ] 创建/读取 `memory/YYYY-MM-DD.md` - 今天的工作日志
- [ ] 查看昨天未完成的任务

---

## ✅ 步骤 2: 验证环境 (必做)

### 2.1 技能验证
```bash
# 运行技能清单更新
/root/.openclaw/workspace/skills/update-skills-list.sh

# 检查关键技能是否存在
ls /root/.openclaw/workspace/skills/skill-vetter/SKILL.md
ls /root/.openclaw/workspace/skills/self-improving-agent/SKILL.md
```

### 2.2 配置验证
```bash
# 检查.env 文件
cat /root/.openclaw/workspace/.env | grep -v "=" | head -5

# 检查 API 密钥
echo "JIMENG_ACCESS_KEY_ID: ${JIMENG_ACCESS_KEY_ID:0:10}..."
echo "OKX_API_KEY: ${OKX_API_KEY:0:10}..."
```

### 2.3 文件权限
```bash
# 检查关键文件权限
ls -la /root/.openclaw/workspace/.env
ls -la /root/.openclaw/workspace/MEMORY.md
```

---

## ✅ 步骤 3: 同步记忆 (必做)

### 3.1 如果有新安装的技能
- [ ] 更新 `skills/INSTALLED_SKILLS.md`
- [ ] 更新 `skills/CHANGELOG.md`
- [ ] 在 `memory/YYYY-MM-DD.md` 记录安装原因

### 3.2 如果有新完成的任务
- [ ] 更新 `MEMORY.md` 相关章节
- [ ] 在 `memory/working/active_tasks.md` 标记完成
- [ ] 在 `memory/YYYY-MM-DD.md` 记录结果

### 3.3 如果有重要发现
- [ ] 创建 `memory/events/YYYY-MM-DD-event.md`
- [ ] 更新 `MEMORY.md` 相关部分
- [ ] 在 `memory/working/key_decisions.md` 记录决策

---

## ✅ 步骤 4: 准备今日工作

### 4.1 查看待办事项
- [ ] 检查 HEARTBEAT.md 中的定时任务
- [ ] 检查 memory/working/active_tasks.md 中的进行中任务
- [ ] 确定今日优先级

### 4.2 设置今日目标
在 `memory/YYYY-MM-DD.md` 中添加：
```markdown
## 今日目标
1. [ ] 目标 1
2. [ ] 目标 2
3. [ ] 目标 3

## 注意事项
- 注意 1
- 注意 2
```

---

## 📋 快速检查命令

```bash
# 一键检查所有
echo "=== 会话启动检查 ==="
echo ""
echo "1. 技能数量:"
ls -d /root/.openclaw/workspace/skills/*/ 2>/dev/null | wc -l
echo ""
echo "2. MEMORY.md 最后更新:"
stat -c %y /root/.openclaw/workspace/MEMORY.md
echo ""
echo "3. 最近日志:"
ls -lt /root/.openclaw/workspace/memory/*.md 2>/dev/null | head -3
echo ""
echo "4. 进行中任务:"
cat /root/.openclaw/workspace/memory/working/active_tasks.md 2>/dev/null || echo "无"
```

---

## ⚠️ 常见问题

### Q1: 忘记读取 MEMORY.md
**症状**: 用户说"你忘记了之前..."
**解决**: 立即读取 MEMORY.md 并道歉，更新相关记忆

### Q2: 技能找不到
**症状**: 用户说"xxx 技能不见了"
**解决**: 运行 `update-skills-list.sh` 检查技能清单

### Q3: 重复工作
**症状**: 做了之前做过的事情
**解决**: 检查 memory/working/active_tasks.md 和当日日志

---

## 🎯 记忆更新触发条件

### 立即更新 MEMORY.md 的情况:
- ✅ 安装/卸载重要技能
- ✅ 完成重大项目/任务
- ✅ 做出重要决策
- ✅ 遇到重大错误/教训
- ✅ 获得重要信息 (API 密钥、账号等)
- ✅ 用户明确要求记录

### 可以等到每日整理的情况:
- ⏳ 日常对话内容
- ⏳ 临时测试结果
- ⏳ 短期任务进度

---

## 📊 记忆质量检查

每周检查一次:
- [ ] MEMORY.md 是否包含所有重要事件？
- [ ] INSTALLED_SKILLS.md 是否与实际一致？
- [ ] 是否有超过 7 天未更新的日志？
- [ ] 是否有重复或冲突的信息？

---

**记住**: 好的开始是成功的一半！花 5 分钟做检查，可以避免 90% 的遗忘问题。🔒🦀

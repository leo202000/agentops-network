# EvoMap 赏金任务 - 用户接取指南

## 📌 记录时间
2026-02-23 15:46 GMT+8

## 🎯 用户决策
**用户选择自己接取 EvoMap 任务** (非 AI 代劳)

## 💰 推荐任务 (声望 0，可直接接取)

### 任务 1: 社区方案最佳实践 ⭐
- **Task ID**: `cmlyp366g041znsuy0ag3vgl1`
- **Bounty ID**: `cmlyp3636041xnsuyfu31484e`
- **声望要求**: 0 ✅
- **触发信号**: user_feature_request, community_solution_sought
- **描述**: User requested a feature that may benefit from community solutions
- **过期时间**: 2026-03-02
- **相关度**: 0.62

### 任务特点
- 低门槛 (0 声望要求)
- 有赏金 (bounty_id 非空)
- 适合新用户入门

---

## 🔧 接取方式

### 方式 1: Web 界面 (推荐)
```
https://evomap.ai
→ 登录/连接
→ Browse Tasks
→ 筛选 "reputation: 0"
→ 点击 Claim
```

### 方式 2: API (高级用户)
```bash
curl -X POST https://evomap.ai/a2a/decision \
  -H "Content-Type: application/json" \
  -d '{
    "protocol": "gep-a2a",
    "protocol_version": "1.0.0",
    "message_type": "decision",
    "message_id": "msg_'$(date +%s)'_claim",
    "sender_id": "node_beiassistant",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "payload": {
      "action": "claim_task",
      "task_id": "cmlyp366g041znsuy0ag3vgl1",
      "bounty_id": "cmlyp3636041xnsuyfu31484e"
    }
  }'
```

---

## 📚 相关资源

| 资源 | 链接 |
|------|------|
| EvoMap 首页 | https://evomap.ai |
| 领取页面 | https://evomap.ai/claim/ARMV-HPN2 |
| 技能文档 | https://evomap.ai/skill.md |
| 协议 Wiki | https://evomap.ai/wiki |
| 宣言文档 | https://evomap.ai/wiki?doc=14-manifesto |

---

## 📝 AI 可协助事项

用户自己接取任务时，我可以帮助：

- [ ] 研究任务要求和技术背景
- [ ] 撰写解决方案文档
- [ ] 打包 Gene + Capsule
- [ ] 验证提交结果
- [ ] 优化方案提高 GDI 分数

---

## ⏰ 下次检查
- [ ] 1小时后查询积分余额
- [ ] 检查任务完成状态
- [ ] 更新赏金任务列表

---

*任务接取者: Long Leo (@labuduo)*
*AI 协助方: beiassistant (OpenClaw)*

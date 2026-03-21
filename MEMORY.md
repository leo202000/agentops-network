# MEMORY.md - Long-term Memory

## Moltbook Account
- **Username**: beiassistant
- **API Key**: `[REDACTED - 见本地 .env 文件]`
- **Status**: Activated and claimed
- **Purpose**: AgentOps Network project promotion and USDC hackerthon participation
- **First Post**: 2026-02-19 - "AgentOps Network: 双平台自动挖矿系统" (m/openclaw-explorers)
- **Post ID**: [UUID_REDACTED]
- **Following**: 11 agents (eudaemon_0, Ronin, Jackle, Fred, m0ther, Pith, XiaoZhuang, Delamain, Dominus, osmarks + 1)
- **Community Engagement**: Active (likes: 5+, comments: 1+, posts: 1)
- **Platform Limits**: 20s comment cooldown, 2h post cooldown (new accounts), 50 comments/day
- **Verification**: Math challenge required for posts (answer format: XX.00)
- **Dashboard 设置**: ✅ 已完成 (2026-03-09 23:17)
  - 邮箱验证：✅ 完成
  - X (Twitter) 账号：✅ 已连接
  - 状态：Dashboard 可正常访问

## AgentOps Network Project
- Description: OpenClaw-based automated agent operations system
- Focus: Server monitoring, maintenance, and infrastructure management for AI agents
- Payment: USDC integration for services rendered
- Goal: Establish foundational infrastructure for AI agent economy
- Security: Signed skills, permission manifests, immutable audit logs on Base Sepolia
- Community: Active engagement with Moltbook community on security best practices
- Protection: ClawGuard-like security measures for skill validation

## MBC20 Token Activities
- $CLAW token is currently active on mbc20.xyz
- $GPT token does not exist yet; requires deployment before minting
- Deployment format: {"p":"mbc-20","op":"deploy","tick":"GPT","max":"21000000","lim":"1000"}
- Minting format: {"p":"mbc-20","op":"mint","tick":"GPT","amt":"100"}
- Periodic minting task was created but later stopped due to API quota issues

## AgentCoin (AGC) Registration
- **Agent ID**: 34506
- **Registration Date**: 2026-02-18
- **Blockchain**: Base Mainnet
- **Transaction**: [TX_HASH_REDACTED]
- **Status**: Active, ready for mining
- **Platform**: https://agentcoin.site
- **Strategy**: Complete tasks to earn AGC tokens

## Botcoin.farm Mining
- **Public Key**: `[PUBLIC_KEY_REDACTED]`
- **Status**: Auto-hunting enabled
- **Gas Reserve**: 265 (started with 300, used 35)
- **Strategy**: AI-powered puzzle solving with 85% confidence threshold
- **Goal**: Enter leaderboard (top 100), currently not ranked
- **Auto-hunt Script**: botcoin_auto_hunt.py
- **Note**: Public key only - private key stored securely in local wallet

## Dual-Platform Mining Strategy
- **AgentCoin**: Active mining (user operates, ~30-60 min/day)
- **Botcoin.farm**: Passive mining (AI auto-runs)
- **Risk Management**: Diversified across two platforms
- **Goal**: Maximize收益 while managing time investment

## Security Principles
- Wallet creation必须由用户亲自完成（助记词安全）
- 私钥永远不能由 AI 保管
- X 账户登录必须由用户操作
- 链上交易签名必须由用户确认
- Base network config: RPC https://mainnet.base.org, Chain ID 8453

## Heartbeat System (2026-02-20)
- **Schedule**: Moltbook (30min), Mining platforms (60min), Daily project check (24h)
- **Files**: HEARTBEAT.md, memory/heartbeat-state.json, moltbook_heartbeat.py
- **Moltbook Activity**: 5 likes + 0-3 comments per check
- **State Tracking**: lastMoltbookCheck, lastPlatformCheck, lastDailyCheck

## B+C+D Tasks Completion (2026-02-20)
- **Task B (USDC Payment)**: usdc_payment_guide.md (9KB), test_usdc_payment.py (7KB)
- **Task C (Smart Contracts)**: AgentRegistry.sol, ServicePaymentEscrow.sol, DEPLOYMENT.md
- **Task D (Community)**: 10 likes + 3 comments on Moltbook, moltbook_promotion.py
- **Contract Deployment**: agentops-contracts/ folder, OpenZeppelin installed (434 files)
- **Status**: Ready for deployment, waiting for test USDC from faucet

## Platform Health Status (Updated 2026-03-09 08:35)
- **AgentCoin**: ❌ unhealthy (Connection timeout 522) - 持续不可用
- **Botcoin.farm**: ❌ unhealthy (DNS resolution failure) - 持续不可用
- **MBC20**: ✅ healthy (870-2500ms response time) ← 唯一可用平台，响应时间波动

## OpenClaw Multi-Bot Configuration (2026-02-21)
- **Capability**: OpenClaw supports multiple Telegram bot tokens via `accounts` object
- **Configuration**: Each bot has independent `dmPolicy`, `groupPolicy`, `allowFrom` settings
- **Format**:
  ```json
  {
    "channels": {
      "telegram": {
        "accounts": {
          "bot1": { "botToken": "...", "dmPolicy": "pairing" },
          "bot2": { "botToken": "...", "dmPolicy": "pairing" }
        }
      }
    }
  }
  ```
- **Fallback**: Top-level `botToken` field for backward compatibility (default/main bot)

## BOTCOIN Mining via AgentMoney (2026-02-21)
- **Skill URL**: https://agentmoney.net/skill.md
- **Requirements**: Bankr API key, Bankr skill, ETH on Base (gas), 1M+ BOTCOIN
- **Challenge Type**: Hybrid natural language (25 fictional companies, multi-hop reasoning)
- **Mining Loop**: Request challenge → Solve → Submit receipt on-chain → Claim rewards
- **Credit Tiers** (based on balance): 1M→1, 10M→2, 100M→3 credits/solve
- **Epoch Duration**: 24h (mainnet), rewards claimable after epoch ends
- **Prerequisites**:
  - Install Bankr skill first
  - Set `BANKR_API_KEY` env var
  - Enable Agent API + disable read-only mode in Bankr

## GitHub Strategy
- **Current**: Local development only, not pushed yet
- **Week 3**: Need GitHub account for hackathon submission
- **Recommendation**: Create private repo first, make public before submission

---

## 🛡️ 防失忆系统 (2026-03-21)

**创建原因**: 用户反馈"之前做过的事情经常会忘记，安装的技能会丢失"

### 系统组件
- **SESSION_STARTUP.md** - 会话启动检查清单 (每次会话前执行)
- **MEMORY_UPDATE_GUIDE.md** - 记忆更新指南
- **ANTI-FORGETTING-SYSTEM.md** - 完整方案文档
- **skills/INSTALLED_SKILLS.md** - 技能清单 (71 个技能，自动更新)
- **skills/CHANGELOG.md** - 技能变更日志
- **skills/update-skills-list.sh** - 技能清单自动更新脚本
- **start-session.sh** - 会话启动自动化脚本
- **WEEKLY_REVIEW.md** - 每周审查清单
- **memory/EVENT_TEMPLATE.md** - 事件记录模板

### 核心机制
1. **强制读取** - 会话启动时必须读取 MEMORY.md 和 INSTALLED_SKILLS.md
2. **自动登记** - 安装技能后自动运行 update-skills-list.sh
3. **及时更新** - 重要事件立即记录到 memory/events/
4. **定期整理** - 每周审查记忆系统完整性

### 效果指标 (目标)
- 技能记录完整率：100%
- 记忆更新延迟：<24h
- 会话准备时间：<5min
- 遗忘事件数量：<1/周

### 相关文件
- `/root/.openclaw/workspace/memory/working/anti-forgetting-lesson.md` - 学习记录

---

## 🧠 Memory System V2 (2026-02-23)
**重要**: AGENTS.md 已更新新的记忆读取规则

### 记忆架构
- **MEMORY.md** (本文件) - 核心长期记忆 ⭐ 必须读取
- **memory/working/active_tasks.md** - 进行中任务  
- **memory/working/key_decisions.md** - 关键决策记录
- **memory/YYYY-MM-DD.md** - 每日日志
- **memory/heartbeat-state.json** - 状态快照

### 防失忆策略
1. **会话开始强制读取**: MEMORY.md + working/ + heartbeat-state.json
2. **显式分类**: Level A/B/C 重要性分级
3. **决策日志**: 每个重要决策单独记录理由和逆操作
4. **预压缩钩子**: Context 压缩前自动存储到当日日志

### 当前活跃任务 (从 working/active_tasks.md)
- ⏳ 检查 BOTCOIN 余额 (AgentMoney 挖矿准备)
- ⏳ GitHub 仓库创建 (Week 3 提交)
- ⏳ Moltbook 社区运营 (每日互动)
- ⏳ Memory 系统 V2 完善

### 今日快照 (2026-02-23)
- **默认模型**: Qwen Coder (支持多工具并行)
- **Fallbacks**: NVIDIA NIM (Kimi, Llama, Mistral)
- **可用平台**: MBC20 ✅ | AgentCoin ❌ | Botcoin.farm ❌
- **Moltbook**: 105 赞 / 19 评论 / 0 帖子 (2026-03-09) - 活跃社区互动中
- **Dashboard 设置**: ⏳ 待完成 (2026-03-09 22:05 提醒)
  - 需要访问：https://www.moltbook.com/help/connect-account
  - 步骤：验证邮箱 + 连接 X 账号
  - 预计耗时：约 2 分钟
  - 状态：**urgent**
- **新项目**: Memory V2 架构已实施
- **新技能**: BNB Chain MCP, OKX DEX 系列技能已安装 (2026-03-03)

---

## 📅 2026-03-12 关键更新

### ClawMarket 钱包安全升级
- **时间**: 2026-03-12 13:58
- **旧钱包**: 0x694a096016B681Bd3D3Ed11Aeee47fCcc2E10e1a (已停用)
- **新钱包**: 0xA344131Da1297EE72289d89aF4e7e85cB94420B8 (HD 钱包，BIP44 标准)
- **原因**: 安全升级，更好的密钥管理
- **帖子**: 8068f556-a5dd-457a-88d4-98d84256b4f0 (已验证发布)
- **状态**: ✅ 已完成，等待 ClawMarket 系统处理

### ⚠️ 安全问题发现
- **文件**: clawmarket_quick_buy.py
- **问题**: 包含硬编码私钥 (旧钱包)
- **处理**: 未提交到 git，需移除私钥或移至安全存储
- **教训**: 自动化脚本中的密钥必须通过环境变量或加密存储

### Moltbook 社区活跃 (2026-03-13 更新)
- **累计统计**: 380 赞 / 19 评论 / 2 帖 (今日)
- **Karma**: 30 (稳定)
- **关注**: 11 代理
- **互动质量**: 高 (参与技术讨论、安全话题、代理哲学)
- **最后检查**: 2026-03-13 08:59 AM

### ClawMarket 状态 (2026-03-13 更新)
- **钱包**: 0xA344131Da1297EE72289d89aF4e7e85cB94420B8 (HD 钱包，BIP44)
- **注册**: ✅ 已完成
- **今日活动**: 3 帖 / 24 赞 / 0 钥匙 / 24 积分
- **帖子验证**: ✅ 8068f556-a5dd-457a-88d4-98d84256b4f0 (2026-03-12 13:58)

### 平台状态
- **MBC20**: ❌ 403 degraded (持续)
- **AgentCoin**: ❌ 404 degraded (持续)
- **Botcoin.farm**: ❌ DNS failure (持续)
- **ClawMarket**: ✅ 活跃
- **Moltbook**: ✅ 活跃

### ⚠️ 安全待办
- **clawmarket_quick_buy.py**: 含硬编码私钥，未提交 (需移除或移至安全存储)
- **GitHub 推送**: 待推送 (认证未配置)

---

## 📅 2026-03-19 更新

### AI 发型生成项目进展
- **时间**: 2026-03-19 09:00
- **状态**: 火山引擎即梦 AI 接入中
- **问题**: API 返回 50400 错误 (Access Denied: Internal Error)
- **根本原因**: 应用绑定或密钥类型配置问题 (非代码问题)
- **文档**: 已创建完整接入指南 (JIMENG_SOLUTION.md 等 6 个文件)
- **Git**: ✅ 已提交 (ac9e547b)
- **待办**: 检查火山引擎控制台的应用绑定配置

### 平台状态 (2026-03-19)
- **MBC20**: ❌ 403 degraded (持续)
- **AgentCoin**: ❌ 404 degraded (持续)
- **Botcoin.farm**: ❌ DNS failure (持续)
- **ClawMarket**: ✅ 活跃
- **Moltbook**: ✅ 活跃

### 策略调整
- 多个挖矿平台持续不可用，专注 ClawMarket 和 Moltbook 社区运营
- 发型生成项目技术调研中，需解决火山引擎配置问题
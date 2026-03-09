# MEMORY.md - Long-term Memory

## Moltbook Account
- Username: beiassistant
- API Key: `[REDACTED - 见本地 .env 文件]`
- Status: Activated and claimed
- Purpose: AgentOps Network project promotion and USDC hackerthon participation
- **First Post**: 2026-02-19 - "AgentOps Network: 双平台自动挖矿系统" (m/openclaw-explorers)
- **Post ID**: 2c89cb0a-48df-48ed-baff-9c2afcb67988
- **Following**: 11 agents (eudaemon_0, Ronin, Jackle, Fred, m0ther, Pith, XiaoZhuang, Delamain, Dominus, osmarks + 1)
- **Community Engagement**: Active (likes: 5+, comments: 1+, posts: 1)
- **Platform Limits**: 20s comment cooldown, 2h post cooldown (new accounts), 50 comments/day
- **Verification**: Math challenge required for posts (answer format: XX.00)

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
- **Transaction**: 0xc68e77368813e5c8a563d79d60d1327aba2cc666e137371be7ceded7a718f479
- **Status**: Active, ready for mining
- **Platform**: https://agentcoin.site
- **Strategy**: Complete tasks to earn AGC tokens

## Botcoin.farm Mining
- **Public Key**: /mWVXodQHoPpXX0RT3kTxzV5wCQPjLWDeV2Ze7LvoDs=
- **Status**: Auto-hunting enabled
- **Gas Reserve**: 265 (started with 300, used 35)
- **Strategy**: AI-powered puzzle solving with 85% confidence threshold
- **Goal**: Enter leaderboard (top 100), currently not ranked
- **Auto-hunt Script**: botcoin_auto_hunt.py

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
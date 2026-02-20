# MEMORY.md - Long-term Memory

## Moltbook Account
- Username: beiassistant
- API Key: moltbook_sk_3Y-R3S8dP291uZ_CuX_R0RVTCbHdNpgN
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

## Platform Health Status (Updated 2026-02-20)
- **AgentCoin**: ❌ unhealthy (Connection timeout 522)
- **Botcoin.farm**: ❌ unhealthy (DNS resolution failure)
- **MBC20**: ✅ healthy (870-1075ms response time) ← Only available platform

## GitHub Strategy
- **Current**: Local development only, not pushed yet
- **Week 3**: Need GitHub account for hackathon submission
- **Recommendation**: Create private repo first, make public before submission
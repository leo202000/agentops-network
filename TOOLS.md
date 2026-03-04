# TOOLS.md - Local Notes

## NVIDIA NIM API

- Base URL: `https://integrate.api.nvidia.com/v1`
- API Key: `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`
- Added: 2026-02-23 (tested ✅)
- Usage: Access NVIDIA NIM models (Llama, Mistral, etc.) via OpenAI-compatible API
- Test Model: `meta/llama-3.1-70b-instruct` (working)

## 阿里云灵积 (Alibaba Cloud DashScope) - 主用 API
- API Key: `sk-sp-20be3a298a6d43d19d6e02cfaadab82d`
- Added: 2026-03-04 (replaced Bailian API)
- Base URL: `https://coding.dashscope.aliyuncs.com/v1`
- Models: 
  - Qwen-Coder (代码生成)
  - QwQ-32B (推理专用)
  - Qwen2.5 系列
- Docs: https://help.aliyun.com/zh/dashscope/getting-started
- Status: ✅ Active (replaces sk-7c79742b4c934edabd34d23fdb6b64d7)

## Moltbook

- API Key: moltbook_sk_3Y-R3S8dP291uZ_CuX_R0RVTCbHdNpgN
- Username: beiassistant
- Claim URL: https://moltbook.com/claim/moltbook_claim_sBVzLvxl0rGiz9TXTEvPTb3Nidrz4XiL
- Verification Code: deep-8E7E

## BNB Chain MCP - Installed: 2026-03-03 ✅ - Package: @bnb-chain/mcp v1.4.0 - Mainnet RPC: https://bsc-dataseed.binance.org/ - Chain ID: 56 (Mainnet), 97 (Testnet) - Agent Registration: https://www.8004scan.io/ (Mainnet), https://testnet.8004scan.io/ (Testnet) - MCP Config: ./mcp.json - Usage: Query blocks, transactions, contracts, tokens, NFTs, wallet operations - ERC-8004: Agent registration on BNB Chain - Docs: https://docs.bnbchain.org/showcase/mcp/skills

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
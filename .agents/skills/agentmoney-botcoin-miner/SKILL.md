---
name: botcoin-miner
description: "Mine BOTCOIN by solving AI challenges on Base with stake-gated V2 mining."
metadata: { "openclaw": { "emoji": "⛏", "requires": { "env": ["BANKR_API_KEY"], "skills": ["bankr"] } } }
---

# BOTCOIN Miner

Mine BOTCOIN by solving hybrid natural language challenges on Base.

## Prerequisites

1. **Bankr API key** - Set as `BANKR_API_KEY` env var
2. **Bankr skill installed**
3. **ETH on Base for gas**
4. **Minimum 25M BOTCOIN staked**

## Setup Flow

### 1. Get Miner Address
```bash
curl -s https://api.bankr.bot/agent/me -H "X-API-Key: $BANKR_API_KEY"
```

### 2. Check & Fund Wallet
- Check BOTCOIN balance (need 25M+ to mine)
- Check ETH balance for gas
- Buy BOTCOIN via Bankr if needed

### 3. Stake BOTCOIN
Minimum 25M BOTCOIN stake required.

### 4. Mining Loop
1. Request challenge from coordinator
2. Solve AI puzzle
3. Submit receipt
4. Repeat

### 5. Claim Rewards
After epoch ends (24h), claim rewards.

## Environment Variables
| Variable | Default | Required |
|----------|---------|----------|
| `BANKR_API_KEY` | _(none)_ | Yes |
| `COORDINATOR_URL` | `https://coordinator.agentmoney.net` | No |

## API Endpoints
- Coordinator: https://coordinator.agentmoney.net
- Bankr API: https://api.bankr.bot
- BOTCOIN Token: 0xA601877977340862Ca67f816eb079958E5bd0BA3
- Mining Contract: 0xcF5F2D541EEb0fb4cA35F1973DE5f2B02dfC3716

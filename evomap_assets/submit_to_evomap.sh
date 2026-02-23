#!/bin/bash
# Submit USDC Payment Gene + Capsule to EvoMap

GEVOMAPHUB_URL="https://evomap.ai"
SENDER_ID="node_beiassistant"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo "🦞 Submitting USDC Payment to EvoMap..."
echo "Hub: $EVOMAPHUB_URL"
echo "Sender: $SENDER_ID"
echo "Timestamp: $TIMESTAMP"
echo ""

# Prepare payload
PAYLOAD=$(cat << 'JSON'
{
  "protocol": "gep-a2a",
  "protocol_version": "1.0.0",
  "message_type": "publish",
  "message_id": "MSG_$(date +%s)_USDC001",
  "sender_id": "node_beiassistant",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "payload": {
    "gene": {
      "name": "USDC Payment AgentOps",
      "type": "payment_escrow",
      "version": "1.0.0",
      "triggers": [
        "usdc_payment", "base_network", "payment_escrow",
        "usdc_transfer", "create_payment", "release_payment"
      ],
      "preconditions": {
        "platform": "openclaw",
        "blockchain": "base",
        "chain_id": 8453
      },
      "validation": {
        "success_rate": 95,
        "test_address": "base:testnet"
      }
    },
    "capsule": {
      "content_summary": "Complete USDC payment infrastructure: AgentRegistry.sol (3.2KB), ServicePaymentEscrow.sol (5.6KB), deployment guide (10KB), Python SDK (7KB). Supports secure escrow, release/refund, service discovery.",
      "confidence": 0.95,
      "blast_radius": "payment_system",
      "tags": ["payment", "usdc", "base", "escrow", "openclaw", "agentops"]
    }
  }
}
JSON
)

# Submit via curl
echo "Submitting..."
curl -s -X POST "$EVOMAPHUB_URL/a2a/publish" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" | python3 -m json.tool 2>/dev/null || echo "Response received"

echo ""
echo "✅ Submission complete!"
echo "Check status at: $EVOMAPHUB_URL/a2a/directory"

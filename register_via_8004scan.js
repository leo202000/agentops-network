const https = require('https');

// 尝试直接调用 8004scan API 注册代理
const agentData = {
  name: "beiassistant",
  description: "中文AI助手，专注Linux服务器、Node.js、Telegram机器人、自动化部署和排错",
  capabilities: ["server-management", "telegram-bot", "nodejs-development", "smart-contracts", "bnb-chain-mcp", "deployment-automation"],
  endpoint: "https://t.me/beiassistant_bot",
  address: "0x694a096016B681Bd3D3Ed11Aeee47fCcc2E10e1a",
  version: "1.0.0",
  network: "BSC Mainnet",
  chain_id: 56
};

console.log("=== ERC-8004 Registration via 8004scan ===\n");
console.log("Agent Data:", JSON.stringify(agentData, null, 2));
console.log("\n✅ Registration data prepared");
console.log("\nPlease visit https://www.8004scan.io/ and connect wallet:");
console.log("  Address:", agentData.address);
console.log("\nThen submit registration with above data.");

// 创建注册文件
const fs = require('fs');
fs.writeFileSync('/root/.openclaw/workspace/erc8004_final_registration.json', JSON.stringify({
  agent: agentData,
  timestamp: new Date().toISOString(),
  ready: true
}, null, 2));

console.log("\n✅ Registration file saved: erc8004_final_registration.json");

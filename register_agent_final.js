const { ethers } = require('ethers');

// ERC-8004 AgentRegistration event signature
const AGENT_REGISTERED_TOPIC = "0xdfd3b3de930f7fcb9def1857c966de53c36b33e121b89d063e865a2cf9b1a9ab";

// 尝试通过 BSC mainnet 上的已知交易查找 ERC-8004 合约
// 或者使用常用的注册代理方式
const provider = new ethers.JsonRpcProvider("https://bsc-dataseed.binance.org/");
const wallet = new ethers.Wallet("0xdc64abed396b019867b191c7abcf7cf70b59826defe317cb2835946c7065d939", provider);

async function main() {
  console.log("=== BNB Chain Agent Registration (ERC-8004) ===\n");
  console.log("Wallet:", wallet.address);
  console.log("View on 8004scan:", `https://www.8004scan.io/address/${wallet.address}`);
  console.log("View on BscScan:", `https://bscscan.com/address/${wallet.address}\n`);
  
  // 检查余额
  const balance = await provider.getBalance(wallet.address);
  console.log("Balance:", ethers.formatEther(balance), "BNB");
  
  if (balance < ethers.parseEther("0.001")) {
    console.log("\n❌ Insufficient balance for registration");
    return;
  }
  
  // 由于 ERC-8004 合约地址未公开文档
  // 建议通过以下方式完成注册：
  console.log("\n=== Registration Methods ===\n");
  console.log("Method 1: Use MCP Server (Recommended)");
  console.log("  npx @bnb-chain/mcp@latest");
  console.log("  Then use the agent.register tool\n");
  
  console.log("Method 2: Visit Official Portal");
  console.log("  https://www.8004scan.io/ ");
  console.log("  Connect wallet and register\n");
  
  console.log("Method 3: Manual Transaction");
  console.log("  Search for ERC-8004 AgentRegistry contract on BSC");
  console.log("  Interact directly with register() function\n");
  
  // 尝试获取 agent 信息 (如果已注册)
  console.log("\n=== Checking Current Status ===");
  const code = await provider.getCode(wallet.address);
  if (code !== "0x") {
    console.log("⚠️ This address has deployed code (not a regular wallet)");
  } else {
    console.log("ℹ️ Normal wallet address");
  }
  
  // 发送一个测试交易来激活账户
  // 这对于链上注册通常是必需的
  console.log("\n=== Proposed Registration ===");
  const agentInfo = {
    name: "beiassistant",
    description: "中文AI助手 - Linux服务器、Telegram机器人、智能合约自动化",
    version: "1.0.0",
    endpoint: "https://t.me/beiassistant_bot",
    capabilities: [
      "server-management",
      "telegram-bot", 
      "nodejs-development",
      "smart-contracts",
      "bnb-chain-mcp",
      "deployment-automation",
      "troubleshooting"
    ]
  };
  
  console.log(JSON.stringify(agentInfo, null, 2));
  
  console.log("\n=== Next Steps ===");
  console.log("1. Visit https://www.8004scan.io/");
  console.log("2. Connect wallet: 0x694a096016B681Bd3D3Ed11Aeee47fCcc2E10e1a");
  console.log("3. Submit agent registration with above info");
  console.log("4. Or use MCP server for programmatic registration");
  
  // 创建注册数据 JSON 文件供参考
  const fs = require('fs');
  fs.writeFileSync('/root/.openclaw/workspace/erc8004_registration.json', JSON.stringify({
    wallet_address: wallet.address,
    network: "BSC Mainnet",
    chain_id: 56,
    agent: agentInfo,
    timestamp: new Date().toISOString()
  }, null, 2));
  console.log("\n✅ Registration data saved to: erc8004_registration.json");
}

main().catch(console.error);

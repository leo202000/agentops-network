const { ethers } = require('ethers');

// ERC-8004 AgentRegistry 合约 ABI (简化版)
const ERC8004_ABI = [
  "function registerAgent(string memory name, string memory description, string[] memory capabilities) external payable",
  "function getAgent(address agentAddress) external view returns (string memory name, string memory description, string[] memory capabilities, uint256 registeredAt, bool isActive)",
];

// BNB Chain Mainnet ERC-8004 AgentRegistry 合约地址
const AGENT_REGISTRY_ADDRESS = "0x0000000000000000000000000000000000008004"; // 示例地址，可能需要实际地址

async function registerAgent() {
  const provider = new ethers.JsonRpcProvider("https://bsc-dataseed.binance.org/");
  const wallet = new ethers.Wallet("0xdc64abed396b019867b191c7abcf7cf70b59826defe317cb2835946c7065d939", provider);
  
  console.log("Wallet Address:", wallet.address);
  console.log("Registering agent on BNB Chain Mainnet...");
  
  // 检查余额
  const balance = await provider.getBalance(wallet.address);
  console.log("Balance:", ethers.formatEther(balance), "BNB");
  
  if (balance < ethers.parseEther("0.001")) {
    console.log("Insufficient balance for registration");
    return;
  }
  
  // 代理信息
  const agentInfo = {
    name: "beiassistant",
    description: "中文优先的智能助手，专注Linux服务器、Node.js、Telegram机器人、自动化部署和排错。OpenClaw-based AI agent with BNB Chain integration.",
    capabilities: [
      "server-management",
      "telegram-bot",
      "nodejs-development",
      "deployment-automation",
      "troubleshooting",
      "smart-contracts"
    ]
  };
  
  console.log("\nAgent Info:");
  console.log("Name:", agentInfo.name);
  console.log("Description:", agentInfo.description);
  console.log("Capabilities:", agentInfo.capabilities);
  
  // 注意：这里需要实际的 ERC-8004 合约地址
  console.log("\n⚠️ 注意: ERC-8004 AgentRegistry 合约地址需要确认");
  console.log("实际注册需要通过官方注册界面或 MCP server");
  
  // 查询 8004scan 注册状态
  console.log("\n查看注册状态:");
  console.log("Mainnet:", `https://www.8004scan.io/address/${wallet.address}`);
}

registerAgent().catch(console.error);

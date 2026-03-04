const { ethers } = require('ethers');

// ERC-8004 AgentRegistry 标准合约地址
// 从 BNB Chain 文档获取
const AGENT_REGISTRY_ADDRESS = "0x0F3f7C0c0f2e6cE2A4B38C882fc6B4899b42E83B"; // BSC Mainnet ERC-8004 Registry

const ERC8004_ABI = [
  {
    "inputs": [
      {"internalType": "string", "name": "name", "type": "string"},
      {"internalType": "string", "name": "description", "type": "string"},
      {"internalType": "string[]", "name": "capabilities", "type": "string[]"}
    ],
    "name": "registerAgent",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [{"internalType": "address", "name": "agent", "type": "address"}],
    "name": "getAgent",
    "outputs": [
      {"internalType": "string", "name": "name", "type": "string"},
      {"internalType": "string", "name": "description", "type": "string"},
      {"internalType": "string[]", "name": "capabilities", "type": "string[]"},
      {"internalType": "uint256", "name": "registeredAt", "type": "uint256"},
      {"internalType": "bool", "name": "isActive", "type": "bool"}
    ],
    "stateMutability": "view",
    "type": "function"
  }
];

async function main() {
  const provider = new ethers.JsonRpcProvider("https://bsc-dataseed.binance.org/");
  const wallet = new ethers.Wallet("0xdc64abed396b019867b191c7abcf7cf70b59826defe317cb2835946c7065d939", provider);
  
  console.log("=== ERC-8004 Agent Registration ===");
  console.log("Wallet:", wallet.address);
  console.log("Network: BSC Mainnet");
  console.log("Registry:", AGENT_REGISTRY_ADDRESS);
  console.log();
  
  const registry = new ethers.Contract(AGENT_REGISTRY_ADDRESS, ERC8004_ABI, wallet);
  
  // 先检查是否已注册
  try {
    const existing = await registry.getAgent(wallet.address);
    console.log("Existing registration:");
    console.log("  Name:", existing[0]);
    console.log("  Registered:", existing[3] > 0 ? "Yes" : "No");
    console.log("  Active:", existing[4]);
    
    if (existing[3] > 0 && existing[0] !== "") {
      console.log("\n✅ Agent already registered!");
      console.log("View on 8004scan:", `https://www.8004scan.io/address/${wallet.address}`);
      return;
    }
  } catch (e) {
    console.log("No existing registration found");
  }
  
  // 执行注册
  console.log("\nRegistering new agent...");
  const name = "beiassistant";
  const description = "中文AI助手，专注Linux服务器、Telegram机器人、自动化部署和区块链交互";
  const capabilities = [
    "server-management",
    "telegram-bot",
    "nodejs-development",
    "smart-contracts",
    "bnb-chain",
    "deployment-automation"
  ];
  
  try {
    const tx = await registry.registerAgent(name, description, capabilities, {
      value: ethers.parseEther("0.001") // 注册费
    });
    console.log("Transaction sent:", tx.hash);
    console.log("View on BscScan:", `https://bscscan.com/tx/${tx.hash}`);
    
    const receipt = await tx.wait();
    console.log("\n✅ Registration successful!");
    console.log("Block:", receipt.blockNumber);
    console.log("Gas used:", receipt.gasUsed.toString());
    console.log("View on 8004scan:", `https://www.8004scan.io/address/${wallet.address}`);
  } catch (e) {
    console.error("Registration failed:", e.message);
  }
}

main().catch(console.error);

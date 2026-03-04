const { ethers } = require('ethers');

// 尝试的 ERC-8004 AgentRegistry 合约地址列表
const POSSIBLE_REGISTRY_ADDRESSES = [
  // 候选地址 (常见的 registry 部署模式)
  "0x0000000000000000000000000000000000008004", // 8004 数字对应的地址
  "0x8004000000000000000000000000000000000000", // 8004 前缀地址
];

// ERC-8004 AgentRegistry ABI
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
      {"internalType": "string", "model": "string"},
      {"internalType": "string[]", "name": "capabilities", "type": "string[]"},
      {"internalType": "uint256", "name": "registeredAt", "type": "uint256"},
      {"internalType": "bool", "name": "isActive", "type": "bool"}
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "registrationFee",
    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
    "stateMutability": "view",
    "type": "function"
  }
];

const provider = new ethers.JsonRpcProvider("https://bsc-dataseed.binance.org/");
const wallet = new ethers.Wallet("0xdc64abed396b019867b191c7abcf7cf70b59826defe317cb2835946c7065d939", provider);

async function findRegistry() {
  console.log("=== ERC-8004 Agent Registration ===\n");
  console.log("Wallet:", wallet.address);
  console.log("Network: BSC Mainnet\n");
  
  // 检查余额
  const balance = await provider.getBalance(wallet.address);
  console.log("Balance:", ethers.formatEther(balance), "BNB\n");
  
  // 尝试查找有效的 registry 合约
  let registryAddress = null;
  let registry = null;
  
  for (const addr of POSSIBLE_REGISTRY_ADDRESSES) {
    try {
      const code = await provider.getCode(addr);
      if (code && code !== "0x") {
        console.log(`✅ Found contract at: ${addr}`);
        registryAddress = addr;
        registry = new ethers.Contract(addr, ERC8004_ABI, wallet);
        break;
      }
    } catch (e) {
      // 继续尝试下一个
    }
  }
  
  if (!registry) {
    console.log("❌ No ERC-8004 registry found at known addresses");
    console.log("\n⚠️ 将尝试通过 8004scan.io 的标准流程注册");
    console.log("   但合约地址未在文档中公开\n");
    return await tryManualRegistration();
  }
  
  // 检查是否已注册
  try {
    const agent = await registry.getAgent(wallet.address);
    if (agent[3] > 0 && agent[0] !== "") {
      console.log("✅ Already registered!");
      console.log("  Name:", agent[0]);
      console.log("  Description:", agent[1]);
      console.log("  Registered at:", new Date(Number(agent[3]) * 1000).toISOString());
      return;
    }
  } catch (e) {
    // 未注册，继续
  }
  
  // 获取注册费用
  let fee = ethers.parseEther("0.001");
  try {
    fee = await registry.registrationFee();
    console.log("Registration fee:", ethers.formatEther(fee), "BNB");
  } catch (e) {
    console.log("Using default fee: 0.001 BNB");
  }
  
  // 执行注册
  console.log("\n=== Registering Agent ===");
  const agentData = {
    name: "beiassistant",
    description: "中文AI助手 - Linux服务器、Telegram机器人、智能合约自动化",
    capabilities: ["server-management", "telegram-bot", "nodejs-development", "smart-contracts", "bnb-chain-mcp", "deployment-automation", "troubleshooting"]
  };
  
  console.log("Name:", agentData.name);
  console.log("Capabilities:", agentData.capabilities.join(", "));
  console.log("\nSending transaction...\n");
  
  try {
    const tx = await registry.registerAgent(
      agentData.name,
      agentData.description,
      agentData.capabilities,
      { value: fee }
    );
    
    console.log("Transaction sent:", tx.hash);
    console.log("View on BscScan:", `https://bscscan.com/tx/${tx.hash}`);
    
    const receipt = await tx.wait();
    console.log("\n✅ Registration successful!");
    console.log("Block:", receipt.blockNumber);
    console.log("Gas used:", receipt.gasUsed.toString());
    console.log("\nView on 8004scan:", `https://www.8004scan.io/address/${wallet.address}`);
    
  } catch (e) {
    console.error("❌ Registration failed:", e.message);
    throw e;
  }
}

async function tryManualRegistration() {
  // 由于没有找到合约，我们生成一个标准的 ERC-8004 注册交易
  // 可以通过 Metamask 或者 8004scan.io 界面提交
  
  console.log("=== Manual Registration Data ===\n");
  
  const agentData = {
    name: "beiassistant",
    description: "中文AI助手，专注Linux服务器、Node.js、Telegram机器人、自动化部署和排错。OpenClaw-based AI agent with BNB Chain integration.",
    capabilities: ["server-management", "telegram-bot", "nodejs-development", "smart-contracts", "bnb-chain-mcp", "deployment-automation", "troubleshooting"],
    endpoint: "https://t.me/beiassistant_bot",
    version: "1.0.0"
  };
  
  console.log("Agent Data (JSON):");
  console.log(JSON.stringify(agentData, null, 2));
  console.log("\n");
  
  console.log("=== Registration Instructions ===");
  console.log("1. Visit: https://www.8004scan.io/");
  console.log("2. Connect wallet:", wallet.address);
  console.log("3. Click 'Register Agent'");
  console.log("4. Use the above JSON data");
  console.log("5. Pay registration fee (suggested: 0.001 BNB)");
  console.log("\n=== Direct Interaction ===");
  console.log("If you have the contract address, you can:");
  console.log(`  npx @bnb-chain/mcp@latest`);
  console.log(`  Then use: agent.register`);
  console.log("\nOr provide the registry contract address and I'll send the transaction.");
  
  // 保存注册数据
  const fs = require('fs');
  fs.writeFileSync('/root/.openclaw/workspace/erc8004_register_data.json', JSON.stringify({
    wallet_address: wallet.address,
    network: "BSC Mainnet",
    chain_id: 56,
    timestamp: new Date().toISOString(),
    agent: agentData,
    balance: (await provider.getBalance(wallet.address)).toString()
  }, null, 2));
  
  console.log("\n✅ Registration data saved to: erc8004_register_data.json");
}

findRegistry().catch(console.error);

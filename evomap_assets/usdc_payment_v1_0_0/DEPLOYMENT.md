# 📜 智能合约部署指南

**网络**: Base Sepolia 测试网  
**合约**: AgentRegistry + ServicePaymentEscrow  
**日期**: 2026-02-20

---

## 📋 部署前准备

### 1. 安装依赖

```bash
# 创建项目目录
mkdir -p agentops-contracts
cd agentops-contracts

# 初始化 npm 项目
npm init -y

# 安装 Hardhat
npm install --save-dev hardhat

# 安装 OpenZeppelin
npm install @openzeppelin/contracts

# 安装其他工具
npm install --save-dev @nomicfoundation/hardhat-toolbox
```

### 2. 初始化 Hardhat

```bash
npx hardhat init
# 选择：Create a TypeScript project
# 选择：Add Etherscan verification
```

### 3. 配置 hardhat.config.ts

```typescript
import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import * as dotenv from "dotenv";

dotenv.config();

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.19",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    baseSepolia: {
      url: "https://sepolia.base.org",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 84532
    },
    baseMainnet: {
      url: "https://mainnet.base.org",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 8453
    }
  },
  etherscan: {
    apiKey: {
      baseSepolia: process.env.BASESCAN_API_KEY || ""
    }
  }
};

export default config;
```

### 4. 创建 .env 文件

```bash
# .env
PRIVATE_KEY=0x你的私钥
BASESCAN_API_KEY=你的 Basescan API key
```

---

## 🚀 部署步骤

### Step 1: 复制合约

将合约文件复制到 `contracts/` 目录：
```
contracts/
├── AgentRegistry.sol
└── ServicePaymentEscrow.sol
```

### Step 2: 创建部署脚本

创建 `scripts/deploy.ts`:

```typescript
import { ethers } from "hardhat";

async function main() {
  console.log("🚀 开始部署合约...");
  
  // 获取部署者地址
  const [deployer] = await ethers.getSigners();
  console.log("📝 部署者地址:", deployer.address);
  
  // 检查余额
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("💰 ETH 余额:", ethers.formatEther(balance));
  
  // 部署 AgentRegistry
  console.log("\n📋 部署 AgentRegistry...");
  const AgentRegistry = await ethers.getContractFactory("AgentRegistry");
  const agentRegistry = await AgentRegistry.deploy();
  await agentRegistry.waitForDeployment();
  const agentRegistryAddress = await agentRegistry.getAddress();
  console.log("✅ AgentRegistry 部署地址:", agentRegistryAddress);
  
  // 部署 ServicePaymentEscrow
  console.log("\n💰 部署 ServicePaymentEscrow...");
  const ServicePaymentEscrow = await ethers.getContractFactory("ServicePaymentEscrow");
  const paymentEscrow = await ServicePaymentEscrow.deploy();
  await paymentEscrow.waitForDeployment();
  const paymentEscrowAddress = await paymentEscrow.getAddress();
  console.log("✅ ServicePaymentEscrow 部署地址:", paymentEscrowAddress);
  
  // 等待确认
  console.log("\n⏳ 等待区块确认...");
  await new Promise(resolve => setTimeout(resolve, 20000));
  
  // 输出部署信息
  console.log("\n" + "=".repeat(70));
  console.log("📊 部署完成！");
  console.log("=".repeat(70));
  console.log("网络：Base Sepolia");
  console.log("AgentRegistry:", agentRegistryAddress);
  console.log("ServicePaymentEscrow:", paymentEscrowAddress);
  console.log("=".repeat(70));
  
  // 保存到文件
  const fs = require('fs');
  const deploymentInfo = {
    network: "baseSepolia",
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    contracts: {
      AgentRegistry: agentRegistryAddress,
      ServicePaymentEscrow: paymentEscrowAddress
    }
  };
  
  fs.writeFileSync(
    'deployment-info.json',
    JSON.stringify(deploymentInfo, null, 2)
  );
  console.log("\n💾 部署信息已保存到 deployment-info.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

### Step 3: 获取测试 ETH

1. 访问：https://faucet.circle.com/
2. 连接 MetaMask 钱包
3. 选择 Base Sepolia 网络
4. 请求测试 ETH

### Step 4: 部署合约

```bash
# 部署到 Base Sepolia
npx hardhat run scripts/deploy.ts --network baseSepolia
```

### Step 5: 验证合约 (可选)

```bash
# 验证 AgentRegistry
npx hardhat verify --network baseSepolia <AgentRegistry 地址>

# 验证 ServicePaymentEscrow
npx hardhat verify --network baseSepolia <ServicePaymentEscrow 地址>
```

---

## 🧪 测试合约

### 创建测试脚本

创建 `scripts/test-contracts.ts`:

```typescript
import { ethers } from "hardhat";

async function main() {
  console.log("🧪 开始测试合约...");
  
  const [deployer, user1, user2] = await ethers.getSigners();
  
  // 部署合约
  const AgentRegistry = await ethers.getContractFactory("AgentRegistry");
  const agentRegistry = await AgentRegistry.deploy();
  await agentRegistry.waitForDeployment();
  
  const ServicePaymentEscrow = await ethers.getContractFactory("ServicePaymentEscrow");
  const paymentEscrow = await ServicePaymentEscrow.deploy();
  await paymentEscrow.waitForDeployment();
  
  console.log("✅ 合约部署完成");
  
  // 测试 AgentRegistry
  console.log("\n📋 测试 AgentRegistry...");
  
  // 注册代理
  const tx = await agentRegistry.registerAgent(
    "agent-001",
    "TestAgent",
    "测试代理"
  );
  await tx.wait();
  console.log("✅ 代理注册成功");
  
  // 获取代理信息
  const agent = await agentRegistry.getAgent("agent-001");
  console.log("代理信息:", agent);
  
  // 测试 ServicePaymentEscrow
  console.log("\n💰 测试 ServicePaymentEscrow...");
  console.log("⚠️  需要 USDC 测试代币才能完整测试");
  
  console.log("\n✅ 所有测试完成！");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

运行测试：
```bash
npx hardhat run scripts/test-contracts.ts --network baseSepolia
```

---

## 📊 合约地址记录

### Base Sepolia (测试网)

| 合约 | 地址 | 状态 |
|------|------|------|
| AgentRegistry | 待部署 | ⏳ |
| ServicePaymentEscrow | 待部署 | ⏳ |
| USDC | 0x036CbD53842c5426634e7929541eC2318f3dCF7e | ✅ |

### Base Mainnet (主网)

| 合约 | 地址 | 状态 |
|------|------|------|
| AgentRegistry | 待部署 | ⏳ |
| ServicePaymentEscrow | 待部署 | ⏳ |
| USDC | 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 | ✅ |

---

## 🔗 区块链浏览器

- **Base Sepolia**: https://sepolia.basescan.org/
- **Base Mainnet**: https://basescan.org/

---

## 💡 下一步

1. [ ] 安装 Hardhat 和依赖
2. [ ] 配置 Base Sepolia 网络
3. [ ] 获取测试 ETH
4. [ ] 部署合约
5. [ ] 验证合约
6. [ ] 测试支付流程
7. [ ] 集成到 AgentOps

---

**预计时间**: 1-2 小时  
**成本**: ~0.01 ETH (测试网，免费)

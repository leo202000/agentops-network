#!/bin/bash
# 智能合约部署脚本 - Base Sepolia

echo "🚀 AgentOps Network 合约部署"
echo "="*70
echo ""

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    echo "请运行：curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -"
    exit 1
fi

echo "✅ Node.js: $(node --version)"
echo ""

# 创建项目目录
PROJECT_DIR="agentops-contracts"
echo "📁 创建项目目录：$PROJECT_DIR"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 初始化 npm
echo "📦 初始化 npm 项目..."
npm init -y > /dev/null 2>&1

# 安装依赖
echo "📦 安装 Hardhat..."
npm install --save-dev hardhat

echo "📦 安装 OpenZeppelin..."
npm install @openzeppelin/contracts

echo "📦 安装开发工具..."
npm install --save-dev @nomicfoundation/hardhat-toolbox dotenv

echo ""
echo "✅ 依赖安装完成"
echo ""

# 创建 hardhat.config.js
echo "📝 创建 Hardhat 配置..."
cat > hardhat.config.js << 'EOF'
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
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
EOF

# 创建 .env 示例文件
echo "📝 创建 .env 示例..."
cat > .env.example << 'EOF'
# 钱包私钥 (不要使用主网私钥！)
PRIVATE_KEY=0x你的测试私钥

# Basescan API Key (用于合约验证，可选)
BASESCAN_API_KEY=你的 API 密钥
EOF

# 复制合约文件
echo "📋 复制合约文件..."
mkdir -p contracts
cp ../contracts/AgentRegistry.sol contracts/
cp ../contracts/ServicePaymentEscrow.sol contracts/

echo ""
echo "✅ 项目设置完成！"
echo ""
echo "="*70
echo "📊 下一步:"
echo "1. 编辑 .env 文件，添加你的私钥"
echo "2. 获取 Base Sepolia 测试 ETH: https://faucet.circle.com/"
echo "3. 运行部署：npx hardhat run scripts/deploy.js --network baseSepolia"
echo "="*70

// deploy.js - 智能合约部署脚本
const hre = require("hardhat");

async function main() {
  console.log("🚀 开始部署合约...\n");
  
  // 获取部署者地址
  const [deployer] = await hre.ethers.getSigners();
  console.log("📝 部署者地址:", deployer.address);
  
  // 检查余额
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("💰 ETH 余额:", hre.ethers.formatEther(balance), "\n");
  
  if (balance === 0n) {
    console.log("❌ 余额不足！请获取测试 ETH:");
    console.log("https://faucet.circle.com/");
    return;
  }
  
  // 部署 AgentRegistry
  console.log("📋 部署 AgentRegistry...");
  const AgentRegistry = await hre.ethers.getContractFactory("AgentRegistry");
  const agentRegistry = await AgentRegistry.deploy();
  await agentRegistry.waitForDeployment();
  const agentRegistryAddress = await agentRegistry.getAddress();
  console.log("✅ AgentRegistry 部署地址:", agentRegistryAddress);
  
  // 部署 ServicePaymentEscrow
  console.log("\n💰 部署 ServicePaymentEscrow...");
  const ServicePaymentEscrow = await hre.ethers.getContractFactory("ServicePaymentEscrow");
  const paymentEscrow = await ServicePaymentEscrow.deploy();
  await paymentEscrow.waitForDeployment();
  const paymentEscrowAddress = await paymentEscrow.getAddress();
  console.log("✅ ServicePaymentEscrow 部署地址:", paymentEscrowAddress);
  
  // 等待确认
  console.log("\n⏳ 等待区块确认 (20 秒)...");
  await new Promise(resolve => setTimeout(resolve, 20000));
  
  // 输出部署信息
  console.log("\n" + "=".repeat(70));
  console.log("📊 部署完成！");
  console.log("=".repeat(70));
  console.log("网络：Base Sepolia");
  console.log("AgentRegistry:", agentRegistryAddress);
  console.log("ServicePaymentEscrow:", paymentEscrowAddress);
  console.log("部署者:", deployer.address);
  console.log("时间:", new Date().toISOString());
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
  
  // 创建测试脚本
  console.log("\n📝 创建测试脚本...");
  const testScript = `
// test-deployment.js
const hre = require("hardhat");

async function main() {
  const deploymentInfo = require("./deployment-info.json");
  
  console.log("🧪 测试合约部署...\\n");
  
  // 连接合约
  const AgentRegistry = await hre.ethers.getContractFactory("AgentRegistry");
  const agentRegistry = AgentRegistry.attach(deploymentInfo.contracts.AgentRegistry);
  
  console.log("✅ AgentRegistry:", deploymentInfo.contracts.AgentRegistry);
  
  // 测试注册代理
  console.log("\\n📋 测试注册代理...");
  const tx = await agentRegistry.registerAgent(
    "agent-001",
    "TestAgent",
    "AgentOps Network 测试代理"
  );
  await tx.wait();
  console.log("✅ 代理注册成功！交易:", tx.hash);
  
  // 获取代理信息
  console.log("\\n📊 获取代理信息...");
  const agent = await agentRegistry.getAgent("agent-001");
  console.log("代理名称:", agent.name);
  console.log("描述:", agent.description);
  console.log("所有者:", agent.owner);
  console.log("状态:", agent.isActive ? "活跃" : "非活跃");
  
  console.log("\\n✅ 所有测试完成！");
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
`;
  
  fs.writeFileSync('scripts/test-deployment.js', testScript);
  console.log("✅ 测试脚本已创建：scripts/test-deployment.js");
  
  console.log("\n" + "=".repeat(70));
  console.log("💡 下一步:");
  console.log("1. 验证合约 (可选):");
  console.log("   npx hardhat verify --network baseSepolia", agentRegistryAddress);
  console.log("   npx hardhat verify --network baseSepolia", paymentEscrowAddress);
  console.log("");
  console.log("2. 测试合约:");
  console.log("   npx hardhat run scripts/test-deployment.js --network baseSepolia");
  console.log("=".repeat(70));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

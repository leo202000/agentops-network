// 合约部署脚本 - 部署 AgentRegistry 和 ServicePaymentEscrow
const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("部署账户:", deployer.address);

  // 部署 AgentRegistry
  console.log("正在部署 AgentRegistry...");
  const AgentRegistry = await ethers.getContractFactory("AgentRegistry");
  const registry = await AgentRegistry.deploy();
  await registry.waitForDeployment();
  console.log("AgentRegistry 已部署到:", await registry.getAddress());

  // 部署 ServicePaymentEscrow
  console.log("正在部署 ServicePaymentEscrow...");
  const ServicePaymentEscrow = await ethers.getContractFactory("ServicePaymentEscrow");
  const escrow = await ServicePaymentEscrow.deploy();
  await escrow.waitForDeployment();
  console.log("ServicePaymentEscrow 已部署到:", await escrow.getAddress());

  console.log("\n=== 部署完成 ===");
  console.log("AgentRegistry:", await registry.getAddress());
  console.log("ServicePaymentEscrow:", await escrow.getAddress());
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

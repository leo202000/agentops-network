// MCP Server 调用 ERC-8004 注册
const { spawn } = require('child_process');

const MCP_COMMAND = 'npx';
const MCP_ARGS = ['@bnb-chain/mcp@latest', '--method', 'agent.register'];
const MCP_ENV = {
  ...process.env,
  PRIVATE_KEY: '0xdc64abed396b019867b191c7abcf7cf70b59826defe317cb2835946c7065d939',
  BNB_CHAIN_RPC: 'https://bsc-dataseed.binance.org/',
  BNB_CHAIN_CHAIN_ID: '56'
};

const agentData = {
  name: "beiassistant",
  description: "中文AI助手，专注Linux服务器、Node.js、Telegram机器人、自动化部署和排错。OpenClaw-based AI agent with BNB Chain integration.",
  capabilities: [
    "server-management",
    "telegram-bot",
    "nodejs-development",
    "smart-contracts",
    "bnb-chain-mcp",
    "deployment-automation",
    "troubleshooting"
  ],
  endpoint: "https://t.me/beiassistant_bot"
};

console.log("=== MCP Agent Registration ===\n");
console.log("Starting MCP server...\n");

const mcp = spawn(MCP_COMMAND, ['@bnb-chain/mcp@latest'], {
  env: MCP_ENV,
  stdio: ['pipe', 'pipe', 'pipe']
});

let buffer = '';

mcp.stdout.on('data', (data) => {
  buffer += data.toString();
  console.log('[MCP]', data.toString());
});

mcp.stderr.on('data', (data) => {
  console.error('[MCP Error]', data.toString());
});

mcp.on('close', (code) => {
  console.log(`\nMCP server exited with code ${code}`);
  console.log('\nAgent Data:', JSON.stringify(agentData, null, 2));
  console.log('\n✅ Registration attempt complete');
  console.log('View on 8004scan:', 'https://www.8004scan.io/address/0x694a096016B681Bd3D3Ed11Aeee47fCcc2E10e1a');
});

// Send requests to stdin
setTimeout(() => {
  const request = JSON.stringify({
    method: 'agent.register',
    params: agentData
  });
  mcp.stdin.write(request + '\n');
  mcp.stdin.end();
}, 3000);

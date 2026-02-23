# 💰 USDC 支付网关 - 实现方案

**网络**: Base Mainnet / Base Sepolia  
**代币**: USDC (ERC-20)  
**最后更新**: 2026-02-20

---

## 📋 实施步骤

### Step 1: 获取测试 USDC (Base Sepolia)

**水龙头**:
- https://faucet.circle.com/ - USDC 测试代币
- https://sepolia.base.org/ - Base Sepolia ETH (Gas)

**步骤**:
1. 连接 MetaMask 到 Base Sepolia
2. 获取测试 ETH (Gas)
3. 获取测试 USDC
4. 确认余额

---

### Step 2: USDC 合约地址

**Base Mainnet**:
```
USDC: 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
```

**Base Sepolia**:
```
USDC: 0x036CbD53842c5426634e7929541eC2318f3dCF7e
```

---

### Step 3: Python 支付网关实现

```python
# payment_gateway.py
from web3 import Web3
import json
import os
from dotenv import load_dotenv

load_dotenv()

class USDCPaymentGateway:
    def __init__(self, network='sepolia'):
        # 配置
        config = {
            'sepolia': {
                'rpc': 'https://sepolia.base.org',
                'usdc': '0x036CbD53842c5426634e7929541eC2318f3dCF7e',
                'chain_id': 84532
            },
            'mainnet': {
                'rpc': 'https://mainnet.base.org',
                'usdc': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
                'chain_id': 8453
            }
        }
        
        self.network = network
        self.config = config[network]
        
        # 连接 Web3
        self.w3 = Web3(Web3.HTTPProvider(self.config['rpc']))
        
        # USDC ABI (简化版 ERC20)
        self.usdc_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]
        
        # 合约实例
        self.usdc_contract = self.w3.eth.contract(
            address=self.config['usdc'],
            abi=self.usdc_abi
        )
        
        # 账户
        self.private_key = os.getenv('PRIVATE_KEY')
        if self.private_key:
            self.account = self.w3.eth.account.from_key(self.private_key)
            self.address = self.account.address
        else:
            self.account = None
            self.address = None
    
    def get_balance(self, address=None):
        """获取 USDC 余额"""
        if address is None:
            address = self.address
        
        if not address:
            return None
        
        balance = self.usdc_contract.functions.balanceOf(address).call()
        decimals = self.usdc_contract.functions.decimals().call()
        
        return balance / (10 ** decimals)
    
    def transfer(self, to_address, amount_usdc):
        """转账 USDC"""
        if not self.account:
            return {"error": "No private key configured"}
        
        decimals = self.usdc_contract.functions.decimals().call()
        amount_wei = int(amount_usdc * (10 ** decimals))
        
        # 构建交易
        tx = self.usdc_contract.functions.transfer(
            to_address,
            amount_wei
        ).build_transaction({
            'from': self.address,
            'nonce': self.w3.eth.get_transaction_count(self.address),
            'maxFeePerGas': self.w3.eth.gas_price,
            'maxPriorityFeePerGas': self.w3.eth.gas_price,
            'chainId': self.config['chain_id']
        })
        
        # 签名交易
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        
        # 发送交易
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        return {
            "hash": tx_hash.hex(),
            "from": self.address,
            "to": to_address,
            "amount": amount_usdc,
            "network": self.network
        }
    
    def wait_for_confirmation(self, tx_hash, timeout=60):
        """等待交易确认"""
        try:
            receipt = self.w3.eth.wait_for_transaction_receipt(
                tx_hash,
                timeout=timeout
            )
            
            return {
                "success": receipt['status'] == 1,
                "hash": tx_hash.hex(),
                "block": receipt['blockNumber'],
                "gas_used": receipt['gasUsed']
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_eth_balance(self, address=None):
        """获取 ETH 余额 (用于 Gas)"""
        if address is None:
            address = self.address
        
        if not address:
            return None
        
        balance = self.w3.eth.get_balance(address)
        return self.w3.from_wei(balance, 'ether')
```

---

### Step 4: 服务计费逻辑

```python
# service_pricing.py
from datetime import datetime, timedelta

class ServicePricing:
    """服务定价和计费"""
    
    PRICING = {
        'server_monitoring': {
            'price': 0.1,  # USDC/hour
            'description': '服务器资源监控'
        },
        'auto_mining': {
            'price': 0.05,  # USDC/hour
            'description': '自动挖矿服务'
        },
        'security_audit': {
            'price': 1.0,  # USDC/audit
            'description': '安全审计服务'
        },
        'task_execution': {
            'price': 0.2,  # USDC/task
            'description': '任务执行'
        }
    }
    
    def __init__(self, payment_gateway):
        self.gateway = payment_gateway
        self.active_services = {}
    
    def start_service(self, service_id, service_type, client_address):
        """开始服务"""
        if service_type not in self.PRICING:
            return {"error": "Unknown service type"}
        
        self.active_services[service_id] = {
            'type': service_type,
            'client': client_address,
            'start_time': datetime.utcnow(),
            'last_billing': datetime.utcnow()
        }
        
        return {
            "service_id": service_id,
            "price_per_hour": self.PRICING[service_type]['price'],
            "started_at": self.active_services[service_id]['start_time'].isoformat()
        }
    
    def calculate_usage(self, service_id):
        """计算使用量和费用"""
        if service_id not in self.active_services:
            return {"error": "Service not found"}
        
        service = self.active_services[service_id]
        pricing = self.PRICING[service_type]
        
        now = datetime.utcnow()
        duration = now - service['start_time']
        hours = duration.total_seconds() / 3600
        
        total_cost = hours * pricing['price']
        
        return {
            "service_id": service_id,
            "duration_hours": hours,
            "total_cost_usdc": total_cost,
            "client": service['client']
        }
    
    def bill_client(self, service_id):
        """向客户计费"""
        usage = self.calculate_usage(service_id)
        
        if 'error' in usage:
            return usage
        
        # 发起支付
        result = self.gateway.transfer(
            usage['client'],
            usage['total_cost_usdc']
        )
        
        return result
```

---

### Step 5: .env 配置

```bash
# .env
# Base 链配置
BASE_NETWORK=sepolia
BASE_RPC=https://sepolia.base.org
BASE_CHAIN_ID=84532

# 钱包配置 (用户自己设置)
PRIVATE_KEY=0x你的私钥

# USDC 合约
USDC_CONTRACT=0x036CbD53842c5426634e7929541eC2318f3dCF7e

# 服务配置
SERVICE_MONITOR_INTERVAL=60
AUTO_BILL_THRESHOLD=1.0  # USDC
```

---

## 🧪 测试步骤

### 1. 安装依赖
```bash
pip install web3 python-dotenv
```

### 2. 测试连接
```python
from payment_gateway import USDCPaymentGateway

gateway = USDCPaymentGateway(network='sepolia')

# 检查连接
print(f"Connected: {gateway.w3.is_connected()}")

# 查看余额
if gateway.address:
    print(f"Address: {gateway.address}")
    print(f"ETH Balance: {gateway.get_eth_balance()} ETH")
    print(f"USDC Balance: {gateway.get_balance()} USDC")
```

### 3. 测试转账
```python
# 小额测试
result = gateway.transfer(
    to_address="0x接收地址",
    amount_usdc=0.1
)

print(f"Transaction: {result}")

# 等待确认
confirmation = gateway.wait_for_confirmation(
    bytes.fromhex(result['hash'])
)

print(f"Confirmation: {confirmation}")
```

---

## 📊 服务定价表

| 服务 | 价格 | 计费单位 | 说明 |
|------|------|----------|------|
| 服务器监控 | 0.1 USDC | 每小时 | CPU/内存/磁盘监控 |
| 自动挖矿 | 0.05 USDC | 每小时 | 多平台自动挖矿 |
| 安全审计 | 1.0 USDC | 每次 | ClawGuard 安全检查 |
| 任务执行 | 0.2 USDC | 每次 | 自定义任务执行 |

---

## 🔒 安全注意事项

### 私钥管理
- ⚠️ **永远不要**在代码中硬编码私钥
- ✅ 使用 .env 文件 (权限 600)
- ✅ 使用环境变量
- ✅ 考虑使用硬件钱包

### 交易安全
- ✅ 设置合理的 Gas 价格
- ✅ 验证接收地址
- ✅ 设置交易限额
- ✅ 记录所有交易

### 测试网优先
- ✅ 先在 Sepolia 测试
- ✅ 确认无误后再上主网
- ✅ 小额测试开始

---

## 📝 待办事项

- [ ] 获取 Base Sepolia 测试 ETH
- [ ] 获取测试 USDC
- [ ] 安装 web3 库
- [ ] 测试支付网关连接
- [ ] 测试小额转账
- [ ] 集成到 AgentOps
- [ ] 记录交易到审计日志

---

## 🔗 相关资源

- Base 文档：https://docs.base.org/
- Circle USDC: https://www.circle.com/en/usdc
- Base Faucet: https://faucet.circle.com/
- Web3.py 文档：https://web3py.readthedocs.io/

---

**下一步**: 创建智能合约 + 测试支付流程

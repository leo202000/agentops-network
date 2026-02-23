# 🚰 获取测试 USDC 完整指南

**更新时间**: 2026-02-21 00:28  
**网络**: Base Sepolia 测试网

---

## 📋 步骤 1: 访问 Circle 水龙头

**网址**: https://faucet.circle.com/

### 要求
- 需要 GitHub 账号 (用于防滥用验证)
- 需要 Base Sepolia 钱包地址
- 每个地址每日限额

---

## 💳 步骤 2: 连接钱包

### 使用 MetaMask

1. **打开 MetaMask**
   - 浏览器扩展或手机 App

2. **添加 Base Sepolia 网络** (如果还没有)
   ```
   网络名称：Base Sepolia
   RPC URL: https://sepolia.base.org
   链 ID: 84532
   货币符号：ETH
   区块浏览器：https://sepolia.basescan.org
   ```

3. **复制钱包地址**
   - 点击账户名称复制地址
   - 格式：`0x...` (42 字符)

---

## 🚰 步骤 3: 领取测试代币

### Circle 水龙头

1. **访问**: https://faucet.circle.com/

2. **选择网络**: Base Sepolia

3. **选择代币**: USDC

4. **输入地址**: 粘贴您的钱包地址

5. **GitHub 验证**: 
   - 点击 "Sign in with GitHub"
   - 授权 Circle Faucet

6. **领取**: 
   - 点击 "Send Tokens"
   - 等待交易确认 (约 15-30 秒)

### 限额
- **USDC**: 每日最多领取一次
- **数量**: 通常 10-100 USDC (测试网)

---

## 🔧 备选方案：其他水龙头

### 1. Base 官方水龙头 (获取 ETH 用于 Gas)

**网址**: https://www.alchemy.com/faucets/base-sepolia

```
需要: Alchemy 账号 (免费)
限额：0.1 ETH/日
用途：Gas 费用
```

### 2. Coinbase 水龙头

**网址**: https://www.coinbase.com/faucets/base-ethereum-faucet

```
需要：Coinbase 账号
限额：变动
用途：ETH Gas 费用
```

### 3. QuickNode 水龙头

**网址**: https://faucet.quicknode.com/base/sepolia

```
需要：邮箱验证
限额：变动
用途：ETH + 代币
```

---

## ✅ 步骤 4: 验证到账

### 方法 1: MetaMask 查看

1. 打开 MetaMask
2. 添加 USDC 代币合约地址:
   ```
   0x036CbD53842c5426634e7929541eC2318f3dCF7e
   ```
3. 查看余额

### 方法 2: BaseScan 查看

**网址**: https://sepolia.basescan.org/

1. 输入钱包地址搜索
2. 查看 "Token Holdings" 标签
3. 确认 USDC 余额

---

## 🧪 步骤 5: 测试支付

获取 USDC 后，运行测试脚本：

```bash
cd /root/.openclaw/workspace

# 1. 安装依赖
pip3 install web3 python-dotenv

# 2. 配置私钥
echo "PRIVATE_KEY=0x 你的私钥" > .env

# 3. 运行测试
python3 test_usdc_payment.py
```

### 测试内容
- ✅ 连接 Base Sepolia
- ✅ 查询 USDC 余额
- ✅ 执行测试转账
- ✅ 验证交易确认

---

## ⚠️ 常见问题

### Q1: "Daily limit reached"
**解决**: 等待 24 小时后重试，或使用其他水龙头

### Q2: "Invalid address"
**解决**: 确认使用 Base Sepolia 网络地址，不是主网地址

### Q3: "Transaction failed"
**解决**: 
- 检查 ETH 余额 (需要 Gas)
- 先领取测试 ETH
- 重试交易

### Q4: GitHub 验证失败
**解决**:
- 确认 GitHub 账号已验证邮箱
- 尝试退出重登
- 清除浏览器缓存

---

## 📊 测试网信息

### Base Sepolia

| 项目 | 值 |
|------|-----|
| 网络名称 | Base Sepolia |
| RPC URL | https://sepolia.base.org |
| 链 ID | 84532 |
| 货币符号 | ETH |
| 区块浏览器 | https://sepolia.basescan.org |
| USDC 合约 | 0x036CbD53842c5426634e7929541eC2318f3dCF7e |

### 测试 USDC vs 主网 USDC

| 特性 | 测试网 | 主网 |
|------|--------|------|
| 价值 | $0 (测试用) | $1 (真实) |
| 获取 | 免费水龙头 | 购买/转账 |
| 用途 | 开发测试 | 真实交易 |
| 风险 | 无 | 有 |

---

## 🎯 下一步

获取测试 USDC 后：

1. ✅ 运行 `test_usdc_payment.py` 测试支付
2. ✅ 部署智能合约到 Base Sepolia
3. ✅ 测试合约交互
4. ✅ 集成到 AgentOps Network

---

## 💡 提示

- **保存私钥安全**: 测试网私钥也不要分享
- **记录交易哈希**: 便于调试和文档
- **多领一些**: 测试可能需要多次交易
- **Gas 费用**: Base Sepolia Gas 很便宜，但仍需要 ETH

---

**准备好后告诉我，我会帮您运行测试！** 🚀

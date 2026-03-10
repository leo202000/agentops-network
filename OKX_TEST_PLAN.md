# 🧪 OKX Agent TradeKit 测试计划

**版本**: 1.0  
**创建日期**: 2026-03-10  
**测试周期**: 2-4 周  
**风险等级**: 🔴 高（涉及真实资金）

---

## 📋 测试目标

### 主要目标

1. ✅ 验证安装流程是否正常
2. ✅ 测试配置管理是否安全
3. ✅ 确认模拟盘与实盘隔离
4. ✅ 验证各 Skills 功能是否正常
5. ✅ 测试错误处理机制
6. ✅ 评估 AI 输出准确性
7. ✅ 确认资金安全

### 不测试的内容

- ❌ 大额资金交易（仅测试小额）
- ❌ 提币功能（禁止测试）
- ❌ 杠杆超过 5x（高风险）
- ❌ 期权等复杂衍生品（初期）

---

## 🎯 测试阶段

### 阶段 1: 环境准备（第 1 天）

#### 任务清单

```bash
# 1. 创建 OKX 子账户
# 访问：https://www.okx.com/account/sub-accounts
- [ ] 创建子账户 "agent-test"
- [ ] 记录子账户 UID

# 2. 配置 API Key
# 访问：https://www.okx.com/account/my-api
- [ ] 创建 API Key（仅子账户）
- [ ] 权限设置：
  ✅ 读取权限
  ✅ 交易权限（仅限现货/合约）
  ❌ 提币权限（禁止！）
- [ ] 绑定 IP 白名单（可选但推荐）
- [ ] 记录 API Key 信息（不要发给 AI）

# 3. 安装 CLI 工具
- [ ] npm install -g @okx_ai/okx-trade-cli
- [ ] npm install -g okx-trade-mcp（如需 MCP）
- [ ] 验证安装：okx --version

# 4. 配置文件
- [ ] mkdir -p ~/.okx
- [ ] okx config init（先模拟盘）
- [ ] chmod 600 ~/.okx/config.toml
- [ ] 验证：okx config show
```

#### 验收标准

- [ ] CLI 工具安装成功
- [ ] 配置文件权限正确（600）
- [ ] 模拟盘配置完成
- [ ] 能够查询余额（模拟盘）

---

### 阶段 2: 基础功能测试（第 2-3 天）

#### 测试用例 1: 行情查询（无需 API）

```bash
# 测试命令
okx market ticker BTC-USDT
okx market candles ETH-USDT --bar 1H --limit 10
okx market orderbook BTC-USDT --sz 10

# 预期结果
- [ ] 返回实时价格
- [ ] K 线数据完整
- [ ] 订单簿深度正常
- [ ] 响应时间 < 3 秒

# 记录
实际响应时间：___秒
数据准确性：✅ / ❌
```

---

#### 测试用例 2: 模拟盘余额查询

```bash
# 测试命令
okx --profile demo account balance
okx --profile demo account balance USDT

# 预期结果
- [ ] 返回模拟盘余额
- [ ] 数据准确
- [ ] 响应时间 < 3 秒

# 记录
余额：___ USDT
响应时间：___秒
```

---

#### 测试用例 3: Profile 切换测试

```bash
# 测试命令
okx --profile demo account balance
okx --profile live account balance  # 如果有实盘配置

# 预期结果
- [ ] 能够正确切换
- [ ] 每次响应标注 [profile: demo/live]
- [ ] 不会混淆模拟盘/实盘

# 记录
切换是否正常：✅ / ❌
标注是否正确：✅ / ❌
```

---

### 阶段 3: 交易功能测试（第 4-7 天）

**⚠️ 警告**: 此阶段开始涉及真实资金风险！

#### 测试用例 4: 模拟盘下单（现货）

```bash
# 前置条件
- 模拟盘有足够 USDT 余额（≥1000）

# 测试命令
# 1. 市价买入
okx --profile demo spot place --instId BTC-USDT --side buy --ordType market --sz 0.001

# 2. 查询订单
okx --profile demo spot orders

# 3. 市价卖出
okx --profile demo spot place --instId BTC-USDT --side sell --ordType market --sz 0.001

# 预期结果
- [ ] 订单成功创建
- [ ] 订单状态正确
- [ ] 成交记录可查
- [ ] 余额更新正确

# 记录
订单 ID: ___
成交价：___
手续费：___
```

---

#### 测试用例 5: 限价单测试（现货）

```bash
# 测试命令
# 1. 查询当前价格
okx market ticker BTC-USDT

# 2. 挂限价单（低于市价）
okx --profile demo spot place --instId BTC-USDT --side buy --ordType limit --sz 0.001 --px <当前价*0.95>

# 3. 查询挂单
okx --profile demo spot orders

# 4. 撤单
okx --profile demo spot cancel --instId BTC-USDT --ordId <订单 ID>

# 预期结果
- [ ] 限价单成功创建
- [ ] 挂单状态正确
- [ ] 撤单成功
- [ ] 资金解冻

# 记录
挂单价格：___
撤单时间：___
```

---

#### 测试用例 6: 止盈止损测试（模拟盘）

```bash
# 测试命令
# 1. 买入现货
okx --profile demo spot place --instId BTC-USDT --side buy --ordType market --sz 0.001

# 2. 设置止盈止损
okx --profile demo spot algo place --instId BTC-USDT --side sell --ordType oco --sz 0.001 \
  --tpTriggerPx <买入价*1.1> --tpOrdPx -1 \
  --slTriggerPx <买入价*0.9> --slOrdPx -1

# 3. 查询算法单
okx --profile demo spot algo orders

# 4. 撤销算法单
okx --profile demo spot algo cancel --ordId <算法单 ID>

# 预期结果
- [ ] 止盈止损设置成功
- [ ] 触发价格正确
- [ ] 查询正常
- [ ] 撤销成功

# 记录
TP 价格：___
SL 价格：___
```

---

### 阶段 4: 合约测试（第 8-14 天）

**⚠️ 警告**: 合约风险高于现货！

#### 测试用例 7: 合约开仓（模拟盘）

```bash
# 测试命令
# 1. 设置杠杆（5x）
okx --profile demo swap leverage --instId BTC-USDT-SWAP --lever 5 --mgnMode cross

# 2. 开多仓
okx --profile demo swap place --instId BTC-USDT-SWAP --side buy --ordType market --sz 100 --tdMode cross

# 3. 查询持仓
okx --profile demo swap positions

# 4. 平仓
okx --profile demo swap close --instId BTC-USDT-SWAP --mgnMode cross --posSide long

# 预期结果
- [ ] 杠杆设置成功
- [ ] 开仓成功
- [ ] 持仓信息正确
- [ ] 平仓成功
- [ ] 盈亏计算正确

# 记录
开仓价：___
平仓价：___
盈亏：___ USDT
杠杆：5x
```

---

#### 测试用例 8: 合约止盈止损

```bash
# 测试命令
# 1. 开仓
okx --profile demo swap place --instId BTC-USDT-SWAP --side buy --ordType market --sz 100 --tdMode cross

# 2. 设置止盈止损
okx --profile demo swap algo place --instId BTC-USDT-SWAP --side sell --ordType oco --sz 100 \
  --tdMode cross --posSide long \
  --tpTriggerPx <开仓价*1.1> --tpOrdPx -1 \
  --slTriggerPx <开仓价*0.9> --slOrdPx -1

# 3. 查询
okx --profile demo swap algo orders

# 4. 撤销
okx --profile demo swap algo cancel --ordId <算法单 ID>

# 预期结果
- [ ] 止盈止损设置成功
- [ ] 触发价格正确
- [ ] 查询正常
- [ ] 撤销成功

# 记录
TP: ___
SL: ___
```

---

### 阶段 5: 网格/DCA 测试（第 15-21 天）

#### 测试用例 9: 网格机器人（模拟盘）

```bash
# 测试命令
# 1. 创建网格
okx --profile demo bot grid create --instId BTC-USDT --algoOrdType grid \
  --minPx 90000 --maxPx 100000 --gridNum 10 --quoteSz 100

# 2. 查询网格
okx --profile demo bot grid orders --algoOrdType grid

# 3. 查询详情
okx --profile demo bot grid details --algoOrdType grid --algoId <algoId>

# 4. 停止网格
okx --profile demo bot grid stop --algoId <algoId> --algoOrdType grid --instId BTC-USDT --stopType 2

# 预期结果
- [ ] 网格创建成功
- [ ] 参数设置正确
- [ ] 运行状态正常
- [ ] 停止成功
- [ ] 资金释放

# 记录
网格区间：___ - ___
网格数：___
投入：___ USDT
运行时长：___
收益：___ USDT
```

---

#### 测试用例 10: DCA 机器人（模拟盘）

```bash
# 测试命令
# 1. 创建 DCA
okx --profile demo bot dca create --instId BTC-USDT-SWAP --lever 3 --direction long \
  --initOrdAmt 100 --safetyOrdAmt 50 --maxSafetyOrds 3 \
  --pxSteps 0.03 --pxStepsMult 1 --volMult 1 --tpPct 0.03

# 2. 查询
okx --profile demo bot dca orders

# 3. 详情
okx --profile demo bot dca details --algoId <algoId>

# 4. 停止
okx --profile demo bot dca stop --algoId <algoId>

# 预期结果
- [ ] DCA 创建成功
- [ ] 参数正确
- [ ] 运行正常
- [ ] 停止成功

# 记录
初始订单：___
补仓订单：___
杠杆：3x
```

---

### 阶段 6: AI 交互测试（第 22-28 天）

#### 测试用例 11: 自然语言下单

```bash
# 测试场景（通过 AI 对话）
用户："市价买入 100 USDT 的 BTC"

# 预期 AI 行为
- [ ] 确认 Profile（实盘/模拟盘）
- [ ] 确认参数（币种、金额、订单类型）
- [ ] 执行前再次确认
- [ ] 执行后验证订单
- [ ] 回复包含 [profile: demo/live]

# 记录
AI 是否确认：✅ / ❌
参数是否正确：✅ / ❌
执行是否准确：✅ / ❌
```

---

#### 测试用例 12: 复杂指令测试

```bash
# 测试场景
用户："Long BTC 永续合约 100U，5 倍杠杆，止盈 10%，止损 5%"

# 预期 AI 行为
- [ ] 识别为合约交易
- [ ] 确认 Profile
- [ ] 确认所有参数（金额、杠杆、TP、SL）
- [ ] 分步执行：
  1. 设置杠杆
  2. 开仓
  3. 设置止盈止损
- [ ] 每步验证
- [ ] 最终汇总

# 记录
理解是否正确：✅ / ❌
参数是否完整：✅ / ❌
执行顺序：✅ / ❌
```

---

#### 测试用例 13: 错误处理测试

```bash
# 测试场景 1: 余额不足
用户："买入 10000 USDT 的 BTC"（实际余额不足）

# 预期
- [ ] AI 检查余额
- [ ] 提示余额不足
- [ ] 不执行下单

# 测试场景 2: 无效参数
用户："买入 -1 个 BTC"（负数）

# 预期
- [ ] AI 验证参数
- [ ] 拒绝无效请求
- [ ] 提示正确格式

# 测试场景 3: 401 错误
操作：故意使用错误 API Key

# 预期
- [ ] AI 识别 401 错误
- [ ] 停止所有操作
- [ ] 引导用户更新配置
- [ ] 不要求用户粘贴密钥

# 记录
错误识别：✅ / ❌
处理流程：✅ / ❌
用户引导：✅ / ❌
```

---

## 📊 测试记录表

### 每日测试日志

```markdown
## 第 X 天测试日志 (2026-03-XX)

### 测试内容
- 测试用例编号：___
- 测试场景：___

### 执行结果
- 成功：✅ / 失败：❌
- 响应时间：___秒
- AI 准确性：___/10

### 发现的问题
1. ___
2. ___

### 备注
___
```

---

### 问题追踪表

| ID | 问题描述 | 严重性 | 发现日期 | 状态 | 解决方案 |
|----|---------|--------|---------|------|---------|
| 001 | | 🔴🟡🟢 | | 待处理/已解决 | |
| 002 | | 🔴🟡🟢 | | 待处理/已解决 | |

---

## 🛡️ 安全检查清单

### 每次测试前

- [ ] 确认使用正确的 Profile（demo/live）
- [ ] 检查 API Key 权限（无提币）
- [ ] 确认测试金额（≤100 USDT）
- [ ] 备份配置文件
- [ ] 记录测试开始时间

### 每次测试后

- [ ] 验证订单状态
- [ ] 检查余额变化
- [ ] 记录测试结果
- [ ] 清理测试数据（如需要）
- [ ] 登出/锁定会话

### 每周检查

- [ ] 审查交易日志
- [ ] 检查异常活动
- [ ] 更新测试文档
- [ ] 评估是否进入下一阶段

---

## 📈 测试进度跟踪

### 阶段完成情况

| 阶段 | 计划日期 | 实际开始 | 实际完成 | 状态 |
|------|---------|---------|---------|------|
| 1. 环境准备 | 第 1 天 | | | ⏸️待开始 |
| 2. 基础功能 | 第 2-3 天 | | | ⏸️待开始 |
| 3. 交易功能 | 第 4-7 天 | | | ⏸️待开始 |
| 4. 合约测试 | 第 8-14 天 | | | ⏸️待开始 |
| 5. 网格/DCA | 第 15-21 天 | | | ⏸️待开始 |
| 6. AI 交互 | 第 22-28 天 | | | ⏸️待开始 |

### 测试用例统计

| 类别 | 总数 | 通过 | 失败 | 跳过 | 通过率 |
|------|------|------|------|------|--------|
| 行情查询 | 1 | | | | |
| 账户管理 | 2 | | | | |
| 现货交易 | 3 | | | | |
| 合约交易 | 2 | | | | |
| 网格/DCA | 2 | | | | |
| AI 交互 | 3 | | | | |
| **总计** | **13** | **0** | **0** | **0** | **0%** |

---

## 🎯 退出标准

### 阶段退出条件

**从阶段 N 进入阶段 N+1 需满足**:

1. ✅ 当前阶段所有测试用例通过率 ≥ 90%
2. ✅ 无 🔴 高危问题未解决
3. ✅ 测试文档完整
4. ✅ 资金安全无异常

### 完全停止测试条件

出现以下情况立即停止：

- 🔴 资金损失超过 10 USDT
- 🔴 发现安全漏洞（密钥泄露等）
- 🔴 AI 频繁误操作（≥3 次）
- 🔴 平台异常（无法连接、数据错误）

---

## 📝 测试报告模板

### 最终测试报告

```markdown
# OKX Agent TradeKit 测试报告

**测试周期**: 2026-03-10 至 2026-04-07 (28 天)
**测试人员**: ___
**测试环境**: ___

## 执行摘要

- 测试用例总数：13
- 通过：___ (___%)
- 失败：___ (___%)
- 跳过：___ (___%)

## 主要发现

### 优点
1. ___
2. ___

### 问题
1. ___
2. ___

## 安全评估

- 资金安全：✅ / ❌
- 配置安全：✅ / ❌
- AI 可靠性：___/10

## 建议

### 可以使用
- [ ] 是 / 否
- 条件：___

### 推荐配置
- API 权限：___
- 测试周期：___
- 资金限额：___

## 结论

___
```

---

## 🔗 相关资源

- **测试脚本**: `scripts/okx_test_*.sh`（待创建）
- **配置模板**: `~/.okx/config.toml.example`
- **问题追踪**: GitHub Issues
- **文档**: `OKX_AGENT_TRADEKIT_ANALYSIS.md`
- **代码审计**: `OKX_CODE_AUDIT_REPORT.md`

---

**创建者**: AgentOps Network  
**创建日期**: 2026-03-10  
**下次更新**: 每次测试后

**免责声明**: 测试涉及真实资金风险，请谨慎操作。本测试计划仅供参考，不构成投资建议。

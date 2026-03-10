# 🔍 OKX Agent TradeKit 代码审计报告

**审计日期**: 2026-03-10  
**审计对象**: OKX Agent TradeKit (GitHub: okx/agent-skills)  
**审计范围**: 4 个核心 Skills + CLI 工具  
**风险等级**: 🟡 中等（代码质量良好，需严格配置）

---

## 📊 审计概览

### 审查的文件

| 文件 | 大小 | 类型 | 风险等级 |
|------|------|------|----------|
| `okx-cex-market/SKILL.md` | ~8KB | 行情数据 | 🟢 低 |
| `okx-cex-trade/SKILL.md` | ~19KB | 交易执行 | 🔴 高 |
| `okx-cex-portfolio/SKILL.md` | ~9KB | 账户管理 | 🟡 中 |
| `okx-cex-bot/SKILL.md` | ~9KB | 网格/DCA | 🔴 高 |
| `README.md` | 2KB | 项目说明 | 🟢 低 |

**总计**: ~47KB 代码文档

---

## ✅ 积极发现

### 1. 代码结构清晰 ⭐⭐⭐⭐⭐

```
okx/agent-skills/
├── skills/
│   ├── okx-cex-market/     # 行情数据（无需 API）
│   ├── okx-cex-trade/      # 交易执行（需要 API）
│   ├── okx-cex-portfolio/  # 账户管理（需要 API）
│   └── okx-cex-bot/        # 网格/DCA（需要 API）
├── README.md
├── CONTRIBUTING.md
└── LICENSE (MIT)
```

**评价**: 模块化设计，职责分离清晰。

---

### 2. 安全设计优秀 ⭐⭐⭐⭐⭐

#### 2.1 凭证管理

```bash
# 配置文件位置
~/.okx/config.toml

# 权限建议
chmod 600 ~/.okx/config.toml  # 仅所有者可读写
```

**优点**:
- ✅ 本地存储，不发送给 AI
- ✅ 支持多 Profile（模拟盘/实盘分离）
- ✅ 配置状态可查询（`okx config show`）

#### 2.2 模拟盘隔离

```bash
# 模拟盘模式
okx --profile demo ...

# 实盘模式
okx --profile live ...
```

**优点**:
- ✅ 完全隔离（不同 API Key）
- ✅ 强制确认机制
- ✅ 每次响应标注 `[profile: demo/live]`

#### 2.3 权限控制

| Skill | 权限需求 | 最小化设计 |
|-------|---------|-----------|
| okx-cex-market | ⚪ 无需 API | ✅ 公开数据 |
| okx-cex-portfolio | 🟡 只读 API | ✅ 仅查询 |
| okx-cex-trade | 🔴 交易 API | ✅ 按需开启 |
| okx-cex-bot | 🔴 交易 API | ✅ 按需开启 |

**评价**: 遵循最小权限原则。

---

### 3. 错误处理完善 ⭐⭐⭐⭐

#### 3.1 401 认证错误处理

```markdown
### Handling 401 Authentication Errors

If any command returns a 401 / authentication error:
1. **Stop immediately** — do not retry the same command
2. Inform the user: "Authentication failed (401)..."
3. Guide the user to update credentials by editing the file directly
4. After the user confirms, run `okx config show` to verify
5. Only then retry the original operation
```

**评价**: 处理流程清晰，避免凭证泄露。

#### 3.2 Profile 确认机制

```markdown
**Resolution rules:**
1. Current message intent clear → use it, inform user
2. Current message has no explicit declaration → check context
   - Found → use it, inform user
   - Not found → ask: "Live (实盘) or Demo (模拟盘)?" — wait for answer
```

**评价**: 双重确认，防止误操作。

---

### 4. 文档质量高 ⭐⭐⭐⭐⭐

**每个 Skill 包含**:
- ✅ 前置条件（Prerequisites）
- ✅ 凭证检查流程（Credential & Profile Check）
- ✅ 快速开始（Quickstart）
- ✅ 命令索引（Command Index）
- ✅ 跨技能协作（Cross-Skill Workflows）
- ✅ 操作流程（Operation Flow）

**示例完整性**:
```bash
# 现货市价买入
okx spot place --instId BTC-USDT --side buy --ordType market --sz 0.01

# 合约开仓 + 止盈止损
okx swap place --instId BTC-USDT-SWAP --side buy --ordType market --sz 1 \
  --tdMode cross --posSide long
okx swap algo place --instId BTC-USDT-SWAP --side sell \
  --ordType oco --sz 1 --tdMode cross --posSide long \
  --tpTriggerPx 105000 --tpOrdPx -1 \
  --slTriggerPx 88000 --slOrdPx -1
```

---

## ⚠️ 潜在风险点

### 风险 1: AI 误操作（无法完全避免） 🔴

**问题**: 即使有完善的确认机制，AI 仍可能：
- 理解错误用户意图
- 生成错误的参数
- 忽略市场条件变化

**缓解措施**:
- ✅ 强制 Profile 确认
- ✅ 写操作前参数确认
- ✅ 执行后验证
- ⚠️ 仍需用户独立核实

**建议**:
```bash
# 启用只读模式测试
okx --read-only ...

# 使用模拟盘
okx --profile demo ...

# 小额测试
# 子账户只放 100-500 USDT
```

---

### 风险 2: 配置文件未加密 🟡

**问题**: `~/.okx/config.toml` 以明文存储 API Key

```toml
[profiles.demo]
api_key = "your-api-key"
secret_key = "your-secret-key"
passphrase = "your-passphrase"
```

**风险**:
- 恶意软件可读取
- 系统被入侵后泄露
- 备份时可能意外暴露

**缓解措施**:
```bash
# 1. 设置文件权限
chmod 600 ~/.okx/config.toml

# 2. 使用子账户（非主账户）

# 3. 禁用提币权限

# 4. 设置 IP 白名单

# 5. 定期轮换密钥（90 天）
```

---

### 风险 3: 依赖第三方 LLM 🟡

**问题**: 技能依赖 Claude/GPT 等外部模型

**风险**:
- 模型可能产生幻觉
- 训练数据可能过时
- 无法控制模型行为

**缓解措施**:
- ✅ 所有命令本地执行
- ✅ 密钥不发送给 LLM
- ✅ 用户最终确认

---

### 风险 4: CLI 工具未审计 🟡

**问题**: 我们审查的是 Skill 文档，而非 CLI 源码

**CLI 包**: `@okx_ai/okx-trade-cli` (npm)

**需要审查**:
```bash
# 1. 下载源码
npm view @okx_ai/okx-trade-cli repository

# 2. 审计依赖
npm audit

# 3. 检查网络请求
grep -r "fetch\|axios" node_modules/@okx_ai/okx-trade-cli/

# 4. 检查密钥处理
grep -r "api_key\|secret_key" node_modules/@okx_ai/okx-trade-cli/
```

**建议**: OKX 应开源 CLI 工具代码。

---

## 🔍 详细代码审查

### 1. okx-cex-market（行情数据）

**审查结果**: ✅ 安全

| 检查项 | 状态 | 说明 |
|--------|------|------|
| API Key 需求 | ⚪ 无需 | 公开数据 |
| 网络请求 | ✅ 只读 | 查询行情 |
| 数据泄露风险 | 🟢 无 | 不发送敏感信息 |
| 权限范围 | 🟢 最小 | 仅查询 |

**推荐**: ✅ 可以放心使用

---

### 2. okx-cex-trade（交易执行）

**审查结果**: ⚠️ 高风险（需严格配置）

| 检查项 | 状态 | 说明 |
|--------|------|------|
| API Key 需求 | 🔴 需要 | 交易权限 |
| 写操作 | 🔴 是 | 下单/撤单/修改 |
| 确认机制 | ✅ 完善 | Profile + 参数双重确认 |
| 错误处理 | ✅ 完善 | 401 错误处理流程 |
| 验证流程 | ✅ 完善 | 执行后验证 |

**关键安全设计**:
```markdown
### Credential & Profile Check

**Step A**: Verify credentials
- `okx config show` → 验证配置状态

**Step B**: Confirm profile (required)
- `live` (实盘) 或 `demo` (模拟盘)
- 必须显式确认，不能隐式添加

**Handling 401 Errors**:
1. Stop immediately
2. Inform user
3. Guide to edit config file (not paste in chat)
4. Verify with `okx config show`
5. Retry only after confirmation
```

**推荐**: ⚠️ 严格测试后再使用

---

### 3. okx-cex-portfolio（账户管理）

**审查结果**: 🟡 中等风险

| 检查项 | 状态 | 说明 |
|--------|------|------|
| API Key 需求 | 🟡 需要 | 只读权限即可 |
| 敏感信息 | 🟡 是 | 余额/持仓/盈亏 |
| 写操作 | ⚠️ 少量 | 转账/切换模式 |
| 确认机制 | ✅ 完善 | 转账前确认 Profile |

**关键命令**:
```bash
# 只读（安全）
okx account balance
okx account positions
okx account fees

# 写操作（需确认）
okx account transfer --ccy USDT --amt 100 --from 18 --to 6
okx account set-position-mode <mode>
```

**推荐**: ⚠️ 使用只读 API Key

---

### 4. okx-cex-bot（网格/DCA）

**审查结果**: 🔴 高风险（需严格配置）

| 检查项 | 状态 | 说明 |
|--------|------|------|
| API Key 需求 | 🔴 需要 | 交易 + 算法权限 |
| 资金管理 | 🔴 是 | 自动投入资金 |
| 风险等级 | 🔴 高 | 可能亏损 |
| 确认机制 | ✅ 完善 | Profile + 参数确认 |

**关键设计**:
```markdown
**Rules:**
1. `--profile` is **required** on every authenticated command
2. Every response must append: `[profile: live]` or `[profile: demo]`
3. For bot create/stop operations, **profile must be explicitly confirmed**
```

**推荐**: 🔴 仅使用模拟盘测试

---

## 📋 安全检查清单

### 安装前

- [x] ✅ GitHub 仓库已审查
- [x] ✅ 代码结构清晰
- [x] ✅ 安全设计完善
- [ ] ⚠️ CLI 源码未审计
- [ ] ⚠️ 需创建专用子账户
- [ ] ⚠️ 需配置 API 权限（禁用提币）

### 安装后

```bash
# 1. 检查 CLI 依赖
npm install -g @okx_ai/okx-trade-cli
npm audit  # 检查依赖安全

# 2. 配置文件权限
chmod 600 ~/.okx/config.toml

# 3. 模拟盘测试
okx --profile demo account balance

# 4. 只读模式测试
okx --read-only market ticker BTC-USDT
```

### 使用中

- [ ] 每次交易前独立核实
- [ ] 使用模拟盘测试 1-2 周
- [ ] 子账户只放少量资金
- [ ] 定期检查交易日志
- [ ] 每 90 天轮换 API Key

---

## 🎯 与之前分析的对比

| 维度 | 官网声明 | 代码实现 | 一致性 |
|------|---------|---------|--------|
| 本地运行 | ✅ 是 | ✅ 是 | ✅ 一致 |
| 密钥本地存储 | ✅ 是 | ✅ 是 | ✅ 一致 |
| 模拟盘隔离 | ✅ 是 | ✅ 是 | ✅ 一致 |
| 只读模式 | ✅ 是 | ⚠️ 文档提到 | ⚠️ 需验证 |
| 完全开源 | ✅ 是 | ⚠️ Skills 开源，CLI 未开源 | ⚠️ 部分一致 |
| 四层安全 | ✅ 是 | ✅ 是 | ✅ 一致 |

**评价**: 官网声明与代码实现基本一致。

---

## 📊 综合评分

| 维度 | 得分 | 说明 |
|------|------|------|
| **代码质量** | 9/10 | 结构清晰，文档完善 |
| **安全设计** | 9/10 | 多重确认，模拟盘隔离 |
| **透明度** | 8/10 | Skills 开源，CLI 未开源 |
| **错误处理** | 9/10 | 401 错误处理完善 |
| **权限控制** | 9/10 | 最小权限原则 |
| **总体评分** | **8.8/10** | 🟢 优秀（需严格配置） |

---

## 💡 最终建议

### ✅ 可以使用，但必须：

1. **创建专用子账户**
   - 不要使用主账户
   - 子账户只放 100-500 USDT 测试

2. **API Key 权限设置**
   ```
   ✅ 读取权限 - 允许
   ✅ 交易权限 - 按需开启
   ❌ 提币权限 - 绝对禁止！
   ```

3. **使用模拟盘测试**
   ```bash
   okx --profile demo ...  # 至少测试 1-2 周
   ```

4. **配置文件安全**
   ```bash
   chmod 600 ~/.okx/config.toml
   ```

5. **独立核实**
   - 每笔交易前确认参数
   - 不盲目信任 AI 输出

---

## 🔗 相关资源

- **GitHub**: https://github.com/okx/agent-skills
- **NPM 包**: https://www.npmjs.com/package/@okx_ai/okx-trade-cli
- **官方文档**: https://www.okx.com/zh-hans/agent-tradekit
- **安全配置指南**: /docs-v5/agent_zh/

---

**审计师**: AgentOps Network  
**审计日期**: 2026-03-10  
**审计方法**: 静态代码分析 + 文档审查  
**限制**: 未审计 CLI 源码（闭源）

**免责声明**: 本审计仅供参考，不构成投资或安全建议。使用前请自行评估风险。

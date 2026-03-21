# 🤖 社区运营自动化配置

**配置时间**: 2026-03-21 08:30  
**状态**: ✅ 已配置

---

## 📋 定时任务配置

### Moltbook 社区运营

**频率**: 一天 3 次  
**时间**: 
- 早上 9:00
- 下午 14:00
- 晚上 20:00

**任务内容**:
- ✅ 点赞 (5 个)
- ✅ 评论 (0-3 条)
- ✅ 状态检查

**脚本**: `moltbook-daily.sh`

**Cron 配置**:
```bash
# Moltbook 社区运营 - 一天 3 次
0 9 * * * cd /root/.openclaw/workspace && ./moltbook-daily.sh >> /var/log/openclaw-moltbook.log 2>&1
0 14 * * * cd /root/.openclaw/workspace && ./moltbook-daily.sh >> /var/log/openclaw-moltbook.log 2>&1
0 20 * * * cd /root/.openclaw/workspace && ./moltbook-daily.sh >> /var/log/openclaw-moltbook.log 2>&1
```

---

### ClawMarket 活跃

**频率**: 一天 3 次  
**时间**:
- 早上 9:30
- 下午 14:30
- 晚上 20:30

**任务内容**:
- ✅ 浏览市场
- ✅ 检查积分
- ✅ 查看推荐
- ✅ 钱包状态

**脚本**: `clawmarket-daily.sh`

**Cron 配置**:
```bash
# ClawMarket 活跃 - 一天 3 次
30 9 * * * cd /root/.openclaw/workspace && ./clawmarket-daily.sh >> /var/log/openclaw-clawmarket.log 2>&1
30 14 * * * cd /root/.openclaw/workspace && ./clawmarket-daily.sh >> /var/log/openclaw-clawmarket.log 2>&1
30 20 * * * cd /root/.openclaw/workspace && ./clawmarket-daily.sh >> /var/log/openclaw-clawmarket.log 2>&1
```

---

## 🎯 特殊任务执行

### 手动执行单个任务

#### Moltbook 特殊任务

```bash
# 额外点赞
cd /root/.openclaw/workspace
./moltbook-daily.sh --extra-likes 10

# 额外评论
./moltbook-daily.sh --extra-comments 5

# 发布新帖子
./moltbook-daily.sh --post "新的帖子内容"

# 查看账号详情
./moltbook-daily.sh --account-info
```

#### ClawMarket 特殊任务

```bash
# 购买代理
cd /root/.openclaw/workspace
./clawmarket-daily.sh --buy <代理地址>

# 出售代理
./clawmarket-daily.sh --sell <代理地址>

# 查看持仓
./clawmarket-daily.sh --portfolio

# 快速购买 (带重试)
python3 clawmarket_quick_buy.py
```

---

## 📊 日志管理

### 日志位置

| 日志 | 位置 |
|------|------|
| Moltbook | `/var/log/openclaw-moltbook.log` |
| ClawMarket | `/var/log/openclaw-clawmarket.log` |
| 详细日志 | `./memory/moltbook/` |
| 详细日志 | `./memory/clawmarket/` |

### 查看日志

```bash
# 查看最新日志
tail -f /var/log/openclaw-moltbook.log
tail -f /var/log/openclaw-clawmarket.log

# 查看今日日志
cat ./memory/moltbook/moltbook-$(date '+%Y-%m-%d').log
cat ./memory/clawmarket/clawmarket-$(date '+%Y-%m-%d').log

# 查看历史记录
ls -la ./memory/moltbook/
ls -la ./memory/clawmarket/
```

---

## 🔧 配置要求

### 环境变量

**编辑**: `/root/.openclaw/workspace/.env`

```bash
# Moltbook 配置
MOLT_API_KEY=your_moltbook_api_key

# ClawMarket 配置
CLAWMARKET_PRIVATE_KEY=your_private_key
```

### 权限设置

```bash
# 设置脚本执行权限
chmod +x /root/.openclaw/workspace/moltbook-daily.sh
chmod +x /root/.openclaw/workspace/clawmarket-daily.sh

# 设置日志文件权限
chmod 644 /var/log/openclaw-*.log
```

---

## 📈 监控和告警

### 监控脚本

**文件**: `monitor-community.sh`

```bash
#!/bin/bash
# 社区运营监控

# 检查 Moltbook 是否执行
MOLT_LOG="/var/log/openclaw-moltbook.log"
if [ -f "$MOLT_LOG" ]; then
    LAST_RUN=$(tail -1 "$MOLT_LOG" | grep -o "[0-9-]* [0-9:]*")
    echo "Moltbook 最后运行：$LAST_RUN"
else
    echo "❌ Moltbook 日志不存在"
fi

# 检查 ClawMarket 是否执行
CLAW_LOG="/var/log/openclaw-clawmarket.log"
if [ -f "$CLAW_LOG" ]; then
    LAST_RUN=$(tail -1 "$CLAW_LOG" | grep -o "[0-9-]* [0-9:]*")
    echo "ClawMarket 最后运行：$LAST_RUN"
else
    echo "❌ ClawMarket 日志不存在"
fi
```

### 告警配置

**Cron 监控**:
```bash
# 每天检查是否执行
0 21 * * * /root/.openclaw/workspace/monitor-community.sh >> /var/log/openclaw-community-monitor.log 2>&1
```

---

## 🎯 使用示例

### 日常执行 (自动)

系统会自动在以下时间执行：
- 09:00 - Moltbook 早间运营
- 09:30 - ClawMarket 早间活跃
- 14:00 - Moltbook 午后运营
- 14:30 - ClawMarket 午后活跃
- 20:00 - Moltbook 晚间运营
- 20:30 - ClawMarket 晚间活跃

### 手动执行 (特殊需求)

```bash
# Moltbook 额外运营
./moltbook-daily.sh --extra-likes 10

# ClawMarket 特殊购买
./clawmarket-daily.sh --buy 0x1234567890abcdef

# 查看今日执行记录
cat ./memory/moltbook/moltbook-$(date '+%Y-%m-%d').log
cat ./memory/clawmarket/clawmarket-$(date '+%Y-%m-%d').log
```

---

## 📝 任务记录模板

### Moltbook 日志模板

```markdown
# Moltbook 运营日志 - YYYY-MM-DD HH:MM

## 执行任务
- ✅ 点赞：X 个
- ✅ 评论：X 个
- ✅ 状态检查：完成

## 账号状态
- Karma: X
- 关注：X
- 累计：X 赞 / X 评论 / X 帖

## 备注
- [特殊操作记录]
```

### ClawMarket 日志模板

```markdown
# ClawMarket 活跃日志 - YYYY-MM-DD HH:MM

## 执行任务
- ✅ 浏览市场
- ✅ 检查积分
- ✅ 查看推荐
- ✅ 钱包状态

## 钱包信息
- 地址：0x...
- 类型：HD 钱包 (BIP44)
- 状态：正常

## 交易记录
- [交易哈希]
```

---

## 🔍 故障排查

### 问题 1: 脚本不执行

**检查**:
```bash
# 检查 Cron 服务
systemctl status cron

# 检查 Cron 任务
crontab -l | grep moltbook
crontab -l | grep clawmarket

# 检查脚本权限
ls -la ./moltbook-daily.sh
ls -la ./clawmarket-daily.sh
```

**解决**:
```bash
# 重新添加 Cron 任务
./setup-community-cron.sh

# 设置权限
chmod +x ./moltbook-daily.sh
chmod +x ./clawmarket-daily.sh
```

### 问题 2: API 密钥错误

**检查**:
```bash
grep "MOLT_API_KEY" .env
grep "CLAWMARKET_PRIVATE_KEY" .env
```

**解决**:
```bash
vim .env
# 更新密钥
source .env
```

### 问题 3: 日志不生成

**检查**:
```bash
ls -la /var/log/openclaw-*.log
ls -la ./memory/moltbook/
ls -la ./memory/clawmarket/
```

**解决**:
```bash
# 创建目录
mkdir -p ./memory/moltbook
mkdir -p ./memory/clawmarket
mkdir -p /var/log

# 手动运行测试
./moltbook-daily.sh
./clawmarket-daily.sh
```

---

## 💡 最佳实践

### 1. 定期检查
- 每周查看日志
- 每月审查效果
- 根据反馈调整策略

### 2. 灵活调整
- 特殊活动增加频次
- 低峰期减少频次
- 根据效果优化时间

### 3. 记录特殊操作
- 额外点赞/评论
- 特殊购买/出售
- 账号状态变化

### 4. 安全注意
- 私钥通过环境变量管理
- 定期更换 API 密钥
- 不在日志中记录敏感信息

---

**配置完成时间**: 2026-03-21 08:30  
**下次审查**: 2026-03-28 (周审查)

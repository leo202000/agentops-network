# ✅ 社区运营自动化配置完成报告

**完成时间**: 2026-03-21 08:35  
**状态**: ✅ 配置完成，已启用

---

## 📊 配置完成情况

### Moltbook 社区运营

**频率**: 一天 3 次  
**时间**: 
- ✅ 09:00 - 早间运营
- ✅ 14:00 - 午后运营
- ✅ 20:00 - 晚间运营

**任务内容**:
- ✅ 点赞 (5 个/次)
- ✅ 评论 (0-3 条/次)
- ✅ 状态检查

**脚本**: `moltbook-daily.sh`

---

### ClawMarket 活跃

**频率**: 一天 3 次  
**时间**:
- ✅ 09:30 - 早间活跃
- ✅ 14:30 - 午后活跃
- ✅ 20:30 - 晚间活跃

**任务内容**:
- ✅ 浏览市场
- ✅ 检查积分
- ✅ 查看推荐
- ✅ 钱包状态

**脚本**: `clawmarket-daily.sh`

---

## 🎯 特殊任务执行

### 脚本**: `community-special.sh`

**Moltbook 特殊任务**:
```bash
# 额外点赞
./community-special.sh moltbook --extra-likes 10

# 额外评论
./community-special.sh moltbook --extra-comments 5

# 发布帖子
./community-special.sh moltbook --post "帖子内容"

# 查看账号
./community-special.sh moltbook --account-info
```

**ClawMarket 特殊任务**:
```bash
# 购买代理
./community-special.sh clawmarket --buy <代理地址>

# 查看持仓
./community-special.sh clawmarket --portfolio

# 快速购买
./community-special.sh clawmarket --quick-buy
```

**通用命令**:
```bash
# 查看运营状态
./community-special.sh status

# 查看今日日志
./community-special.sh logs

# 查看帮助
./community-special.sh help
```

---

## 📁 创建的文件

| 文件 | 大小 | 用途 | 状态 |
|------|------|------|------|
| `moltbook-daily.sh` | 1.2KB | Moltbook 日常运营 | ✅ |
| `clawmarket-daily.sh` | 1.5KB | ClawMarket 日常活跃 | ✅ |
| `community-special.sh` | 3.6KB | 特殊任务执行 | ✅ |
| `COMMUNITY_AUTOMATION.md` | 5.1KB | 完整配置文档 | ✅ |

**总计**: 4 个文件，11.4KB

---

## ⏰ Cron 定时任务

### 已配置的任务

```bash
# Moltbook 社区运营 - 一天 3 次
0 9 * * * ./moltbook-daily.sh >> /var/log/openclaw-moltbook.log 2>&1
0 14 * * * ./moltbook-daily.sh >> /var/log/openclaw-moltbook.log 2>&1
0 20 * * * ./moltbook-daily.sh >> /var/log/openclaw-moltbook.log 2>&1

# ClawMarket 活跃 - 一天 3 次
30 9 * * * ./clawmarket-daily.sh >> /var/log/openclaw-clawmarket.log 2>&1
30 14 * * * ./clawmarket-daily.sh >> /var/log/openclaw-clawmarket.log 2>&1
30 20 * * * ./clawmarket-daily.sh >> /var/log/openclaw-clawmarket.log 2>&1
```

**总计**: 6 个定时任务

---

## 📊 日志管理

### 日志位置

| 类型 | 位置 |
|------|------|
| Moltbook 日志 | `/var/log/openclaw-moltbook.log` |
| ClawMarket 日志 | `/var/log/openclaw-clawmarket.log` |
| Moltbook 详情 | `./memory/moltbook/moltbook-YYYY-MM-DD.log` |
| ClawMarket 详情 | `./memory/clawmarket/clawmarket-YYYY-MM-DD.log` |

### 查看日志

```bash
# 实时查看
tail -f /var/log/openclaw-moltbook.log
tail -f /var/log/openclaw-clawmarket.log

# 查看今日
cat ./memory/moltbook/moltbook-$(date '+%Y-%m-%d').log
cat ./memory/clawmarket/clawmarket-$(date '+%Y-%m-%d').log
```

---

## 🎯 执行时间表

### 每日自动执行

| 时间 | 任务 | 脚本 |
|------|------|------|
| 09:00 | Moltbook 早间运营 | moltbook-daily.sh |
| 09:30 | ClawMarket 早间活跃 | clawmarket-daily.sh |
| 14:00 | Moltbook 午后运营 | moltbook-daily.sh |
| 14:30 | ClawMarket 午后活跃 | clawmarket-daily.sh |
| 20:00 | Moltbook 晚间运营 | moltbook-daily.sh |
| 20:30 | ClawMarket 晚间活跃 | clawmarket-daily.sh |

**每日执行**: 6 次自动任务

---

## 📈 预期效果

### Moltbook 社区运营

| 指标 | 当前 | 每日目标 | 每周目标 |
|------|------|---------|---------|
| 点赞 | 380 | +15 | +105 |
| 评论 | 19 | +3-9 | +21-63 |
| 帖子 | 2 | 按需 | 按需 |
| Karma | 30 | +1-3 | +7-21 |

### ClawMarket 活跃

| 指标 | 状态 | 检查频率 |
|------|------|---------|
| 钱包状态 | ✅ 正常 | 一天 3 次 |
| 市场浏览 | ✅ 正常 | 一天 3 次 |
| 积分检查 | ✅ 正常 | 一天 3 次 |
| 推荐查看 | ✅ 正常 | 一天 3 次 |

---

## 🔧 配置要求

### 环境变量

**文件**: `/root/.openclaw/workspace/.env`

```bash
# Moltbook 配置
MOLT_API_KEY=your_moltbook_api_key

# ClawMarket 配置
CLAWMARKET_PRIVATE_KEY=your_private_key
```

### 权限设置

```bash
# 脚本权限 (已设置)
chmod +x moltbook-daily.sh
chmod +x clawmarket-daily.sh
chmod +x community-special.sh

# 日志权限
chmod 644 /var/log/openclaw-*.log
```

---

## 🎯 使用方式

### 自动执行 (已配置)

系统会自动在指定时间执行，无需手动操作。

### 手动执行 (特殊需求)

```bash
# 查看状态
./community-special.sh status

# 额外点赞
./community-special.sh moltbook --extra-likes 10

# 购买代理
./community-special.sh clawmarket --buy 0x1234567890abcdef

# 查看日志
./community-special.sh logs
```

### 监控执行

```bash
# 查看 Cron 任务
crontab -l | grep -E "moltbook|clawmarket"

# 查看执行日志
tail -f /var/log/openclaw-moltbook.log
tail -f /var/log/openclaw-clawmarket.log

# 检查今日执行次数
grep -c "$(date '+%Y-%m-%d')" /var/log/openclaw-*.log
```

---

## 📝 任务更新

### 已完成任务

| 任务 | 优先级 | 状态 | 完成时间 |
|------|--------|------|---------|
| 安全修复 | 🔴 高 | ✅ 完成 | 08:25 |
| Moltbook+ClawMarket 定时 | 🟡 中 | ✅ 完成 | 08:35 |

### 进行中任务

| 任务 | 优先级 | 状态 | 进度 |
|------|--------|------|------|
| 即梦 API 问题 | 🔴 高 | 🔄 进行中 | 70% |

---

## 💡 最佳实践

### 1. 定期检查
- 每天查看执行日志
- 每周审查运营效果
- 每月优化策略

### 2. 灵活调整
- 特殊活动增加频次
- 低峰期减少频次
- 根据效果调整时间

### 3. 记录特殊操作
- 使用 special 脚本执行特殊任务
- 自动记录到日志
- 便于后续审查

### 4. 安全第一
- 私钥通过环境变量管理
- 不在日志中记录敏感信息
- 定期更换 API 密钥

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
ls -la *.sh
```

### 问题 2: 日志不生成

**检查**:
```bash
# 检查日志目录
ls -la ./memory/moltbook/
ls -la ./memory/clawmarket/

# 手动运行测试
./moltbook-daily.sh
./clawmarket-daily.sh
```

### 问题 3: API 错误

**检查**:
```bash
# 检查环境变量
grep "MOLT_API_KEY" .env
grep "CLAWMARKET_PRIVATE_KEY" .env

# 测试 API 连接
./moltbook-daily.sh --verbose
```

---

## 🎉 总结

**社区运营自动化配置完成！**

### 已实现
- ✅ Moltbook 一天 3 次自动运营
- ✅ ClawMarket 一天 3 次自动活跃
- ✅ 特殊任务手动执行脚本
- ✅ 完整的日志系统
- ✅ Cron 定时任务配置

### 自动化程度
- **完全自动**: 日常运营、日志记录
- **半自动**: 特殊任务 (一键执行)
- **需手动**: 策略调整、效果审查

### 下一步
1. 监控今日执行情况
2. 收集运营数据
3. 周审查时评估效果
4. 根据效果优化策略

---

**配置完成时间**: 2026-03-21 08:35  
**首次执行**: 2026-03-21 09:00 (Moltbook), 09:30 (ClawMarket)  
**下次审查**: 2026-03-28 (周审查)

# 🤖 自动运行配置指南

**说明**: 配置会话启动脚本自动运行

---

## 方案 1: Bash 别名 (推荐)

### 步骤 1: 添加到 .bashrc

```bash
# 编辑 .bashrc
vim ~/.bashrc

# 添加别名
alias oc-start='cd /root/.openclaw/workspace && ./start-session.sh'
alias oc-skill='cd /root/.openclaw/workspace && ./skills/update-skills-list.sh'
alias oc-review='cd /root/.openclaw/workspace && vim WEEKLY_REVIEW.md'

# 使配置生效
source ~/.bashrc
```

### 步骤 2: 使用方式

```bash
# 启动会话
oc-start

# 更新技能清单
oc-skill

# 每周审查
oc-review
```

---

## 方案 2: Systemd 服务 (高级)

### 步骤 1: 创建服务文件

```bash
sudo vim /etc/systemd/system/openclaw-session.service

[Unit]
Description=OpenClaw Session Startup
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=/root/.openclaw/workspace
ExecStart=/root/.openclaw/workspace/start-session.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 步骤 2: 创建定时器

```bash
sudo vim /etc/systemd/system/openclaw-session.timer

[Unit]
Description=Run OpenClaw Session Startup
Requires=openclaw-session.service

[Timer]
OnBootSec=1min
OnUnitActiveSec=1h
Unit=openclaw-session.service

[Install]
WantedBy=timers.target
```

### 步骤 3: 启用服务

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启用定时器
sudo systemctl enable openclaw-session.timer
sudo systemctl start openclaw-session.timer

# 查看状态
sudo systemctl status openclaw-session.timer
```

---

## 方案 3: Cron 定时任务

### 步骤 1: 编辑 crontab

```bash
crontab -e
```

### 步骤 2: 添加定时任务

```bash
# 每小时运行一次 (仅更新技能清单)
0 * * * * cd /root/.openclaw/workspace && ./skills/update-skills-list.sh >> /var/log/openclaw-skills.log 2>&1

# 每天上午 9 点运行完整检查
0 9 * * * cd /root/.openclaw/workspace && ./start-session.sh >> /var/log/openclaw-session.log 2>&1

# 每周日晚上 8 点提醒每周审查
0 20 * * 0 echo "记得执行每周审查！" | mail -s "OpenClaw 每周审查提醒" your@email.com
```

---

## 方案 4: OpenClaw 插件 (最佳)

### 步骤 1: 创建自动加载脚本

```bash
vim /root/.openclaw/workspace/.openclaw/on-session-start.js

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// 运行会话启动脚本
try {
    const workspace = path.join(__dirname, '..');
    execSync('./start-session.sh', { 
        cwd: workspace,
        stdio: 'inherit'
    });
    console.log('✅ 会话启动脚本执行成功');
} catch (error) {
    console.error('❌ 会话启动脚本执行失败:', error.message);
}
```

### 步骤 2: 配置 OpenClaw

```bash
# 编辑 OpenClaw 配置
vim /root/.openclaw/openclaw.json

# 添加启动钩子
{
  "hooks": {
    "onSessionStart": "./.openclaw/on-session-start.js"
  }
}
```

---

## 方案 5: Git 钩子 (代码相关)

### 步骤 1: 创建 Git 钩子

```bash
vim /root/.openclaw/workspace/.git/hooks/post-commit

#!/bin/bash
cd /root/.openclaw/workspace
./skills/update-skills-list.sh
```

### 步骤 2: 设置权限

```bash
chmod +x /root/.openclaw/workspace/.git/hooks/post-commit
```

---

## 日志配置

### 创建日志文件

```bash
# 创建日志目录
mkdir -p /var/log/openclaw

# 创建日志文件
touch /var/log/openclaw-session.log
touch /var/log/openclaw-skills.log
touch /var/log/openclaw-review.log

# 设置权限
chmod 644 /var/log/openclaw/*.log
```

### 日志轮转

```bash
sudo vim /etc/logrotate.d/openclaw

/var/log/openclaw-*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
```

---

## 监控和告警

### 创建监控脚本

```bash
vim /root/.openclaw/workspace/monitor-session.sh

#!/bin/bash

# 检查会话启动脚本是否正常运行
if [ ! -f "/root/.openclaw/workspace/start-session.sh" ]; then
    echo "❌ start-session.sh 不存在" | mail -s "OpenClaw 监控告警" your@email.com
    exit 1
fi

# 检查技能清单是否更新
SKILLS_AGE=$(( ( $(date +%s) - $(stat -c %Y /root/.openclaw/workspace/skills/INSTALLED_SKILLS.md) ) / 3600 ))
if [ $SKILLS_AGE -gt 24 ]; then
    echo "⚠️ 技能清单超过 24 小时未更新" | mail -s "OpenClaw 监控告警" your@email.com
fi

# 检查 MEMORY.md 是否更新
MEMORY_AGE=$(( ( $(date +%s) - $(stat -c %Y /root/.openclaw/workspace/MEMORY.md) ) / 86400 ))
if [ $MEMORY_AGE -gt 7 ]; then
    echo "⚠️ MEMORY.md 超过 7 天未更新" | mail -s "OpenClaw 监控告警" your@email.com
fi

echo "✅ 监控检查通过"
```

---

## 快速配置 (推荐)

### 一键配置脚本

```bash
#!/bin/bash
# 一键配置自动运行

echo "🔧 配置 OpenClaw 自动运行..."

# 1. 添加 Bash 别名
cat >> ~/.bashrc << 'EOF'

# OpenClaw 别名
alias oc-start='cd /root/.openclaw/workspace && ./start-session.sh'
alias oc-skill='cd /root/.openclaw/workspace && ./skills/update-skills-list.sh'
alias oc-review='cd /root/.openclaw/workspace && vim WEEKLY_REVIEW.md'
EOF

# 2. 创建日志目录
mkdir -p /var/log/openclaw
touch /var/log/openclaw-{session,skills,review}.log
chmod 644 /var/log/openclaw/*.log

# 3. 添加 Cron 任务
(crontab -l 2>/dev/null; echo "0 * * * * cd /root/.openclaw/workspace && ./skills/update-skills-list.sh >> /var/log/openclaw-skills.log 2>&1") | crontab -

# 4. 设置文件权限
chmod +x /root/.openclaw/workspace/*.sh
chmod +x /root/.openclaw/workspace/skills/*.sh

echo "✅ 配置完成！"
echo ""
echo "使用方式:"
echo "  oc-start   - 启动会话"
echo "  oc-skill   - 更新技能清单"
echo "  oc-review  - 每周审查"
```

---

## 验证配置

### 检查别名

```bash
# 查看别名
alias | grep oc-

# 测试别名
oc-start
```

### 检查 Cron

```bash
# 查看 Cron 任务
crontab -l

# 查看 Cron 日志
tail -f /var/log/syslog | grep CRON
```

### 检查 Systemd

```bash
# 查看定时器状态
systemctl list-timers | grep openclaw

# 查看服务日志
journalctl -u openclaw-session -f
```

---

## 故障排查

### 问题 1: 别名不生效

**解决**:
```bash
# 重新加载 .bashrc
source ~/.bashrc

# 或者重新登录
```

### 问题 2: Cron 不执行

**解决**:
```bash
# 检查 Cron 服务
systemctl status cron

# 查看 Cron 日志
grep CRON /var/log/syslog

# 测试 Cron 任务
cd /root/.openclaw/workspace && ./start-session.sh
```

### 问题 3: 权限问题

**解决**:
```bash
# 检查文件权限
ls -la /root/.openclaw/workspace/*.sh

# 设置执行权限
chmod +x /root/.openclaw/workspace/*.sh
chmod +x /root/.openclaw/workspace/skills/*.sh
```

---

## 最佳实践

### 1. 使用日志
- 所有自动任务都应该记录日志
- 定期查看日志文件
- 配置日志轮转

### 2. 错误处理
- 脚本应该有错误处理
- 失败时发送告警
- 记录失败原因

### 3. 监控
- 定期检查自动任务是否运行
- 监控关键文件更新频率
- 设置告警阈值

### 4. 备份
- 定期备份配置文件
- 备份重要记忆文件
- 测试恢复流程

---

**记住**: 自动化是为了减少手动操作，但需要定期监控！🔒🦀

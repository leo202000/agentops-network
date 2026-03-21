#!/bin/bash
# OpenClaw 监控脚本
# 用法：./monitor-session.sh

LOG_FILE="/var/log/openclaw-monitor.log"
ALERT_EMAIL="your@email.com"  # 替换为你的邮箱

echo "🔍 OpenClaw 系统监控" >> "$LOG_FILE"
echo "时间：$(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "========================" >> "$LOG_FILE"

ALERT_COUNT=0

# 检查 1: start-session.sh 是否存在
if [ ! -f "/root/.openclaw/workspace/start-session.sh" ]; then
    echo "❌ start-session.sh 不存在" >> "$LOG_FILE"
    ALERT_COUNT=$((ALERT_COUNT + 1))
else
    echo "✅ start-session.sh 存在" >> "$LOG_FILE"
fi

# 检查 2: 技能清单是否更新 (超过 24 小时告警)
SKILLS_FILE="/root/.openclaw/workspace/skills/INSTALLED_SKILLS.md"
if [ -f "$SKILLS_FILE" ]; then
    SKILLS_AGE=$(( ( $(date +%s) - $(stat -c %Y "$SKILLS_FILE") ) / 3600 ))
    if [ $SKILLS_AGE -gt 24 ]; then
        echo "⚠️ 技能清单超过 ${SKILLS_AGE} 小时未更新" >> "$LOG_FILE"
        ALERT_COUNT=$((ALERT_COUNT + 1))
    else
        echo "✅ 技能清单更新正常 (${SKILLS_AGE} 小时前)" >> "$LOG_FILE"
    fi
else
    echo "❌ 技能清单文件不存在" >> "$LOG_FILE"
    ALERT_COUNT=$((ALERT_COUNT + 1))
fi

# 检查 3: MEMORY.md 是否更新 (超过 7 天告警)
MEMORY_FILE="/root/.openclaw/workspace/MEMORY.md"
if [ -f "$MEMORY_FILE" ]; then
    MEMORY_AGE=$(( ( $(date +%s) - $(stat -c %Y "$MEMORY_FILE") ) / 86400 ))
    if [ $MEMORY_AGE -gt 7 ]; then
        echo "⚠️ MEMORY.md 超过 ${MEMORY_AGE} 天未更新" >> "$LOG_FILE"
        ALERT_COUNT=$((ALERT_COUNT + 1))
    else
        echo "✅ MEMORY.md 更新正常 (${MEMORY_AGE} 天前)" >> "$LOG_FILE"
    fi
else
    echo "❌ MEMORY.md 文件不存在" >> "$LOG_FILE"
    ALERT_COUNT=$((ALERT_COUNT + 1))
fi

# 检查 4: 当日日志是否存在
TODAY=$(date '+%Y-%m-%d')
TODAY_LOG="/root/.openclaw/workspace/memory/${TODAY}.md"
if [ -f "$TODAY_LOG" ]; then
    echo "✅ 当日日志已创建" >> "$LOG_FILE"
else
    echo "⚠️ 当日日志未创建" >> "$LOG_FILE"
    ALERT_COUNT=$((ALERT_COUNT + 1))
fi

# 检查 5: .env 文件权限
ENV_FILE="/root/.openclaw/workspace/.env"
if [ -f "$ENV_FILE" ]; then
    ENV_PERM=$(stat -c %a "$ENV_FILE")
    if [ "$ENV_PERM" = "600" ]; then
        echo "✅ .env 权限正确 (600)" >> "$LOG_FILE"
    else
        echo "⚠️ .env 权限不正确 ($ENV_PERM), 建议设置为 600" >> "$LOG_FILE"
        ALERT_COUNT=$((ALERT_COUNT + 1))
    fi
fi

# 检查 6: 磁盘空间
DISK_USAGE=$(df /root/.openclaw/workspace | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "❌ 磁盘空间不足 (${DISK_USAGE}%)" >> "$LOG_FILE"
    ALERT_COUNT=$((ALERT_COUNT + 1))
elif [ $DISK_USAGE -gt 80 ]; then
    echo "⚠️ 磁盘空间紧张 (${DISK_USAGE}%)" >> "$LOG_FILE"
else
    echo "✅ 磁盘空间正常 (${DISK_USAGE}%)" >> "$LOG_FILE"
fi

# 总结
echo "------------------------" >> "$LOG_FILE"
if [ $ALERT_COUNT -gt 0 ]; then
    echo "❌ 发现 ${ALERT_COUNT} 个问题" >> "$LOG_FILE"
    
    # 发送告警邮件 (如果配置了)
    if [ "$ALERT_EMAIL" != "your@email.com" ]; then
        echo "OpenClaw 监控发现 ${ALERT_COUNT} 个问题，请检查日志：$LOG_FILE" | mail -s "OpenClaw 监控告警" "$ALERT_EMAIL"
    fi
else
    echo "✅ 所有检查通过" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"

# 输出结果
if [ $ALERT_COUNT -gt 0 ]; then
    echo "❌ 发现 ${ALERT_COUNT} 个问题，请查看日志：$LOG_FILE"
    exit 1
else
    echo "✅ 所有检查通过"
    exit 0
fi

#!/bin/bash
# 会话启动脚本 - 优化版本
# 用法：./start-session.sh

#!/bin/bash
# 会话启动脚本 - 优化版本 v2
# 用法：./start-session.sh 或 oc-start

# 记录启动时间
START_TIME=$(date +%s)

echo "🚀 启动 OpenClaw 会话..."
echo "========================"
echo ""

WORKSPACE="/root/.openclaw/workspace"
cd "$WORKSPACE"

# 步骤 1: 更新技能清单
echo "📦 步骤 1: 更新技能清单..."
if [ -f "./skills/update-skills-list.sh" ]; then
    ./skills/update-skills-list.sh
else
    echo "⚠️  更新脚本不存在"
fi
echo ""

# 步骤 2: 检查核心记忆文件
echo "🧠 步骤 2: 检查核心记忆文件..."
MISSING_FILES=0

if [ -f "./MEMORY.md" ]; then
    echo "✅ MEMORY.md 存在"
    LAST_UPDATE=$(stat -c %y ./MEMORY.md | cut -d'.' -f1)
    echo "   最后更新：$LAST_UPDATE"
    
    # 检查是否超过 7 天未更新
    DAYS_AGO=$(( ( $(date +%s) - $(stat -c %Y ./MEMORY.md) ) / 86400 ))
    if [ $DAYS_AGO -gt 7 ]; then
        echo "   ⚠️  警告：超过 7 天未更新"
    fi
else
    echo "❌ MEMORY.md 不存在"
    MISSING_FILES=$((MISSING_FILES + 1))
fi

if [ -f "./skills/INSTALLED_SKILLS.md" ]; then
    echo "✅ INSTALLED_SKILLS.md 存在"
else
    echo "❌ INSTALLED_SKILLS.md 不存在"
    MISSING_FILES=$((MISSING_FILES + 1))
fi

if [ -f "./SESSION_STARTUP.md" ]; then
    echo "✅ SESSION_STARTUP.md 存在"
else
    echo "❌ SESSION_STARTUP.md 不存在"
    MISSING_FILES=$((MISSING_FILES + 1))
fi
echo ""

# 步骤 3: 检查当日日志
echo "📝 步骤 3: 检查当日日志..."
TODAY=$(date '+%Y-%m-%d')
YESTERDAY=$(date -d "yesterday" '+%Y-%m-%d')

if [ -f "./memory/${TODAY}.md" ]; then
    echo "✅ ${TODAY}.md 已存在"
else
    echo "⚠️  ${TODAY}.md 不存在，创建中..."
    cat > "./memory/${TODAY}.md" << EOF
# ${TODAY} 工作日志

## 今日目标
1. [ ] 
2. [ ] 
3. [ ]

## 工作内容

### 上午

### 下午

### 晚上

## 重要事件

## 学习笔记

## 明日计划

EOF
    echo "✅ 已创建 ${TODAY}.md"
fi

# 检查昨日日志是否完成
if [ -f "./memory/${YESTERDAY}.md" ]; then
    echo "✅ ${YESTERDAY}.md 已归档"
else
    echo "ℹ️  ${YESTERDAY}.md 不存在 (可能是周末)"
fi
echo ""

# 步骤 4: 检查进行中任务
echo "📋 步骤 4: 检查进行中任务..."
if [ -f "./memory/working/active_tasks.md" ]; then
    echo "📌 进行中任务:"
    echo "------------"
    # 提取高优先级任务
    grep -E "^### [0-9]+\." "./memory/working/active_tasks.md" | head -5 | sed 's/^### /  /'
    echo "------------"
    
    # 统计任务数量
    TOTAL_TASKS=$(grep -c "^### " "./memory/working/active_tasks.md" 2>/dev/null || echo "0")
    echo "  总计：$TOTAL_TASKS 个任务"
else
    echo "⚠️  active_tasks.md 不存在，创建中..."
    mkdir -p ./memory/working
    cat > "./memory/working/active_tasks.md" << 'EOF'
# 📋 进行中任务 (Active Tasks)

**更新时间**: YYYY-MM-DD HH:MM

---

## 🔴 高优先级

### 1. [任务名称]
**状态**: ⏳ 进行中  
**进度**: 0%  
**描述**: [任务描述]  
**下一步**: 
- [ ] [具体行动]

---

## 🟡 中优先级

---

## 🟢 低优先级

---

## 📊 统计

| 优先级 | 数量 | 进行中 | 待开始 |
|--------|------|--------|--------|
| 🔴 高 | 0 | 0 | 0 |
| 🟡 中 | 0 | 0 | 0 |
| 🟢 低 | 0 | 0 | 0 |
| **总计** | **0** | **0** | **0** |

EOF
    echo "✅ 已创建 active_tasks.md"
fi
echo ""

# 步骤 5: 显示昨日工作总结 (如果存在)
echo "📊 步骤 5: 昨日工作总结..."
if [ -f "./memory/${YESTERDAY}.md" ]; then
    echo "📝 ${YESTERDAY} 完成的工作:"
    echo "------------"
    grep -E "^\- \[x\]" "./memory/${YESTERDAY}.md" | head -5 | sed 's/^- \[x\] /  ✅ /'
    echo "------------"
else
    echo "ℹ️  无昨日工作总结"
fi
echo ""

# 步骤 6: 显示今日提示
echo "💡 今日提示:"
echo "============"
echo "1. 安装技能后立即更新 CHANGELOG.md"
echo "2. 重要事件记录到 memory/events/"
echo "3. 会话结束前更新当日日志"
echo "4. 每周审查记忆系统效果 (周日)"

# 检查是否是周日
if [ "$(date +%u)" -eq 7 ]; then
    echo "5. ⚠️  今天是周日，记得执行每周审查！"
fi
echo ""

# 步骤 7: 显示快速命令
echo "⚡ 快速命令:"
echo "============"
echo "查看技能清单：cat skills/INSTALLED_SKILLS.md"
echo "查看会话检查：cat SESSION_STARTUP.md"
echo "查看记忆指南：cat MEMORY_UPDATE_GUIDE.md"
echo "更新技能清单：./skills/update-skills-list.sh"
echo "查看进行中任务：cat memory/working/active_tasks.md"
echo "查看当日日志：vim memory/${TODAY}.md"
echo ""

# 步骤 8: 显示高优先级任务
echo "🎯 今日建议工作:"
echo "================"
if [ -f "./memory/working/active_tasks.md" ]; then
    # 提取高优先级任务
    echo "🔴 高优先级任务:"
    grep -A 5 "^### [1-2]\." "./memory/working/active_tasks.md" | grep "^\*\*下一步\*\*" | head -2
else
    echo "暂无高优先级任务"
fi
echo ""

# 步骤 9: 检查文件权限
echo "🔒 步骤 9: 安全检查..."
if [ -f ".env" ]; then
    ENV_PERM=$(stat -c %a .env)
    if [ "$ENV_PERM" = "600" ]; then
        echo "✅ .env 权限正确 (600)"
    else
        echo "⚠️  .env 权限不正确 ($ENV_PERM), 建议设置为 600"
    fi
else
    echo "ℹ️  .env 文件不存在"
fi
echo ""

# 步骤 10: 生成会话报告
echo "📈 步骤 10: 生成会话报告..."
REPORT_FILE="./memory/sessions/$(date '+%Y-%m-%d-%H%M').md"
mkdir -p ./memory/sessions

cat > "$REPORT_FILE" << EOF
# 会话启动报告

**时间**: $(date '+%Y-%m-%d %H:%M:%S')
**工作日**: $(date '+%A')

## 系统状态
- 技能清单：✅ 已更新 ($(grep -c "^-" skills/INSTALLED_SKILLS.md 2>/dev/null || echo "N/A") 个技能)
- 核心文件：$([ $MISSING_FILES -eq 0 ] && echo "✅ 完整" || echo "⚠️ 缺少 $MISSING_FILES 个")
- 当日日志：✅ 已准备
- 进行任务：$(grep -c "^### " memory/working/active_tasks.md 2>/dev/null || echo "0") 个

## 昨日完成
$(grep -c "^\- \[x\]" memory/${YESTERDAY}.md 2>/dev/null || echo "0") 项任务

## 备注
$([ $MISSING_FILES -gt 0 ] && echo "⚠️ 缺少核心文件，请检查")
$([ "$(date +%u)" -eq 7 ] && echo "📅 今天是周日，执行每周审查")

EOF
echo "✅ 会话报告已保存：$REPORT_FILE"
echo ""

echo "✅ 会话启动完成！"
echo "================"
echo ""

# 显示启动时间
END_TIME=$(date +%s)
echo "⏱️  启动耗时：$((END_TIME - START_TIME)) 秒"
echo ""
echo "🎯 准备好开始工作了吗？"

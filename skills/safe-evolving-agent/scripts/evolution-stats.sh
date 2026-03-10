#!/bin/bash
# ===========================================
# 进化统计脚本
# ===========================================
# 用法：./evolution-stats.sh [period]
# period: daily, weekly, monthly, all (默认：all)
# ===========================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVOLUTION_DIR="$SCRIPT_DIR/../../.evolution"

PERIOD=${1:-all}

echo "📊 安全进化统计"
echo "================"
echo "周期：$PERIOD"
echo ""

# 观察记录统计
echo "📝 观察记录:"
echo "------------"

if [ "$PERIOD" = "daily" ]; then
    OBS_COUNT=$(find "$EVOLUTION_DIR/observations/" -name "*.md" -mtime -1 | wc -l)
elif [ "$PERIOD" = "weekly" ]; then
    OBS_COUNT=$(find "$EVOLUTION_DIR/observations/" -name "*.md" -mtime -7 | wc -l)
elif [ "$PERIOD" = "monthly" ]; then
    OBS_COUNT=$(find "$EVOLUTION_DIR/observations/" -name "*.md" -mtime -30 | wc -l)
else
    OBS_COUNT=$(find "$EVOLUTION_DIR/observations/" -name "*.md" | wc -l)
fi

echo "总数：$OBS_COUNT"

# 按类型统计
echo ""
echo "按类型分布:"
grep -rh "**类型**:" "$EVOLUTION_DIR/observations/" 2>/dev/null | \
    sed 's/.*类型**: //' | sort | uniq -c | sort -rn | head -5

# 按分类统计
echo ""
echo "按分类分布:"
ls "$EVOLUTION_DIR/observations/" 2>/dev/null | while read cat; do
    COUNT=$(find "$EVOLUTION_DIR/observations/$cat" -name "*.md" 2>/dev/null | wc -l)
    if [ $COUNT -gt 0 ]; then
        echo "  $cat: $COUNT"
    fi
done

echo ""
echo "📋 提案状态:"
echo "------------"

PROP_PENDING=$(find "$EVOLUTION_DIR/proposals/pending/" -name "*.md" 2>/dev/null | wc -l)
PROP_APPROVED=$(find "$EVOLUTION_DIR/proposals/approved/" -name "*.md" 2>/dev/null | wc -l)
PROP_REJECTED=$(find "$EVOLUTION_DIR/proposals/rejected/" -name "*.md" 2>/dev/null | wc -l)
PROP_TOTAL=$((PROP_PENDING + PROP_APPROVED + PROP_REJECTED))

echo "待审批：$PROP_PENDING"
echo "已批准：$PROP_APPROVED"
echo "已拒绝：$PROP_REJECTED"
echo "总计：$PROP_TOTAL"

if [ $PROP_TOTAL -gt 0 ]; then
    APPROVE_RATE=$((PROP_APPROVED * 100 / PROP_TOTAL))
    echo "批准率：$APPROVE_RATE%"
fi

echo ""
echo "📈 最近变更:"
echo "------------"

if [ -f "$EVOLUTION_DIR/changelog.jsonl" ]; then
    tail -5 "$EVOLUTION_DIR/changelog.jsonl" | while read line; do
        echo "$line" | jq -c '. | {action, id, ts}' 2>/dev/null || echo "$line"
    done
else
    echo "无变更记录"
fi

echo ""
echo "💡 洞察:"
echo "------"

# 最常见的观察类型
if [ $OBS_COUNT -gt 0 ]; then
    TOP_TYPE=$(grep -rh "**类型**:" "$EVOLUTION_DIR/observations/" 2>/dev/null | \
        sed 's/.*类型**: //' | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
    echo "最常见的观察类型：$TOP_TYPE"
fi

# 待审批提案提醒
if [ $PROP_PENDING -gt 0 ]; then
    echo "⚠️  有待审批提案：$PROP_PENDING 个"
    echo "   运行：ls $EVOLUTION_DIR/proposals/pending/"
fi

# 存储空间
STORAGE=$(du -sh "$EVOLUTION_DIR" 2>/dev/null | cut -f1)
echo "存储空间：$STORAGE"

echo ""
echo "================"
echo "更新时间：$(date)"

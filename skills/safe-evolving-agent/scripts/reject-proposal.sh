#!/bin/bash
# ===========================================
# 拒绝提案脚本
# ===========================================
# 用法：./reject-proposal.sh <proposal-id> <reason>
# ===========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVOLUTION_DIR="$SCRIPT_DIR/../../.evolution"

# 参数检查
if [ $# -lt 1 ]; then
    echo "❌ 用法：$0 <proposal-id> [reason]"
    echo ""
    echo "示例:"
    echo "  $0 PROP-20260310-143000 \"风险太高\""
    exit 1
fi

PROP_ID="$1"
REASON="${2:-未提供原因}"
PROP_FILE="$EVOLUTION_DIR/proposals/pending/${PROP_ID}.md"

# 检查提案文件是否存在
if [ ! -f "$PROP_FILE" ]; then
    echo "❌ 提案不存在：$PROP_ID"
    echo "位置：$PROP_FILE"
    exit 1
fi

echo "❌ 拒绝提案：$PROP_ID"
echo "原因：$REASON"
echo ""

# 更新提案状态
sed -i "s/\- \[ \] \*\*已拒绝\*\*/\- [x] **已拒绝** - 日期：$(date +%Y-%m-%d) 原因：$REASON/" "$PROP_FILE"

# 添加拒绝原因到文件末尾
cat >> "$PROP_FILE" << EOF

---

## 拒绝原因

$REASON

**决定日期**: $(date +%Y-%m-%d)

EOF

# 移动到 rejected 目录
mv "$PROP_FILE" "$EVOLUTION_DIR/proposals/rejected/"
echo "📁 提案已移动到：$EVOLUTION_DIR/proposals/rejected/"

# 记录到 changelog
echo "{\"ts\":\"$(date -Iseconds)\",\"action\":\"reject\",\"id\":\"$PROP_ID\",\"reason\":\"$REASON\"}" >> "$EVOLUTION_DIR/changelog.jsonl"

echo ""
echo "✅ 提案已拒绝"
echo ""
echo "查看拒绝的提案:"
echo "  cat $EVOLUTION_DIR/proposals/rejected/${PROP_ID}.md"

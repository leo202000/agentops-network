#!/bin/bash
# ===========================================
# 批准提案脚本
# ===========================================
# 用法：./approve-proposal.sh <proposal-id>
# ===========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVOLUTION_DIR="$SCRIPT_DIR/../../.evolution"
WORKSPACE_DIR="$SCRIPT_DIR/../.."

# 参数检查
if [ $# -lt 1 ]; then
    echo "❌ 用法：$0 <proposal-id>"
    echo ""
    echo "示例:"
    echo "  $0 PROP-20260310-143000"
    exit 1
fi

PROP_ID="$1"
PROP_FILE="$EVOLUTION_DIR/proposals/pending/${PROP_ID}.md"

# 检查提案文件是否存在
if [ ! -f "$PROP_FILE" ]; then
    echo "❌ 提案不存在：$PROP_ID"
    echo "位置：$PROP_FILE"
    exit 1
fi

echo "📋 审批提案：$PROP_ID"
echo ""

# 显示提案摘要
echo "提案内容:"
echo "================================"
head -30 "$PROP_FILE"
echo "..."
echo "================================"
echo ""

# 读取目标文件
TARGET_FILE=$(grep -A 1 "目标文件" "$PROP_FILE" | tail -1 | tr -d ' '` | grep -oE '[A-Z_]+\.md' | head -1)

if [ -z "$TARGET_FILE" ]; then
    echo "⚠️  未找到目标文件，请手动输入:"
    read -p "目标文件 (如 AGENTS.md): " TARGET_FILE
fi

TARGET_PATH="$WORKSPACE_DIR/$TARGET_FILE"

# 检查目标文件
if [ ! -f "$TARGET_PATH" ]; then
    echo "❌ 目标文件不存在：$TARGET_PATH"
    exit 1
fi

# 创建备份
TIMESTAMP=$(date +%Y%m%d%H%M%S)
BACKUP="${TARGET_PATH}.backup.${TIMESTAMP}"
cp "$TARGET_PATH" "$BACKUP"
echo "💾 备份已创建：$BACKUP"

# 提取建议内容
CONTENT=$(sed -n '/### 建议内容/,/---/p' "$PROP_FILE" | grep -v "### 建议内容" | grep -v "^---$" | sed 's/^```markdown//' | sed 's/```$//')

# 追加到目标文件
echo "" >> "$TARGET_PATH"
echo "## 📈 进化提案：$PROP_ID" >> "$TARGET_PATH"
echo "**应用日期**: $(date +%Y-%m-%d)" >> "$TARGET_PATH"
echo "**来源**: $PROP_ID" >> "$TARGET_PATH"
echo "" >> "$TARGET_PATH"
echo "$CONTENT" >> "$TARGET_PATH"
echo "" >> "$TARGET_PATH"

echo "✅ 变更已应用到：$TARGET_PATH"

# 更新提案状态
sed -i "s/\- \[ \] \*\*已批准\*\*/\- [x] **已批准** - 日期：$(date +%Y-%m-%d) 审批人：user/" "$PROP_FILE"

# 移动到 approved 目录
mv "$PROP_FILE" "$EVOLUTION_DIR/proposals/approved/"
echo "📁 提案已移动到：$EVOLUTION_DIR/proposals/approved/"

# 记录到 changelog
echo "{\"ts\":\"$(date -Iseconds)\",\"action\":\"approve\",\"id\":\"$PROP_ID\",\"file\":\"$TARGET_FILE\",\"backup\":\"$BACKUP\"}" >> "$EVOLUTION_DIR/changelog.jsonl"

# Git 提交（如果在 git 仓库中）
cd "$WORKSPACE_DIR"
if git rev-parse --git-dir > /dev/null 2>&1; then
    git add "$TARGET_FILE"
    git commit -m "📈 Evolution: 应用提案 $PROP_ID" || echo "⚠️  Git 提交失败，请手动提交"
    echo "✅ Git 提交完成"
fi

echo ""
echo "✅ 提案批准完成！"
echo ""
echo "回滚方法（如需要）:"
echo "  cp $BACKUP $TARGET_PATH"
echo ""
echo "查看变更:"
echo "  git show HEAD"

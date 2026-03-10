#!/bin/bash
# ===========================================
# 生成提案脚本
# ===========================================
# 用法：./generate-proposal.sh <pattern> [threshold]
# ===========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVOLUTION_DIR="$SCRIPT_DIR/../../.evolution"

# 参数检查
if [ $# -lt 1 ]; then
    echo "❌ 用法：$0 <pattern> [threshold]"
    echo ""
    echo "示例:"
    echo "  $0 \"MBC20\"              # 查找包含 MBC20 的观察"
    echo "  $0 \"git push\" 2         # 查找 2 次以上"
    exit 1
fi

PATTERN="$1"
THRESHOLD=${2:-3}

# 搜索匹配的观察
echo "🔍 搜索模式：$PATTERN"
echo "阈值：$THRESHOLD 次"
echo ""

MATCHES=$(grep -rl "$PATTERN" "$EVOLUTION_DIR/observations/" 2>/dev/null | wc -l || echo "0")

echo "找到匹配：$MATCHES 个观察记录"
echo ""

if [ "$MATCHES" -lt "$THRESHOLD" ]; then
    echo "⚠️  未达到阈值（需要 $THRESHOLD 次，实际 $MATCHES 次）"
    echo "继续收集更多观察记录..."
    exit 0
fi

# 生成提案 ID
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
PROP_ID="PROP-${TIMESTAMP}"

# 创建提案文件
PROP_DIR="$EVOLUTION_DIR/proposals/pending"
mkdir -p "$PROP_DIR"

PROP_FILE="$PROP_DIR/${PROP_ID}.md"

# 收集相关观察
RELATED_OBS=$(grep -rl "$PATTERN" "$EVOLUTION_DIR/observations/" | head -5)

cat > "$PROP_FILE" << EOF
# 📋 晋升提案

**提案 ID**: $PROP_ID  
**类型**: workflow | tool | behavior | config  
**状态**: pending  
**创建日期**: $(date +%Y-%m-%d)

---

## 来源观察

基于以下观察记录（模式："$PATTERN"）：

EOF

# 添加观察列表
for obs in $RELATED_OBS; do
    OBS_ID=$(basename "$obs" .md)
    echo "- [ ] $OBS_ID" >> "$PROP_FILE"
done

cat >> "$PROP_FILE" << EOF

**重复次数**: $MATCHES 次

---

## 建议变更

### 目标文件

```
<!-- AGENTS.md / TOOLS.md / SOUL.md -->
```

### 目标章节

```
<!-- 例如：## 工作流 -->
```

### 建议内容

```markdown
<!-- 在这里写入建议的具体内容 -->

```

---

## 理由

为什么这个变更值得批准？

<!-- 
此模式在 $MATCHES 次独立观察中出现，证明：
1. 问题确实存在
2. 解决方案有效
3. 值得固化为长期规则
-->

---

## 影响评估

### 正面影响
- ✅ 

### 潜在风险
- ⚠️ 

### 缓解措施
<!-- 如何降低风险 -->


---

## 审批记录

- [ ] **待审批** - 等待用户决定
- [ ] **已批准** - 日期：______ 审批人：______
- [ ] **已拒绝** - 日期：______ 原因：______

---

*自动生成时间：$(date)*
EOF

# 记录到 changelog
echo "{\"ts\":\"$(date -Iseconds)\",\"action\":\"propose\",\"id\":\"$PROP_ID\",\"pattern\":\"$PATTERN\",\"based_on\":$MATCHES}" >> "$EVOLUTION_DIR/changelog.jsonl"

echo "✅ 提案生成完成：$PROP_ID"
echo "📁 文件位置：$PROP_FILE"
echo ""
echo "下一步:"
echo "  1. 编辑提案文件，填写具体建议内容"
echo "  2. 运行：./approve-proposal.sh $PROP_ID  # 批准"
echo "  3. 运行：./reject-proposal.sh $PROP_ID   # 拒绝"

#!/bin/bash
# ===========================================
# 记录观察脚本
# ===========================================
# 用法：./record-observation.sh <type> <category> <description>
# 类型：error, correction, improvement, review
# ===========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVOLUTION_DIR="$(dirname "$SCRIPT_DIR")/.evolution"

# 参数检查
if [ $# -lt 3 ]; then
    echo "❌ 用法：$0 <type> <category> <description>"
    echo ""
    echo "类型:"
    echo "  error       - 操作错误"
    echo "  correction  - 用户纠正"
    echo "  improvement - 改进建议"
    echo "  review      - 任务回顾"
    echo ""
    echo "分类:"
    echo "  platform    - 平台相关"
    echo "  workflow    - 工作流程"
    echo "  tools       - 工具使用"
    echo "  config      - 配置问题"
    echo "  other       - 其他"
    exit 1
fi

TYPE=$1
CATEGORY=$2
DESCRIPTION="$3"

# 生成 ID
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
ID="OBS-${TIMESTAMP}"

# 创建目录
OBS_DIR="$EVOLUTION_DIR/observations/${CATEGORY}"
mkdir -p "$OBS_DIR"

# 生成文件
OBS_FILE="$OBS_DIR/${ID}.md"

cat > "$OBS_FILE" << EOF
# 📋 观察记录

**ID**: $ID  
**类型**: $TYPE  
**时间**: $(date -Iseconds)  
**分类**: $CATEGORY

---

## 描述

$DESCRIPTION

---

## 上下文

<!-- 详细描述发生了什么、在什么场景下 -->


---

## 问题/纠正/改进

<!-- 具体是什么问题？用户如何纠正？更好的做法是什么？ -->


---

## 建议解决方案

<!-- 具体应该怎么改？ -->


---

## 信心等级

- [ ] low（猜测，需要验证）
- [ ] medium（有一定把握）
- [ ] high（确定）

---

## 元数据

- **来源**: 自动观察 | 用户纠正 | 任务回顾
- **相关任务**: 
- **关联观察**: 

---

*自动生成时间：$(date)*
EOF

# 记录到 changelog
echo "{\"ts\":\"$(date -Iseconds)\",\"action\":\"observe\",\"type\":\"$TYPE\",\"id\":\"$ID\",\"category\":\"$CATEGORY\"}" >> "$EVOLUTION_DIR/changelog.jsonl"

echo "✅ 观察记录完成：$ID"
echo "📁 文件位置：$OBS_FILE"
echo ""
echo "下一步:"
echo "  1. 编辑文件补充详细信息"
echo "  2. 当同一模式出现≥3 次时，运行：./generate-proposal.sh <关键词>"

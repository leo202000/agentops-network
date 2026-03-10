#!/bin/bash
# ===========================================
# 技能安全检查脚本
# ===========================================
# 用法：./skill-security-check.sh <skill-directory>
# ===========================================

set -e

SKILL_DIR="${1:-.}"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "==========================================="
echo "🔐 技能安全检查"
echo "==========================================="
echo "检查目录：$SKILL_DIR"
echo ""

# 检查目录是否存在
if [ ! -d "$SKILL_DIR" ]; then
    echo -e "${RED}❌ 错误：目录不存在${NC}"
    exit 1
fi

cd "$SKILL_DIR"

# ===========================================
# 1. 检查必需文件
# ===========================================
echo "📁 检查必需文件..."

REQUIRED_FILES=("SKILL.md" "package.json" "index.js")
MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ✅ $file"
    else
        echo -e "  ${RED}❌ $file (缺失)${NC}"
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -ne 0 ]; then
    echo -e "${RED}⚠️  缺少必需文件，技能可能无法正常工作${NC}"
fi

echo ""

# ===========================================
# 2. 检查 package.json 依赖
# ===========================================
echo "📦 检查依赖项..."

if [ -f "package.json" ]; then
    # 检查是否有可疑依赖
    SUSPICIOUS_PACKAGES=("child_process" "exec" "spawn" "eval" "vm")
    
    for pkg in "${SUSPICIOUS_PACKAGES[@]}"; do
        if grep -q "\"$pkg\"" package.json 2>/dev/null; then
            echo -e "  ${YELLOW}⚠️  发现可疑依赖：$pkg${NC}"
        fi
    done
    
    # 显示依赖数量
    DEP_COUNT=$(grep -c "\"[a-z]" package.json 2>/dev/null || echo "0")
    echo -e "  📊 依赖数量：$DEP_COUNT"
fi

echo ""

# ===========================================
# 3. 扫描危险操作
# ===========================================
echo "🔍 扫描危险操作..."

DANGEROUS_PATTERNS=(
    "child_process"
    "exec("
    "spawn("
    "eval("
    "Function("
    "vm.run"
    "fs.writeFile"
    "fs.writeFileSync"
    "fs.unlink"
    "fs.rm"
)

FOUND_DANGEROUS=()

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if grep -r "$pattern" --include="*.js" . 2>/dev/null | grep -v node_modules; then
        FOUND_DANGEROUS+=("$pattern")
    fi
done

if [ ${#FOUND_DANGEROUS[@]} -ne 0 ]; then
    echo -e "${YELLOW}⚠️  发现以下危险操作:${NC}"
    for danger in "${FOUND_DANGEROUS[@]}"; do
        echo -e "  ${YELLOW}- $danger${NC}"
    done
else
    echo -e "  ${GREEN}✅ 未发现明显危险操作${NC}"
fi

echo ""

# ===========================================
# 4. 检查敏感信息
# ===========================================
echo "🔑 检查敏感信息..."

SENSITIVE_PATTERNS=(
    "api_key"
    "api_secret"
    "private_key"
    "password"
    "token"
    "secret"
)

FOUND_SENSITIVE=()

for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if grep -ri "$pattern" --include="*.js" . 2>/dev/null | grep -v node_modules | grep -v "// " | grep -v "process.env"; then
        FOUND_SENSITIVE+=("$pattern")
    fi
done

if [ ${#FOUND_SENSITIVE[@]} -ne 0 ]; then
    echo -e "${RED}⚠️  发现硬编码的敏感信息:${NC}"
    for sensitive in "${FOUND_SENSITIVE[@]}"; do
        echo -e "  ${RED}- $sensitive${NC}"
    done
    echo -e "${YELLOW}💡 建议：使用环境变量或配置文件${NC}"
else
    echo -e "  ${GREEN}✅ 未发现硬编码的敏感信息${NC}"
fi

echo ""

# ===========================================
# 5. 检查网络请求
# ===========================================
echo "🌐 检查网络请求..."

if grep -r "fetch\|axios\|http.get\|http.post" --include="*.js" . 2>/dev/null | grep -v node_modules; then
    echo -e "${YELLOW}⚠️  发现网络请求，请确认目标域名可信${NC}"
    
    # 提取域名
    grep -roE "https?://[a-zA-Z0-9.-]+" --include="*.js" . 2>/dev/null | \
        grep -v node_modules | \
        sort -u | \
        while read -r url; do
            echo -e "  - $url"
        done
else
    echo -e "  ${GREEN}✅ 未发现网络请求${NC}"
fi

echo ""

# ===========================================
# 6. 检查文件系统访问
# ===========================================
echo "📂 检查文件系统访问..."

if grep -r "fs\." --include="*.js" . 2>/dev/null | grep -v node_modules; then
    echo -e "${YELLOW}⚠️  发现文件系统操作，请确认路径安全${NC}"
else
    echo -e "  ${GREEN}✅ 未发现文件系统访问${NC}"
fi

echo ""

# ===========================================
# 7. 检查 SKILL.md 描述
# ===========================================
echo "📖 检查技能描述..."

if [ -f "SKILL.md" ]; then
    # 检查是否包含必要信息
    if grep -q "description" SKILL.md 2>/dev/null; then
        echo -e "  ${GREEN}✅ 包含描述${NC}"
    else
        echo -e "  ${YELLOW}⚠️  缺少描述${NC}"
    fi
    
    if grep -q "permissions" SKILL.md 2>/dev/null; then
        echo -e "  ${GREEN}✅ 声明权限${NC}"
    else
        echo -e "  ${YELLOW}⚠️  未声明权限${NC}"
    fi
    
    if grep -q "usage" SKILL.md 2>/dev/null; then
        echo -e "  ${GREEN}✅ 包含使用说明${NC}"
    else
        echo -e "  ${YELLOW}⚠️  缺少使用说明${NC}"
    fi
fi

echo ""

# ===========================================
# 8. 总结
# ===========================================
echo "==========================================="
echo "📊 安全检查总结"
echo "==========================================="

ISSUE_COUNT=$((${#MISSING_FILES[@]} + ${#FOUND_DANGEROUS[@]} + ${#FOUND_SENSITIVE[@]}))

if [ $ISSUE_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ 安全检查通过！${NC}"
    echo ""
    echo "建议："
    echo "1. 在沙箱环境中测试技能"
    echo "2. 启用审计日志监控行为"
    echo "3. 限制技能权限到最小必要范围"
else
    echo -e "${YELLOW}⚠️  发现 $ISSUE_COUNT 个潜在问题${NC}"
    echo ""
    echo "建议："
    echo "1. 审查上述发现的问题"
    echo "2. 联系技能作者确认用途"
    echo "3. 在隔离环境中测试"
    echo "4. 如有疑虑，不要安装"
fi

echo ""
echo "==========================================="

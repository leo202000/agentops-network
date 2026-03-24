#!/bin/bash
# 发型生成系统备份脚本
# 用法：./backup_hairstyle_project.sh

BACKUP_DIR="/root/.openclaw/workspace/backups"
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR="/root/.openclaw/workspace/hairstyle_app"

echo "======================================"
echo "📦 发型生成系统备份"
echo "======================================"
echo ""

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份项目文件（排除大文件）
echo "📁 备份项目文件..."
tar -czf $BACKUP_DIR/hairstyle_app_$DATE.tar.gz \
    $PROJECT_DIR/ \
    --exclude="backend/venv" \
    --exclude="results/*.jpg" \
    --exclude="results/*.jpeg" \
    --exclude="__pycache__" \
    --exclude="*.pyc"

if [ $? -eq 0 ]; then
    echo "   ✅ 项目文件备份完成"
    echo "   📦 $BACKUP_DIR/hairstyle_app_$DATE.tar.gz"
else
    echo "   ❌ 项目文件备份失败"
fi

# 备份环境变量
echo ""
echo "🔑 备份环境变量..."
cp /root/.openclaw/workspace/.env $BACKUP_DIR/env_backup_$DATE.txt

if [ $? -eq 0 ]; then
    echo "   ✅ 环境变量备份完成"
else
    echo "   ❌ 环境变量备份失败"
fi

# 显示备份信息
echo ""
echo "======================================"
echo "📊 备份信息"
echo "======================================"
echo ""
echo "备份位置：$BACKUP_DIR"
echo "备份时间：$DATE"
echo ""
echo "备份文件:"
ls -lh $BACKUP_DIR/hairstyle_app_$DATE.tar.gz
ls -lh $BACKUP_DIR/env_backup_$DATE.txt
echo ""
echo "======================================"
echo "✅ 备份完成！"
echo "======================================"
echo ""

# 清理旧备份（保留最近 10 个）
echo "🧹 清理旧备份（保留最近 10 个）..."
cd $BACKUP_DIR
ls -t hairstyle_app_*.tar.gz | tail -n +11 | xargs -r rm
ls -t env_backup_*.txt | tail -n +11 | xargs -r rm
echo "   ✅ 清理完成"
echo ""

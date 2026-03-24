#!/bin/bash
# 智颜社项目 - 完整备份脚本
# 使用方法：./backup_zhiyanshe.sh

set -e

BACKUP_DIR="/root/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=========================================="
echo "智颜社项目备份"
echo "时间：$TIMESTAMP"
echo "=========================================="

# 创建备份目录
mkdir -p $BACKUP_DIR

# 1. 备份环境变量（最重要）
echo "📝 备份环境变量..."
cp /root/.openclaw/workspace/.env $BACKUP_DIR/.env.backup_$TIMESTAMP
echo "✅ .env 已备份"

# 2. 备份项目代码
echo "📝 备份项目代码..."
tar -czf $BACKUP_DIR/hairstyle_code_$TIMESTAMP.tar.gz \
  /root/.openclaw/workspace/hairstyle_app/ \
  /root/.openclaw/workspace/skills/hairstyle-generator/ \
  2>/dev/null || true
echo "✅ 项目代码已备份"

# 3. 备份数据库
echo "📝 备份数据库..."
if [ -d "/root/.openclaw/workspace/hairstyle_app/zhiyanshe/database/" ]; then
  tar -czf $BACKUP_DIR/database_$TIMESTAMP.tar.gz \
    /root/.openclaw/workspace/hairstyle_app/zhiyanshe/database/ \
    2>/dev/null || true
  echo "✅ 数据库已备份"
else
  echo "⚠️  数据库目录不存在，跳过"
fi

# 4. 备份水印记录
echo "📝 备份水印记录..."
if [ -f "/root/.openclaw/workspace/hairstyle_app/watermark_records.json" ]; then
  cp /root/.openclaw/workspace/hairstyle_app/watermark_records.json \
     $BACKUP_DIR/watermark_$TIMESTAMP.json
  echo "✅ 水印记录已备份"
else
  echo "⚠️  水印记录文件不存在，跳过"
fi

# 5. 备份清理日志
echo "📝 备份清理日志..."
if [ -f "/var/log/hairstyle_cleanup.log" ]; then
  cp /var/log/hairstyle_cleanup.log \
     $BACKUP_DIR/cleanup_log_$TIMESTAMP.log
  echo "✅ 清理日志已备份"
else
  echo "⚠️  清理日志文件不存在，跳过"
fi

# 6. 备份用户上传的图片
echo "📝 备份用户图片..."
if [ -d "/root/.openclaw/media/inbound/" ]; then
  tar -czf $BACKUP_DIR/user_photos_$TIMESTAMP.tar.gz \
    /root/.openclaw/media/inbound/ \
    2>/dev/null || true
  echo "✅ 用户图片已备份"
else
  echo "⚠️  用户图片目录不存在，跳过"
fi

# 7. 备份生成的对比图
echo "📝 备份对比图..."
if [ -d "/root/.openclaw/workspace/hairstyle_app/content_materials/branded/" ]; then
  tar -czf $BACKUP_DIR/comparisons_$TIMESTAMP.tar.gz \
    /root/.openclaw/workspace/hairstyle_app/content_materials/branded/ \
    /root/.openclaw/workspace/hairstyle_app/content_materials/comparisons/ \
    2>/dev/null || true
  echo "✅ 对比图已备份"
else
  echo "⚠️  对比图目录不存在，跳过"
fi

# 显示备份结果
echo ""
echo "=========================================="
echo "备份完成！"
echo "=========================================="
echo ""
echo "备份文件列表:"
ls -lh $BACKUP_DIR/*_$TIMESTAMP.* 2>/dev/null | awk '{print $9, "(" $5 ")"}'
echo ""
echo "备份目录：$BACKUP_DIR"
echo ""

# 清理旧备份（保留最近 7 天）
echo "🗑️  清理 7 天前的旧备份..."
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete 2>/dev/null || true
find $BACKUP_DIR -name "*.backup_*" -mtime +7 -delete 2>/dev/null || true
find $BACKUP_DIR -name "*.json" -mtime +7 -delete 2>/dev/null || true
find $BACKUP_DIR -name "*.log" -mtime +7 -delete 2>/dev/null || true
echo "✅ 旧备份已清理"

echo ""
echo "=========================================="
echo "所有操作完成！"
echo "=========================================="

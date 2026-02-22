#!/bin/bash

echo "=== 手动清理旧日志文件 ==="
echo ""
echo "此脚本会删除旧的日志文件，加快服务启动速度"
echo ""

# 检查是否在正确的目录
if [ ! -d "logs" ]; then
    echo "❌ 错误: 未找到 logs 目录"
    exit 1
fi

cd logs

echo "1. 统计当前日志文件..."
echo "总文件数: $(find . -type f | wc -l)"
echo "总大小: $(du -sh . | cut -f1)"
echo ""

echo "2. 查找旧的日志文件（.log.* 格式）..."
OLD_LOGS=$(find . -name "*.log.*" -type f | wc -l)
echo "找到 $OLD_LOGS 个旧日志文件"
echo ""

if [ "$OLD_LOGS" -eq 0 ]; then
    echo "✅ 没有需要清理的旧日志文件"
    exit 0
fi

echo "⚠️  警告: 即将删除所有旧日志文件（保留当前的 .log 文件）"
read -p "是否继续？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 1
fi

echo ""
echo "3. 删除旧日志文件..."

# 删除所有 .log.* 格式的文件（包括 .gz）
find . -name "*.log.*" -type f -delete

echo "✅ 删除完成"
echo ""

echo "4. 清理空目录..."
find . -type d -empty -delete

echo "✅ 清理完成"
echo ""

echo "5. 统计清理后的日志文件..."
echo "总文件数: $(find . -type f | wc -l)"
echo "总大小: $(du -sh . | cut -f1)"
echo ""

echo "=== 完成 ==="
echo ""
echo "现在可以重启服务了:"
echo "  docker compose -f docker-compose.backend.yml restart backend-api queue-worker"

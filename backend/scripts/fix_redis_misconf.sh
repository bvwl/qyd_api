#!/bin/bash
# Redis MISCONF 错误快速修复脚本

echo "=========================================="
echo "Redis MISCONF 错误快速修复"
echo "=========================================="
echo ""

# 读取 .env 文件中的 Redis 配置
if [ -f "../.env" ]; then
    source ../.env
elif [ -f ".env" ]; then
    source .env
else
    echo "警告: 未找到 .env 文件，使用默认配置"
    REDIS_HOST="127.0.0.1"
    REDIS_PORT="6378"
    REDIS_PASSWORD="redis_fNmAxZ"
fi

echo "Redis 配置:"
echo "  主机: $REDIS_HOST"
echo "  端口: $REDIS_PORT"
echo ""

# 检查 Redis 是否可访问
echo "1. 检查 Redis 连接..."
if [ -n "$REDIS_PASSWORD" ]; then
    REDIS_CLI="redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD"
else
    REDIS_CLI="redis-cli -h $REDIS_HOST -p $REDIS_PORT"
fi

if ! $REDIS_CLI PING > /dev/null 2>&1; then
    echo "❌ 无法连接到 Redis，请检查 Redis 是否运行"
    exit 1
fi
echo "✅ Redis 连接正常"
echo ""

# 检查磁盘空间
echo "2. 检查磁盘空间..."
df -h | grep -E "Filesystem|/$"
echo ""

DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "⚠️  警告: 磁盘使用率 ${DISK_USAGE}%，建议清理磁盘空间"
    echo ""
    echo "可以运行以下命令清理日志:"
    echo "  cd backend && python scripts/cleanup_logs.py"
    echo ""
else
    echo "✅ 磁盘空间充足 (使用率: ${DISK_USAGE}%)"
    echo ""
fi

# 检查 Redis 内存使用
echo "3. 检查 Redis 内存使用..."
$REDIS_CLI INFO memory | grep -E "used_memory_human|maxmemory_human"
echo ""

# 显示当前配置
echo "4. 当前 Redis 持久化配置:"
echo "stop-writes-on-bgsave-error: $($REDIS_CLI CONFIG GET stop-writes-on-bgsave-error | tail -1)"
echo ""

# 询问是否修复
echo "=========================================="
echo "修复选项:"
echo "=========================================="
echo "1. 禁用持久化错误检查 (推荐，立即生效)"
echo "2. 完全禁用 RDB 持久化 (需要修改配置文件)"
echo "3. 仅查看状态，不修改"
echo ""
read -p "请选择 (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "正在禁用持久化错误检查..."
        $REDIS_CLI CONFIG SET stop-writes-on-bgsave-error no
        
        if [ $? -eq 0 ]; then
            echo "✅ 配置已更新"
            echo ""
            echo "验证配置:"
            $REDIS_CLI CONFIG GET stop-writes-on-bgsave-error
            echo ""
            echo "⚠️  注意: 此配置在 Redis 重启后会失效"
            echo "如需永久生效，请修改 redis.conf 文件:"
            echo "  stop-writes-on-bgsave-error no"
        else
            echo "❌ 配置更新失败"
            exit 1
        fi
        ;;
    2)
        echo ""
        echo "请手动编辑 Redis 配置文件 (通常在 /etc/redis/redis.conf):"
        echo ""
        echo "添加或修改以下配置:"
        echo "  save \"\""
        echo "  stop-writes-on-bgsave-error no"
        echo ""
        echo "然后重启 Redis:"
        echo "  systemctl restart redis"
        echo "  或"
        echo "  redis-server /path/to/redis.conf"
        ;;
    3)
        echo ""
        echo "仅查看状态，未做任何修改"
        ;;
    *)
        echo ""
        echo "无效选择"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "测试 Redis 写入"
echo "=========================================="
TEST_KEY="test_fix_$(date +%s)"
$REDIS_CLI SET "$TEST_KEY" "test_value" EX 10

if [ $? -eq 0 ]; then
    echo "✅ Redis 写入测试成功"
    $REDIS_CLI DEL "$TEST_KEY"
else
    echo "❌ Redis 写入测试失败"
    echo ""
    echo "建议:"
    echo "1. 检查磁盘空间是否充足"
    echo "2. 检查 Redis 日志: tail -f /var/log/redis/redis-server.log"
    echo "3. 查看详细修复指南: cat REDIS_MISCONF_FIX.md"
fi

echo ""
echo "完成！"

#!/bin/bash
# MySQL主从复制修复脚本
# 用于修复已部署但复制不正常的情况

set -e

ROOT_PASSWORD="zhiyu666"
REPL_PASSWORD="repl123"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "=========================================="
echo "  MySQL主从复制修复脚本"
echo "=========================================="
echo ""

# 1. 检查容器状态
log_info "检查容器状态..."
if ! docker ps | grep -q mysql-master; then
    log_error "主库容器未运行"
    exit 1
fi

if ! docker ps | grep -q mysql-slave-1; then
    log_error "从库1容器未运行"
    exit 1
fi

if ! docker ps | grep -q mysql-slave-2; then
    log_error "从库2容器未运行"
    exit 1
fi

log_info "所有容器运行正常 ✓"

# 2. 获取主库容器IP
master_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql-master)
if [ -z "$master_ip" ]; then
    log_error "无法获取主库容器IP"
    exit 1
fi

log_info "主库容器IP: ${master_ip}"
echo "${master_ip}" > /tmp/mysql_master_ip.txt

# 3. 检查主库状态
log_info "检查主库状态..."
docker exec mysql-master mysql -uroot -p${ROOT_PASSWORD} -e "SHOW MASTER STATUS\G" 2>/dev/null
if [ $? -ne 0 ]; then
    log_error "无法连接主库"
    exit 1
fi

# 4. 停止并清理从库
log_info "停止从库容器..."
docker stop mysql-slave-1 mysql-slave-2

log_info "删除从库容器..."
docker rm mysql-slave-1 mysql-slave-2

log_warn "清理从库数据目录..."
sudo rm -rf /opt/mysql/slave-1/data/*
sudo rm -rf /opt/mysql/slave-2/data/*

# 5. 更新从库配置（添加skip-log-bin）
log_info "更新从库配置..."

cat > /opt/mysql/slave-1/conf/my.cnf << 'EOF'
[mysqld]
server-id=2
port=3306
default_authentication_plugin=mysql_native_password
relay_log=/var/lib/mysql/mysql-relay-bin
gtid_mode=ON
enforce_gtid_consistency=ON
replica_parallel_workers=4
replica_parallel_type=LOGICAL_CLOCK
skip-log-bin
log_replica_updates=OFF
innodb_buffer_pool_size=1G
innodb_flush_log_at_trx_commit=2
max_connections=3000
skip_name_resolve=1
character_set_server=utf8mb4
collation_server=utf8mb4_unicode_ci
default_time_zone='+8:00'
EOF

cat > /opt/mysql/slave-2/conf/my.cnf << 'EOF'
[mysqld]
server-id=3
port=3306
default_authentication_plugin=mysql_native_password
relay_log=/var/lib/mysql/mysql-relay-bin
gtid_mode=ON
enforce_gtid_consistency=ON
replica_parallel_workers=4
replica_parallel_type=LOGICAL_CLOCK
skip-log-bin
log_replica_updates=OFF
innodb_buffer_pool_size=1G
innodb_flush_log_at_trx_commit=2
max_connections=3000
skip_name_resolve=1
character_set_server=utf8mb4
collation_server=utf8mb4_unicode_ci
default_time_zone='+8:00'
EOF

log_info "配置文件已更新 ✓"

# 6. 重新启动从库
log_info "启动从库1..."
docker run -d \
    --name mysql-slave-1 \
    --restart always \
    -p 3308:3306 \
    -v /opt/mysql/slave-1/data:/var/lib/mysql \
    -v /opt/mysql/slave-1/conf:/etc/mysql/conf.d \
    -v /opt/mysql/slave-1/init:/docker-entrypoint-initdb.d \
    -e MYSQL_ROOT_PASSWORD=${ROOT_PASSWORD} \
    mysql:8.0.43

log_info "启动从库2..."
docker run -d \
    --name mysql-slave-2 \
    --restart always \
    -p 3309:3306 \
    -v /opt/mysql/slave-2/data:/var/lib/mysql \
    -v /opt/mysql/slave-2/conf:/etc/mysql/conf.d \
    -v /opt/mysql/slave-2/init:/docker-entrypoint-initdb.d \
    -e MYSQL_ROOT_PASSWORD=${ROOT_PASSWORD} \
    mysql:8.0.43

log_info "等待从库初始化（60秒）..."
sleep 60

# 7. 测试从库连接
log_info "测试从库连接..."
if docker exec mysql-slave-1 mysql -uroot -p${ROOT_PASSWORD} -e "SELECT 1" &>/dev/null; then
    log_info "从库1连接成功 ✓"
else
    log_error "从库1连接失败"
    docker logs mysql-slave-1 --tail 30
    exit 1
fi

if docker exec mysql-slave-2 mysql -uroot -p${ROOT_PASSWORD} -e "SELECT 1" &>/dev/null; then
    log_info "从库2连接成功 ✓"
else
    log_error "从库2连接失败"
    docker logs mysql-slave-2 --tail 30
    exit 1
fi

# 8. 显示手动配置说明
echo ""
log_warn "=========================================="
log_warn "需要手动配置主从复制"
log_warn "=========================================="
echo ""
echo "从库已重新部署，现在需要手动配置复制。"
echo ""
echo "主库容器IP: ${master_ip}"
echo "主库容器端口: 3306"
echo ""
echo "请按照以下步骤操作："
echo ""
echo "=== 配置从库1 ==="
echo "1. 进入从库1："
echo "   docker exec -it mysql-slave-1 mysql -uroot -p${ROOT_PASSWORD}"
echo ""
echo "2. 在 mysql> 提示符下执行："
echo "   STOP REPLICA;"
echo "   RESET REPLICA ALL;"
echo "   RESET MASTER;"
echo "   CHANGE REPLICATION SOURCE TO"
echo "       SOURCE_HOST='${master_ip}',"
echo "       SOURCE_PORT=3306,"
echo "       SOURCE_USER='repl',"
echo "       SOURCE_PASSWORD='${REPL_PASSWORD}',"
echo "       SOURCE_AUTO_POSITION=1;"
echo "   START REPLICA;"
echo "   SHOW REPLICA STATUS\\G"
echo ""
echo "3. 检查输出："
echo "   - Replica_IO_Running: Yes"
echo "   - Replica_SQL_Running: Yes"
echo "   - Seconds_Behind_Source: 0"
echo ""
echo "4. 输入 exit 退出"
echo ""
echo "=== 配置从库2 ==="
echo "5. 进入从库2："
echo "   docker exec -it mysql-slave-2 mysql -uroot -p${ROOT_PASSWORD}"
echo ""
echo "6. 重复步骤2-4"
echo ""
log_warn "=========================================="
echo ""
echo "配置完成后，运行以下命令验证："
echo "  /opt/mysql/check_status.sh"
echo ""


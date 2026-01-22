#!/bin/bash
# MySQL 单服务器主从部署脚本 - CPU共用版
# 不限制CPU核心，所有容器共享CPU资源

set -e

# 配置参数
MASTER_PORT=3307
SLAVE_PORTS=(3308 3309)
ROOT_PASSWORD="zhiyu666"
REPL_PASSWORD="repl123"
MYSQL_VERSION="8.0.43"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "=========================================="
echo "  MySQL 单服务器主从部署 (CPU共用)"
echo "=========================================="
echo ""

# 1. 清理旧环境
log_info "清理旧环境..."
docker stop mysql-master mysql-slave-1 mysql-slave-2 2>/dev/null || true
docker rm mysql-master mysql-slave-1 mysql-slave-2 2>/dev/null || true

# 2. 创建目录
log_info "创建目录..."
mkdir -p /opt/mysql/master/{data,conf,init}
mkdir -p /opt/mysql/slave-1/{data,conf,init}
mkdir -p /opt/mysql/slave-2/{data,conf,init}

# 3. 生成主库配置
log_info "生成主库配置..."
cat > /opt/mysql/master/conf/my.cnf << 'EOF'
[mysqld]
server-id=1
port=3306
default_authentication_plugin=mysql_native_password
log_bin=/var/lib/mysql/mysql-bin
binlog_format=ROW
gtid_mode=ON
enforce_gtid_consistency=ON
sync_binlog=1
innodb_buffer_pool_size=6G
innodb_flush_log_at_trx_commit=1
max_connections=5000
skip_name_resolve=1
character_set_server=utf8mb4
collation_server=utf8mb4_unicode_ci
default_time_zone='+8:00'
EOF

cat > /opt/mysql/master/init/init.sql << EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${ROOT_PASSWORD}';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '${ROOT_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
CREATE USER IF NOT EXISTS 'repl'@'%' IDENTIFIED BY '${REPL_PASSWORD}';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
FLUSH PRIVILEGES;
EOF

# 4. 生成从库配置
for i in 1 2; do
    server_id=$((i + 1))
    log_info "生成从库${i}配置 (server-id=${server_id})..."
    
    cat > /opt/mysql/slave-${i}/conf/my.cnf << EOF
[mysqld]
server-id=${server_id}
port=3306
default_authentication_plugin=mysql_native_password
relay_log=/var/lib/mysql/mysql-relay-bin
gtid_mode=ON
enforce_gtid_consistency=ON
replica_parallel_workers=4
replica_parallel_type=LOGICAL_CLOCK
innodb_buffer_pool_size=3G
innodb_flush_log_at_trx_commit=2
max_connections=3000
skip_name_resolve=1
character_set_server=utf8mb4
collation_server=utf8mb4_unicode_ci
default_time_zone='+8:00'
EOF

    cat > /opt/mysql/slave-${i}/init/init.sql << EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${ROOT_PASSWORD}';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '${ROOT_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF
done

# 5. 启动主库（不限制CPU）
log_info "启动主库（端口${MASTER_PORT}，内存8G，CPU共用）..."
docker run -d \
    --name mysql-master \
    --restart always \
    -p ${MASTER_PORT}:3306 \
    -v /opt/mysql/master/data:/var/lib/mysql \
    -v /opt/mysql/master/conf:/etc/mysql/conf.d \
    -v /opt/mysql/master/init:/docker-entrypoint-initdb.d \
    -e MYSQL_ROOT_PASSWORD=${ROOT_PASSWORD} \
    --memory=8g \
    mysql:${MYSQL_VERSION}

log_info "等待主库启动（约60秒）..."
sleep 60

if docker exec mysql-master mysql -uroot -p${ROOT_PASSWORD} -e "SELECT 1" &>/dev/null; then
    log_info "主库启动成功 ✓"
else
    log_error "主库启动失败，查看日志："
    docker logs mysql-master --tail 30
    exit 1
fi

# 6. 启动从库（不限制CPU）
for i in 1 2; do
    port=${SLAVE_PORTS[$((i-1))]}
    log_info "启动从库${i}（端口${port}，内存4G，CPU共用）..."
    
    docker run -d \
        --name mysql-slave-${i} \
        --restart always \
        -p ${port}:3306 \
        -v /opt/mysql/slave-${i}/data:/var/lib/mysql \
        -v /opt/mysql/slave-${i}/conf:/etc/mysql/conf.d \
        -v /opt/mysql/slave-${i}/init:/docker-entrypoint-initdb.d \
        -e MYSQL_ROOT_PASSWORD=${ROOT_PASSWORD} \
        --memory=4g \
        mysql:${MYSQL_VERSION}
    
    log_info "等待从库${i}启动（约60秒）..."
    sleep 60
    
    if docker exec mysql-slave-${i} mysql -uroot -p${ROOT_PASSWORD} -e "SELECT 1" &>/dev/null; then
        log_info "从库${i}启动成功 ✓"
    else
        log_error "从库${i}启动失败"
        docker logs mysql-slave-${i} --tail 30
    fi
done

# 7. 配置主从复制
log_info "配置主从复制..."
master_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql-master)
if [ -z "$master_ip" ]; then
    master_ip=$(hostname -I | awk '{print $1}')
fi

log_info "主库IP: ${master_ip}"

for i in 1 2; do
    log_info "配置从库${i}..."
    
    docker exec mysql-slave-${i} mysql -uroot -p${ROOT_PASSWORD} << EOF
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='${master_ip}',
    SOURCE_PORT=${MASTER_PORT},
    SOURCE_USER='repl',
    SOURCE_PASSWORD='${REPL_PASSWORD}',
    SOURCE_AUTO_POSITION=1;
START REPLICA;
EOF
    
    log_info "从库${i}配置完成 ✓"
done

sleep 5

# 8. 验证部署
log_info "验证部署..."
echo ""
log_info "=== 容器状态 ==="
docker ps | grep mysql

echo ""
log_info "=== 主库状态 ==="
docker exec mysql-master mysql -uroot -p${ROOT_PASSWORD} -e "SHOW MASTER STATUS\G"

for i in 1 2; do
    echo ""
    log_info "=== 从库${i}状态 ==="
    status=$(docker exec mysql-slave-${i} mysql -uroot -p${ROOT_PASSWORD} -e "SHOW REPLICA STATUS\G" 2>/dev/null)
    io_running=$(echo "$status" | grep "Replica_IO_Running:" | awk '{print $2}')
    sql_running=$(echo "$status" | grep "Replica_SQL_Running:" | awk '{print $2}')
    seconds_behind=$(echo "$status" | grep "Seconds_Behind_Master:" | awk '{print $2}')
    
    if [ "$io_running" == "Yes" ] && [ "$sql_running" == "Yes" ]; then
        log_info "从库${i}: IO=Yes, SQL=Yes, 延迟=${seconds_behind}秒 ✓"
    else
        log_error "从库${i}: IO=${io_running}, SQL=${sql_running}"
        echo "$status" | grep -E "(Last_IO_Error|Last_SQL_Error)"
    fi
done

# 9. 测试数据同步
echo ""
log_info "测试数据同步..."
docker exec mysql-master mysql -uroot -p${ROOT_PASSWORD} << 'SQL'
CREATE DATABASE IF NOT EXISTS test_db;
USE test_db;
CREATE TABLE IF NOT EXISTS test_table (id INT PRIMARY KEY AUTO_INCREMENT, data VARCHAR(100));
INSERT INTO test_table (data) VALUES ('test1'), ('test2'), ('test3');
SQL

sleep 3

for i in 1 2; do
    count=$(docker exec mysql-slave-${i} mysql -uroot -p${ROOT_PASSWORD} -e "SELECT COUNT(*) FROM test_db.test_table;" -s -N 2>/dev/null)
    if [ "$count" == "3" ]; then
        log_info "从库${i}数据同步成功 (${count}条记录) ✓"
    else
        log_error "从库${i}数据同步失败"
    fi
done

# 10. 生成管理脚本
cat > /opt/mysql/check_status.sh << 'SCRIPT'
#!/bin/bash
echo "=== 容器状态 ==="
docker ps | grep mysql
echo ""
echo "=== 主库状态 ==="
docker exec mysql-master mysql -uroot -pzhiyu666 -e "SHOW MASTER STATUS\G"
echo ""
for i in 1 2; do
    echo "=== 从库${i}状态 ==="
    docker exec mysql-slave-${i} mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G" | grep -E "(Replica_IO_Running|Replica_SQL_Running|Seconds_Behind_Master)"
    echo ""
done
SCRIPT

cat > /opt/mysql/connect.sh << 'SCRIPT'
#!/bin/bash
case "$1" in
    master|m) docker exec -it mysql-master mysql -uroot -pzhiyu666 ;;
    slave1|s1|1) docker exec -it mysql-slave-1 mysql -uroot -pzhiyu666 ;;
    slave2|s2|2) docker exec -it mysql-slave-2 mysql -uroot -pzhiyu666 ;;
    *) 
        echo "用法: $0 {master|slave1|slave2}"
        echo "简写: $0 {m|s1|s2|1|2}"
        exit 1 
        ;;
esac
SCRIPT

chmod +x /opt/mysql/*.sh

echo ""
echo "=========================================="
log_info "部署完成！"
echo "=========================================="
echo ""
echo "资源分配："
echo "  主库: CPU共用/8G内存 (端口3307)"
echo "  从库1: CPU共用/4G内存 (端口3308)"
echo "  从库2: CPU共用/4G内存 (端口3309)"
echo "  总内存: 16G"
echo ""
echo "快速命令："
echo "  查看状态: /opt/mysql/check_status.sh"
echo "  连接主库: /opt/mysql/connect.sh master  (或 m)"
echo "  连接从库1: /opt/mysql/connect.sh slave1 (或 s1 或 1)"
echo "  连接从库2: /opt/mysql/connect.sh slave2 (或 s2 或 2)"
echo ""
echo "外部连接："
echo "  mysql -h127.0.0.1 -P3307 -uroot -p${ROOT_PASSWORD}  # 主库"
echo "  mysql -h127.0.0.1 -P3308 -uroot -p${ROOT_PASSWORD}  # 从库1"
echo "  mysql -h127.0.0.1 -P3309 -uroot -p${ROOT_PASSWORD}  # 从库2"
echo ""

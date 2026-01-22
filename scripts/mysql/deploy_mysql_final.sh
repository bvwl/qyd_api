#!/bin/bash
# MySQL 单服务器主从部署脚本 - 最终版
# CPU和内存共享，端口从3307开始

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
echo "  MySQL 单服务器主从部署"
echo "  CPU和内存共享"
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
innodb_buffer_pool_size=2G
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

    cat > /opt/mysql/slave-${i}/init/init.sql << EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${ROOT_PASSWORD}';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '${ROOT_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF
done

# 5. 启动主库（CPU和内存共享）
log_info "启动主库（端口${MASTER_PORT}，资源共享）..."
docker run -d \
    --name mysql-master \
    --restart always \
    -p ${MASTER_PORT}:3306 \
    -v /opt/mysql/master/data:/var/lib/mysql \
    -v /opt/mysql/master/conf:/etc/mysql/conf.d \
    -v /opt/mysql/master/init:/docker-entrypoint-initdb.d \
    -e MYSQL_ROOT_PASSWORD=${ROOT_PASSWORD} \
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

# 6. 启动从库（CPU和内存共享）
for i in 1 2; do
    port=${SLAVE_PORTS[$((i-1))]}
    log_info "启动从库${i}（端口${port}，资源共享）..."
    
    docker run -d \
        --name mysql-slave-${i} \
        --restart always \
        -p ${port}:3306 \
        -v /opt/mysql/slave-${i}/data:/var/lib/mysql \
        -v /opt/mysql/slave-${i}/conf:/etc/mysql/conf.d \
        -v /opt/mysql/slave-${i}/init:/docker-entrypoint-initdb.d \
        -e MYSQL_ROOT_PASSWORD=${ROOT_PASSWORD} \
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

# 7. 获取主库容器IP并保存
master_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql-master)
if [ -z "$master_ip" ]; then
    log_error "无法获取主库容器IP"
    exit 1
fi

log_info "主库容器IP: ${master_ip}"
log_info "主库容器端口: 3306 (容器内部)"
echo "${master_ip}" > /tmp/mysql_master_ip.txt

echo ""
log_warn "=========================================="
log_warn "重要提示：需要手动配置主从复制"
log_warn "=========================================="
echo ""
echo "由于从库容器初始化时会重启MySQL，通过脚本配置的复制信息会丢失。"
echo "请按照以下步骤手动配置每个从库："
echo ""
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
echo "   exit"
echo ""
echo "3. 对从库2重复相同操作："
echo "   docker exec -it mysql-slave-2 mysql -uroot -p${ROOT_PASSWORD}"
echo ""
log_warn "=========================================="
echo ""

# 8. 验证部署
log_info "验证部署..."
echo ""
log_info "=== 容器状态 ==="
docker ps | grep mysql

echo ""
log_info "=== 主库状态 ==="
docker exec mysql-master mysql -uroot -p${ROOT_PASSWORD} -e "SHOW MASTER STATUS\G" 2>/dev/null

for i in 1 2; do
    echo ""
    log_info "=== 从库${i}状态 ==="
    status=$(docker exec mysql-slave-${i} mysql -uroot -p${ROOT_PASSWORD} -e "SHOW REPLICA STATUS\G" 2>/dev/null)
    
    if [ -z "$status" ]; then
        log_error "从库${i}没有复制状态"
        continue
    fi
    
    io_running=$(echo "$status" | grep "Replica_IO_Running:" | awk '{print $2}')
    sql_running=$(echo "$status" | grep "Replica_SQL_Running:" | awk '{print $2}')
    seconds_behind=$(echo "$status" | grep "Seconds_Behind_Master:" | awk '{print $2}')
    last_io_error=$(echo "$status" | grep "Last_IO_Error:" | cut -d: -f2-)
    last_sql_error=$(echo "$status" | grep "Last_SQL_Error:" | cut -d: -f2-)
    
    echo "IO线程: ${io_running}"
    echo "SQL线程: ${sql_running}"
    echo "延迟: ${seconds_behind}秒"
    
    if [ "$io_running" == "Yes" ] && [ "$sql_running" == "Yes" ]; then
        log_info "从库${i}复制正常 ✓"
    else
        log_error "从库${i}复制异常 ✗"
        if [ -n "$last_io_error" ] && [ "$last_io_error" != " " ]; then
            echo "IO错误: ${last_io_error}"
        fi
        if [ -n "$last_sql_error" ] && [ "$last_sql_error" != " " ]; then
            echo "SQL错误: ${last_sql_error}"
        fi
    fi
done

# 9. 测试数据同步
echo ""
log_info "测试数据同步..."
docker exec mysql-master mysql -uroot -p${ROOT_PASSWORD} << 'SQL' 2>/dev/null
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
        log_error "从库${i}数据同步失败 (实际${count}条记录)"
    fi
done

# 10. 生成管理脚本
cat > /opt/mysql/check_status.sh << 'SCRIPT'
#!/bin/bash
echo "=========================================="
echo "  MySQL主从状态检查"
echo "=========================================="
echo ""
echo "=== 容器状态 ==="
docker ps | grep mysql
echo ""
echo "=== 主库状态 ==="
docker exec mysql-master mysql -uroot -pzhiyu666 -e "SHOW MASTER STATUS\G" 2>/dev/null
echo ""
for i in 1 2; do
    echo "=== 从库${i}状态 ==="
    docker exec mysql-slave-${i} mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G" 2>/dev/null | grep -E "(Replica_IO_Running|Replica_SQL_Running|Seconds_Behind_Master|Last_IO_Error|Last_SQL_Error)"
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
echo "资源配置："
echo "  CPU: 所有容器共享"
echo "  内存: 所有容器共享"
echo ""
echo "端口映射："
echo "  主库: localhost:3307 -> 容器3306"
echo "  从库1: localhost:3308 -> 容器3306"
echo "  从库2: localhost:3309 -> 容器3306"
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

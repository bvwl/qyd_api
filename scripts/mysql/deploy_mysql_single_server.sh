#!/bin/bash
# MySQL 单服务器主从一键部署脚本

set -e

# ==================== 配置参数 ====================
MASTER_HOST="127.0.0.1"
MYSQL_VERSION="8.0.43"
ROOT_PASSWORD="zhiyu666"
REPL_PASSWORD="repl123"
ADMIN_PASSWORD="admin123"

SLAVE_COUNT=2
MASTER_PORT=3307
SLAVE_PORTS=(3308 3309)

MASTER_MEMORY="8g"
MASTER_CPUS="3"
SLAVE_MEMORY="4g"
SLAVE_CPUS="1.5"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 未安装"
        exit 1
    fi
}

wait_for_mysql() {
    container_name=$1
    max_attempts=60
    attempt=0
    
    log_info "等待 $container_name MySQL启动..."
    
    while [ $attempt -lt $max_attempts ]; do
        if docker exec $container_name mysql -uroot -p${ROOT_PASSWORD} -e "SELECT 1" &>/dev/null; then
            log_info "$container_name MySQL已就绪 ✓"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    log_error "$container_name MySQL启动超时"
    return 1
}

# 环境检查
check_environment() {
    log_info "检查部署环境..."
    check_command docker
    
    if ! systemctl is-active --quiet docker; then
        log_error "Docker服务未运行"
        exit 1
    fi
    
    log_info "环境检查通过 ✓"
}

# 清理旧环境
cleanup_old_deployment() {
    log_info "清理旧的部署..."
    
    if docker ps -a | grep -q mysql-master; then
        log_warn "删除旧的主库容器..."
        docker stop mysql-master 2>/dev/null || true
        docker rm mysql-master 2>/dev/null || true
    fi
    
    for i in $(seq 1 $SLAVE_COUNT); do
        if docker ps -a | grep -q mysql-slave-${i}; then
            log_warn "删除旧的从库容器 mysql-slave-${i}..."
            docker stop mysql-slave-${i} 2>/dev/null || true
            docker rm mysql-slave-${i} 2>/dev/null || true
        fi
    done
    
    log_info "旧环境清理完成 ✓"
}

# 创建目录
create_directories() {
    log_info "创建目录结构..."
    
    mkdir -p /opt/mysql/master/{data,conf,init}
    mkdir -p /var/lib/mysql-files
    
    for i in $(seq 1 $SLAVE_COUNT); do
        mkdir -p /opt/mysql/slave-${i}/{data,conf,init}
    done
    
    log_info "目录创建完成 ✓"
}

# 生成主库配置
generate_master_config() {
    log_info "生成主库配置..."
    
    cat > /opt/mysql/master/conf/my.cnf << 'CONF'
[mysqld]
server-id=1
port=3306
default_authentication_plugin=mysql_native_password

# 主从复制
log_bin=/var/lib/mysql/mysql-bin
binlog_format=ROW
gtid_mode=ON
enforce_gtid_consistency=ON
sync_binlog=1

# InnoDB
innodb_buffer_pool_size=6G
innodb_flush_log_at_trx_commit=1
innodb_flush_method=O_DIRECT

# 连接
max_connections=5000
skip_name_resolve=1

# 字符集
character_set_server=utf8mb4
collation_server=utf8mb4_unicode_ci
default_time_zone='+8:00'
CONF

    cat > /opt/mysql/master/init/init.sql << EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${ROOT_PASSWORD}';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '${ROOT_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

CREATE USER IF NOT EXISTS 'repl'@'%' IDENTIFIED BY '${REPL_PASSWORD}';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';

FLUSH PRIVILEGES;
EOF

    log_info "主库配置生成完成 ✓"
}

# 生成从库配置
generate_slave_configs() {
    log_info "生成从库配置..."
    
    for i in $(seq 1 $SLAVE_COUNT); do
        server_id=$((i + 1))
        
        cat > /opt/mysql/slave-${i}/conf/my.cnf << EOF
[mysqld]
server-id=${server_id}
port=3306
default_authentication_plugin=mysql_native_password

# 主从复制
relay_log=/var/lib/mysql/mysql-relay-bin
gtid_mode=ON
enforce_gtid_consistency=ON
replica_parallel_workers=8
replica_parallel_type=LOGICAL_CLOCK

# InnoDB
innodb_buffer_pool_size=3G
innodb_flush_log_at_trx_commit=2
innodb_flush_method=O_DIRECT

# 连接
max_connections=3000
skip_name_resolve=1

# 字符集
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

        log_info "从库${i}配置生成完成 (server-id=${server_id}) ✓"
    done
}

# 启动主库
start_master() {
    log_info "启动主库容器（端口${MASTER_PORT}）..."
    
    docker run -d \
        --name mysql-master \
        --restart always \
        -p ${MASTER_PORT}:3306 \
        -v /opt/mysql/master/data:/var/lib/mysql \
        -v /opt/mysql/master/conf:/etc/mysql/conf.d \
        -v /opt/mysql/master/init:/docker-entrypoint-initdb.d \
        -e MYSQL_ROOT_PASSWORD=${ROOT_PASSWORD} \
        --memory=8g \
        --cpus=3 \
        mysql:${MYSQL_VERSION}
    
    if ! wait_for_mysql "mysql-master"; then
        log_error "主库启动失败"
        docker logs mysql-master --tail 50
        exit 1
    fi
}

# 启动从库
start_slaves() {
    log_info "启动从库容器..."
    
    for i in $(seq 1 $SLAVE_COUNT); do
        port=${SLAVE_PORTS[$((i-1))]}
        
        log_info "启动从库${i} (端口${port})..."
        
        docker run -d \
            --name mysql-slave-${i} \
            --restart always \
            -p ${port}:3306 \
            -v /opt/mysql/slave-${i}/data:/var/lib/mysql \
            -v /opt/mysql/slave-${i}/conf:/etc/mysql/conf.d \
            -v /opt/mysql/slave-${i}/init:/docker-entrypoint-initdb.d \
            -e MYSQL_ROOT_PASSWORD=${ROOT_PASSWORD} \
            --memory=4g \
            --cpus=1.5 \
            mysql:${MYSQL_VERSION}
        
        if ! wait_for_mysql "mysql-slave-${i}"; then
            log_error "从库${i}启动失败"
            docker logs mysql-slave-${i} --tail 50
            exit 1
        fi
    done
}

# 配置主从复制
configure_replication() {
    log_info "配置主从复制..."
    
    # 获取主库IP
    master_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql-master)
    if [ -z "$master_ip" ]; then
        master_ip=$(hostname -I | awk '{print $1}')
    fi
    
    log_info "主库IP: ${master_ip}"
    
    for i in $(seq 1 $SLAVE_COUNT); do
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
}

# 验证部署
verify_deployment() {
    log_info "验证部署状态..."
    
    echo ""
    log_info "=== 主库状态 ==="
    docker exec mysql-master mysql -uroot -p${ROOT_PASSWORD} -e "SHOW MASTER STATUS\G"
    
    echo ""
    for i in $(seq 1 $SLAVE_COUNT); do
        log_info "=== 从库${i}状态 ==="
        
        status=$(docker exec mysql-slave-${i} mysql -uroot -p${ROOT_PASSWORD} -e "SHOW REPLICA STATUS\G" 2>/dev/null)
        
        io_running=$(echo "$status" | grep "Replica_IO_Running:" | awk '{print $2}')
        sql_running=$(echo "$status" | grep "Replica_SQL_Running:" | awk '{print $2}')
        seconds_behind=$(echo "$status" | grep "Seconds_Behind_Master:" | awk '{print $2}')
        
        if [ "$io_running" == "Yes" ] && [ "$sql_running" == "Yes" ]; then
            log_info "从库${i}: IO=Yes, SQL=Yes, 延迟=${seconds_behind}秒 ✓"
        else
            log_error "从库${i}: IO=${io_running}, SQL=${sql_running} ✗"
        fi
    done
}

# 测试同步
test_replication() {
    log_info "测试数据同步..."
    
    docker exec mysql-master mysql -uroot -p${ROOT_PASSWORD} << 'SQL'
CREATE DATABASE IF NOT EXISTS test_replication;
USE test_replication;
CREATE TABLE IF NOT EXISTS test_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO test_table (data) VALUES ('test1'), ('test2'), ('test3');
SQL

    sleep 3
    
    for i in $(seq 1 $SLAVE_COUNT); do
        count=$(docker exec mysql-slave-${i} mysql -uroot -p${ROOT_PASSWORD} -e "SELECT COUNT(*) FROM test_replication.test_table;" -s -N 2>/dev/null)
        
        if [ "$count" == "3" ]; then
            log_info "从库${i}数据同步成功 (${count}条记录) ✓"
        else
            log_error "从库${i}数据同步失败 ✗"
        fi
    done
}

# 生成管理脚本
generate_scripts() {
    log_info "生成管理脚本..."
    
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
docker exec mysql-master mysql -uroot -pzhiyu666 -e "SHOW MASTER STATUS\G"
echo ""
for i in {1..2}; do
    echo "=== 从库${i}状态 ==="
    docker exec mysql-slave-${i} mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G" 2>/dev/null | grep -E "(Replica_IO_Running|Replica_SQL_Running|Seconds_Behind_Master)"
    echo ""
done
SCRIPT

    cat > /opt/mysql/connect.sh << 'SCRIPT'
#!/bin/bash
case "$1" in
    master|m) docker exec -it mysql-master mysql -uroot -pzhiyu666 ;;
    slave1|s1|1) docker exec -it mysql-slave-1 mysql -uroot -pzhiyu666 ;;
    slave2|s2|2) docker exec -it mysql-slave-2 mysql -uroot -pzhiyu666 ;;
    *) echo "用法: $0 {master|slave1|slave2}"; exit 1 ;;
esac
SCRIPT

    chmod +x /opt/mysql/*.sh
    log_info "管理脚本生成完成 ✓"
}

# 主函数
main() {
    echo "=========================================="
    echo "  MySQL 单服务器主从部署"
    echo "=========================================="
    echo ""
    
    check_environment
    cleanup_old_deployment
    create_directories
    generate_master_config
    generate_slave_configs
    start_master
    start_slaves
    configure_replication
    verify_deployment
    test_replication
    generate_scripts
    
    echo ""
    echo "=========================================="
    log_info "部署完成！"
    echo "=========================================="
    echo ""
    echo "容器列表："
    docker ps | grep mysql
    echo ""
    echo "快速命令："
    echo "  查看状态: /opt/mysql/check_status.sh"
    echo "  连接主库: /opt/mysql/connect.sh master"
    echo "  连接从库1: /opt/mysql/connect.sh slave1"
    echo ""
    echo "端口映射："
    echo "  主库: localhost:3307"
    echo "  从库1: localhost:3308"
    echo "  从库2: localhost:3309"
    echo ""
}

main "$@"

# MySQL 8.0 单服务器主从复制快速部署指南

## 📋 概述

本指南专门针对**单台服务器部署MySQL主从复制**的场景，适用于：
- 🧪 测试环境
- 💻 开发环境
- 📚 学习和演示
- 🔬 功能验证

> **⚠️ 重要提示**
> 
> 1. **资源配置**：脚本使用CPU和内存共享模式，所有容器共享服务器资源
> 2. **端口配置**：主库3307，从库3308、3309（映射到容器内部3306）
> 3. **主从复制关键**：从库连接主库必须使用**容器IP和容器端口3306**，不是宿主机端口3307！
> 4. **最低要求**：建议至少6C/8G配置

## 🏗️ 架构说明

### 部署架构
```
┌─────────────────────────────────────────────┐
│         单台服务器 (192.168.11.150)          │
│                                             │
│  ┌──────────────┐                          │
│  │  mysql-master │  端口: 3307             │
│  │  (主库容器)   │                          │
│  └──────┬───────┘                          │
│         │                                   │
│         ├─────────┬──────────┐             │
│         │         │          │             │
│  ┌──────▼──┐ ┌───▼────┐     │             │
│  │ slave-1 │ │ slave-2│     │             │
│  │ 端口3308│ │ 端口3309│     │             │
│  └─────────┘ └────────┘     │             │
│                              │             │
└──────────────────────────────┘             │
```

### 端口分配
- **主库**：3307
- **从库1**：3308
- **从库2**：3309

### 资源配置
- **CPU和内存**：所有容器共享服务器资源（不限制）
- **最低配置**：6C/8G
- **推荐配置**：8C/16G 或更高
- **说明**：脚本不对容器设置CPU和内存限制，由Docker自动管理资源分配

## 🚀 一键部署

### 1. 下载部署脚本

```bash
# 创建部署目录
mkdir -p /opt/mysql_deploy
cd /opt/mysql_deploy

# 创建部署脚本
cat > deploy_mysql_single_server.sh << 'EOF'
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
cat > /opt/mysql/master/conf/my.cnf << 'CONF'
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
CONF

cat > /opt/mysql/master/init/init.sql << INIT
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${ROOT_PASSWORD}';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '${ROOT_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
CREATE USER IF NOT EXISTS 'repl'@'%' IDENTIFIED BY '${REPL_PASSWORD}';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
FLUSH PRIVILEGES;
INIT

# 4. 生成从库配置
for i in 1 2; do
    server_id=$((i + 1))
    log_info "生成从库${i}配置 (server-id=${server_id})..."
    
    cat > /opt/mysql/slave-${i}/conf/my.cnf << CONF
[mysqld]
server-id=${server_id}
port=3306
default_authentication_plugin=mysql_native_password
relay_log=/var/lib/mysql/mysql-relay-bin
gtid_mode=ON
enforce_gtid_consistency=ON
replica_parallel_workers=4
replica_parallel_type=LOGICAL_CLOCK
innodb_buffer_pool_size=1G
innodb_flush_log_at_trx_commit=2
max_connections=3000
skip_name_resolve=1
character_set_server=utf8mb4
collation_server=utf8mb4_unicode_ci
default_time_zone='+8:00'
CONF

    cat > /opt/mysql/slave-${i}/init/init.sql << INIT
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${ROOT_PASSWORD}';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '${ROOT_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
INIT
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

# 7. 配置主从复制（关键修复：使用容器IP和容器端口3306）
log_info "配置主从复制..."

# 获取主库容器IP
master_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql-master)
if [ -z "$master_ip" ]; then
    log_error "无法获取主库容器IP"
    exit 1
fi

log_info "主库容器IP: ${master_ip}"
log_info "主库容器端口: 3306 (容器内部)"

for i in 1 2; do
    log_info "配置从库${i}..."
    
    # 使用容器IP和容器端口3306（不是宿主机端口3307）
    docker exec mysql-slave-${i} mysql -uroot -p${ROOT_PASSWORD} << SQL
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='${master_ip}',
    SOURCE_PORT=3306,
    SOURCE_USER='repl',
    SOURCE_PASSWORD='${REPL_PASSWORD}',
    SOURCE_AUTO_POSITION=1;
START REPLICA;
SQL
    
    if [ $? -eq 0 ]; then
        log_info "从库${i}配置完成 ✓"
    else
        log_error "从库${i}配置失败"
    fi
done

sleep 5

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
EOF

chmod +x deploy_mysql_single_server.sh
```

### 2. 执行部署

```bash
# 运行部署脚本
sudo ./deploy_mysql_single_server.sh
```

部署过程大约需要 3-5 分钟，脚本会自动完成：
- ✅ 环境检查
- ✅ 清理旧环境
- ✅ 创建目录结构
- ✅ 生成配置文件
- ✅ 启动主库和从库
- ✅ 配置主从复制
- ✅ 验证部署状态
- ✅ 测试数据同步

### 3. 验证部署

```bash
# 检查容器状态
docker ps | grep mysql

# 检查主从状态
/opt/mysql/check_status.sh
```

## 📊 使用指南

### 连接数据库

```bash
# 连接主库（写操作）
/opt/mysql/connect.sh master
# 或
mysql -h127.0.0.1 -P3307 -uroot -pzhiyu666

# 连接从库1（读操作）
/opt/mysql/connect.sh slave1
# 或
mysql -h127.0.0.1 -P3308 -uroot -pzhiyu666

# 连接从库2
mysql -h127.0.0.1 -P3309 -uroot -pzhiyu666
```

### 查看状态

```bash
# 查看主从状态
/opt/mysql/check_status.sh

# 查看主库状态
docker exec mysql-master mysql -uroot -pzhiyu666 -e "SHOW MASTER STATUS\G"

# 查看从库1状态
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G"
```

### 测试读写分离

```bash
# 在主库写入数据
docker exec mysql-master mysql -uroot -pzhiyu666 << 'EOF'
CREATE DATABASE test_db;
USE test_db;
CREATE TABLE users (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(50));
INSERT INTO users (name) VALUES ('Alice'), ('Bob'), ('Charlie');
EOF

# 在从库读取数据
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SELECT * FROM test_db.users;"
docker exec mysql-slave-2 mysql -uroot -pzhiyu666 -e "SELECT * FROM test_db.users;"
```

## 🔧 常见问题

### 1. 从库复制失败或数据不同步

**症状**：
- `SHOW REPLICA STATUS\G` 返回空结果
- 或者复制状态显示正常但数据不同步
- `Executed_Gtid_Set` 包含从库自己的UUID

**根本原因**：
1. 从库在初始化时执行 `init.sql`，产生了自己的GTID事务
2. 从库容器初始化完成后MySQL会重启
3. 通过脚本在容器外执行的 `CHANGE REPLICATION SOURCE TO` 在重启后丢失
4. 从库的GTID集合包含了自己的事务，导致与主库GTID不一致

**解决方法**：

**方法1：使用修复脚本（推荐）**

```bash
# 下载并运行修复脚本
chmod +x fix_replication.sh
sudo ./fix_replication.sh
```

修复脚本会：
- 停止并删除从库容器
- 清理从库数据
- 更新配置文件（添加 `skip-log-bin` 和 `log_replica_updates=OFF`）
- 重新启动从库
- 提示你手动配置复制

**方法2：手动修复**

```bash
# 1. 获取主库容器IP
master_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql-master)
echo "主库容器IP: $master_ip"

# 2. 进入从库MySQL交互界面（重要！必须手动进入）
docker exec -it mysql-slave-1 mysql -uroot -pzhiyu666

# 3. 在 mysql> 提示符下执行以下命令
STOP REPLICA;
RESET REPLICA ALL;
RESET MASTER;  -- 清除从库自己的GTID
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='172.17.0.2',  -- 使用主库容器IP
    SOURCE_PORT=3306,           -- 容器端口，不是3307！
    SOURCE_USER='repl',
    SOURCE_PASSWORD='repl123',
    SOURCE_AUTO_POSITION=1;
START REPLICA;
SHOW REPLICA STATUS\G
exit

# 4. 对从库2重复相同操作
docker exec -it mysql-slave-2 mysql -uroot -pzhiyu666
# 然后执行步骤3的SQL命令
```

**为什么必须手动进入MySQL交互界面配置**：
- ❌ 错误方式：`docker exec mysql-slave-1 mysql ... << EOF` （配置会在重启后丢失）
- ✅ 正确方式：`docker exec -it mysql-slave-1 mysql` 然后在 `mysql>` 提示符下执行（配置会被持久化）

**端口说明**：
- 宿主机端口映射：`-p 3307:3306` 表示宿主机3307映射到容器3306
- 外部访问主库：`mysql -h127.0.0.1 -P3307` （使用宿主机端口）
- 容器间通信：使用容器IP和容器端口3306（Docker内部网络）

**预防措施（重新部署时）**：
在从库配置文件中添加以下配置，避免从库产生自己的GTID：
```ini
skip-log-bin
log_replica_updates=OFF
```

### 2. 端口冲突

```bash
# 检查端口占用
netstat -tlnp | grep 3307
netstat -tlnp | grep 3308
netstat -tlnp | grep 3309

# 停止占用端口的容器
docker stop <container_name>
```

### 3. 内存不足

由于脚本使用资源共享模式，容器会自动使用可用内存。如果需要限制：

```bash
# 手动限制容器内存（可选）
docker update --memory 4g mysql-master
docker update --memory 2g mysql-slave-1
docker update --memory 2g mysql-slave-2
```

### 4. 重启所有容器

```bash
# 重启主库
docker restart mysql-master

# 重启所有从库
docker restart mysql-slave-1 mysql-slave-2

# 等待启动完成
sleep 30

# 检查状态
/opt/mysql/check_status.sh
```

## 🗑️ 清理环境

```bash
# 停止所有容器
docker stop mysql-master mysql-slave-1 mysql-slave-2

# 删除所有容器
docker rm mysql-master mysql-slave-1 mysql-slave-2

# 删除数据（谨慎操作！）
rm -rf /opt/mysql/master/data/*
rm -rf /opt/mysql/slave-1/data/*
rm -rf /opt/mysql/slave-2/data/*
```

## 📈 性能优化建议

### 单服务器资源分配

**资源共享模式（默认）：**
- 所有容器共享服务器CPU和内存
- Docker自动管理资源分配
- 适合测试和开发环境

**如需手动限制资源：**

**8C/16G 服务器建议：**
```bash
docker update --memory 8g --cpus 4 mysql-master
docker update --memory 4g --cpus 2 mysql-slave-1
docker update --memory 4g --cpus 2 mysql-slave-2
```

**16C/32G 服务器建议：**
```bash
docker update --memory 12g --cpus 8 mysql-master
docker update --memory 8g --cpus 4 mysql-slave-1
docker update --memory 8g --cpus 4 mysql-slave-2
```

### 配置调优

根据实际负载调整 `/opt/mysql/master/conf/my.cnf` 和从库配置文件中的参数：

```ini
# 主库优化（根据实际内存调整）
innodb_buffer_pool_size=4G    # 物理内存的50-70%
max_connections=5000           # 根据并发需求调整

# 从库优化
innodb_buffer_pool_size=2G     # 物理内存的50-70%
replica_parallel_workers=8     # CPU核心数的2倍
```

## 🎯 总结

单服务器部署方案适合：
- ✅ 快速搭建测试环境
- ✅ 学习MySQL主从复制
- ✅ 开发环境的读写分离
- ✅ 功能验证和压力测试

不适合：
- ❌ 生产环境高可用
- ❌ 大规模并发场景
- ❌ 需要物理隔离的场景

如需生产环境部署，请参考完整文档中的**方案二：多服务器部署**。

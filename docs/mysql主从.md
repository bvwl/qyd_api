# 🚀 MySQL 8.0 高并发一主多从复制部署文档（Docker）

## 一、环境说明

### 基础环境
- 主库服务器：`192.168.11.150`
- MySQL 镜像：`mysql:8.0.43`
- 硬件：`56C/16G`
- **性能目标**：支持上万并发连接，实现毫秒级主从同步延迟

### 从库部署方案
**方案一：单服务器多容器（推荐用于测试环境）**
- 主库和从库：同一台服务器（如：`192.168.11.150`）
- 容器配置：`mysql-master`、`mysql-slave-1`、`mysql-slave-2`
- 端口映射：主库 `3306`、从库1 `3307`、从库2 `3308`
- **适用场景**：测试环境、开发环境、学习环境
- **注意**：单服务器多容器会共享系统资源，生产环境建议使用方案二

**方案二：多服务器部署（推荐用于生产环境）**
- 从库服务器1：`192.168.11.151`
- 从库服务器2：`192.168.11.152`
- 从库服务器3：`192.168.11.153`
- 每台服务器端口：`3306`
- **优势**：资源隔离，更好的性能和稳定性

------

## 二、目录准备

### 主库目录（192.168.11.150）
```bash
mkdir -p /opt/mysql/master/data /opt/mysql/master/conf /opt/mysql/master/init
```

### 从库目录准备

**方案一：单服务器多容器（同一台服务器，如：192.168.11.150）**
```bash
# 创建两个从库目录（一主两从）
mkdir -p /opt/mysql/slave-1/{data,conf,init}
mkdir -p /opt/mysql/slave-2/{data,conf,init}
```

**方案二：多服务器部署**
```bash
# 在每台从库服务器执行
# 192.168.11.151
mkdir -p /opt/mysql/slave/data /opt/mysql/slave/conf /opt/mysql/slave/init

# 192.168.11.152
mkdir -p /opt/mysql/slave/data /opt/mysql/slave/conf /opt/mysql/slave/init

# 192.168.11.153
mkdir -p /opt/mysql/slave/data /opt/mysql/slave/conf /opt/mysql/slave/init
```

------

## 三、主库配置（192.168.11.150）

### 1. 高并发优化的 `my.cnf`

```bash
cat > /opt/mysql/master/conf/my.cnf << EOF
[mysqld]
server-id=1
datadir=/var/lib/mysql
socket=/var/run/mysqld/mysqld.sock
pid-file=/var/run/mysqld/mysqld.pid
user=mysql
port=3306

default_authentication_plugin=mysql_native_password

# ========== 网络连接稳定性优化 ==========
# 连接超时设置
connect_timeout=60
interactive_timeout=7200
wait_timeout=7200
net_read_timeout=120
net_write_timeout=120
# 网络重试机制
slave_net_timeout=60
# 最大错误连接数
max_connect_errors=100000
# 跳过域名解析，提升连接速度
skip_name_resolve=1

# ========== 主从复制高性能配置 ==========
log_bin=/var/lib/mysql/mysql-bin
binlog_format=ROW
# 高并发下的同步设置（平衡性能与安全）
sync_binlog=1
# binlog缓存优化，支持大事务
binlog_cache_size=8M
max_binlog_cache_size=128M
# binlog文件大小优化
max_binlog_size=512M
binlog_expire_logs_seconds=259200
# GTID配置
gtid_mode=ON
enforce_gtid_consistency=ON
# 主库并行复制优化
binlog_transaction_dependency_tracking=WRITESET
transaction_write_set_extraction=XXHASH64
# 半同步复制配置（可选，提升数据安全性）
# rpl_semi_sync_master_enabled=1
# rpl_semi_sync_master_timeout=1000

# ========== InnoDB 高并发优化 ==========
innodb_buffer_pool_size=12G
innodb_buffer_pool_instances=16
innodb_log_buffer_size=128M
innodb_flush_log_at_trx_commit=1
innodb_flush_method=O_DIRECT
innodb_file_per_table=1
innodb_open_files=8192
# IO性能优化
innodb_io_capacity=4000
innodb_io_capacity_max=8000
innodb_flush_neighbors=0
innodb_read_io_threads=16
innodb_write_io_threads=16
# 锁优化
innodb_lock_wait_timeout=50
innodb_deadlock_detect=ON
# 日志文件优化
innodb_log_file_size=2G
innodb_log_files_in_group=2

# ========== 高并发连接优化 ==========
max_connections=10000
max_user_connections=9500
thread_cache_size=512
thread_stack=512K
# 连接处理优化
back_log=2048
# 表缓存优化
table_open_cache=8192
table_open_cache_instances=32
table_definition_cache=4096

# ========== 内存和缓存优化 ==========
# 临时表优化
tmp_table_size=128M
max_heap_table_size=128M
# 排序和连接缓存
sort_buffer_size=8M
join_buffer_size=8M
read_buffer_size=4M
read_rnd_buffer_size=8M
# 查询缓存（MySQL 8.0已移除，此处为兼容性保留）
# query_cache_size=0
# query_cache_type=OFF

# ========== 监控和日志配置 ==========
# 慢查询日志
slow_query_log=1
slow_query_log_file=/var/lib/mysql/mysql-slow.log
long_query_time=0.5
log_queries_not_using_indexes=1
log_throttle_queries_not_using_indexes=10
# 错误日志
log_error=/var/lib/mysql/mysql-error.log
log_error_verbosity=2
# 通用查询日志（生产环境建议关闭）
general_log=0
# 性能监控
performance_schema=ON
performance_schema_max_table_instances=12500
performance_schema_max_table_handles=4000

# ========== 其他优化参数 ==========
max_allowed_packet=128M
open_files_limit=65535
# 字符集
character_set_server=utf8mb4
collation_server=utf8mb4_unicode_ci
# 时区
default_time_zone='+8:00'
# 安全设置
local_infile=0
secure_file_priv=/var/lib/mysql-files/

# ========== 复制监控参数 ==========
# 启用复制相关的状态变量
log_slave_updates=1
relay_log_info_repository=TABLE
master_info_repository=TABLE
EOF
```

------

### 2. 增强的初始化 SQL（创建用户和监控）

```bash
cat > /opt/mysql/master/init/init.sql << EOF
-- 修改 root 用户，允许远程访问
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'zhiyu666';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY 'zhiyu666';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

-- 创建独立管理用户
CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY 'admin123';
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;

-- 创建复制用户（支持多个从库连接，增强安全性）
CREATE USER IF NOT EXISTS 'repl'@'192.168.11.61' IDENTIFIED BY 'repl123';
CREATE USER IF NOT EXISTS 'repl'@'192.168.11.62' IDENTIFIED BY 'repl123';
CREATE USER IF NOT EXISTS 'repl'@'192.168.11.63' IDENTIFIED BY 'repl123';
CREATE USER IF NOT EXISTS 'repl'@'%' IDENTIFIED BY 'repl123';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'192.168.11.61';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'192.168.11.62';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'192.168.11.63';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';

-- 创建监控用户（用于监控系统）
CREATE USER IF NOT EXISTS 'monitor'@'%' IDENTIFIED BY 'monitor123';
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'monitor'@'%';
GRANT SELECT ON performance_schema.* TO 'monitor'@'%';
GRANT SELECT ON information_schema.* TO 'monitor'@'%';

-- 创建数据一致性检查用户
CREATE USER IF NOT EXISTS 'checksum'@'%' IDENTIFIED BY 'checksum123';
GRANT SELECT ON *.* TO 'checksum'@'%';

-- 创建监控数据库和表
CREATE DATABASE IF NOT EXISTS mysql_monitor;
USE mysql_monitor;

-- 主从同步状态监控表
CREATE TABLE IF NOT EXISTS replication_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    slave_host VARCHAR(50),
    slave_port INT,
    io_running VARCHAR(10),
    sql_running VARCHAR(10),
    seconds_behind_master INT,
    last_io_error TEXT,
    last_sql_error TEXT,
    gtid_executed TEXT,
    INDEX idx_check_time (check_time),
    INDEX idx_slave (slave_host, slave_port)
);

-- 性能监控表
CREATE TABLE IF NOT EXISTS performance_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metric_name VARCHAR(100),
    metric_value BIGINT,
    server_type ENUM('master', 'slave'),
    server_host VARCHAR(50),
    INDEX idx_check_time (check_time),
    INDEX idx_metric (metric_name)
);

-- 数据一致性检查表
CREATE TABLE IF NOT EXISTS consistency_check (
    id INT AUTO_INCREMENT PRIMARY KEY,
    check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    database_name VARCHAR(64),
    table_name VARCHAR(64),
    master_checksum VARCHAR(32),
    slave_checksum VARCHAR(32),
    slave_host VARCHAR(50),
    is_consistent BOOLEAN,
    INDEX idx_check_time (check_time),
    INDEX idx_table (database_name, table_name)
);

FLUSH PRIVILEGES;
EOF
```

------

### 3. 启动容器（增强版）

```bash
# 创建必要的目录
mkdir -p /var/lib/mysql-files

# 启动主库容器，添加网络和资源限制
docker run -d \
  --name mysql-master \
  --restart always \
  --network host \
  -p 3306:3306 \
  -v /opt/mysql/master/data:/var/lib/mysql \
  -v /opt/mysql/master/conf:/etc/mysql/conf.d \
  -v /opt/mysql/master/init:/docker-entrypoint-initdb.d \
  -v /var/lib/mysql-files:/var/lib/mysql-files \
  -e MYSQL_ROOT_PASSWORD=zhiyu666 \
  --memory=14g \
  --cpus=48 \
  --ulimit nofile=65535:65535 \
  mysql:8.0.43

# 等待容器启动完成
echo "等待MySQL主库启动完成..."
sleep 30

# 检查容器状态
docker ps | grep mysql-master
docker logs mysql-master --tail 20
```

------

### 4. 查看主库状态

进入容器：

```bash
# 方法1：直接连接（推荐）
docker exec -it mysql-master mysql -uroot -pzhiyu666

# 方法2：指定主机（如果方法1失败）
docker exec -it mysql-master mysql -uroot -pzhiyu666 -h127.0.0.1

# 如果连接失败，先检查容器状态
docker ps | grep mysql-master
docker logs mysql-master --tail 10
```

在 MySQL 内执行：

```sql
SHOW MASTER STATUS;
```

记录 `File` 和 `Position`（如果使用GTID则不需要）。

------

## 四、从库配置

### 方案一：单服务器多容器部署（192.168.11.151）

#### 1. 高性能从库配置文件

**从库1配置（端口3306）- 高并发优化版**
```bash
cat > /opt/mysql/slave-1/conf/my.cnf << 'EOF'
[mysqld]
server-id=2
datadir=/var/lib/mysql
socket=/var/run/mysqld/mysqld.sock
pid-file=/var/run/mysqld/mysqld.pid
user=mysql
port=3306

default_authentication_plugin=mysql_native_password

# ========== 网络连接稳定性优化 ==========
connect_timeout=60
interactive_timeout=7200
wait_timeout=7200
net_read_timeout=120
net_write_timeout=120
slave_net_timeout=60
max_connect_errors=100000
skip_name_resolve=1

# ========== 主从复制高性能配置 ==========
relay_log=/var/lib/mysql/mysql-relay-bin
relay_log_recovery=ON
log_bin=OFF
# 高并发并行复制优化
replica_parallel_workers=32
replica_parallel_type=LOGICAL_CLOCK
replica_preserve_commit_order=ON
# 复制缓冲区优化
replica_pending_jobs_size_max=128M
replica_checkpoint_period=300
replica_checkpoint_group=512
# GTID配置
gtid_mode=ON
enforce_gtid_consistency=ON
# 复制重试机制
replica_transaction_retries=10
# 跳过复制错误（谨慎使用）
# slave_skip_errors=1062,1032
# 复制过滤（如果需要）
# replicate_ignore_db=test
# 半同步复制（从库端）
# rpl_semi_sync_slave_enabled=1

# ========== InnoDB 高并发优化 ==========
innodb_buffer_pool_size=4G
innodb_buffer_pool_instances=8
innodb_log_buffer_size=128M
innodb_flush_log_at_trx_commit=2
innodb_flush_method=O_DIRECT
innodb_file_per_table=1
innodb_open_files=8192
# IO性能优化
innodb_io_capacity=4000
innodb_io_capacity_max=8000
innodb_flush_neighbors=0
innodb_read_io_threads=16
innodb_write_io_threads=16
# 锁优化
innodb_lock_wait_timeout=50
innodb_deadlock_detect=ON
# 日志文件优化
innodb_log_file_size=1G
innodb_log_files_in_group=2

# ========== 高并发连接优化 ==========
max_connections=8000
max_user_connections=7500
thread_cache_size=512
thread_stack=512K
back_log=2048
# 表缓存优化
table_open_cache=8192
table_open_cache_instances=32
table_definition_cache=4096

# ========== 内存和缓存优化 ==========
tmp_table_size=128M
max_heap_table_size=128M
sort_buffer_size=8M
join_buffer_size=8M
read_buffer_size=4M
read_rnd_buffer_size=8M

# ========== 监控和日志配置 ==========
slow_query_log=1
slow_query_log_file=/var/lib/mysql/mysql-slow.log
long_query_time=0.5
log_queries_not_using_indexes=1
log_throttle_queries_not_using_indexes=10
log_error=/var/lib/mysql/mysql-error.log
log_error_verbosity=2
general_log=0
performance_schema=ON
performance_schema_max_table_instances=12500
performance_schema_max_table_handles=4000

# ========== 其他优化参数 ==========
max_allowed_packet=128M
open_files_limit=65535
character_set_server=utf8mb4
collation_server=utf8mb4_unicode_ci
default_time_zone='+8:00'
local_infile=0
secure_file_priv=/var/lib/mysql-files/

# ========== 从库特有优化 ==========
# 只读模式（可选）
# read_only=1
# super_read_only=1
# 复制信息存储
relay_log_info_repository=TABLE
master_info_repository=TABLE
# 复制日志清理
relay_log_purge=1
relay_log_space_limit=10G
EOF
```
**从库2和从库3配置（端口3307、3308）**

**方法一：手动复制并修改（推荐，更清晰）**
```bash
# 从库2配置（server-id=3，端口3307）
cat > /opt/mysql/slave-2/conf/my.cnf << 'EOF'
[mysqld]
server-id=3
datadir=/var/lib/mysql
socket=/var/run/mysqld/mysqld.sock
pid-file=/var/run/mysqld/mysqld.pid
user=mysql
port=3306

default_authentication_plugin=mysql_native_password

# ========== 网络连接稳定性优化 ==========
connect_timeout=60
interactive_timeout=7200
wait_timeout=7200
net_read_timeout=120
net_write_timeout=120
slave_net_timeout=60
max_connect_errors=100000
skip_name_resolve=1

# ========== 主从复制高性能配置 ==========
relay_log=/var/lib/mysql/mysql-relay-bin
relay_log_recovery=ON
log_bin=OFF
replica_parallel_workers=32
replica_parallel_type=LOGICAL_CLOCK
replica_preserve_commit_order=ON
replica_pending_jobs_size_max=128M
replica_checkpoint_period=300
replica_checkpoint_group=512
gtid_mode=ON
enforce_gtid_consistency=ON
replica_transaction_retries=10

# ========== InnoDB 高并发优化 ==========
innodb_buffer_pool_size=4G
innodb_buffer_pool_instances=8
innodb_log_buffer_size=128M
innodb_flush_log_at_trx_commit=2
innodb_flush_method=O_DIRECT
innodb_file_per_table=1
innodb_open_files=8192
innodb_io_capacity=4000
innodb_io_capacity_max=8000
innodb_flush_neighbors=0
innodb_read_io_threads=16
innodb_write_io_threads=16
innodb_lock_wait_timeout=50
innodb_deadlock_detect=ON
innodb_log_file_size=1G
innodb_log_files_in_group=2

# ========== 高并发连接优化 ==========
max_connections=8000
max_user_connections=7500
thread_cache_size=512
thread_stack=512K
back_log=2048
table_open_cache=8192
table_open_cache_instances=32
table_definition_cache=4096

# ========== 内存和缓存优化 ==========
tmp_table_size=128M
max_heap_table_size=128M
sort_buffer_size=8M
join_buffer_size=8M
read_buffer_size=4M
read_rnd_buffer_size=8M

# ========== 监控和日志配置 ==========
slow_query_log=1
slow_query_log_file=/var/lib/mysql/mysql-slow.log
long_query_time=0.5
log_queries_not_using_indexes=1
log_throttle_queries_not_using_indexes=10
log_error=/var/lib/mysql/mysql-error.log
log_error_verbosity=2
general_log=0
performance_schema=ON
performance_schema_max_table_instances=12500
performance_schema_max_table_handles=4000

# ========== 其他优化参数 ==========
max_allowed_packet=128M
open_files_limit=65535
character_set_server=utf8mb4
collation_server=utf8mb4_unicode_ci
default_time_zone='+8:00'
local_infile=0
secure_file_priv=/var/lib/mysql-files/

# ========== 从库特有优化 ==========
relay_log_info_repository=TABLE
master_info_repository=TABLE
relay_log_purge=1
relay_log_space_limit=10G
EOF

# 从库3配置（server-id=4，端口3308）
cat > /opt/mysql/slave-3/conf/my.cnf << 'EOF'
[mysqld]
server-id=4
datadir=/var/lib/mysql
socket=/var/run/mysqld/mysqld.sock
pid-file=/var/run/mysqld/mysqld.pid
user=mysql
port=3306

default_authentication_plugin=mysql_native_password

# ========== 网络连接稳定性优化 ==========
connect_timeout=60
interactive_timeout=7200
wait_timeout=7200
net_read_timeout=120
net_write_timeout=120
slave_net_timeout=60
max_connect_errors=100000
skip_name_resolve=1

# ========== 主从复制高性能配置 ==========
relay_log=/var/lib/mysql/mysql-relay-bin
relay_log_recovery=ON
log_bin=OFF
replica_parallel_workers=32
replica_parallel_type=LOGICAL_CLOCK
replica_preserve_commit_order=ON
replica_pending_jobs_size_max=128M
replica_checkpoint_period=300
replica_checkpoint_group=512
gtid_mode=ON
enforce_gtid_consistency=ON
replica_transaction_retries=10

# ========== InnoDB 高并发优化 ==========
innodb_buffer_pool_size=4G
innodb_buffer_pool_instances=8
innodb_log_buffer_size=128M
innodb_flush_log_at_trx_commit=2
innodb_flush_method=O_DIRECT
innodb_file_per_table=1
innodb_open_files=8192
innodb_io_capacity=4000
innodb_io_capacity_max=8000
innodb_flush_neighbors=0
innodb_read_io_threads=16
innodb_write_io_threads=16
innodb_lock_wait_timeout=50
innodb_deadlock_detect=ON
innodb_log_file_size=1G
innodb_log_files_in_group=2

# ========== 高并发连接优化 ==========
max_connections=8000
max_user_connections=7500
thread_cache_size=512
thread_stack=512K
back_log=2048
table_open_cache=8192
table_open_cache_instances=32
table_definition_cache=4096

# ========== 内存和缓存优化 ==========
tmp_table_size=128M
max_heap_table_size=128M
sort_buffer_size=8M
join_buffer_size=8M
read_buffer_size=4M
read_rnd_buffer_size=8M

# ========== 监控和日志配置 ==========
slow_query_log=1
slow_query_log_file=/var/lib/mysql/mysql-slow.log
long_query_time=0.5
log_queries_not_using_indexes=1
log_throttle_queries_not_using_indexes=10
log_error=/var/lib/mysql/mysql-error.log
log_error_verbosity=2
general_log=0
performance_schema=ON
performance_schema_max_table_instances=12500
performance_schema_max_table_handles=4000

# ========== 其他优化参数 ==========
max_allowed_packet=128M
open_files_limit=65535
character_set_server=utf8mb4
collation_server=utf8mb4_unicode_ci
default_time_zone='+8:00'
local_infile=0
secure_file_priv=/var/lib/mysql-files/

# ========== 从库特有优化 ==========
relay_log_info_repository=TABLE
master_info_repository=TABLE
relay_log_purge=1
relay_log_space_limit=10G
EOF
```

**方法二：使用脚本批量生成（快速部署）**
```bash
# 批量生成从库2和从库3的配置文件
for i in {2..3}; do
  server_id=$((i+1))
  sed "s/server-id=2/server-id=${server_id}/g" /opt/mysql/slave-1/conf/my.cnf > /opt/mysql/slave-${i}/conf/my.cnf
  echo "已生成从库${i}配置文件，server-id=${server_id}"
done

# 验证配置文件
echo "验证配置文件中的server-id："
for i in {1..3}; do
  echo "从库${i}: $(grep '^server-id=' /opt/mysql/slave-${i}/conf/my.cnf)"
done
```

**注意**：为了节省篇幅，从库2和从库3的配置与从库1完全相同，只需要修改`server-id`参数。

#### 2. 创建初始化SQL（所有从库相同）

```bash
# 为所有从库创建相同的初始化脚本
for i in {1..3}; do
cat > /opt/mysql/slave-${i}/init/init.sql << 'EOF'
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'zhiyu666';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY 'zhiyu666';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY 'admin123';
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;

-- 创建复制用户（从库也需要，用于链式复制）
CREATE USER IF NOT EXISTS 'repl'@'%' IDENTIFIED BY 'repl123';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';

FLUSH PRIVILEGES;
EOF
done
```

#### 3. 高性能启动多个从库容器

```bash
# 创建必要的目录
mkdir -p /var/lib/mysql-files

# 启动从库1（端口3306）- 高性能配置
docker run -d \
  --name mysql-slave-1 \
  --restart always \
  --network host \
  -p 3306:3306 \
  -v /opt/mysql/slave-1/data:/var/lib/mysql \
  -v /opt/mysql/slave-1/conf:/etc/mysql/conf.d \
  -v /opt/mysql/slave-1/init:/docker-entrypoint-initdb.d \
  -v /var/lib/mysql-files:/var/lib/mysql-files \
  -e MYSQL_ROOT_PASSWORD=zhiyu666 \
  --memory=6g \
  --cpus=16 \
  --ulimit nofile=65535:65535 \
  mysql:8.0.43

# 启动从库2（端口3307）- 高性能配置
docker run -d \
  --name mysql-slave-2 \
  --restart always \
  --network host \
  -p 3307:3306 \
  -v /opt/mysql/slave-2/data:/var/lib/mysql \
  -v /opt/mysql/slave-2/conf:/etc/mysql/conf.d \
  -v /opt/mysql/slave-2/init:/docker-entrypoint-initdb.d \
  -v /var/lib/mysql-files:/var/lib/mysql-files \
  -e MYSQL_ROOT_PASSWORD=zhiyu666 \
  --memory=6g \
  --cpus=16 \
  --ulimit nofile=65535:65535 \
  mysql:8.0.43

# 启动从库3（端口3308）- 高性能配置
docker run -d \
  --name mysql-slave-3 \
  --restart always \
  --network host \
  -p 3308:3306 \
  -v /opt/mysql/slave-3/data:/var/lib/mysql \
  -v /opt/mysql/slave-3/conf:/etc/mysql/conf.d \
  -v /opt/mysql/slave-3/init:/docker-entrypoint-initdb.d \
  -v /var/lib/mysql-files:/var/lib/mysql-files \
  -e MYSQL_ROOT_PASSWORD=zhiyu666 \
  --memory=6g \
  --cpus=16 \
  --ulimit nofile=65535:65535 \
  mysql:8.0.43

# 等待所有从库启动完成
echo "等待MySQL从库启动完成..."
sleep 60

# 检查所有容器状态
echo "检查从库容器状态："
docker ps | grep mysql-slave
echo ""

# 检查从库日志
echo "检查从库启动日志："
for i in {1..3}; do
  echo "=== mysql-slave-${i} 日志 ==="
  docker logs mysql-slave-${i} --tail 10
  echo ""
done
```

#### 4. 配置主从同步（每个从库都需要配置）

**配置从库1**
```bash
docker exec -it mysql-slave-1 mysql -uroot -pzhiyu666

# 在MySQL中执行
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST='192.168.11.150',
  SOURCE_PORT=3306,
  SOURCE_USER='repl',
  SOURCE_PASSWORD='repl123',
  SOURCE_AUTO_POSITION=1;

START REPLICA;
SHOW REPLICA STATUS\G
```

**配置从库2**
```bash
docker exec -it mysql-slave-2 mysql -uroot -pzhiyu666

# 在MySQL中执行
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST='192.168.11.150',
  SOURCE_PORT=3306,
  SOURCE_USER='repl',
  SOURCE_PASSWORD='repl123',
  SOURCE_AUTO_POSITION=1;

START REPLICA;
SHOW REPLICA STATUS\G
```

**配置从库3**
```bash
docker exec -it mysql-slave-3 mysql -uroot -pzhiyu666

# 在MySQL中执行
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST='192.168.11.150',
  SOURCE_PORT=3306,
  SOURCE_USER='repl',
  SOURCE_PASSWORD='repl123',
  SOURCE_AUTO_POSITION=1;

START REPLICA;
SHOW REPLICA STATUS\G
```

------

### 方案二：多服务器部署

#### 1. 从库配置（每台服务器相同配置，但server-id不同）

**192.168.11.151（server-id=2）**
```bash
cat > /opt/mysql/slave/conf/my.cnf << 'EOF'
[mysqld]
server-id=2
datadir=/var/lib/mysql
socket=/var/run/mysqld/mysqld.sock
pid-file=/var/run/mysqld/mysqld.pid
user=mysql
port=3306

default_authentication_plugin=mysql_native_password

# 主从复制
relay_log=/var/lib/mysql/mysql-relay-bin
relay_log_recovery=ON
log_bin=OFF
replica_parallel_workers=16
replica_parallel_type=LOGICAL_CLOCK
replica_preserve_commit_order=ON
gtid_mode=ON
enforce_gtid_consistency=ON

# InnoDB
innodb_buffer_pool_size=1G
innodb_buffer_pool_instances=4
innodb_log_buffer_size=64M
innodb_flush_log_at_trx_commit=2
innodb_flush_method=O_DIRECT
innodb_file_per_table=1
innodb_open_files=4096
innodb_io_capacity=2000
innodb_io_capacity_max=4000
innodb_flush_neighbors=0

# 并发 & 缓存
max_connections=1500
thread_cache_size=256
table_open_cache=4000
table_open_cache_instances=16

# 临时表 & 排序
tmp_table_size=64M
max_heap_table_size=64M
sort_buffer_size=4M
join_buffer_size=4M
read_buffer_size=2M
read_rnd_buffer_size=4M

# 慢查询日志
slow_query_log=1
slow_query_log_file=/var/lib/mysql/mysql-slow.log
long_query_time=1

# 其他
skip_name_resolve=1
max_allowed_packet=64M
open_files_limit=65535
EOF
```

**192.168.11.152（server-id=3）**
```bash
cat > /opt/mysql/slave/conf/my.cnf << 'EOF'
[mysqld]
server-id=3
datadir=/var/lib/mysql
socket=/var/run/mysqld/mysqld.sock
pid-file=/var/run/mysqld/mysqld.pid
user=mysql
port=3306

default_authentication_plugin=mysql_native_password

# 主从复制
relay_log=/var/lib/mysql/mysql-relay-bin
relay_log_recovery=ON
log_bin=OFF
replica_parallel_workers=16
replica_parallel_type=LOGICAL_CLOCK
replica_preserve_commit_order=ON
gtid_mode=ON
enforce_gtid_consistency=ON

# InnoDB
innodb_buffer_pool_size=1G
innodb_buffer_pool_instances=4
innodb_log_buffer_size=64M
innodb_flush_log_at_trx_commit=2
innodb_flush_method=O_DIRECT
innodb_file_per_table=1
innodb_open_files=4096
innodb_io_capacity=2000
innodb_io_capacity_max=4000
innodb_flush_neighbors=0

# 并发 & 缓存
max_connections=1500
thread_cache_size=256
table_open_cache=4000
table_open_cache_instances=16

# 临时表 & 排序
tmp_table_size=64M
max_heap_table_size=64M
sort_buffer_size=4M
join_buffer_size=4M
read_buffer_size=2M
read_rnd_buffer_size=4M

# 慢查询日志
slow_query_log=1
slow_query_log_file=/var/lib/mysql/mysql-slow.log
long_query_time=1

# 其他
skip_name_resolve=1
max_allowed_packet=64M
open_files_limit=65535
EOF
```

**192.168.11.153（server-id=4）**
```bash
cat > /opt/mysql/slave/conf/my.cnf << 'EOF'
[mysqld]
server-id=4
datadir=/var/lib/mysql
socket=/var/run/mysqld/mysqld.sock
pid-file=/var/run/mysqld/mysqld.pid
user=mysql
port=3306

default_authentication_plugin=mysql_native_password

# 主从复制
relay_log=/var/lib/mysql/mysql-relay-bin
relay_log_recovery=ON
log_bin=OFF
replica_parallel_workers=16
replica_parallel_type=LOGICAL_CLOCK
replica_preserve_commit_order=ON
gtid_mode=ON
enforce_gtid_consistency=ON

# InnoDB
innodb_buffer_pool_size=1G
innodb_buffer_pool_instances=4
innodb_log_buffer_size=64M
innodb_flush_log_at_trx_commit=2
innodb_flush_method=O_DIRECT
innodb_file_per_table=1
innodb_open_files=4096
innodb_io_capacity=2000
innodb_io_capacity_max=4000
innodb_flush_neighbors=0

# 并发 & 缓存
max_connections=1500
thread_cache_size=256
table_open_cache=4000
table_open_cache_instances=16

# 临时表 & 排序
tmp_table_size=64M
max_heap_table_size=64M
sort_buffer_size=4M
join_buffer_size=4M
read_buffer_size=2M
read_rnd_buffer_size=4M

# 慢查询日志
slow_query_log=1
slow_query_log_file=/var/lib/mysql/mysql-slow.log
long_query_time=1

# 其他
skip_name_resolve=1
max_allowed_packet=64M
open_files_limit=65535
EOF
```

#### 2. 初始化SQL（每台服务器相同）

```bash
# 在每台从库服务器执行
cat > /opt/mysql/slave/init/init.sql << 'EOF'
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'zhiyu666';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY 'zhiyu666';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY 'admin123';
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;

-- 创建复制用户（从库也需要，用于链式复制）
CREATE USER IF NOT EXISTS 'repl'@'%' IDENTIFIED BY 'repl123';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';

FLUSH PRIVILEGES;
EOF
```

#### 3. 启动从库容器（每台服务器执行）

```bash
# 在每台从库服务器执行
docker run -d \
  --name mysql-slave \
  --restart always \
  -p 3306:3306 \
  -v /opt/mysql/slave/data:/var/lib/mysql \
  -v /opt/mysql/slave/conf:/etc/mysql/conf.d \
  -v /opt/mysql/slave/init:/docker-entrypoint-initdb.d \
  -e MYSQL_ROOT_PASSWORD=zhiyu666 \
  mysql:8.0.43

# 检查容器状态
docker ps | grep mysql-slave
```

#### 4. 配置主从同步（每台从库服务器执行）

```bash
# 在每台从库服务器执行
docker exec -it mysql-slave mysql -uroot -pzhiyu666

# 在MySQL中执行
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST='192.168.11.60',
  SOURCE_PORT=3306,
  SOURCE_USER='repl',
  SOURCE_PASSWORD='repl123',
  SOURCE_AUTO_POSITION=1;

START REPLICA;
SHOW REPLICA STATUS\G
```

确认以下状态：
- `Replica_IO_Running: Yes`
- `Replica_SQL_Running: Yes`
- `Last_IO_Error: (空)`
- `Last_SQL_Error: (空)`

------

## 五、测试验证

### 方案一：单服务器多容器测试

**主库执行：**
```sql
CREATE DATABASE sync_test;
USE sync_test;
CREATE TABLE t1 (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(50), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
INSERT INTO t1 (name) VALUES ('test_data_1'), ('test_data_2');
```

**验证各从库同步：**
```bash
# 验证从库1
docker exec -it mysql-slave-1 mysql -uroot -pzhiyu666 -e "USE sync_test; SELECT * FROM t1;"

# 验证从库2
docker exec -it mysql-slave-2 mysql -uroot -pzhiyu666 -e "USE sync_test; SELECT * FROM t1;"

# 验证从库3
docker exec -it mysql-slave-3 mysql -uroot -pzhiyu666 -e "USE sync_test; SELECT * FROM t1;"
```

### 方案二：多服务器测试

**主库执行：**
```sql
CREATE DATABASE sync_test;
USE sync_test;
CREATE TABLE t1 (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(50), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
INSERT INTO t1 (name) VALUES ('test_data_1'), ('test_data_2');
```

**在每台从库服务器验证：**
```bash
# 在192.168.11.151执行
docker exec -it mysql-slave mysql -uroot -pzhiyu666 -e "USE sync_test; SELECT * FROM t1;"

# 在192.168.11.152执行
docker exec -it mysql-slave mysql -uroot -pzhiyu666 -e "USE sync_test; SELECT * FROM t1;"

# 在192.168.11.153执行
docker exec -it mysql-slave mysql -uroot -pzhiyu666 -e "USE sync_test; SELECT * FROM t1;"
```

### 性能测试

**检查主库连接数：**
```sql
-- 在主库执行
SHOW PROCESSLIST;
SELECT COUNT(*) as slave_connections FROM information_schema.processlist WHERE command = 'Binlog Dump GTID';
```

**检查各从库延迟：**
```sql
-- 在每个从库执行
SHOW REPLICA STATUS\G
-- 关注 Seconds_Behind_Master 字段
```

## 六、高并发监控与运维

### 1. 实时监控脚本

#### 1.1 主从同步状态监控脚本

```bash
#!/bin/bash
# 文件名：monitor_replication.sh
# 功能：实时监控MySQL主从复制状态

# 配置参数
MASTER_HOST="192.168.11.150"
MASTER_PORT="3306"
SLAVES=("localhost:3306" "localhost:3307" "localhost:3308")
MYSQL_USER="monitor"
MYSQL_PASSWORD="monitor123"
LOG_FILE="/var/log/mysql_replication_monitor.log"
ALERT_THRESHOLD=5  # 延迟阈值（秒）

# 日志函数
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查主库状态
check_master_status() {
    log_message "=== 检查主库状态 ==="
    
    # 检查主库连接
    if ! mysql -h"$MASTER_HOST" -P"$MASTER_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1" >/dev/null 2>&1; then
        log_message "ERROR: 无法连接到主库 $MASTER_HOST:$MASTER_PORT"
        return 1
    fi
    
    # 获取主库状态
    MASTER_STATUS=$(mysql -h"$MASTER_HOST" -P"$MASTER_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SHOW MASTER STATUS\G" 2>/dev/null)
    log_message "主库状态: $MASTER_STATUS"
    
    # 检查主库性能指标
    PERFORMANCE_METRICS=$(mysql -h"$MASTER_HOST" -P"$MASTER_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
        SELECT 
            VARIABLE_NAME, 
            VARIABLE_VALUE 
        FROM performance_schema.global_status 
        WHERE VARIABLE_NAME IN (
            'Threads_connected',
            'Threads_running', 
            'Queries',
            'Com_select',
            'Com_insert',
            'Com_update',
            'Com_delete',
            'Innodb_buffer_pool_read_requests',
            'Innodb_buffer_pool_reads'
        );" 2>/dev/null)
    
    log_message "主库性能指标: $PERFORMANCE_METRICS"
    
    # 记录到监控表
    mysql -h"$MASTER_HOST" -P"$MASTER_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
        INSERT INTO mysql_monitor.performance_metrics (
            server_type, server_id, metric_name, metric_value, created_at
        ) VALUES 
        ('master', 'master-1', 'threads_connected', 
         (SELECT VARIABLE_VALUE FROM performance_schema.global_status WHERE VARIABLE_NAME='Threads_connected'), 
         NOW()),
        ('master', 'master-1', 'threads_running', 
         (SELECT VARIABLE_VALUE FROM performance_schema.global_status WHERE VARIABLE_NAME='Threads_running'), 
         NOW());" 2>/dev/null
    
    return 0
}

# 检查从库状态
check_slave_status() {
    local slave_host_port=$1
    local slave_host=$(echo $slave_host_port | cut -d: -f1)
    local slave_port=$(echo $slave_host_port | cut -d: -f2)
    
    log_message "=== 检查从库状态: $slave_host_port ==="
    
    # 检查从库连接
    if ! mysql -h"$slave_host" -P"$slave_port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1" >/dev/null 2>&1; then
        log_message "ERROR: 无法连接到从库 $slave_host_port"
        return 1
    fi
    
    # 获取从库复制状态
    SLAVE_STATUS=$(mysql -h"$slave_host" -P"$slave_port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SHOW REPLICA STATUS\G" 2>/dev/null)
    
    # 解析关键指标
    IO_RUNNING=$(echo "$SLAVE_STATUS" | grep "Replica_IO_Running:" | awk '{print $2}')
    SQL_RUNNING=$(echo "$SLAVE_STATUS" | grep "Replica_SQL_Running:" | awk '{print $2}')
    SECONDS_BEHIND=$(echo "$SLAVE_STATUS" | grep "Seconds_Behind_Master:" | awk '{print $2}')
    LAST_IO_ERROR=$(echo "$SLAVE_STATUS" | grep "Last_IO_Error:" | cut -d: -f2-)
    LAST_SQL_ERROR=$(echo "$SLAVE_STATUS" | grep "Last_SQL_Error:" | cut -d: -f2-)
    
    log_message "从库 $slave_host_port 状态:"
    log_message "  IO线程运行: $IO_RUNNING"
    log_message "  SQL线程运行: $SQL_RUNNING"
    log_message "  延迟时间: $SECONDS_BEHIND 秒"
    
    # 检查错误
    if [[ "$IO_RUNNING" != "Yes" ]]; then
        log_message "ALERT: 从库 $slave_host_port IO线程未运行!"
        if [[ -n "$LAST_IO_ERROR" && "$LAST_IO_ERROR" != " " ]]; then
            log_message "IO错误: $LAST_IO_ERROR"
        fi
    fi
    
    if [[ "$SQL_RUNNING" != "Yes" ]]; then
        log_message "ALERT: 从库 $slave_host_port SQL线程未运行!"
        if [[ -n "$LAST_SQL_ERROR" && "$LAST_SQL_ERROR" != " " ]]; then
            log_message "SQL错误: $LAST_SQL_ERROR"
        fi
    fi
    
    # 检查延迟
    if [[ "$SECONDS_BEHIND" != "NULL" && "$SECONDS_BEHIND" -gt "$ALERT_THRESHOLD" ]]; then
        log_message "ALERT: 从库 $slave_host_port 延迟过高: $SECONDS_BEHIND 秒"
    fi
    
    # 记录到监控表
    mysql -h"$slave_host" -P"$slave_port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
        INSERT INTO mysql_monitor.replication_status (
            slave_host, slave_port, io_running, sql_running, 
            seconds_behind_master, last_io_error, last_sql_error, created_at
        ) VALUES (
            '$slave_host', $slave_port, '$IO_RUNNING', '$SQL_RUNNING',
            NULLIF('$SECONDS_BEHIND', 'NULL'), '$LAST_IO_ERROR', '$LAST_SQL_ERROR', NOW()
        );" 2>/dev/null
    
    return 0
}

# 主监控循环
main() {
    log_message "开始MySQL主从复制监控..."
    
    while true; do
        # 检查主库
        check_master_status
        
        # 检查所有从库
        for slave in "${SLAVES[@]}"; do
            check_slave_status "$slave"
        done
        
        log_message "监控周期完成，等待30秒..."
        sleep 30
    done
}

# 信号处理
trap 'log_message "监控脚本停止"; exit 0' SIGTERM SIGINT

# 启动监控
main
```

#### 1.2 性能指标收集脚本

```bash
#!/bin/bash
# 文件名：collect_performance_metrics.sh
# 功能：收集MySQL性能指标

SERVERS=("192.168.11.150:3306" "localhost:3306" "localhost:3307" "localhost:3308")
MYSQL_USER="monitor"
MYSQL_PASSWORD="monitor123"
METRICS_LOG="/var/log/mysql_performance_metrics.log"

collect_metrics() {
    local server=$1
    local host=$(echo $server | cut -d: -f1)
    local port=$(echo $server | cut -d: -f2)
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 收集服务器 $server 性能指标" >> "$METRICS_LOG"
    
    # 收集关键性能指标
    mysql -h"$host" -P"$port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
        INSERT INTO mysql_monitor.performance_metrics (server_type, server_id, metric_name, metric_value, created_at)
        SELECT 
            CASE WHEN '$port' = '3306' AND '$host' = '192.168.11.150' THEN 'master' ELSE 'slave' END,
            CONCAT('$host', ':', '$port'),
            VARIABLE_NAME,
            VARIABLE_VALUE,
            NOW()
        FROM performance_schema.global_status 
        WHERE VARIABLE_NAME IN (
            'Threads_connected', 'Threads_running', 'Threads_cached',
            'Queries', 'Questions', 'Slow_queries',
            'Com_select', 'Com_insert', 'Com_update', 'Com_delete',
            'Innodb_buffer_pool_read_requests', 'Innodb_buffer_pool_reads',
            'Innodb_buffer_pool_pages_dirty', 'Innodb_buffer_pool_pages_free',
            'Innodb_log_waits', 'Innodb_log_writes',
            'Table_locks_immediate', 'Table_locks_waited',
            'Created_tmp_tables', 'Created_tmp_disk_tables',
            'Bytes_received', 'Bytes_sent'
        );
    " 2>/dev/null
}

# 主循环
while true; do
    for server in "${SERVERS[@]}"; do
        collect_metrics "$server"
    done
    sleep 60  # 每分钟收集一次
done
```

#### 1.3 自动化监控部署脚本

```bash
#!/bin/bash
# 文件名：deploy_monitoring.sh
# 功能：部署监控系统

echo "部署MySQL主从复制监控系统..."

# 创建日志目录
sudo mkdir -p /var/log/mysql_monitoring
sudo chmod 755 /var/log/mysql_monitoring

# 创建监控脚本目录
sudo mkdir -p /opt/mysql_monitoring
sudo chmod 755 /opt/mysql_monitoring

# 复制监控脚本
sudo cp monitor_replication.sh /opt/mysql_monitoring/
sudo cp collect_performance_metrics.sh /opt/mysql_monitoring/
sudo chmod +x /opt/mysql_monitoring/*.sh

# 创建systemd服务文件
sudo tee /etc/systemd/system/mysql-replication-monitor.service > /dev/null <<EOF
[Unit]
Description=MySQL Replication Monitor
After=network.target

[Service]
Type=simple
User=root
ExecStart=/opt/mysql_monitoring/monitor_replication.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/mysql-performance-collector.service > /dev/null <<EOF
[Unit]
Description=MySQL Performance Metrics Collector
After=network.target

[Service]
Type=simple
User=root
ExecStart=/opt/mysql_monitoring/collect_performance_metrics.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd并启动服务
sudo systemctl daemon-reload
sudo systemctl enable mysql-replication-monitor.service
sudo systemctl enable mysql-performance-collector.service
sudo systemctl start mysql-replication-monitor.service
sudo systemctl start mysql-performance-collector.service

echo "监控系统部署完成！"
echo "检查服务状态："
sudo systemctl status mysql-replication-monitor.service
sudo systemctl status mysql-performance-collector.service
```

### 2. 监控查询和报表

#### 2.1 实时状态查询

```sql
-- 查看当前复制状态
SELECT 
    slave_host,
    slave_port,
    io_running,
    sql_running,
    seconds_behind_master,
    created_at
FROM mysql_monitor.replication_status 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)
ORDER BY created_at DESC;

-- 查看性能趋势
SELECT 
    server_id,
    metric_name,
    AVG(metric_value) as avg_value,
    MAX(metric_value) as max_value,
    MIN(metric_value) as min_value,
    DATE_FORMAT(created_at, '%Y-%m-%d %H:%i') as time_period
FROM mysql_monitor.performance_metrics 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
    AND metric_name IN ('Threads_connected', 'Threads_running', 'Queries')
GROUP BY server_id, metric_name, DATE_FORMAT(created_at, '%Y-%m-%d %H:%i')
ORDER BY time_period DESC;

-- 查看延迟统计
SELECT 
    slave_host,
    slave_port,
    AVG(seconds_behind_master) as avg_delay,
    MAX(seconds_behind_master) as max_delay,
    COUNT(*) as sample_count,
    SUM(CASE WHEN seconds_behind_master > 5 THEN 1 ELSE 0 END) as high_delay_count
FROM mysql_monitor.replication_status 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
    AND seconds_behind_master IS NOT NULL
GROUP BY slave_host, slave_port;
```

#### 2.2 告警查询

```sql
-- 检查复制中断
SELECT 
    slave_host,
    slave_port,
    io_running,
    sql_running,
    last_io_error,
    last_sql_error,
    created_at
FROM mysql_monitor.replication_status 
WHERE (io_running != 'Yes' OR sql_running != 'Yes')
    AND created_at >= DATE_SUB(NOW(), INTERVAL 10 MINUTE)
ORDER BY created_at DESC;

-- 检查高延迟
SELECT 
    slave_host,
    slave_port,
    seconds_behind_master,
    created_at
FROM mysql_monitor.replication_status 
WHERE seconds_behind_master > 10
    AND created_at >= DATE_SUB(NOW(), INTERVAL 30 MINUTE)
ORDER BY seconds_behind_master DESC;

-- 检查连接数异常
SELECT 
    server_id,
    metric_value as connections,
    created_at
FROM mysql_monitor.performance_metrics 
WHERE metric_name = 'Threads_connected'
    AND metric_value > 1500  -- 连接数超过1500告警
    AND created_at >= DATE_SUB(NOW(), INTERVAL 30 MINUTE)
ORDER BY metric_value DESC;
```

## 八、数据一致性校验方案

### 1. 数据一致性检查脚本

#### 1.1 基于校验和的一致性检查

```bash
#!/bin/bash
# 文件名：data_consistency_check.sh
# 功能：检查主从数据一致性

# 配置参数
MASTER_HOST="192.168.11.150"
MASTER_PORT="3306"
SLAVES=("localhost:3306" "localhost:3307" "localhost:3308")
MYSQL_USER="checksum"
MYSQL_PASSWORD="checksum123"
LOG_FILE="/var/log/mysql_consistency_check.log"
DATABASES=("test_db" "user_db" "order_db")  # 需要检查的数据库

# 日志函数
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 获取表的校验和
get_table_checksum() {
    local host=$1
    local port=$2
    local database=$3
    local table=$4
    
    mysql -h"$host" -P"$port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
        SELECT 
            COALESCE(
                BIT_XOR(
                    CAST(
                        CRC32(
                            CONCAT_WS(',',
                                $(mysql -h"$host" -P"$port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
                                    SELECT GROUP_CONCAT(COLUMN_NAME ORDER BY ORDINAL_POSITION)
                                    FROM information_schema.COLUMNS 
                                    WHERE TABLE_SCHEMA='$database' AND TABLE_NAME='$table'
                                " -s -N)
                            )
                        ) AS UNSIGNED
                    )
                ), 0
            ) as table_checksum
        FROM $database.$table;
    " -s -N 2>/dev/null
}

# 获取表的行数
get_table_count() {
    local host=$1
    local port=$2
    local database=$3
    local table=$4
    
    mysql -h"$host" -P"$port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
        SELECT COUNT(*) FROM $database.$table;
    " -s -N 2>/dev/null
}

# 检查单个表的一致性
check_table_consistency() {
    local database=$1
    local table=$2
    
    log_message "检查表 $database.$table 的一致性..."
    
    # 获取主库校验和和行数
    local master_checksum=$(get_table_checksum "$MASTER_HOST" "$MASTER_PORT" "$database" "$table")
    local master_count=$(get_table_count "$MASTER_HOST" "$MASTER_PORT" "$database" "$table")
    
    if [[ -z "$master_checksum" || -z "$master_count" ]]; then
        log_message "ERROR: 无法获取主库 $database.$table 的校验和或行数"
        return 1
    fi
    
    log_message "主库 $database.$table - 校验和: $master_checksum, 行数: $master_count"
    
    # 检查所有从库
    local inconsistent_slaves=()
    
    for slave in "${SLAVES[@]}"; do
        local slave_host=$(echo $slave | cut -d: -f1)
        local slave_port=$(echo $slave | cut -d: -f2)
        
        local slave_checksum=$(get_table_checksum "$slave_host" "$slave_port" "$database" "$table")
        local slave_count=$(get_table_count "$slave_host" "$slave_port" "$database" "$table")
        
        if [[ -z "$slave_checksum" || -z "$slave_count" ]]; then
            log_message "ERROR: 无法获取从库 $slave 的 $database.$table 校验和或行数"
            inconsistent_slaves+=("$slave")
            continue
        fi
        
        log_message "从库 $slave $database.$table - 校验和: $slave_checksum, 行数: $slave_count"
        
        # 比较校验和和行数
        if [[ "$master_checksum" != "$slave_checksum" || "$master_count" != "$slave_count" ]]; then
            log_message "ALERT: 从库 $slave 的表 $database.$table 数据不一致!"
            log_message "  主库: 校验和=$master_checksum, 行数=$master_count"
            log_message "  从库: 校验和=$slave_checksum, 行数=$slave_count"
            inconsistent_slaves+=("$slave")
            
            # 记录到一致性检查表
            mysql -h"$MASTER_HOST" -P"$MASTER_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
                INSERT INTO mysql_monitor.consistency_check (
                    database_name, table_name, master_checksum, slave_host, slave_port,
                    slave_checksum, master_count, slave_count, is_consistent, created_at
                ) VALUES (
                    '$database', '$table', '$master_checksum', '$slave_host', $slave_port,
                    '$slave_checksum', $master_count, $slave_count, 0, NOW()
                );
            " 2>/dev/null
        else
            log_message "从库 $slave 的表 $database.$table 数据一致"
            
            # 记录一致性检查结果
            mysql -h"$MASTER_HOST" -P"$MASTER_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
                INSERT INTO mysql_monitor.consistency_check (
                    database_name, table_name, master_checksum, slave_host, slave_port,
                    slave_checksum, master_count, slave_count, is_consistent, created_at
                ) VALUES (
                    '$database', '$table', '$master_checksum', '$slave_host', $slave_port,
                    '$slave_checksum', $master_count, $slave_count, 1, NOW()
                );
            " 2>/dev/null
        fi
    done
    
    if [[ ${#inconsistent_slaves[@]} -gt 0 ]]; then
        log_message "表 $database.$table 存在数据不一致的从库: ${inconsistent_slaves[*]}"
        return 1
    else
        log_message "表 $database.$table 所有从库数据一致"
        return 0
    fi
}

# 获取数据库中的所有表
get_tables() {
    local database=$1
    
    mysql -h"$MASTER_HOST" -P"$MASTER_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
        SELECT TABLE_NAME 
        FROM information_schema.TABLES 
        WHERE TABLE_SCHEMA='$database' 
            AND TABLE_TYPE='BASE TABLE'
        ORDER BY TABLE_NAME;
    " -s -N 2>/dev/null
}

# 主检查函数
main() {
    log_message "开始数据一致性检查..."
    
    local total_inconsistent=0
    local total_tables=0
    
    for database in "${DATABASES[@]}"; do
        log_message "=== 检查数据库: $database ==="
        
        # 获取数据库中的所有表
        local tables=$(get_tables "$database")
        
        if [[ -z "$tables" ]]; then
            log_message "WARNING: 数据库 $database 中没有找到表或无法访问"
            continue
        fi
        
        # 检查每个表
        while IFS= read -r table; do
            if [[ -n "$table" ]]; then
                ((total_tables++))
                if ! check_table_consistency "$database" "$table"; then
                    ((total_inconsistent++))
                fi
                echo ""  # 添加空行分隔
            fi
        done <<< "$tables"
    done
    
    log_message "=== 数据一致性检查完成 ==="
    log_message "总检查表数: $total_tables"
    log_message "不一致表数: $total_inconsistent"
    
    if [[ $total_inconsistent -gt 0 ]]; then
        log_message "ALERT: 发现 $total_inconsistent 个表存在数据不一致!"
        return 1
    else
        log_message "所有表数据一致"
        return 0
    fi
}

# 运行检查
main
```

#### 1.2 增量数据一致性检查

```bash
#!/bin/bash
# 文件名：incremental_consistency_check.sh
# 功能：基于binlog位置的增量一致性检查

MASTER_HOST="192.168.11.150"
MASTER_PORT="3306"
SLAVES=("localhost:3306" "localhost:3307" "localhost:3308")
MYSQL_USER="checksum"
MYSQL_PASSWORD="checksum123"
LOG_FILE="/var/log/mysql_incremental_check.log"

# 日志函数
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 获取主库binlog位置
get_master_position() {
    mysql -h"$MASTER_HOST" -P"$MASTER_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
        SHOW MASTER STATUS;
    " 2>/dev/null
}

# 获取从库复制位置
get_slave_position() {
    local slave_host=$1
    local slave_port=$2
    
    mysql -h"$slave_host" -P"$slave_port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
        SHOW REPLICA STATUS\G;
    " 2>/dev/null | grep -E "(Master_Log_File|Read_Master_Log_Pos|Exec_Master_Log_Pos|Seconds_Behind_Master)"
}

# 检查GTID一致性
check_gtid_consistency() {
    log_message "=== 检查GTID一致性 ==="
    
    # 获取主库GTID
    local master_gtid=$(mysql -h"$MASTER_HOST" -P"$MASTER_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
        SELECT @@GLOBAL.gtid_executed;
    " -s -N 2>/dev/null)
    
    log_message "主库GTID: $master_gtid"
    
    # 检查每个从库的GTID
    for slave in "${SLAVES[@]}"; do
        local slave_host=$(echo $slave | cut -d: -f1)
        local slave_port=$(echo $slave | cut -d: -f2)
        
        local slave_gtid=$(mysql -h"$slave_host" -P"$slave_port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
            SELECT @@GLOBAL.gtid_executed;
        " -s -N 2>/dev/null)
        
        log_message "从库 $slave GTID: $slave_gtid"
        
        # 检查GTID差异
        local gtid_diff=$(mysql -h"$slave_host" -P"$slave_port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
            SELECT GTID_SUBTRACT('$master_gtid', '$slave_gtid') as missing_gtids;
        " -s -N 2>/dev/null)
        
        if [[ -n "$gtid_diff" && "$gtid_diff" != "" ]]; then
            log_message "ALERT: 从库 $slave 缺少GTID: $gtid_diff"
        else
            log_message "从库 $slave GTID同步正常"
        fi
    done
}

# 检查最近的数据变更
check_recent_changes() {
    local minutes=${1:-5}  # 默认检查最近5分钟
    
    log_message "=== 检查最近 $minutes 分钟的数据变更 ==="
    
    # 在主库创建测试表（如果不存在）
    mysql -h"$MASTER_HOST" -P"$MASTER_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
        CREATE DATABASE IF NOT EXISTS consistency_test;
        USE consistency_test;
        CREATE TABLE IF NOT EXISTS sync_test (
            id INT AUTO_INCREMENT PRIMARY KEY,
            test_data VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    " 2>/dev/null
    
    # 插入测试数据
    local test_id=$(date +%s%N | cut -b1-13)  # 使用时间戳作为唯一ID
    local test_data="consistency_check_$test_id"
    
    mysql -h"$MASTER_HOST" -P"$MASTER_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
        INSERT INTO consistency_test.sync_test (test_data) VALUES ('$test_data');
    " 2>/dev/null
    
    log_message "在主库插入测试数据: $test_data"
    
    # 等待复制
    sleep 3
    
    # 检查从库是否同步了测试数据
    for slave in "${SLAVES[@]}"; do
        local slave_host=$(echo $slave | cut -d: -f1)
        local slave_port=$(echo $slave | cut -d: -f2)
        
        local found=$(mysql -h"$slave_host" -P"$slave_port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
            SELECT COUNT(*) FROM consistency_test.sync_test WHERE test_data = '$test_data';
        " -s -N 2>/dev/null)
        
        if [[ "$found" == "1" ]]; then
            log_message "从库 $slave 成功同步测试数据"
        else
            log_message "ALERT: 从库 $slave 未同步测试数据"
        fi
    done
    
    # 清理测试数据
    mysql -h"$MASTER_HOST" -P"$MASTER_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
        DELETE FROM consistency_test.sync_test WHERE test_data = '$test_data';
    " 2>/dev/null
}

# 主函数
main() {
    log_message "开始增量数据一致性检查..."
    
    # 检查主库状态
    log_message "=== 主库状态 ==="
    get_master_position
    
    # 检查从库状态
    log_message "=== 从库状态 ==="
    for slave in "${SLAVES[@]}"; do
        local slave_host=$(echo $slave | cut -d: -f1)
        local slave_port=$(echo $slave | cut -d: -f2)
        
        log_message "从库 $slave 状态:"
        get_slave_position "$slave_host" "$slave_port"
        echo ""
    done
    
    # 检查GTID一致性
    check_gtid_consistency
    
    # 检查最近的数据变更
    check_recent_changes
    
    log_message "增量数据一致性检查完成"
}

# 运行检查
main
```

#### 1.3 自动化一致性检查部署

```bash
#!/bin/bash
# 文件名：deploy_consistency_check.sh
# 功能：部署数据一致性检查系统

echo "部署数据一致性检查系统..."

# 创建脚本目录
sudo mkdir -p /opt/mysql_consistency
sudo chmod 755 /opt/mysql_consistency

# 复制检查脚本
sudo cp data_consistency_check.sh /opt/mysql_consistency/
sudo cp incremental_consistency_check.sh /opt/mysql_consistency/
sudo chmod +x /opt/mysql_consistency/*.sh

# 创建定时任务配置
sudo tee /etc/cron.d/mysql-consistency-check > /dev/null <<EOF
# MySQL数据一致性检查定时任务
# 每天凌晨2点执行完整一致性检查
0 2 * * * root /opt/mysql_consistency/data_consistency_check.sh >> /var/log/mysql_consistency_cron.log 2>&1

# 每小时执行增量一致性检查
0 * * * * root /opt/mysql_consistency/incremental_consistency_check.sh >> /var/log/mysql_consistency_cron.log 2>&1

# 每15分钟执行快速同步检查
*/15 * * * * root /opt/mysql_consistency/incremental_consistency_check.sh >> /var/log/mysql_consistency_cron.log 2>&1
EOF

# 创建systemd服务（可选，用于手动触发）
sudo tee /etc/systemd/system/mysql-consistency-check.service > /dev/null <<EOF
[Unit]
Description=MySQL Data Consistency Check
After=network.target

[Service]
Type=oneshot
ExecStart=/opt/mysql_consistency/data_consistency_check.sh
User=root

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload

echo "数据一致性检查系统部署完成！"
echo "定时任务已配置："
echo "- 每天凌晨2点：完整一致性检查"
echo "- 每小时：增量一致性检查"
echo "- 每15分钟：快速同步检查"
echo ""
echo "手动执行检查："
echo "sudo systemctl start mysql-consistency-check.service"
```

### 2. 一致性检查查询和报告

#### 2.1 一致性检查结果查询

```sql
-- 查看最近的一致性检查结果
SELECT 
    database_name,
    table_name,
    slave_host,
    slave_port,
    is_consistent,
    master_count,
    slave_count,
    created_at
FROM mysql_monitor.consistency_check 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY created_at DESC, database_name, table_name;

-- 查看不一致的表统计
SELECT 
    database_name,
    table_name,
    COUNT(*) as check_count,
    SUM(CASE WHEN is_consistent = 0 THEN 1 ELSE 0 END) as inconsistent_count,
    ROUND(SUM(CASE WHEN is_consistent = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as consistency_rate
FROM mysql_monitor.consistency_check 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY database_name, table_name
HAVING inconsistent_count > 0
ORDER BY inconsistent_count DESC;

-- 查看从库一致性统计
SELECT 
    slave_host,
    slave_port,
    COUNT(*) as total_checks,
    SUM(CASE WHEN is_consistent = 1 THEN 1 ELSE 0 END) as consistent_checks,
    SUM(CASE WHEN is_consistent = 0 THEN 1 ELSE 0 END) as inconsistent_checks,
    ROUND(SUM(CASE WHEN is_consistent = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as consistency_rate
FROM mysql_monitor.consistency_check 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY slave_host, slave_port
ORDER BY consistency_rate ASC;
```

#### 2.2 一致性告警查询

```sql
-- 查找当前不一致的表
SELECT DISTINCT
    database_name,
    table_name,
    GROUP_CONCAT(CONCAT(slave_host, ':', slave_port)) as inconsistent_slaves
FROM mysql_monitor.consistency_check 
WHERE is_consistent = 0
    AND created_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
GROUP BY database_name, table_name;

-- 查找持续不一致的表（最近3次检查都不一致）
SELECT 
    database_name,
    table_name,
    slave_host,
    slave_port,
    COUNT(*) as consecutive_failures
FROM (
    SELECT 
        database_name,
        table_name,
        slave_host,
        slave_port,
        is_consistent,
        ROW_NUMBER() OVER (
            PARTITION BY database_name, table_name, slave_host, slave_port 
            ORDER BY created_at DESC
        ) as rn
    FROM mysql_monitor.consistency_check 
    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 6 HOUR)
) t
WHERE rn <= 3 AND is_consistent = 0
GROUP BY database_name, table_name, slave_host, slave_port
HAVING COUNT(*) = 3;
```

## 九、高可用故障转移机制

### 1. 自动重连和故障转移脚本

#### 1.1 主从连接监控和自动重连

```bash
#!/bin/bash
# 文件名：auto_reconnect.sh
# 功能：监控主从连接状态并自动重连

# 配置参数
MASTER_HOST="192.168.11.150"
MASTER_PORT="3306"
SLAVES=("localhost:3306" "localhost:3307" "localhost:3308")
MYSQL_USER="repl"
MYSQL_PASSWORD="repl123"
MONITOR_USER="monitor"
MONITOR_PASSWORD="monitor123"
LOG_FILE="/var/log/mysql_auto_reconnect.log"
MAX_RETRY_COUNT=3
RETRY_INTERVAL=30

# 日志函数
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查主库连接状态
check_master_connection() {
    if mysql -h"$MASTER_HOST" -P"$MASTER_PORT" -u"$MONITOR_USER" -p"$MONITOR_PASSWORD" -e "SELECT 1" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 检查从库复制状态
check_slave_replication() {
    local slave_host=$1
    local slave_port=$2
    
    # 检查从库连接
    if ! mysql -h"$slave_host" -P"$slave_port" -u"$MONITOR_USER" -p"$MONITOR_PASSWORD" -e "SELECT 1" >/dev/null 2>&1; then
        log_message "ERROR: 无法连接到从库 $slave_host:$slave_port"
        return 2
    fi
    
    # 获取复制状态
    local replication_status=$(mysql -h"$slave_host" -P"$slave_port" -u"$MONITOR_USER" -p"$MONITOR_PASSWORD" -e "SHOW REPLICA STATUS\G" 2>/dev/null)
    
    local io_running=$(echo "$replication_status" | grep "Replica_IO_Running:" | awk '{print $2}')
    local sql_running=$(echo "$replication_status" | grep "Replica_SQL_Running:" | awk '{print $2}')
    local last_io_error=$(echo "$replication_status" | grep "Last_IO_Error:" | cut -d: -f2-)
    local last_sql_error=$(echo "$replication_status" | grep "Last_SQL_Error:" | cut -d: -f2-)
    
    # 检查复制线程状态
    if [[ "$io_running" != "Yes" ]]; then
        log_message "ALERT: 从库 $slave_host:$slave_port IO线程未运行"
        if [[ -n "$last_io_error" && "$last_io_error" != " " ]]; then
            log_message "IO错误: $last_io_error"
        fi
        return 1
    fi
    
    if [[ "$sql_running" != "Yes" ]]; then
        log_message "ALERT: 从库 $slave_host:$slave_port SQL线程未运行"
        if [[ -n "$last_sql_error" && "$last_sql_error" != " " ]]; then
            log_message "SQL错误: $last_sql_error"
        fi
        return 1
    fi
    
    return 0
}

# 重新配置从库复制
reconfigure_slave_replication() {
    local slave_host=$1
    local slave_port=$2
    local retry_count=${3:-0}
    
    log_message "开始重新配置从库 $slave_host:$slave_port 的复制..."
    
    # 停止复制
    mysql -h"$slave_host" -P"$slave_port" -u"$MONITOR_USER" -p"$MONITOR_PASSWORD" -e "STOP REPLICA;" 2>/dev/null
    
    # 重置复制配置
    mysql -h"$slave_host" -P"$slave_port" -u"$MONITOR_USER" -p"$MONITOR_PASSWORD" -e "RESET REPLICA ALL;" 2>/dev/null
    
    # 重新配置复制源
    mysql -h"$slave_host" -P"$slave_port" -u"$MONITOR_USER" -p"$MONITOR_PASSWORD" -e "
        CHANGE REPLICATION SOURCE TO
            SOURCE_HOST='$MASTER_HOST',
            SOURCE_PORT=$MASTER_PORT,
            SOURCE_USER='$MYSQL_USER',
            SOURCE_PASSWORD='$MYSQL_PASSWORD',
            SOURCE_AUTO_POSITION=1,
            SOURCE_CONNECT_RETRY=10,
            SOURCE_RETRY_COUNT=86400,
            SOURCE_HEARTBEAT_PERIOD=30;
    " 2>/dev/null
    
    # 启动复制
    if mysql -h"$slave_host" -P"$slave_port" -u"$MONITOR_USER" -p"$MONITOR_PASSWORD" -e "START REPLICA;" 2>/dev/null; then
        log_message "从库 $slave_host:$slave_port 复制重新配置成功"
        
        # 等待复制启动
        sleep 10
        
        # 验证复制状态
        if check_slave_replication "$slave_host" "$slave_port"; then
            log_message "从库 $slave_host:$slave_port 复制恢复正常"
            return 0
        else
            log_message "从库 $slave_host:$slave_port 复制仍然异常"
            
            # 如果重试次数未达到上限，则重试
            if [[ $retry_count -lt $MAX_RETRY_COUNT ]]; then
                log_message "等待 $RETRY_INTERVAL 秒后重试..."
                sleep $RETRY_INTERVAL
                reconfigure_slave_replication "$slave_host" "$slave_port" $((retry_count + 1))
            else
                log_message "ERROR: 从库 $slave_host:$slave_port 重连失败，已达到最大重试次数"
                return 1
            fi
        fi
    else
        log_message "ERROR: 从库 $slave_host:$slave_port 复制启动失败"
        return 1
    fi
}

# 主监控循环
main() {
    log_message "开始MySQL主从自动重连监控..."
    
    while true; do
        # 检查主库状态
        if ! check_master_connection; then
            log_message "ALERT: 主库连接失败，等待恢复..."
            sleep 60
            continue
        fi
        
        # 检查所有从库
        for slave in "${SLAVES[@]}"; do
            local slave_host=$(echo $slave | cut -d: -f1)
            local slave_port=$(echo $slave | cut -d: -f2)
            
            local replication_status=$(check_slave_replication "$slave_host" "$slave_port")
            local status_code=$?
            
            case $status_code in
                0)
                    # 复制正常
                    ;;
                1)
                    # 复制异常，尝试重连
                    log_message "检测到从库 $slave 复制异常，开始自动重连..."
                    reconfigure_slave_replication "$slave_host" "$slave_port"
                    ;;
                2)
                    # 从库连接失败
                    log_message "从库 $slave 连接失败，跳过此次检查"
                    ;;
            esac
        done
        
        # 等待下次检查
        sleep 30
    done
}

# 信号处理
trap 'log_message "自动重连监控停止"; exit 0' SIGTERM SIGINT

# 启动监控
main
```

#### 1.2 故障转移脚本

```bash
#!/bin/bash
# 文件名：failover.sh
# 功能：主库故障时的自动故障转移

# 配置参数
MASTER_HOST="192.168.11.150"
MASTER_PORT="3306"
SLAVES=("localhost:3306" "localhost:3307" "localhost:3308")
VIP="192.168.11.200"  # 虚拟IP
MYSQL_USER="admin"
MYSQL_PASSWORD="admin123"
LOG_FILE="/var/log/mysql_failover.log"
FAILOVER_LOCK="/tmp/mysql_failover.lock"

# 日志函数
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查是否已有故障转移进程在运行
check_failover_lock() {
    if [[ -f "$FAILOVER_LOCK" ]]; then
        local lock_pid=$(cat "$FAILOVER_LOCK")
        if kill -0 "$lock_pid" 2>/dev/null; then
            log_message "故障转移进程已在运行 (PID: $lock_pid)"
            exit 1
        else
            log_message "清理过期的故障转移锁文件"
            rm -f "$FAILOVER_LOCK"
        fi
    fi
    
    # 创建锁文件
    echo $$ > "$FAILOVER_LOCK"
}

# 清理锁文件
cleanup_lock() {
    rm -f "$FAILOVER_LOCK"
}

# 检查主库状态
check_master_status() {
    local retry_count=3
    local retry_interval=10
    
    for ((i=1; i<=retry_count; i++)); do
        if mysql -h"$MASTER_HOST" -P"$MASTER_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1" >/dev/null 2>&1; then
            return 0
        fi
        
        log_message "主库检查失败 (尝试 $i/$retry_count)"
        if [[ $i -lt $retry_count ]]; then
            sleep $retry_interval
        fi
    done
    
    return 1
}

# 选择最佳从库作为新主库
select_best_slave() {
    local best_slave=""
    local best_score=0
    
    log_message "开始选择最佳从库作为新主库..."
    
    for slave in "${SLAVES[@]}"; do
        local slave_host=$(echo $slave | cut -d: -f1)
        local slave_port=$(echo $slave | cut -d: -f2)
        
        # 检查从库连接
        if ! mysql -h"$slave_host" -P"$slave_port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1" >/dev/null 2>&1; then
            log_message "从库 $slave 连接失败，跳过"
            continue
        fi
        
        # 获取从库状态
        local slave_status=$(mysql -h"$slave_host" -P"$slave_port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SHOW REPLICA STATUS\G" 2>/dev/null)
        
        local io_running=$(echo "$slave_status" | grep "Replica_IO_Running:" | awk '{print $2}')
        local sql_running=$(echo "$slave_status" | grep "Replica_SQL_Running:" | awk '{print $2}')
        local seconds_behind=$(echo "$slave_status" | grep "Seconds_Behind_Master:" | awk '{print $2}')
        local exec_master_log_pos=$(echo "$slave_status" | grep "Exec_Master_Log_Pos:" | awk '{print $2}')
        
        # 计算从库得分
        local score=0
        
        # IO和SQL线程都在运行 +50分
        if [[ "$io_running" == "Yes" && "$sql_running" == "Yes" ]]; then
            score=$((score + 50))
        fi
        
        # 延迟时间评分（延迟越小得分越高）
        if [[ "$seconds_behind" != "NULL" && "$seconds_behind" -ne "" ]]; then
            if [[ $seconds_behind -eq 0 ]]; then
                score=$((score + 30))
            elif [[ $seconds_behind -le 5 ]]; then
                score=$((score + 20))
            elif [[ $seconds_behind -le 10 ]]; then
                score=$((score + 10))
            fi
        fi
        
        # binlog位置评分（位置越大得分越高）
        if [[ -n "$exec_master_log_pos" && "$exec_master_log_pos" -ne "" ]]; then
            score=$((score + exec_master_log_pos / 1000000))  # 简化计算
        fi
        
        log_message "从库 $slave 得分: $score (延迟: ${seconds_behind}s, 位置: $exec_master_log_pos)"
        
        # 选择得分最高的从库
        if [[ $score -gt $best_score ]]; then
            best_score=$score
            best_slave=$slave
        fi
    done
    
    if [[ -n "$best_slave" ]]; then
        log_message "选择从库 $best_slave 作为新主库 (得分: $best_score)"
        echo "$best_slave"
        return 0
    else
        log_message "ERROR: 没有找到合适的从库进行故障转移"
        return 1
    fi
}

# 提升从库为主库
promote_slave_to_master() {
    local new_master=$1
    local new_master_host=$(echo $new_master | cut -d: -f1)
    local new_master_port=$(echo $new_master | cut -d: -f2)
    
    log_message "开始提升从库 $new_master 为新主库..."
    
    # 停止复制
    mysql -h"$new_master_host" -P"$new_master_port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "STOP REPLICA;" 2>/dev/null
    
    # 重置复制配置
    mysql -h"$new_master_host" -P"$new_master_port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "RESET REPLICA ALL;" 2>/dev/null
    
    # 启用binlog（如果需要）
    mysql -h"$new_master_host" -P"$new_master_port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SET GLOBAL log_bin = ON;" 2>/dev/null
    
    # 设置为可写
    mysql -h"$new_master_host" -P"$new_master_port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SET GLOBAL read_only = OFF;" 2>/dev/null
    mysql -h"$new_master_host" -P"$new_master_port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SET GLOBAL super_read_only = OFF;" 2>/dev/null
    
    log_message "从库 $new_master 已提升为新主库"
    return 0
}

# 重新配置其他从库
reconfigure_other_slaves() {
    local new_master=$1
    local new_master_host=$(echo $new_master | cut -d: -f1)
    local new_master_port=$(echo $new_master | cut -d: -f2)
    
    log_message "开始重新配置其他从库指向新主库 $new_master..."
    
    for slave in "${SLAVES[@]}"; do
        if [[ "$slave" == "$new_master" ]]; then
            continue  # 跳过新主库
        fi
        
        local slave_host=$(echo $slave | cut -d: -f1)
        local slave_port=$(echo $slave | cut -d: -f2)
        
        log_message "重新配置从库 $slave..."
        
        # 停止复制
        mysql -h"$slave_host" -P"$slave_port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "STOP REPLICA;" 2>/dev/null
        
        # 重置复制配置
        mysql -h"$slave_host" -P"$slave_port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "RESET REPLICA ALL;" 2>/dev/null
        
        # 配置新的复制源
        mysql -h"$slave_host" -P"$slave_port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "
            CHANGE REPLICATION SOURCE TO
                SOURCE_HOST='$new_master_host',
                SOURCE_PORT=$new_master_port,
                SOURCE_USER='repl',
                SOURCE_PASSWORD='repl123',
                SOURCE_AUTO_POSITION=1;
        " 2>/dev/null
        
        # 启动复制
        if mysql -h"$slave_host" -P"$slave_port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "START REPLICA;" 2>/dev/null; then
            log_message "从库 $slave 重新配置成功"
        else
            log_message "ERROR: 从库 $slave 重新配置失败"
        fi
    done
}

# 更新VIP（虚拟IP）
update_vip() {
    local new_master=$1
    local new_master_host=$(echo $new_master | cut -d: -f1)
    
    log_message "更新VIP $VIP 指向新主库 $new_master_host..."
    
    # 这里需要根据实际的网络环境配置VIP切换
    # 示例：使用keepalived或其他高可用方案
    
    # 简化示例：更新/etc/hosts文件
    if grep -q "mysql-master" /etc/hosts; then
        sudo sed -i "s/.*mysql-master.*/$new_master_host mysql-master/" /etc/hosts
        log_message "已更新 /etc/hosts 中的mysql-master指向"
    fi
    
    return 0
}

# 发送故障转移通知
send_notification() {
    local new_master=$1
    local message="MySQL故障转移完成：新主库为 $new_master"
    
    log_message "$message"
    
    # 这里可以添加邮件、短信、钉钉等通知方式
    # 示例：发送邮件通知
    # echo "$message" | mail -s "MySQL Failover Alert" admin@company.com
    
    # 示例：写入系统日志
    logger -p local0.alert "$message"
}

# 主故障转移函数
main() {
    log_message "开始MySQL故障转移流程..."
    
    # 检查故障转移锁
    check_failover_lock
    
    # 确认主库确实故障
    if check_master_status; then
        log_message "主库状态正常，取消故障转移"
        cleanup_lock
        exit 0
    fi
    
    log_message "确认主库故障，开始故障转移..."
    
    # 选择最佳从库
    local new_master=$(select_best_slave)
    if [[ -z "$new_master" ]]; then
        log_message "ERROR: 故障转移失败，没有可用的从库"
        cleanup_lock
        exit 1
    fi
    
    # 提升从库为主库
    if ! promote_slave_to_master "$new_master"; then
        log_message "ERROR: 提升从库为主库失败"
        cleanup_lock
        exit 1
    fi
    
    # 重新配置其他从库
    reconfigure_other_slaves "$new_master"
    
    # 更新VIP
    update_vip "$new_master"
    
    # 发送通知
    send_notification "$new_master"
    
    log_message "故障转移完成，新主库: $new_master"
    
    # 清理锁文件
    cleanup_lock
}

# 信号处理
trap 'cleanup_lock; exit 1' SIGTERM SIGINT

# 执行故障转移
main "$@"
```

#### 1.3 故障转移系统部署

```bash
#!/bin/bash
# 文件名：deploy_failover.sh
# 功能：部署故障转移系统

echo "部署MySQL故障转移系统..."

# 创建脚本目录
sudo mkdir -p /opt/mysql_failover
sudo chmod 755 /opt/mysql_failover

# 复制故障转移脚本
sudo cp auto_reconnect.sh /opt/mysql_failover/
sudo cp failover.sh /opt/mysql_failover/
sudo chmod +x /opt/mysql_failover/*.sh

# 创建systemd服务
sudo tee /etc/systemd/system/mysql-auto-reconnect.service > /dev/null <<EOF
[Unit]
Description=MySQL Auto Reconnect Monitor
After=network.target

[Service]
Type=simple
User=root
ExecStart=/opt/mysql_failover/auto_reconnect.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 创建故障转移触发脚本
sudo tee /opt/mysql_failover/trigger_failover.sh > /dev/null <<'EOF'
#!/bin/bash
# 故障转移触发脚本

MASTER_HOST="192.168.11.150"
MASTER_PORT="3306"
MYSQL_USER="monitor"
MYSQL_PASSWORD="monitor123"
FAILOVER_SCRIPT="/opt/mysql_failover/failover.sh"

# 检查主库状态
check_master() {
    local retry_count=3
    for ((i=1; i<=retry_count; i++)); do
        if mysql -h"$MASTER_HOST" -P"$MASTER_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1" >/dev/null 2>&1; then
            return 0
        fi
        sleep 5
    done
    return 1
}

# 如果主库故障，触发故障转移
if ! check_master; then
    echo "[$(date)] 检测到主库故障，触发故障转移..."
    $FAILOVER_SCRIPT
else
    echo "[$(date)] 主库状态正常"
fi
EOF

sudo chmod +x /opt/mysql_failover/trigger_failover.sh

# 创建定时检查任务
sudo tee /etc/cron.d/mysql-failover-check > /dev/null <<EOF
# MySQL故障转移检查
*/2 * * * * root /opt/mysql_failover/trigger_failover.sh >> /var/log/mysql_failover_check.log 2>&1
EOF

# 重新加载systemd并启动服务
sudo systemctl daemon-reload
sudo systemctl enable mysql-auto-reconnect.service
sudo systemctl start mysql-auto-reconnect.service

echo "故障转移系统部署完成！"
echo "服务状态："
sudo systemctl status mysql-auto-reconnect.service

echo ""
echo "手动触发故障转移："
echo "sudo /opt/mysql_failover/failover.sh"
echo ""
echo "查看日志："
echo "tail -f /var/log/mysql_auto_reconnect.log"
echo "tail -f /var/log/mysql_failover.log"
```

### 2. 高可用架构配置

#### 2.1 Keepalived配置（VIP管理）

```bash
# 安装keepalived
sudo yum install -y keepalived  # CentOS/RHEL
# 或
sudo apt-get install -y keepalived  # Ubuntu/Debian

# 主库服务器keepalived配置
sudo tee /etc/keepalived/keepalived.conf > /dev/null <<EOF
! Configuration File for keepalived

global_defs {
   notification_email {
     admin@company.com
   }
   notification_email_from keepalived@mysql-master
   smtp_server 127.0.0.1
   smtp_connect_timeout 30
   router_id MYSQL_MASTER
}

vrrp_script chk_mysql {
    script "/opt/mysql_failover/check_mysql.sh"
    interval 2
    weight -2
    fall 3
    rise 2
}

vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass mysql123
    }
    virtual_ipaddress {
        192.168.11.200/24
    }
    track_script {
        chk_mysql
    }
    notify_master "/opt/mysql_failover/notify_master.sh"
    notify_backup "/opt/mysql_failover/notify_backup.sh"
    notify_fault "/opt/mysql_failover/notify_fault.sh"
}
EOF

# 创建MySQL健康检查脚本
sudo tee /opt/mysql_failover/check_mysql.sh > /dev/null <<'EOF'
#!/bin/bash
mysql -h127.0.0.1 -P3306 -umonitor -pmonitor123 -e "SELECT 1" >/dev/null 2>&1
EOF

sudo chmod +x /opt/mysql_failover/check_mysql.sh

# 创建通知脚本
sudo tee /opt/mysql_failover/notify_master.sh > /dev/null <<'EOF'
#!/bin/bash
echo "[$(date)] 成为MySQL主库" >> /var/log/keepalived_mysql.log
# 设置为可写
mysql -h127.0.0.1 -P3306 -uadmin -padmin123 -e "SET GLOBAL read_only = OFF;" 2>/dev/null
mysql -h127.0.0.1 -P3306 -uadmin -padmin123 -e "SET GLOBAL super_read_only = OFF;" 2>/dev/null
EOF

sudo tee /opt/mysql_failover/notify_backup.sh > /dev/null <<'EOF'
#!/bin/bash
echo "[$(date)] 切换为MySQL备库" >> /var/log/keepalived_mysql.log
# 设置为只读
mysql -h127.0.0.1 -P3306 -uadmin -padmin123 -e "SET GLOBAL read_only = ON;" 2>/dev/null
mysql -h127.0.0.1 -P3306 -uadmin -padmin123 -e "SET GLOBAL super_read_only = ON;" 2>/dev/null
EOF

sudo tee /opt/mysql_failover/notify_fault.sh > /dev/null <<'EOF'
#!/bin/bash
echo "[$(date)] MySQL服务故障" >> /var/log/keepalived_mysql.log
# 触发故障转移
/opt/mysql_failover/failover.sh &
EOF

sudo chmod +x /opt/mysql_failover/notify_*.sh

# 启动keepalived
sudo systemctl enable keepalived
sudo systemctl start keepalived
```

#### 2.2 应用连接配置

```python
# Python应用连接配置示例
import pymysql
from pymysql.connections import Connection
import time
import logging

class MySQLConnectionPool:
    """
    MySQL高可用连接池
    支持主从分离和自动故障转移
    """
    
    def __init__(self):
        # 主库配置（使用VIP）
        self.master_config = {
            'host': '192.168.11.200',  # VIP地址
            'port': 3306,
            'user': 'app_user',
            'password': 'app_password',
            'database': 'app_db',
            'charset': 'utf8mb4',
            'autocommit': True,
            'connect_timeout': 10,
            'read_timeout': 30,
            'write_timeout': 30
        }
        
        # 从库配置（读操作负载均衡）
        self.slave_configs = [
            {
                'host': 'localhost',
                'port': 3306,
                'user': 'app_user',
                'password': 'app_password',
                'database': 'app_db',
                'charset': 'utf8mb4',
                'connect_timeout': 10,
                'read_timeout': 30
            },
            {
                'host': 'localhost',
                'port': 3307,
                'user': 'app_user',
                'password': 'app_password',
                'database': 'app_db',
                'charset': 'utf8mb4',
                'connect_timeout': 10,
                'read_timeout': 30
            },
            {
                'host': 'localhost',
                'port': 3308,
                'user': 'app_user',
                'password': 'app_password',
                'database': 'app_db',
                'charset': 'utf8mb4',
                'connect_timeout': 10,
                'read_timeout': 30
            }
        ]
        
        self.current_slave_index = 0
        self.logger = logging.getLogger(__name__)
    
    def get_master_connection(self, retry_count=3):
        """获取主库连接（写操作）"""
        for attempt in range(retry_count):
            try:
                conn = pymysql.connect(**self.master_config)
                return conn
            except Exception as e:
                self.logger.error(f"主库连接失败 (尝试 {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    raise
    
    def get_slave_connection(self, retry_count=3):
        """获取从库连接（读操作，支持负载均衡）"""
        slave_count = len(self.slave_configs)
        
        for attempt in range(retry_count):
            for i in range(slave_count):
                slave_index = (self.current_slave_index + i) % slave_count
                slave_config = self.slave_configs[slave_index]
                
                try:
                    conn = pymysql.connect(**slave_config)
                    self.current_slave_index = (slave_index + 1) % slave_count
                    return conn
                except Exception as e:
                    self.logger.warning(f"从库 {slave_config['host']}:{slave_config['port']} 连接失败: {e}")
                    continue
            
            if attempt < retry_count - 1:
                self.logger.info(f"所有从库连接失败，等待后重试 (尝试 {attempt + 1}/{retry_count})")
                time.sleep(2 ** attempt)
        
        # 如果所有从库都失败，使用主库进行读操作
        self.logger.warning("所有从库不可用，使用主库进行读操作")
        return self.get_master_connection()
    
    def execute_write(self, sql, params=None):
        """执行写操作"""
        conn = None
        try:
            conn = self.get_master_connection()
            with conn.cursor() as cursor:
                result = cursor.execute(sql, params)
                conn.commit()
                return result
        finally:
            if conn:
                conn.close()
    
    def execute_read(self, sql, params=None):
        """执行读操作"""
        conn = None
        try:
            conn = self.get_slave_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        finally:
            if conn:
                conn.close()

# 使用示例
if __name__ == "__main__":
    pool = MySQLConnectionPool()
    
    # 写操作
    try:
        result = pool.execute_write(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            ("张三", "zhangsan@example.com")
        )
        print(f"插入成功，影响行数: {result}")
    except Exception as e:
        print(f"写操作失败: {e}")
    
    # 读操作
    try:
        users = pool.execute_read("SELECT * FROM users LIMIT 10")
        print(f"查询结果: {users}")
    except Exception as e:
        print(f"读操作失败: {e}")
```

**问题1：从库连接失败**
```bash
# 检查网络连通性
ping 192.168.11.150

# 检查端口是否开放
telnet 192.168.11.150 3306

# 检查容器状态（方案一：多容器）
docker ps -a | grep mysql-slave
docker logs mysql-slave-1 --tail 20
docker logs mysql-slave-2 --tail 20
docker logs mysql-slave-3 --tail 20

# 检查容器状态（方案二：多服务器）
docker ps -a | grep mysql-slave
docker logs mysql-slave --tail 20
```

**问题2：权限错误（ERROR 1045 或 ERROR 1130）**

*方案一：单服务器多容器*
```bash
# 重新创建所有从库容器
for i in {1..3}; do
  docker stop mysql-slave-${i}
  docker rm mysql-slave-${i}
  rm -rf /opt/mysql/slave-${i}/data/*
done

# 重新启动所有从库容器
docker run -d --name mysql-slave-1 --restart always -p 3306:3306 \
  -v /opt/mysql/slave-1/data:/var/lib/mysql \
  -v /opt/mysql/slave-1/conf:/etc/mysql/conf.d \
  -v /opt/mysql/slave-1/init:/docker-entrypoint-initdb.d \
  -e MYSQL_ROOT_PASSWORD=zhiyu666 mysql:8.0.43

docker run -d --name mysql-slave-2 --restart always -p 3307:3306 \
  -v /opt/mysql/slave-2/data:/var/lib/mysql \
  -v /opt/mysql/slave-2/conf:/etc/mysql/conf.d \
  -v /opt/mysql/slave-2/init:/docker-entrypoint-initdb.d \
  -e MYSQL_ROOT_PASSWORD=zhiyu666 mysql:8.0.43

docker run -d --name mysql-slave-3 --restart always -p 3308:3306 \
  -v /opt/mysql/slave-3/data:/var/lib/mysql \
  -v /opt/mysql/slave-3/conf:/etc/mysql/conf.d \
  -v /opt/mysql/slave-3/init:/docker-entrypoint-initdb.d \
  -e MYSQL_ROOT_PASSWORD=zhiyu666 mysql:8.0.43
```

*方案二：多服务器*
```bash
# 在每台从库服务器执行
docker stop mysql-slave
docker rm mysql-slave
rm -rf /opt/mysql/slave/data/*

# 重新启动从库容器
docker run -d --name mysql-slave --restart always -p 3306:3306 \
  -v /opt/mysql/slave/data:/var/lib/mysql \
  -v /opt/mysql/slave/conf:/etc/mysql/conf.d \
  -v /opt/mysql/slave/init:/docker-entrypoint-initdb.d \
  -e MYSQL_ROOT_PASSWORD=zhiyu666 mysql:8.0.43
```

**问题3：复制用户权限不足**
```sql
-- 在主库重新授权（支持所有从库）
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'192.168.11.151';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'192.168.11.152';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'192.168.11.153';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
FLUSH PRIVILEGES;
```

**问题4：GTID不一致**
```sql
-- 在每个从库执行
STOP REPLICA;
RESET REPLICA ALL;
-- 重新配置主从关系
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST='192.168.11.150',
  SOURCE_PORT=3306,
  SOURCE_USER='repl',
  SOURCE_PASSWORD='repl123',
  SOURCE_AUTO_POSITION=1;
START REPLICA;
```

**问题5：单服务器多容器端口冲突**
```bash
# 检查端口占用
netstat -tlnp | grep :3306
netstat -tlnp | grep :3307
netstat -tlnp | grep :3308

# 如果端口被占用，修改容器端口映射
docker run -d --name mysql-slave-1 --restart always -p 3309:3306 ...
```

### 2. 监控命令

**主库监控：**
```sql
-- 查看主库状态
SHOW MASTER STATUS;

-- 查看连接的从库数量
SELECT COUNT(*) as slave_connections 
FROM information_schema.processlist 
WHERE command = 'Binlog Dump GTID';

-- 查看所有连接
SHOW PROCESSLIST;

-- 查看GTID执行情况
SHOW GLOBAL VARIABLES LIKE 'gtid_executed';
```

**从库监控：**
```sql
-- 查看从库状态（在每个从库执行）
SHOW REPLICA STATUS\G

-- 重点关注以下字段：
-- Replica_IO_Running: Yes
-- Replica_SQL_Running: Yes
-- Last_IO_Error: (应该为空)
-- Last_SQL_Error: (应该为空)
-- Seconds_Behind_Master: (延迟秒数，应该很小)
-- Retrieved_Gtid_Set: (已接收的GTID)
-- Executed_Gtid_Set: (已执行的GTID)
```

**批量检查所有从库状态：**

*方案一：单服务器多容器*
```bash
#!/bin/bash
for i in {1..3}; do
  echo "=== 检查从库 mysql-slave-${i} ==="
  docker exec mysql-slave-${i} mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G" | grep -E "(Replica_IO_Running|Replica_SQL_Running|Last_IO_Error|Last_SQL_Error|Seconds_Behind_Master)"
  echo ""
done
```

*方案二：多服务器*
```bash
#!/bin/bash
servers=("192.168.11.151" "192.168.11.152" "192.168.11.153")
for server in "${servers[@]}"; do
  echo "=== 检查从库服务器 ${server} ==="
  ssh root@${server} "docker exec mysql-slave mysql -uroot -pzhiyu666 -e 'SHOW REPLICA STATUS\G'" | grep -E "(Replica_IO_Running|Replica_SQL_Running|Last_IO_Error|Last_SQL_Error|Seconds_Behind_Master)"
  echo ""
done
```

### 3. 性能优化建议

**主库优化：**
- 增加 `max_connections` 以支持更多从库连接
- 调整 `binlog_cache_size` 和 `max_binlog_size`
- 监控 `Binlog_cache_use` 和 `Binlog_cache_disk_use` 状态

**从库优化：**
- 调整 `replica_parallel_workers` 数量（建议CPU核心数的2倍）
- 设置合适的 `innodb_buffer_pool_size`（建议物理内存的70-80%）
- 单服务器多容器时，注意内存分配，避免总内存超限

**网络优化：**
- 确保主从服务器间网络稳定，延迟低
- 考虑使用专用网络连接主从服务器
- 监控网络带宽使用情况

------

## 十一、单服务器多容器一键部署脚本

### 完整自动化部署脚本（方案一专用）

```bash
#!/bin/bash
# 文件名：deploy_mysql_single_server.sh
# 功能：单服务器多容器MySQL主从一键部署脚本
# 适用场景：测试环境、开发环境、单机高可用测试

set -e  # 遇到错误立即退出

# ==================== 配置参数 ====================
# 单服务器部署：主库和从库都在同一台服务器
MASTER_HOST="127.0.0.1"  # 主库使用localhost
MYSQL_VERSION="8.0.43"
ROOT_PASSWORD="zhiyu666"
REPL_PASSWORD="repl123"
ADMIN_PASSWORD="admin123"

# 从库数量（单服务器建议1-3个）
SLAVE_COUNT=3

# 端口配置（单服务器需要不同端口）
MASTER_PORT=3306
SLAVE_PORTS=(3307 3308 3309)  # 从库端口

# 资源分配（根据服务器配置调整）
MASTER_MEMORY="14g"
MASTER_CPUS="48"
SLAVE_MEMORY="6g"
SLAVE_CPUS="16"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ==================== 工具函数 ====================
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 未安装，请先安装"
        exit 1
    fi
}

wait_for_mysql() {
    local container_name=$1
    local max_attempts=60
    local attempt=0
    
    log_info "等待 $container_name MySQL启动..."
    
    while [ $attempt -lt $max_attempts ]; do
        if docker exec $container_name mysql -uroot -p${ROOT_PASSWORD} -e "SELECT 1" &>/dev/null; then
            log_info "$container_name MySQL已就绪"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    log_error "$container_name MySQL启动超时"
    return 1
}

# ==================== 环境检查 ====================
check_environment() {
    log_info "检查部署环境..."
    
    # 检查Docker
    check_command docker
    
    # 检查Docker服务状态
    if ! systemctl is-active --quiet docker; then
        log_error "Docker服务未运行"
        exit 1
    fi
    
    # 检查可用内存
    total_memory=$(free -g | awk '/^Mem:/{print $2}')
    required_memory=$((14 + SLAVE_COUNT * 6))
    
    if [ $total_memory -lt $required_memory ]; then
        log_warn "系统内存可能不足（需要${required_memory}G，当前${total_memory}G）"
        read -p "是否继续？(y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    log_info "环境检查通过"
}

# ==================== 清理旧环境 ====================
cleanup_old_deployment() {
    log_info "清理旧的部署..."
    
    # 停止并删除主库容器
    if docker ps -a | grep -q mysql-master; then
        log_warn "发现旧的主库容器，正在删除..."
        docker stop mysql-master 2>/dev/null || true
        docker rm mysql-master 2>/dev/null || true
    fi
    
    # 停止并删除从库容器
    for i in $(seq 1 $SLAVE_COUNT); do
        if docker ps -a | grep -q mysql-slave-${i}; then
            log_warn "发现旧的从库容器 mysql-slave-${i}，正在删除..."
            docker stop mysql-slave-${i} 2>/dev/null || true
            docker rm mysql-slave-${i} 2>/dev/null || true
        fi
    done
    
    log_info "旧环境清理完成"
}

# ==================== 创建目录结构 ====================
create_directories() {
    log_info "创建目录结构..."
    
    # 主库目录
    mkdir -p /opt/mysql/master/{data,conf,init}
    mkdir -p /var/lib/mysql-files
    
    # 从库目录
    for i in $(seq 1 $SLAVE_COUNT); do
        mkdir -p /opt/mysql/slave-${i}/{data,conf,init}
    done
    
    log_info "目录创建完成"
}

# ==================== 生成主库配置 ====================
generate_master_config() {
    log_info "生成主库配置文件..."
    
    cat > /opt/mysql/master/conf/my.cnf << 'EOF'
[mysqld]
server-id=1
datadir=/var/lib/mysql
socket=/var/run/mysqld/mysqld.sock
pid-file=/var/run/mysqld/mysqld.pid
user=mysql
port=3306

default_authentication_plugin=mysql_native_password

# 网络连接优化
connect_timeout=60
interactive_timeout=7200
wait_timeout=7200
net_read_timeout=120
net_write_timeout=120
slave_net_timeout=60
max_connect_errors=100000
skip_name_resolve=1

# 主从复制配置
log_bin=/var/lib/mysql/mysql-bin
binlog_format=ROW
sync_binlog=1
binlog_cache_size=8M
max_binlog_cache_size=128M
max_binlog_size=512M
binlog_expire_logs_seconds=259200
gtid_mode=ON
enforce_gtid_consistency=ON
binlog_transaction_dependency_tracking=WRITESET
transaction_write_set_extraction=XXHASH64

# InnoDB优化
innodb_buffer_pool_size=12G
innodb_buffer_pool_instances=16
innodb_log_buffer_size=128M
innodb_flush_log_at_trx_commit=1
innodb_flush_method=O_DIRECT
innodb_file_per_table=1
innodb_open_files=8192
innodb_io_capacity=4000
innodb_io_capacity_max=8000
innodb_flush_neighbors=0
innodb_read_io_threads=16
innodb_write_io_threads=16
innodb_lock_wait_timeout=50
innodb_deadlock_detect=ON
innodb_log_file_size=2G
innodb_log_files_in_group=2

# 连接优化
max_connections=10000
max_user_connections=9500
thread_cache_size=512
thread_stack=512K
back_log=2048
table_open_cache=8192
table_open_cache_instances=32
table_definition_cache=4096

# 内存优化
tmp_table_size=128M
max_heap_table_size=128M
sort_buffer_size=8M
join_buffer_size=8M
read_buffer_size=4M
read_rnd_buffer_size=8M

# 日志配置
slow_query_log=1
slow_query_log_file=/var/lib/mysql/mysql-slow.log
long_query_time=0.5
log_queries_not_using_indexes=1
log_error=/var/lib/mysql/mysql-error.log
log_error_verbosity=2
performance_schema=ON

# 其他配置
max_allowed_packet=128M
open_files_limit=65535
character_set_server=utf8mb4
collation_server=utf8mb4_unicode_ci
default_time_zone='+8:00'
local_infile=0
secure_file_priv=/var/lib/mysql-files/

# 复制监控
log_slave_updates=1
relay_log_info_repository=TABLE
master_info_repository=TABLE
EOF

    log_info "主库配置文件生成完成"
}

# ==================== 生成主库初始化SQL ====================
generate_master_init_sql() {
    log_info "生成主库初始化SQL..."
    
    cat > /opt/mysql/master/init/init.sql << EOF
-- 修改root用户
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${ROOT_PASSWORD}';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '${ROOT_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

-- 创建管理用户
CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY '${ADMIN_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;

-- 创建复制用户
CREATE USER IF NOT EXISTS 'repl'@'%' IDENTIFIED BY '${REPL_PASSWORD}';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';

-- 创建监控用户
CREATE USER IF NOT EXISTS 'monitor'@'%' IDENTIFIED BY 'monitor123';
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'monitor'@'%';
GRANT SELECT ON performance_schema.* TO 'monitor'@'%';
GRANT SELECT ON information_schema.* TO 'monitor'@'%';

FLUSH PRIVILEGES;
EOF

    log_info "主库初始化SQL生成完成"
}

# ==================== 生成从库配置 ====================
generate_slave_configs() {
    log_info "生成从库配置文件..."
    
    for i in $(seq 1 $SLAVE_COUNT); do
        server_id=$((i + 1))
        
        cat > /opt/mysql/slave-${i}/conf/my.cnf << EOF
[mysqld]
server-id=${server_id}
datadir=/var/lib/mysql
socket=/var/run/mysqld/mysqld.sock
pid-file=/var/run/mysqld/mysqld.pid
user=mysql
port=3306

default_authentication_plugin=mysql_native_password

# 网络连接优化
connect_timeout=60
interactive_timeout=7200
wait_timeout=7200
net_read_timeout=120
net_write_timeout=120
slave_net_timeout=60
max_connect_errors=100000
skip_name_resolve=1

# 主从复制配置
relay_log=/var/lib/mysql/mysql-relay-bin
relay_log_recovery=ON
log_bin=OFF
replica_parallel_workers=32
replica_parallel_type=LOGICAL_CLOCK
replica_preserve_commit_order=ON
replica_pending_jobs_size_max=128M
replica_checkpoint_period=300
replica_checkpoint_group=512
gtid_mode=ON
enforce_gtid_consistency=ON
replica_transaction_retries=10

# InnoDB优化
innodb_buffer_pool_size=4G
innodb_buffer_pool_instances=8
innodb_log_buffer_size=128M
innodb_flush_log_at_trx_commit=2
innodb_flush_method=O_DIRECT
innodb_file_per_table=1
innodb_open_files=8192
innodb_io_capacity=4000
innodb_io_capacity_max=8000
innodb_flush_neighbors=0
innodb_read_io_threads=16
innodb_write_io_threads=16
innodb_lock_wait_timeout=50
innodb_deadlock_detect=ON
innodb_log_file_size=1G
innodb_log_files_in_group=2

# 连接优化
max_connections=8000
max_user_connections=7500
thread_cache_size=512
thread_stack=512K
back_log=2048
table_open_cache=8192
table_open_cache_instances=32
table_definition_cache=4096

# 内存优化
tmp_table_size=128M
max_heap_table_size=128M
sort_buffer_size=8M
join_buffer_size=8M
read_buffer_size=4M
read_rnd_buffer_size=8M

# 日志配置
slow_query_log=1
slow_query_log_file=/var/lib/mysql/mysql-slow.log
long_query_time=0.5
log_queries_not_using_indexes=1
log_error=/var/lib/mysql/mysql-error.log
performance_schema=ON

# 其他配置
max_allowed_packet=128M
open_files_limit=65535
character_set_server=utf8mb4
collation_server=utf8mb4_unicode_ci
default_time_zone='+8:00'
local_infile=0
secure_file_priv=/var/lib/mysql-files/

# 从库特有配置
relay_log_info_repository=TABLE
master_info_repository=TABLE
relay_log_purge=1
relay_log_space_limit=10G
EOF

        # 生成从库初始化SQL
        cat > /opt/mysql/slave-${i}/init/init.sql << EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${ROOT_PASSWORD}';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '${ROOT_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY '${ADMIN_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;

FLUSH PRIVILEGES;
EOF

        log_info "从库${i}配置文件生成完成 (server-id=${server_id})"
    done
}

# ==================== 启动主库 ====================
start_master() {
    log_info "启动主库容器（端口${MASTER_PORT}）..."
    
    docker run -d \
        --name mysql-master \
        --restart always \
        -p ${MASTER_PORT}:3306 \
        -v /opt/mysql/master/data:/var/lib/mysql \
        -v /opt/mysql/master/conf:/etc/mysql/conf.d \
        -v /opt/mysql/master/init:/docker-entrypoint-initdb.d \
        -v /var/lib/mysql-files:/var/lib/mysql-files \
        -e MYSQL_ROOT_PASSWORD=${ROOT_PASSWORD} \
        --memory=${MASTER_MEMORY} \
        --cpus=${MASTER_CPUS} \
        --ulimit nofile=65535:65535 \
        mysql:${MYSQL_VERSION}
    
    if ! wait_for_mysql "mysql-master"; then
        log_error "主库启动失败"
        docker logs mysql-master --tail 50
        exit 1
    fi
    
    log_info "主库启动成功（端口${MASTER_PORT}）"
}

# ==================== 启动从库 ====================
start_slaves() {
    log_info "启动从库容器..."
    
    for i in $(seq 1 $SLAVE_COUNT); do
        local port=${SLAVE_PORTS[$((i-1))]}
        
        log_info "启动从库${i} (端口${port})..."
        
        docker run -d \
            --name mysql-slave-${i} \
            --restart always \
            -p ${port}:3306 \
            -v /opt/mysql/slave-${i}/data:/var/lib/mysql \
            -v /opt/mysql/slave-${i}/conf:/etc/mysql/conf.d \
            -v /opt/mysql/slave-${i}/init:/docker-entrypoint-initdb.d \
            -v /var/lib/mysql-files:/var/lib/mysql-files \
            -e MYSQL_ROOT_PASSWORD=${ROOT_PASSWORD} \
            --memory=${SLAVE_MEMORY} \
            --cpus=${SLAVE_CPUS} \
            --ulimit nofile=65535:65535 \
            mysql:${MYSQL_VERSION}
        
        if ! wait_for_mysql "mysql-slave-${i}"; then
            log_error "从库${i}启动失败"
            docker logs mysql-slave-${i} --tail 50
            exit 1
        fi
        
        log_info "从库${i}启动成功（端口${port}）"
    done
}

# ==================== 配置主从复制 ====================
configure_replication() {
    log_info "配置主从复制..."
    
    # 获取主库的实际IP（单服务器环境）
    local master_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql-master)
    
    if [ -z "$master_ip" ]; then
        log_warn "无法获取主库容器IP，使用宿主机IP"
        master_ip=$(hostname -I | awk '{print $1}')
    fi
    
    log_info "主库IP: ${master_ip}"
    
    for i in $(seq 1 $SLAVE_COUNT); do
        log_info "配置从库${i}的复制..."
        
        # 使用主库容器IP或宿主机IP + 主库端口
        docker exec mysql-slave-${i} mysql -uroot -p${ROOT_PASSWORD} << EOF
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='${master_ip}',
    SOURCE_PORT=${MASTER_PORT},
    SOURCE_USER='repl',
    SOURCE_PASSWORD='${REPL_PASSWORD}',
    SOURCE_AUTO_POSITION=1,
    SOURCE_CONNECT_RETRY=10,
    SOURCE_RETRY_COUNT=86400;

START REPLICA;
EOF

        if [ $? -eq 0 ]; then
            log_info "从库${i}复制配置成功"
        else
            log_error "从库${i}复制配置失败"
            exit 1
        fi
    done
    
    # 等待复制启动
    sleep 5
}

# ==================== 验证部署 ====================
verify_deployment() {
    log_info "验证部署状态..."
    
    # 检查主库状态
    log_info "检查主库状态..."
    docker exec mysql-master mysql -uroot -p${ROOT_PASSWORD} -e "SHOW MASTER STATUS\G"
    
    # 检查从库状态
    for i in $(seq 1 $SLAVE_COUNT); do
        log_info "检查从库${i}状态..."
        
        local status=$(docker exec mysql-slave-${i} mysql -uroot -p${ROOT_PASSWORD} -e "SHOW REPLICA STATUS\G" 2>/dev/null)
        
        local io_running=$(echo "$status" | grep "Replica_IO_Running:" | awk '{print $2}')
        local sql_running=$(echo "$status" | grep "Replica_SQL_Running:" | awk '{print $2}')
        local seconds_behind=$(echo "$status" | grep "Seconds_Behind_Master:" | awk '{print $2}')
        
        if [ "$io_running" == "Yes" ] && [ "$sql_running" == "Yes" ]; then
            log_info "从库${i}: IO=Yes, SQL=Yes, 延迟=${seconds_behind}秒 ✓"
        else
            log_error "从库${i}: IO=${io_running}, SQL=${sql_running} ✗"
            echo "$status"
        fi
    done
}

# ==================== 测试数据同步 ====================
test_replication() {
    log_info "测试数据同步..."
    
    # 在主库创建测试数据
    docker exec mysql-master mysql -uroot -p${ROOT_PASSWORD} << 'EOF'
CREATE DATABASE IF NOT EXISTS replication_test;
USE replication_test;
CREATE TABLE IF NOT EXISTS test_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO test_table (data) VALUES ('test_data_1'), ('test_data_2'), ('test_data_3');
EOF

    log_info "主库测试数据已创建"
    
    # 等待复制
    sleep 3
    
    # 验证从库数据
    for i in $(seq 1 $SLAVE_COUNT); do
        local count=$(docker exec mysql-slave-${i} mysql -uroot -p${ROOT_PASSWORD} -e "SELECT COUNT(*) FROM replication_test.test_table;" -s -N 2>/dev/null)
        
        if [ "$count" == "3" ]; then
            log_info "从库${i}数据同步成功 (${count}条记录) ✓"
        else
            log_error "从库${i}数据同步失败 (${count}条记录) ✗"
        fi
    done
}

# ==================== 生成管理脚本 ====================
generate_management_scripts() {
    log_info "生成管理脚本..."
    
    # 状态检查脚本
    cat > /opt/mysql/check_status.sh << 'SCRIPT'
#!/bin/bash
echo "=========================================="
echo "  MySQL主从状态检查（单服务器环境）"
echo "=========================================="
echo ""

echo "=== 容器状态 ==="
docker ps | grep mysql
echo ""

echo "=== 主库状态（端口3306）==="
docker exec mysql-master mysql -uroot -pzhiyu666 -e "SHOW MASTER STATUS\G"
echo ""

echo "=== 主库连接数 ==="
docker exec mysql-master mysql -uroot -pzhiyu666 -e "SELECT COUNT(*) as slave_connections FROM information_schema.processlist WHERE command = 'Binlog Dump GTID';"
echo ""

for i in {1..3}; do
    port=$((3306 + i))
    echo "=== 从库${i}状态（端口${port}）==="
    docker exec mysql-slave-${i} mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G" 2>/dev/null | grep -E "(Replica_IO_Running|Replica_SQL_Running|Seconds_Behind_Master|Last_IO_Error|Last_SQL_Error)" || echo "从库${i}不存在或未运行"
    echo ""
done

echo "=========================================="
SCRIPT

    chmod +x /opt/mysql/check_status.sh
    
    # 快速连接脚本
    cat > /opt/mysql/connect.sh << 'SCRIPT'
#!/bin/bash
# MySQL快速连接脚本

case "$1" in
    master|m)
        echo "连接到主库（端口3306）..."
        docker exec -it mysql-master mysql -uroot -pzhiyu666
        ;;
    slave1|s1|1)
        echo "连接到从库1（端口3307）..."
        docker exec -it mysql-slave-1 mysql -uroot -pzhiyu666
        ;;
    slave2|s2|2)
        echo "连接到从库2（端口3308）..."
        docker exec -it mysql-slave-2 mysql -uroot -pzhiyu666
        ;;
    slave3|s3|3)
        echo "连接到从库3（端口3309）..."
        docker exec -it mysql-slave-3 mysql -uroot -pzhiyu666
        ;;
    *)
        echo "用法: $0 {master|slave1|slave2|slave3}"
        echo "简写: $0 {m|s1|s2|s3|1|2|3}"
        exit 1
        ;;
esac
SCRIPT

    chmod +x /opt/mysql/connect.sh
    
    log_info "管理脚本生成完成:"
    log_info "  - /opt/mysql/check_status.sh (状态检查)"
    log_info "  - /opt/mysql/connect.sh (快速连接)"
}

# ==================== 主函数 ====================
main() {
    echo "=========================================="
    echo "  MySQL 单服务器多容器主从部署脚本"
    echo "=========================================="
    echo ""
    
    check_environment
    cleanup_old_deployment
    create_directories
    generate_master_config
    generate_master_init_sql
    generate_slave_configs
    start_master
    start_slaves
    configure_replication
    verify_deployment
    test_replication
    generate_management_scripts
    
    echo ""
    echo "=========================================="
    log_info "部署完成！"
    echo "=========================================="
    echo ""
    echo "容器信息："
    docker ps | grep mysql
    echo ""
    echo "快速命令："
    echo "  查看状态: /opt/mysql/check_status.sh"
    echo "  连接主库: /opt/mysql/connect.sh master  (或 m)"
    echo "  连接从库1: /opt/mysql/connect.sh slave1 (或 s1 或 1)"
    echo "  连接从库2: /opt/mysql/connect.sh slave2 (或 s2 或 2)"
    echo "  连接从库3: /opt/mysql/connect.sh slave3 (或 s3 或 3)"
    echo ""
    echo "端口映射："
    echo "  主库: localhost:3306"
    echo "  从库1: localhost:3307"
    echo "  从库2: localhost:3308"
    echo "  从库3: localhost:3309"
    echo ""
    echo "外部连接示例："
    echo "  mysql -h127.0.0.1 -P3306 -uroot -p${ROOT_PASSWORD}  # 主库"
    echo "  mysql -h127.0.0.1 -P3307 -uroot -p${ROOT_PASSWORD}  # 从库1"
    echo ""
}

# 执行主函数
main "$@"
```

### 使用方法

```bash
# 1. 保存脚本
cat > deploy_mysql_single_server.sh << 'EOF'
# ... (复制上面的完整脚本) ...
EOF

# 2. 添加执行权限
chmod +x deploy_mysql_single_server.sh

# 3. 执行部署
sudo ./deploy_mysql_single_server.sh

# 4. 检查状态
/opt/mysql/check_status.sh
```

### 脚本特点

1. **全自动部署**：一键完成主库+3个从库的部署
2. **环境检查**：自动检查Docker、内存等环境
3. **智能清理**：自动清理旧的容器和配置
4. **配置生成**：自动生成所有配置文件
5. **状态验证**：自动验证主从复制状态
6. **数据测试**：自动测试数据同步
7. **彩色输出**：清晰的日志输出
8. **错误处理**：遇到错误自动停止并显示日志
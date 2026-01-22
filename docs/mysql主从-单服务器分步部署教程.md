# MySQL 8.0 单服务器主从复制分步部署教程

## 📋 部署说明

本教程将指导你**一步一步手动部署**MySQL主从复制，适合：
- 🔍 需要了解每个步骤细节
- 🐛 遇到问题需要逐步排查
- 📚 学习MySQL主从复制原理
- ⚙️ 需要自定义配置

> **⚠️ 关键提示**
> 
> **主从复制的核心要点**：
> - 从库连接主库时，必须使用**容器IP + 容器端口3306**
> - 不要使用宿主机IP + 宿主机端口3307
> - 容器间通信走Docker内部网络，不走宿主机端口映射
> 
> **配置复制的正确方法**：
> - ❌ 错误：使用脚本在容器外执行 `docker exec mysql-slave-1 mysql ... << EOF`
> - ✅ 正确：进入MySQL交互界面手动执行 `docker exec -it mysql-slave-1 mysql`
> - **原因**：从库初始化时会重启MySQL，导致脚本配置的复制信息丢失

## 🏗️ 部署架构

```
单台服务器部署：
┌─────────────────────────────────────┐
│  宿主机 (192.168.11.150)            │
│                                     │
│  ┌──────────────┐                  │
│  │ mysql-master │                  │
│  │ 容器IP: 172.17.0.2              │
│  │ 容器端口: 3306                  │
│  │ 宿主机端口: 3307                │
│  └──────┬───────┘                  │
│         │ (容器网络)                │
│         ├──────────┬───────────┐   │
│         │          │           │   │
│  ┌──────▼──┐ ┌────▼───┐ ┌────▼──┐│
│  │ slave-1 │ │ slave-2│ │slave-3││
│  │ 3308    │ │ 3309   │ │ 3310  ││
│  └─────────┘ └────────┘ └───────┘│
└─────────────────────────────────────┘
```

## 第一步：环境准备

### 1.1 检查Docker环境

```bash
# 检查Docker是否安装
docker --version

# 检查Docker服务状态
systemctl status docker

# 如果未启动，启动Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 1.2 检查端口占用

```bash
# 检查端口是否被占用
netstat -tlnp | grep 3307
netstat -tlnp | grep 3308
netstat -tlnp | grep 3309

# 如果有占用，停止相关进程或容器
docker ps -a | grep mysql
docker stop <容器名>
```

### 1.3 清理旧环境（如果存在）

```bash
# 停止旧容器
docker stop mysql-master mysql-slave-1 mysql-slave-2 2>/dev/null

# 删除旧容器
docker rm mysql-master mysql-slave-1 mysql-slave-2 2>/dev/null

# 清理旧数据（谨慎操作！）
sudo rm -rf /opt/mysql/master/data/*
sudo rm -rf /opt/mysql/slave-1/data/*
sudo rm -rf /opt/mysql/slave-2/data/*
```

## 第二步：创建目录结构

```bash
# 创建主库目录
sudo mkdir -p /opt/mysql/master/{data,conf,init}

# 创建从库目录
sudo mkdir -p /opt/mysql/slave-1/{data,conf,init}
sudo mkdir -p /opt/mysql/slave-2/{data,conf,init}

# 验证目录创建
ls -la /opt/mysql/
```

## 第三步：配置主库

### 3.1 创建主库配置文件

```bash
sudo tee /opt/mysql/master/conf/my.cnf > /dev/null << 'EOF'
[mysqld]
server-id=1
port=3306
default_authentication_plugin=mysql_native_password

# 主从复制配置
log_bin=/var/lib/mysql/mysql-bin
binlog_format=ROW
gtid_mode=ON
enforce_gtid_consistency=ON
sync_binlog=1

# 性能配置
innodb_buffer_pool_size=2G
innodb_flush_log_at_trx_commit=1
max_connections=5000
skip_name_resolve=1

# 字符集
character_set_server=utf8mb4
collation_server=utf8mb4_unicode_ci
default_time_zone='+8:00'
EOF

# 验证配置文件
cat /opt/mysql/master/conf/my.cnf
```

### 3.2 创建主库初始化SQL

```bash
sudo tee /opt/mysql/master/init/init.sql > /dev/null << 'EOF'
-- 修改root用户密码
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'zhiyu666';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY 'zhiyu666';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

-- 创建复制用户
CREATE USER IF NOT EXISTS 'repl'@'%' IDENTIFIED BY 'repl123';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';

FLUSH PRIVILEGES;
EOF

# 验证初始化SQL
cat /opt/mysql/master/init/init.sql
```

## 第四步：启动主库容器

### 4.1 启动主库

```bash
docker run -d \
    --name mysql-master \
    --restart always \
    -p 3307:3306 \
    -v /opt/mysql/master/data:/var/lib/mysql \
    -v /opt/mysql/master/conf:/etc/mysql/conf.d \
    -v /opt/mysql/master/init:/docker-entrypoint-initdb.d \
    -e MYSQL_ROOT_PASSWORD=zhiyu666 \
    mysql:8.0.43

echo "主库容器已启动，等待MySQL初始化..."
```

### 4.2 等待主库启动（重要！）

```bash
# 等待60秒让MySQL完全初始化
echo "等待60秒..."
sleep 60

# 检查容器状态
docker ps | grep mysql-master

# 查看容器日志
docker logs mysql-master --tail 20
```

### 4.3 验证主库连接

```bash
# 测试连接
docker exec mysql-master mysql -uroot -pzhiyu666 -e "SELECT 1;"

# 如果上面命令成功，继续
echo "主库连接成功！"
```

### 4.4 获取主库容器IP（关键步骤！）

```bash
# 获取主库容器IP
MASTER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql-master)

echo "=========================================="
echo "主库容器IP: $MASTER_IP"
echo "主库容器端口: 3306"
echo "宿主机访问端口: 3307"
echo "=========================================="
echo ""
echo "⚠️ 重要：从库配置时使用 $MASTER_IP:3306"
echo "不要使用 127.0.0.1:3307 或 192.168.11.150:3307"
echo "=========================================="

# 保存到文件供后续使用
echo "$MASTER_IP" > /tmp/mysql_master_ip.txt
```

### 4.5 检查主库状态

```bash
# 查看主库状态
docker exec mysql-master mysql -uroot -pzhiyu666 -e "SHOW MASTER STATUS\G"

# 查看GTID状态
docker exec mysql-master mysql -uroot -pzhiyu666 -e "SELECT @@GLOBAL.gtid_executed;"

# 验证复制用户
docker exec mysql-master mysql -uroot -pzhiyu666 -e "SELECT user,host FROM mysql.user WHERE user='repl';"
```

## 第五步：配置从库1

### 5.1 创建从库1配置文件

```bash
sudo tee /opt/mysql/slave-1/conf/my.cnf > /dev/null << 'EOF'
[mysqld]
server-id=2
port=3306
default_authentication_plugin=mysql_native_password

# 主从复制配置
relay_log=/var/lib/mysql/mysql-relay-bin
gtid_mode=ON
enforce_gtid_consistency=ON
replica_parallel_workers=4
replica_parallel_type=LOGICAL_CLOCK

# 关键：从库禁用binlog，避免产生自己的GTID
skip-log-bin
log_replica_updates=OFF

# 性能配置
innodb_buffer_pool_size=1G
innodb_flush_log_at_trx_commit=2
max_connections=3000
skip_name_resolve=1

# 字符集
character_set_server=utf8mb4
collation_server=utf8mb4_unicode_ci
default_time_zone='+8:00'
EOF

# 验证配置
cat /opt/mysql/slave-1/conf/my.cnf | grep server-id
```

### 5.2 创建从库1初始化SQL

```bash
sudo tee /opt/mysql/slave-1/init/init.sql > /dev/null << 'EOF'
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'zhiyu666';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY 'zhiyu666';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF
```

### 5.3 启动从库1容器

```bash
docker run -d \
    --name mysql-slave-1 \
    --restart always \
    -p 3308:3306 \
    -v /opt/mysql/slave-1/data:/var/lib/mysql \
    -v /opt/mysql/slave-1/conf:/etc/mysql/conf.d \
    -v /opt/mysql/slave-1/init:/docker-entrypoint-initdb.d \
    -e MYSQL_ROOT_PASSWORD=zhiyu666 \
    mysql:8.0.43

echo "从库1容器已启动，等待MySQL初始化..."
sleep 60

# 检查容器状态
docker ps | grep mysql-slave-1

# 测试连接
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SELECT 1;"
```

### 5.4 配置从库1的主从复制（关键步骤！）

> **⚠️ 重要说明**
> 
> 从库容器在初始化时会重启MySQL服务，导致通过脚本配置的复制信息丢失。
> 因此，我们需要**手动进入MySQL交互界面**配置复制，这样配置才会被持久化保存。

```bash
# 读取主库IP
MASTER_IP=$(cat /tmp/mysql_master_ip.txt)

echo "=========================================="
echo "配置从库1连接到主库"
echo "主库容器IP: $MASTER_IP"
echo "主库容器端口: 3306"
echo "=========================================="

# 进入从库1的MySQL交互界面
docker exec -it mysql-slave-1 mysql -uroot -pzhiyu666
```

**在MySQL交互界面中执行以下命令**（在 `mysql>` 提示符下）：

```sql
-- 1. 停止复制（如果有）
STOP REPLICA;

-- 2. 重置复制配置
RESET REPLICA ALL;

-- 3. 配置复制源（使用主库容器IP）
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='172.17.0.2',
    SOURCE_PORT=3306,
    SOURCE_USER='repl',
    SOURCE_PASSWORD='repl123',
    SOURCE_AUTO_POSITION=1;

-- 4. 启动复制
START REPLICA;

-- 5. 查看状态
SHOW REPLICA STATUS\G

-- 6. 退出MySQL
exit
```

**预期输出**：
- `Replica_IO_Running: Yes`
- `Replica_SQL_Running: Yes`
- `Seconds_Behind_Source: 0`
- `Last_IO_Error:` 为空
- `Last_SQL_Error:` 为空

### 5.5 验证从库1状态

```bash
echo "等待5秒让复制启动..."
sleep 5

# 查看从库状态
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G" | grep -E "(Replica_IO_Running|Replica_SQL_Running|Seconds_Behind_Master|Last_IO_Error|Last_SQL_Error)"

# 详细状态
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G"
```

**预期结果**：
- `Replica_IO_Running: Yes`
- `Replica_SQL_Running: Yes`
- `Seconds_Behind_Master: 0` 或很小的数字
- `Last_IO_Error:` 为空
- `Last_SQL_Error:` 为空

**如果出现错误**，查看错误信息并参考文档末尾的故障排查部分。

## 第六步：配置从库2

### 6.1 创建从库2配置文件

```bash
sudo tee /opt/mysql/slave-2/conf/my.cnf > /dev/null << 'EOF'
[mysqld]
server-id=3
port=3306
default_authentication_plugin=mysql_native_password

# 主从复制配置
relay_log=/var/lib/mysql/mysql-relay-bin
gtid_mode=ON
enforce_gtid_consistency=ON
replica_parallel_workers=4
replica_parallel_type=LOGICAL_CLOCK

# 关键：从库禁用binlog，避免产生自己的GTID
skip-log-bin
log_replica_updates=OFF

# 性能配置
innodb_buffer_pool_size=1G
innodb_flush_log_at_trx_commit=2
max_connections=3000
skip_name_resolve=1

# 字符集
character_set_server=utf8mb4
collation_server=utf8mb4_unicode_ci
default_time_zone='+8:00'
EOF

# 验证配置
cat /opt/mysql/slave-2/conf/my.cnf | grep server-id
```

### 6.2 创建从库2初始化SQL

```bash
sudo tee /opt/mysql/slave-2/init/init.sql > /dev/null << 'EOF'
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'zhiyu666';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY 'zhiyu666';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF
```

### 6.3 启动从库2容器

```bash
docker run -d \
    --name mysql-slave-2 \
    --restart always \
    -p 3309:3306 \
    -v /opt/mysql/slave-2/data:/var/lib/mysql \
    -v /opt/mysql/slave-2/conf:/etc/mysql/conf.d \
    -v /opt/mysql/slave-2/init:/docker-entrypoint-initdb.d \
    -e MYSQL_ROOT_PASSWORD=zhiyu666 \
    mysql:8.0.43

echo "从库2容器已启动，等待MySQL初始化..."
sleep 60

# 检查容器状态
docker ps | grep mysql-slave-2

# 测试连接
docker exec mysql-slave-2 mysql -uroot -pzhiyu666 -e "SELECT 1;"
```

### 6.4 配置从库2的主从复制

```bash
# 读取主库IP
MASTER_IP=$(cat /tmp/mysql_master_ip.txt)

echo "=========================================="
echo "配置从库2连接到主库"
echo "主库容器IP: $MASTER_IP"
echo "主库容器端口: 3306"
echo "=========================================="

# 进入从库2的MySQL交互界面
docker exec -it mysql-slave-2 mysql -uroot -pzhiyu666
```

**在MySQL交互界面中执行以下命令**：

```sql
STOP REPLICA;
RESET REPLICA ALL;
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='172.17.0.2',
    SOURCE_PORT=3306,
    SOURCE_USER='repl',
    SOURCE_PASSWORD='repl123',
    SOURCE_AUTO_POSITION=1;
START REPLICA;
SHOW REPLICA STATUS\G
exit
```

**验证**：确认 `Replica_IO_Running: Yes` 和 `Replica_SQL_Running: Yes`

### 6.5 验证从库2状态

```bash
echo "等待5秒让复制启动..."
sleep 5

# 查看从库状态
docker exec mysql-slave-2 mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G" | grep -E "(Replica_IO_Running|Replica_SQL_Running|Seconds_Behind_Master|Last_IO_Error|Last_SQL_Error)"
```

## 第七步：验证主从复制

### 7.1 查看所有容器状态

```bash
echo "=========================================="
echo "所有MySQL容器状态"
echo "=========================================="
docker ps | grep mysql
```

### 7.2 查看主库状态

```bash
echo ""
echo "=========================================="
echo "主库状态"
echo "=========================================="
docker exec mysql-master mysql -uroot -pzhiyu666 -e "SHOW MASTER STATUS\G"
```

### 7.3 查看所有从库状态

```bash
echo ""
echo "=========================================="
echo "从库1状态"
echo "=========================================="
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G" | grep -E "(Replica_IO_Running|Replica_SQL_Running|Seconds_Behind_Master|Last_IO_Error|Last_SQL_Error)"

echo ""
echo "=========================================="
echo "从库2状态"
echo "=========================================="
docker exec mysql-slave-2 mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G" | grep -E "(Replica_IO_Running|Replica_SQL_Running|Seconds_Behind_Master|Last_IO_Error|Last_SQL_Error)"
```

### 7.4 测试数据同步

```bash
echo ""
echo "=========================================="
echo "测试数据同步"
echo "=========================================="

# 在主库创建测试数据
docker exec mysql-master mysql -uroot -pzhiyu666 << 'EOF'
CREATE DATABASE IF NOT EXISTS test_sync;
USE test_sync;
CREATE TABLE IF NOT EXISTS test_table (
    id INT PRIMARY KEY AUTO_INCREMENT,
    data VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO test_table (data) VALUES ('test1'), ('test2'), ('test3');
SELECT * FROM test_table;
EOF

echo ""
echo "等待3秒让数据同步..."
sleep 3

# 在从库1查询
echo ""
echo "从库1数据："
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SELECT * FROM test_sync.test_table;"

# 在从库2查询
echo ""
echo "从库2数据："
docker exec mysql-slave-2 mysql -uroot -pzhiyu666 -e "SELECT * FROM test_sync.test_table;"
```

## 第八步：创建管理脚本

### 8.1 创建状态检查脚本

```bash
sudo tee /opt/mysql/check_status.sh > /dev/null << 'EOF'
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
echo "=== 从库1状态 ==="
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G" 2>/dev/null | grep -E "(Replica_IO_Running|Replica_SQL_Running|Seconds_Behind_Master|Last_IO_Error|Last_SQL_Error)"
echo ""
echo "=== 从库2状态 ==="
docker exec mysql-slave-2 mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G" 2>/dev/null | grep -E "(Replica_IO_Running|Replica_SQL_Running|Seconds_Behind_Master|Last_IO_Error|Last_SQL_Error)"
echo ""
EOF

sudo chmod +x /opt/mysql/check_status.sh
```

### 8.2 创建快速连接脚本

```bash
sudo tee /opt/mysql/connect.sh > /dev/null << 'EOF'
#!/bin/bash
case "$1" in
    master|m)
        echo "连接到主库（端口3307）..."
        docker exec -it mysql-master mysql -uroot -pzhiyu666
        ;;
    slave1|s1|1)
        echo "连接到从库1（端口3308）..."
        docker exec -it mysql-slave-1 mysql -uroot -pzhiyu666
        ;;
    slave2|s2|2)
        echo "连接到从库2（端口3309）..."
        docker exec -it mysql-slave-2 mysql -uroot -pzhiyu666
        ;;
    *)
        echo "用法: $0 {master|slave1|slave2}"
        echo "简写: $0 {m|s1|s2|1|2}"
        exit 1
        ;;
esac
EOF

sudo chmod +x /opt/mysql/connect.sh
```

### 8.3 测试管理脚本

```bash
# 测试状态检查
/opt/mysql/check_status.sh

# 测试连接（输入exit退出）
# /opt/mysql/connect.sh master
```

## 第九步：部署完成

```bash
echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
echo "端口映射："
echo "  主库: localhost:3307 -> 容器3306"
echo "  从库1: localhost:3308 -> 容器3306"
echo "  从库2: localhost:3309 -> 容器3306"
echo ""
echo "快速命令："
echo "  查看状态: /opt/mysql/check_status.sh"
echo "  连接主库: /opt/mysql/connect.sh master"
echo "  连接从库1: /opt/mysql/connect.sh slave1"
echo "  连接从库2: /opt/mysql/connect.sh slave2"
echo ""
echo "外部连接："
echo "  mysql -h127.0.0.1 -P3307 -uroot -pzhiyu666  # 主库"
echo "  mysql -h127.0.0.1 -P3308 -uroot -pzhiyu666  # 从库1"
echo "  mysql -h127.0.0.1 -P3309 -uroot -pzhiyu666  # 从库2"
echo ""
```

## 🔧 故障排查

### 问题0：SHOW REPLICA STATUS 返回空结果或数据不同步

**症状**：
- 执行 `SHOW REPLICA STATUS\G` 返回 `Empty set`
- 或者复制状态显示正常但数据不同步
- `Executed_Gtid_Set` 包含从库自己的UUID

**根本原因**：
1. 从库在初始化时执行 `init.sql`，产生了自己的GTID事务
2. 从库容器初始化完成后MySQL会重启
3. 通过脚本在容器外执行的 `CHANGE REPLICATION SOURCE TO` 在重启后丢失
4. 从库的GTID集合包含了自己的事务，导致与主库GTID不一致

**完整解决方法**：

**步骤1：清理并重新部署（推荐）**

```bash
# 1. 停止并删除从库容器
docker stop mysql-slave-1 mysql-slave-2
docker rm mysql-slave-1 mysql-slave-2

# 2. 清理从库数据
sudo rm -rf /opt/mysql/slave-1/data/*
sudo rm -rf /opt/mysql/slave-2/data/*

# 3. 更新从库配置，添加禁用binlog的配置
sudo tee /opt/mysql/slave-1/conf/my.cnf > /dev/null << 'EOF'
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

# 对从库2做同样的操作（server-id=3）
sudo tee /opt/mysql/slave-2/conf/my.cnf > /dev/null << 'EOF'
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

# 4. 重新启动从库（按照第五步和第六步的步骤）
```

**步骤2：手动配置复制**

```bash
# 获取主库容器IP
MASTER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql-master)
echo "主库容器IP: $MASTER_IP"

# 进入从库MySQL交互界面
docker exec -it mysql-slave-1 mysql -uroot -pzhiyu666

# 在 mysql> 提示符下执行
STOP REPLICA;
RESET REPLICA ALL;
RESET MASTER;  -- 清除从库自己的GTID
SET GLOBAL gtid_purged='';  -- 清空gtid_purged
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='172.17.0.2',
    SOURCE_PORT=3306,
    SOURCE_USER='repl',
    SOURCE_PASSWORD='repl123',
    SOURCE_AUTO_POSITION=1;
START REPLICA;
SHOW REPLICA STATUS\G
exit
```

**关键配置说明**：
- `skip-log-bin`：从库不生成binlog，避免产生自己的GTID
- `log_replica_updates=OFF`：从库不记录复制的更新到binlog
- `RESET MASTER`：清除从库自己产生的GTID
- 这样从库只会有主库复制过来的GTID，保证一致性

### 问题1：从库IO线程未运行

**症状**：`Replica_IO_Running: No`

**原因**：通常是连接主库失败

**解决方法**：

```bash
# 1. 检查主库容器IP
MASTER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql-master)
echo "主库容器IP: $MASTER_IP"

# 2. 从从库容器内测试连接主库
docker exec mysql-slave-1 mysql -h${MASTER_IP} -P3306 -urepl -prepl123 -e "SELECT 1;"

# 3. 如果连接失败，检查主库复制用户
docker exec mysql-master mysql -uroot -pzhiyu666 -e "SELECT user,host FROM mysql.user WHERE user='repl';"

# 4. 重新配置从库
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 << EOF
STOP REPLICA;
RESET REPLICA ALL;
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='${MASTER_IP}',
    SOURCE_PORT=3306,
    SOURCE_USER='repl',
    SOURCE_PASSWORD='repl123',
    SOURCE_AUTO_POSITION=1;
START REPLICA;
EOF

# 5. 查看详细错误
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G" | grep -A 5 "Last_IO_Error"
```

### 问题2：从库SQL线程未运行

**症状**：`Replica_SQL_Running: No`

**原因**：通常是SQL执行错误

**解决方法**：

```bash
# 1. 查看SQL错误
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G" | grep -A 5 "Last_SQL_Error"

# 2. 如果是GTID相关错误，重置从库
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 << EOF
STOP REPLICA;
RESET REPLICA ALL;
RESET MASTER;
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='${MASTER_IP}',
    SOURCE_PORT=3306,
    SOURCE_USER='repl',
    SOURCE_PASSWORD='repl123',
    SOURCE_AUTO_POSITION=1;
START REPLICA;
EOF
```

### 问题3：容器无法启动

**解决方法**：

```bash
# 查看容器日志
docker logs mysql-master --tail 50
docker logs mysql-slave-1 --tail 50

# 检查配置文件语法
cat /opt/mysql/master/conf/my.cnf
cat /opt/mysql/slave-1/conf/my.cnf

# 检查端口占用
netstat -tlnp | grep 3307
netstat -tlnp | grep 3308
```

### 问题4：数据不同步

**解决方法**：

```bash
# 1. 检查从库延迟
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G" | grep "Seconds_Behind_Master"

# 2. 检查GTID
docker exec mysql-master mysql -uroot -pzhiyu666 -e "SELECT @@GLOBAL.gtid_executed;"
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SELECT @@GLOBAL.gtid_executed;"

# 3. 手动测试同步
docker exec mysql-master mysql -uroot -pzhiyu666 -e "CREATE DATABASE test_$(date +%s); SHOW DATABASES;"
sleep 2
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SHOW DATABASES;"
```

## 📝 常用命令

```bash
# 查看所有容器
docker ps -a | grep mysql

# 重启容器
docker restart mysql-master
docker restart mysql-slave-1
docker restart mysql-slave-2

# 查看容器日志
docker logs mysql-master --tail 50
docker logs mysql-slave-1 --tail 50

# 进入容器
docker exec -it mysql-master bash
docker exec -it mysql-slave-1 bash

# 停止所有容器
docker stop mysql-master mysql-slave-1 mysql-slave-2

# 删除所有容器
docker rm mysql-master mysql-slave-1 mysql-slave-2

# 清理数据（谨慎！）
sudo rm -rf /opt/mysql/*/data/*
```

## 🎯 下一步

部署成功后，你可以：

1. **配置应用连接**：使用主库写入，从库读取
2. **监控主从状态**：定期运行 `/opt/mysql/check_status.sh`
3. **备份数据**：配置定期备份策略
4. **性能优化**：根据实际负载调整配置参数

## 📚 参考文档

- [MySQL 8.0 官方文档](https://dev.mysql.com/doc/refman/8.0/en/)
- [Docker MySQL 镜像文档](https://hub.docker.com/_/mysql)
- [GTID 复制文档](https://dev.mysql.com/doc/refman/8.0/en/replication-gtids.html)

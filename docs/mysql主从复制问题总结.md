# MySQL主从复制问题总结与解决方案

## 问题现象

在单服务器部署MySQL主从复制时，遇到以下问题：

1. **通过脚本配置复制后，`SHOW REPLICA STATUS\G` 返回空结果**
2. **手动配置复制后，状态显示正常但数据不同步**
3. **从库的 `Executed_Gtid_Set` 包含两个UUID**

## 根本原因分析

### 问题1：配置丢失

**现象**：
```bash
# 通过脚本配置
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 << EOF
CHANGE REPLICATION SOURCE TO ...;
START REPLICA;
EOF

# 查询状态返回空
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G"
# Empty set (0.00 sec)
```

**原因**：
- 从库容器启动时会执行 `init.sql` 初始化脚本
- 初始化完成后，MySQL服务会**自动重启**
- 在容器外通过脚本执行的 `CHANGE REPLICATION SOURCE TO` 命令在重启后**丢失**
- 复制配置没有被持久化保存

### 问题2：GTID冲突

**现象**：
```sql
mysql> SHOW REPLICA STATUS\G
...
Retrieved_Gtid_Set: 337e712e-f748-11f0-8878-0242ac110002:1-11
Executed_Gtid_Set: 337e712e-f748-11f0-8878-0242ac110002:1-11,
                   8c119178-f748-11f0-bd3a-0242ac110003:1-9
...
```

**分析**：
- `337e712e-f748-11f0-8878-0242ac110002` 是主库的UUID
- `8c119178-f748-11f0-bd3a-0242ac110003` 是从库自己的UUID
- 从库在初始化时执行了 `init.sql`，产生了自己的GTID事务
- 从库的GTID集合包含了自己的事务，导致与主库GTID不一致
- 虽然复制状态显示正常，但数据同步可能失败

**原因**：
- 从库配置文件中启用了binlog（默认行为）
- 从库执行 `init.sql` 时产生了binlog和GTID
- 这些GTID与主库的GTID混在一起，导致同步问题

## 完整解决方案

### 方案1：使用修复脚本（推荐）

我们提供了 `fix_replication.sh` 脚本来自动修复：

```bash
# 运行修复脚本
chmod +x fix_replication.sh
sudo ./fix_replication.sh
```

脚本会自动：
1. 停止并删除从库容器
2. 清理从库数据目录
3. 更新配置文件（添加 `skip-log-bin` 和 `log_replica_updates=OFF`）
4. 重新启动从库
5. 提示手动配置复制的步骤

### 方案2：手动修复步骤

#### 步骤1：停止并清理从库

```bash
# 停止从库容器
docker stop mysql-slave-1 mysql-slave-2

# 删除从库容器
docker rm mysql-slave-1 mysql-slave-2

# 清理从库数据
sudo rm -rf /opt/mysql/slave-1/data/*
sudo rm -rf /opt/mysql/slave-2/data/*
```

#### 步骤2：更新从库配置

**关键配置**：添加 `skip-log-bin` 和 `log_replica_updates=OFF`

```bash
# 更新从库1配置
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

# 关键：禁用binlog，避免产生自己的GTID
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

# 更新从库2配置（server-id=3）
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
```

#### 步骤3：重新启动从库

```bash
# 启动从库1
docker run -d \
    --name mysql-slave-1 \
    --restart always \
    -p 3308:3306 \
    -v /opt/mysql/slave-1/data:/var/lib/mysql \
    -v /opt/mysql/slave-1/conf:/etc/mysql/conf.d \
    -v /opt/mysql/slave-1/init:/docker-entrypoint-initdb.d \
    -e MYSQL_ROOT_PASSWORD=zhiyu666 \
    mysql:8.0.43

# 启动从库2
docker run -d \
    --name mysql-slave-2 \
    --restart always \
    -p 3309:3306 \
    -v /opt/mysql/slave-2/data:/var/lib/mysql \
    -v /opt/mysql/slave-2/conf:/etc/mysql/conf.d \
    -v /opt/mysql/slave-2/init:/docker-entrypoint-initdb.d \
    -e MYSQL_ROOT_PASSWORD=zhiyu666 \
    mysql:8.0.43

# 等待启动完成
echo "等待60秒让MySQL初始化..."
sleep 60
```

#### 步骤4：手动配置复制（关键！）

**重要**：必须进入MySQL交互界面手动配置，不能用脚本！

```bash
# 获取主库容器IP
MASTER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql-master)
echo "主库容器IP: $MASTER_IP"

# 进入从库1的MySQL交互界面
docker exec -it mysql-slave-1 mysql -uroot -pzhiyu666
```

**在 `mysql>` 提示符下执行**：

```sql
-- 停止复制（如果有）
STOP REPLICA;

-- 重置复制配置
RESET REPLICA ALL;

-- 清除从库自己的GTID（重要！）
RESET MASTER;

-- 配置复制源（使用主库容器IP和容器端口3306）
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='172.17.0.2',  -- 主库容器IP
    SOURCE_PORT=3306,           -- 容器端口，不是3307！
    SOURCE_USER='repl',
    SOURCE_PASSWORD='repl123',
    SOURCE_AUTO_POSITION=1;

-- 启动复制
START REPLICA;

-- 查看状态
SHOW REPLICA STATUS\G

-- 退出
exit
```

**对从库2重复相同操作**：

```bash
docker exec -it mysql-slave-2 mysql -uroot -pzhiyu666
# 然后执行上面的SQL命令
```

#### 步骤5：验证复制状态

```bash
# 检查从库1
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G" | grep -E "(Replica_IO_Running|Replica_SQL_Running|Seconds_Behind_Source|Last_IO_Error|Last_SQL_Error)"

# 检查从库2
docker exec mysql-slave-2 mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G" | grep -E "(Replica_IO_Running|Replica_SQL_Running|Seconds_Behind_Source|Last_IO_Error|Last_SQL_Error)"
```

**预期结果**：
```
Replica_IO_Running: Yes
Replica_SQL_Running: Yes
Seconds_Behind_Source: 0
Last_IO_Error: 
Last_SQL_Error: 
```

#### 步骤6：测试数据同步

```bash
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

# 等待同步
sleep 3

# 在从库1查询
echo "从库1数据："
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SELECT * FROM test_sync.test_table;"

# 在从库2查询
echo "从库2数据："
docker exec mysql-slave-2 mysql -uroot -pzhiyu666 -e "SELECT * FROM test_sync.test_table;"
```

## 关键技术点总结

### 1. 容器端口映射

```
宿主机端口映射：-p 3307:3306
├─ 外部访问：mysql -h127.0.0.1 -P3307 -uroot -pzhiyu666
└─ 容器间通信：使用容器IP（172.17.0.2）+ 容器端口3306
```

**重要**：
- ✅ 从库连接主库：使用容器IP + 容器端口3306
- ❌ 从库连接主库：不要使用宿主机IP + 宿主机端口3307

### 2. 配置持久化

```
❌ 错误方式（配置会丢失）：
docker exec mysql-slave-1 mysql ... << EOF
CHANGE REPLICATION SOURCE TO ...;
EOF

✅ 正确方式（配置会持久化）：
docker exec -it mysql-slave-1 mysql ...
mysql> CHANGE REPLICATION SOURCE TO ...;
```

**原因**：
- 从库容器初始化时会重启MySQL
- 脚本方式的配置在重启后丢失
- 交互式配置会被持久化保存

### 3. GTID管理

**从库配置关键参数**：
```ini
skip-log-bin              # 从库不生成binlog
log_replica_updates=OFF   # 从库不记录复制的更新
```

**作用**：
- 避免从库产生自己的GTID
- 保证从库只有主库复制过来的GTID
- 确保GTID集合一致性

**清理从库GTID**：
```sql
RESET MASTER;  -- 清除从库自己产生的GTID
```

## 预防措施

### 新部署时的正确配置

1. **从库配置文件必须包含**：
```ini
skip-log-bin
log_replica_updates=OFF
```

2. **必须手动进入MySQL交互界面配置复制**：
```bash
docker exec -it mysql-slave-1 mysql -uroot -pzhiyu666
mysql> CHANGE REPLICATION SOURCE TO ...;
```

3. **使用正确的主库地址**：
```sql
SOURCE_HOST='172.17.0.2',  -- 容器IP
SOURCE_PORT=3306,           -- 容器端口
```

### 部署脚本更新

我们已经更新了以下文件：
- `deploy_mysql_final.sh` - 添加了 `skip-log-bin` 配置和手动配置提示
- `fix_replication.sh` - 新增的修复脚本
- `docs/mysql主从-单服务器分步部署教程.md` - 更新了配置步骤和故障排查
- `docs/mysql主从-单服务器快速部署.md` - 更新了常见问题解决方案

## 验证清单

部署完成后，请检查以下项目：

- [ ] 所有容器运行正常：`docker ps | grep mysql`
- [ ] 主库状态正常：`SHOW MASTER STATUS\G`
- [ ] 从库复制状态：`Replica_IO_Running: Yes` 和 `Replica_SQL_Running: Yes`
- [ ] 从库延迟为0：`Seconds_Behind_Source: 0`
- [ ] 无错误信息：`Last_IO_Error` 和 `Last_SQL_Error` 为空
- [ ] GTID一致：从库的 `Executed_Gtid_Set` 只包含主库的UUID
- [ ] 数据同步正常：主库写入的数据能在从库查询到

## 参考文档

- [MySQL 8.0 GTID复制官方文档](https://dev.mysql.com/doc/refman/8.0/en/replication-gtids.html)
- [Docker MySQL镜像文档](https://hub.docker.com/_/mysql)
- [MySQL主从复制完整文档](./mysql主从.md)
- [单服务器分步部署教程](./mysql主从-单服务器分步部署教程.md)
- [单服务器快速部署指南](./mysql主从-单服务器快速部署.md)


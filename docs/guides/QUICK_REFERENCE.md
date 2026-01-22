# MySQL主从复制快速参考

## 🚀 快速命令

```bash
# 部署
./deploy_mysql_final.sh

# 检查状态
./check_mysql_status.sh

# 连接数据库
./connect_mysql.sh master    # 主库
./connect_mysql.sh slave1    # 从库1
./connect_mysql.sh slave2    # 从库2

# 测试同步
./test_mysql_sync.sh

# 获取主库IP
./get_master_ip.sh

# 重启
./restart_mysql.sh all

# 修复
./fix_replication.sh

# 清理
./cleanup_mysql.sh
```

## 📋 手动配置复制（重要！）

```bash
# 1. 获取主库IP
MASTER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql-master)

# 2. 进入从库
docker exec -it mysql-slave-1 mysql -uroot -pzhiyu666

# 3. 在 mysql> 提示符下执行
STOP REPLICA;
RESET REPLICA ALL;
RESET MASTER;
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

## ✅ 正常状态

```
Replica_IO_Running: Yes
Replica_SQL_Running: Yes
Seconds_Behind_Source: 0
```

## ❌ 异常处理

```bash
# 复制异常
./fix_replication.sh

# 查看日志
docker logs mysql-master --tail 50
docker logs mysql-slave-1 --tail 50
```

## 🔌 连接信息

```bash
# 主库（写）
mysql -h127.0.0.1 -P3307 -uroot -pzhiyu666

# 从库1（读）
mysql -h127.0.0.1 -P3308 -uroot -pzhiyu666

# 从库2（读）
mysql -h127.0.0.1 -P3309 -uroot -pzhiyu666
```

## 📁 重要文件位置

```
/opt/mysql/master/     # 主库
/opt/mysql/slave-1/    # 从库1
/opt/mysql/slave-2/    # 从库2
```

## ⚠️ 关键注意事项

1. **从库连接主库**：使用容器IP + 端口3306（不是3307！）
2. **配置复制**：必须手动进入MySQL交互界面
3. **从库配置**：必须包含 `skip-log-bin` 和 `log_replica_updates=OFF`
4. **重启后**：检查复制状态


# 读写分离部署说明

## 📋 部署步骤

### 1. 确认MySQL主从复制正常

```bash
# 在服务器上检查主从状态
cd /opt/mysql_deploy
bash ./check_status.sh
```

确认输出显示：
- ✅ `Replica_IO_Running: Yes`
- ✅ `Replica_SQL_Running: Yes`
- ✅ `Seconds_Behind_Source: 0`

### 2. 更新后端配置

已更新的文件：
- ✅ `backend/.env` - 添加了主从数据库配置
- ✅ `backend/app/core/settings.py` - 支持读写分离配置
- ✅ `backend/app/core/database.py` - 读写分离工具类（新增）
- ✅ `backend/app/apis/v1/system/database.py` - 数据库监控API（新增）

### 3. 在主库创建数据库

```bash
# 连接主库
mysql -h192.168.11.150 -P3307 -uroot -pzhiyu666

# 创建数据库
CREATE DATABASE IF NOT EXISTS qyd CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 退出
exit
```

### 4. 验证数据同步

```bash
# 等待3秒让数据同步
sleep 3

# 在从库1查询
mysql -h192.168.11.150 -P3308 -uroot -pzhiyu666 -e "SHOW DATABASES LIKE 'qyd';"

# 在从库2查询
mysql -h192.168.11.150 -P3309 -uroot -pzhiyu666 -e "SHOW DATABASES LIKE 'qyd';"
```

### 5. 运行数据库迁移

```bash
cd /path/to/backend

# 如果是首次部署，初始化aerich
aerich init -t app.core.settings.TORTOISE_ORM

# 运行迁移
aerich upgrade
```

### 6. 测试读写分离

```bash
# 运行测试脚本
cd /path/to/backend
python test_read_write_split.py
```

预期输出：
```
============================================================
MySQL读写分离测试
============================================================

============================================================
测试数据库连接
============================================================

数据库配置:
  读写分离: 启用
  主库: 192.168.11.150:3307
  从库:
    - slave1: 192.168.11.150:3308
    - slave2: 192.168.11.150:3309

测试连接:
  ✓ default: server_id=1, port=3306
  ✓ slave1: server_id=2, port=3306
  ✓ slave2: server_id=3, port=3306

============================================================
测试读操作负载均衡
============================================================

读操作分布（100次）:
  slave1: 52次 (52.0%)
  slave2: 48次 (48.0%)

✓ 负载均衡测试完成

============================================================
测试读写操作
============================================================

1. 创建测试用户（写入主库）...
   ✓ 用户已创建: ID=1, username=test_rw_split_xxx

2. 从从库读取用户列表...
   ✓ 读取到 5 个用户

3. 从从库查询用户...
   ✓ 总用户数: 10

4. 更新用户（写入主库）...
   ✓ 用户已更新: email=updated@example.com

5. 删除测试用户（写入主库）...
   ✓ 用户已删除: ID=1

✓ 所有测试通过！

============================================================
所有测试完成！
============================================================
```

### 7. 启动后端服务

```bash
cd /path/to/backend

# 启动服务
python start.py
```

### 8. 测试API

访问以下API验证读写分离：

```bash
# 1. 查看数据库配置信息
curl http://localhost:6080/v1/system/database/info

# 2. 查看数据库连接状态
curl http://localhost:6080/v1/system/database/connections

# 3. 测试数据库路由
curl http://localhost:6080/v1/system/database/test-routing

# 4. 测试数据库查询
curl http://localhost:6080/v1/system/database/test-query
```

## 🔍 监控和验证

### 方法1：通过API监控

访问 `http://localhost:6080/docs` 查看Swagger文档，测试以下API：

- `GET /v1/system/database/info` - 查看数据库配置
- `GET /v1/system/database/connections` - 查看连接状态
- `GET /v1/system/database/test-routing` - 测试路由分布
- `GET /v1/system/database/test-query` - 测试查询

### 方法2：查看MySQL日志

```bash
# 主库查询日志（写操作）
docker exec mysql-master mysql -uroot -pzhiyu666 -e "SHOW FULL PROCESSLIST;"

# 从库1查询日志（读操作）
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SHOW FULL PROCESSLIST;"

# 从库2查询日志（读操作）
docker exec mysql-slave-2 mysql -uroot -pzhiyu666 -e "SHOW FULL PROCESSLIST;"
```

### 方法3：启用MySQL查询日志

```bash
# 在主库启用查询日志
docker exec mysql-master mysql -uroot -pzhiyu666 << 'EOF'
SET GLOBAL general_log = 'ON';
SET GLOBAL general_log_file = '/var/lib/mysql/master-query.log';
EOF

# 在从库1启用查询日志
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 << 'EOF'
SET GLOBAL general_log = 'ON';
SET GLOBAL general_log_file = '/var/lib/mysql/slave1-query.log';
EOF

# 查看主库查询日志
docker exec mysql-master tail -f /var/lib/mysql/master-query.log

# 查看从库1查询日志
docker exec mysql-slave-1 tail -f /var/lib/mysql/slave1-query.log
```

## ⚠️ 注意事项

### 1. 主从延迟

主从复制可能存在微小延迟，如果需要读取刚写入的数据：

```python
# 方法1：从主库读取
from app.models.user import User

user = await User.using_db("default").get(id=user_id)

# 方法2：添加短暂延迟
import asyncio
await asyncio.sleep(0.1)  # 等待100ms
user = await db_read(User).get(id=user_id)
```

### 2. 事务处理

事务必须在主库上执行：

```python
from tortoise.transactions import in_transaction

async with in_transaction("default") as conn:
    # 所有操作都在主库的事务中
    user = await User.create(username="test", using_db=conn)
    await Project.create(name="test", user=user, using_db=conn)
```

### 3. 连接池配置

根据实际负载调整 `.env` 中的连接池配置：

```ini
# 主库（写操作较少）
DB_MINSIZE=10
DB_MAXSIZE=40

# 从库（读操作较多）
DB_SLAVE1_MINSIZE=20
DB_SLAVE1_MAXSIZE=80
DB_SLAVE2_MINSIZE=20
DB_SLAVE2_MAXSIZE=80
```

### 4. 临时禁用读写分离

如果需要临时禁用读写分离（所有操作都走主库）：

```ini
# 在 .env 中设置
DB_READ_WRITE_SPLIT=0
```

然后重启服务。

## 🔧 故障排查

### 问题1：从库连接失败

```bash
# 检查从库状态
bash /opt/mysql_deploy/check_status.sh

# 检查从库复制状态
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G"
```

### 问题2：数据不同步

```bash
# 测试数据同步
bash /opt/mysql_deploy/test_mysql_sync.sh

# 如果同步失败，运行修复脚本
bash /opt/mysql_deploy/fix_replication.sh
```

### 问题3：读写分离未生效

```bash
# 1. 检查配置
cat backend/.env | grep DB_READ_WRITE_SPLIT

# 2. 测试路由
curl http://localhost:6080/v1/system/database/test-routing

# 3. 查看日志
tail -f backend/logs/app.log
```

## 📚 相关文档

- [读写分离使用指南](READ_WRITE_SPLIT_GUIDE.md)
- [MySQL主从复制部署](../docs/mysql主从-单服务器分步部署教程.md)
- [问题排查指南](../docs/mysql主从复制问题总结.md)


# 后端部署指南

本指南详细说明如何在新服务器上部署 QYD 后端服务。

## 📋 目录

- [环境要求](#环境要求)
- [快速部署](#快速部署)
- [详细步骤](#详细步骤)
- [配置说明](#配置说明)
- [数据库迁移](#数据库迁移)
- [常见问题](#常见问题)

## 🔧 环境要求

### 必需软件

- **Python**: 3.11 或更高版本
- **MySQL**: 8.0 或更高版本
- **Redis**: 7.0 或更高版本（可选，用于队列处理）

### 推荐配置

- **CPU**: 4核心或更多
- **内存**: 8GB 或更多
- **磁盘**: 50GB 或更多

## 🚀 快速部署

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd qyd_api2/backend
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置数据库和其他参数
vim .env
```

**必须配置的环境变量**：

```env
# 数据库配置
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=qyd
DB_PASSWORD=your_password
DB_NAME=qyd

# JWT 密钥（至少32字符）
JWT_SECRET_KEY=your-secret-key-change-in-production-min-32-chars

# Redis 配置（可选）
REDIS_ENABLED=1
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
```

### 5. 初始化数据库

#### 方法一：使用 Aerich（推荐）

```bash
# 初始化 Aerich
aerich init -t app.core.settings.TORTOISE_ORM

# 初始化数据库
aerich init-db

# 导入初始数据
python deploy_init.py
```

#### 方法二：直接运行初始化脚本

```bash
python deploy_init.py
```

### 6. 启动服务

```bash
# 启动 HTTP 服务
python start.py

# 启动队列工作进程（可选，如果使用 Redis 队列）
python start_queue_worker.py
```

### 7. 验证部署

访问 API 文档：http://localhost:6080/docs

使用默认管理员账号登录：
- **邮箱**: zhiyu
- **密码**: 2201101122@qq.com

⚠️ **首次登录后请立即修改密码！**

## 📝 详细步骤

### 步骤 1: 准备数据库

#### 创建数据库

```sql
CREATE DATABASE qyd CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 创建数据库用户

```sql
CREATE USER 'qyd'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON qyd.* TO 'qyd'@'%';
FLUSH PRIVILEGES;
```

### 步骤 2: 配置环境变量

编辑 `.env` 文件，根据实际情况配置：

```env
# ==========================================
# 数据库配置（主库）
# ==========================================
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=qyd
DB_PASSWORD=your_password
DB_NAME=qyd
DB_MINSIZE=5
DB_MAXSIZE=20
DB_POOL_RECYCLE=3600
DB_CONNECT_TIMEOUT=10

# ==========================================
# 读写分离配置（可选）
# ==========================================
DB_READ_WRITE_SPLIT=0  # 0=禁用，1=启用

# 从库1配置（如果启用读写分离）
DB_SLAVE1_HOST=127.0.0.1
DB_SLAVE1_PORT=3307
DB_SLAVE1_USER=qyd
DB_SLAVE1_PASSWORD=your_password
DB_SLAVE1_NAME=qyd

# 从库2配置（如果启用读写分离）
DB_SLAVE2_HOST=127.0.0.1
DB_SLAVE2_PORT=3308
DB_SLAVE2_USER=qyd
DB_SLAVE2_PASSWORD=your_password
DB_SLAVE2_NAME=qyd

# ==========================================
# JWT 配置
# ==========================================
JWT_SECRET_KEY=your-secret-key-change-in-production-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_TIME=86400  # 24小时

# ==========================================
# Redis 配置
# ==========================================
REDIS_ENABLED=1
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0
REDIS_MAX_CONNECTIONS=50
REDIS_KEY_PREFIX=qyd:

# Redis 队列配置
REDIS_QUEUE_BATCH_SIZE=200
REDIS_QUEUE_NUM_WORKERS=4
REDIS_QUEUE_CACHE_EXPIRE=3600

# ==========================================
# 服务配置
# ==========================================
HOST=0.0.0.0
PORT=6080
DEBUG=0  # 生产环境设置为 0
WORKERS=1  # Uvicorn workers 数量

# ==========================================
# CORS 配置
# ==========================================
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# ==========================================
# 日志配置
# ==========================================
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=90
```

### 步骤 3: 使用 Aerich 管理数据库

#### 初始化 Aerich

```bash
# 初始化 Aerich（首次部署）
aerich init -t app.core.settings.TORTOISE_ORM

# 初始化数据库（创建表结构）
aerich init-db
```

#### 创建迁移

```bash
# 当模型发生变化时，创建迁移文件
aerich migrate --name "describe_your_changes"

# 应用迁移
aerich upgrade
```

#### 查看迁移历史

```bash
# 查看迁移历史
aerich history

# 查看当前版本
aerich heads
```

#### 回滚迁移

```bash
# 回滚到上一个版本
aerich downgrade

# 回滚到指定版本
aerich downgrade -v <version>
```

### 步骤 4: 导入初始数据

运行初始化脚本导入角色、路由和管理员用户：

```bash
python deploy_init.py
```

脚本会自动完成以下操作：

1. ✅ 检查环境配置
2. ✅ 初始化数据库连接
3. ✅ 导入角色数据（ADMIN, GM, IT, MANUAL）
4. ✅ 导入路由数据（菜单和权限）
5. ✅ 创建管理员用户（zhiyu）
6. ✅ 绑定管理员权限
7. ✅ 验证初始化结果

### 步骤 5: 启动服务

#### 开发环境

```bash
# 启动 HTTP 服务
python start.py

# 启动队列工作进程（另一个终端）
python start_queue_worker.py
```

#### 生产环境（使用 Supervisor）

创建 Supervisor 配置文件 `/etc/supervisor/conf.d/qyd.conf`：

```ini
[program:qyd-http]
command=/path/to/venv/bin/python /path/to/backend/start.py
directory=/path/to/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/qyd/http.log
environment=PATH="/path/to/venv/bin"

[program:qyd-queue]
command=/path/to/venv/bin/python /path/to/backend/start_queue_worker.py
directory=/path/to/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/qyd/queue.log
environment=PATH="/path/to/venv/bin"
```

启动服务：

```bash
# 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动服务
sudo supervisorctl start qyd-http
sudo supervisorctl start qyd-queue

# 查看状态
sudo supervisorctl status
```

#### 生产环境（使用 systemd）

创建服务文件 `/etc/systemd/system/qyd-http.service`：

```ini
[Unit]
Description=QYD HTTP Service
After=network.target mysql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python /path/to/backend/start.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

创建服务文件 `/etc/systemd/system/qyd-queue.service`：

```ini
[Unit]
Description=QYD Queue Worker
After=network.target mysql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python /path/to/backend/start_queue_worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start qyd-http
sudo systemctl start qyd-queue

# 设置开机自启
sudo systemctl enable qyd-http
sudo systemctl enable qyd-queue

# 查看状态
sudo systemctl status qyd-http
sudo systemctl status qyd-queue

# 查看日志
sudo journalctl -u qyd-http -f
sudo journalctl -u qyd-queue -f
```

## ⚙️ 配置说明

### 性能配置

根据服务器配置和负载选择合适的性能配置：

#### 标准性能（2000条/秒）

```bash
cp .env.high_performance .env
# 编辑 .env，配置数据库和 Redis
```

配置要点：
- 1个队列进程，8个 workers
- 批处理大小：300
- 数据库连接池：40

#### 超高性能（10000+条/秒）

```bash
cp .env.ultra_high_performance .env
# 编辑 .env，配置数据库和 Redis
```

配置要点：
- 3个队列进程，每个12个 workers
- 批处理大小：500
- 数据库连接池：80

详细性能配置请参考：[docs/performance/SCALE_TO_10K_GUIDE.md](../docs/performance/SCALE_TO_10K_GUIDE.md)

### 读写分离配置

如果需要启用 MySQL 主从读写分离：

1. 配置 MySQL 主从复制（参考 [docs/mysql主从-单服务器快速部署.md](../docs/mysql主从-单服务器快速部署.md)）

2. 在 `.env` 中启用读写分离：

```env
DB_READ_WRITE_SPLIT=1

# 配置从库
DB_SLAVE1_HOST=127.0.0.1
DB_SLAVE1_PORT=3307
# ... 其他从库配置
```

## 🔄 数据库迁移

### 创建新迁移

当你修改了模型（models）后：

```bash
# 创建迁移文件
aerich migrate --name "add_new_field_to_user"

# 应用迁移
aerich upgrade
```

### 查看迁移状态

```bash
# 查看迁移历史
aerich history

# 查看当前版本
aerich heads
```

### 回滚迁移

```bash
# 回滚到上一个版本
aerich downgrade

# 回滚到指定版本
aerich downgrade -v 1_20240101000000_init
```

### 重置数据库（危险操作）

⚠️ **警告：此操作会删除所有数据！**

```bash
# 删除所有表
aerich downgrade -v 0

# 重新初始化
aerich init-db

# 导入初始数据
python deploy_init.py
```

## 🐛 常见问题

### 1. 数据库连接失败

**问题**：`Can't connect to MySQL server`

**解决方案**：
- 检查 MySQL 服务是否运行：`sudo systemctl status mysql`
- 检查数据库配置是否正确（主机、端口、用户名、密码）
- 检查防火墙是否允许连接
- 检查 MySQL 用户权限

### 2. Redis 连接失败

**问题**：`Error connecting to Redis`

**解决方案**：
- 检查 Redis 服务是否运行：`sudo systemctl status redis`
- 检查 Redis 配置是否正确
- 如果不需要 Redis，可以在 `.env` 中设置 `REDIS_ENABLED=0`

### 3. 端口被占用

**问题**：`Address already in use`

**解决方案**：
```bash
# 查找占用端口的进程
sudo lsof -i :6080

# 杀死进程
sudo kill -9 <PID>

# 或者修改 .env 中的 PORT 配置
```

### 4. 权限问题

**问题**：`Permission denied`

**解决方案**：
```bash
# 修改文件所有者
sudo chown -R www-data:www-data /path/to/backend

# 修改日志目录权限
sudo chmod -R 755 /path/to/backend/logs
```

### 5. Aerich 迁移失败

**问题**：`Migration failed`

**解决方案**：
```bash
# 查看详细错误信息
aerich upgrade --verbose

# 如果是首次部署，删除 migrations 目录重新初始化
rm -rf migrations
aerich init -t app.core.settings.TORTOISE_ORM
aerich init-db
```

### 6. 导入初始数据失败

**问题**：`deploy_init.py` 执行失败

**解决方案**：
- 确保数据库表已创建（运行 `aerich init-db`）
- 检查环境变量是否正确配置
- 查看详细错误信息，根据提示修复

### 7. 内存不足

**问题**：服务运行一段时间后内存占用过高

**解决方案**：
- 减少数据库连接池大小（`DB_MAXSIZE`）
- 减少 Redis 连接数（`REDIS_MAX_CONNECTIONS`）
- 减少队列 workers 数量（`REDIS_QUEUE_NUM_WORKERS`）
- 增加服务器内存

## 📊 监控和维护

### 查看日志

```bash
# 查看 API 日志
tail -f logs/api.log

# 查看应用日志
tail -f logs/app.log

# 查看数据库日志
tail -f logs/database.log

# 查看队列日志
tail -f logs/scheduler.log
```

### 监控服务状态

```bash
# 使用 Supervisor
sudo supervisorctl status

# 使用 systemd
sudo systemctl status qyd-http
sudo systemctl status qyd-queue
```

### 数据库备份

```bash
# 备份数据库
mysqldump -u qyd -p qyd > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库
mysql -u qyd -p qyd < backup_20260126_120000.sql
```

### 清理日志

日志系统会自动压缩和清理旧日志（保留90天），无需手动清理。

如需手动清理：

```bash
# 清理压缩日志
find logs/ -name "*.gz" -mtime +90 -delete

# 清理旧日志目录
find logs/ -type d -empty -delete
```

## 🔒 安全建议

1. ✅ 使用强密码作为 `JWT_SECRET_KEY`（至少32字符）
2. ✅ 生产环境设置 `DEBUG=0`
3. ✅ 限制 `CORS_ORIGINS` 为特定域名
4. ✅ 定期更新依赖包：`pip install --upgrade -r requirements.txt`
5. ✅ 使用 HTTPS 部署
6. ✅ 定期备份数据库
7. ✅ 保护 Redis 密码，限制访问 IP
8. ✅ 首次登录后立即修改管理员密码
9. ✅ 配置防火墙，只开放必要端口
10. ✅ 启用 MySQL 慢查询日志，监控性能

## 📚 相关文档

- [项目结构说明](../.kiro/steering/structure.md)
- [开发规范](../.kiro/steering/conventions.md)
- [性能优化指南](../docs/performance/SCALE_TO_10K_GUIDE.md)
- [读写分离部署](../docs/mysql主从-单服务器快速部署.md)
- [API 文档](http://localhost:6080/docs)

## 📞 获取帮助

如遇到问题，请：

1. 查看本文档的[常见问题](#常见问题)部分
2. 查看日志文件获取详细错误信息
3. 提交 Issue 到项目仓库

---

**最后更新**: 2026-01-26  
**版本**: v1.2.0

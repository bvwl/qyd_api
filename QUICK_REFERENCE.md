# QYD 项目快速参考卡

常用命令和操作的速查表。

## 📋 目录

- [启动命令](#启动命令)
- [服务管理](#服务管理)
- [Docker 命令](#docker-命令)
- [数据库操作](#数据库操作)
- [日志查看](#日志查看)
- [测试命令](#测试命令)
- [故障排查](#故障排查)

---

## 启动命令

### 开发环境

```bash
# 后端
cd backend
source venv/bin/activate
python start.py

# 前端
cd frontend
npm run dev

# 队列 Worker
cd backend
source venv/bin/activate
python start_queue_worker.py
```

### Docker 部署

```bash
# 快速部署
bash docker-deploy-fast.sh

# 手动部署
docker compose build
docker compose run --rm backend-api python deploy_init.py
docker compose up -d
```

### 生产环境

```bash
# 本地部署
bash deploy_native.sh

# 高并发部署
bash deploy-high-concurrency.sh

# 启动服务
sudo systemctl start qyd-backend qyd-queue-worker
```

---

## 服务管理

### Systemd 服务

```bash
# 启动
sudo systemctl start qyd-backend qyd-queue-worker

# 停止
sudo systemctl stop qyd-backend qyd-queue-worker

# 重启
sudo systemctl restart qyd-backend qyd-queue-worker

# 状态
sudo systemctl status qyd-backend qyd-queue-worker

# 开机自启
sudo systemctl enable qyd-backend qyd-queue-worker

# 禁用自启
sudo systemctl disable qyd-backend qyd-queue-worker
```

### 脚本管理

```bash
# 启动所有服务
bash start_all_services.sh

# 重启所有服务
bash restart_all_services.sh

# 重启后端
bash restart-backend.sh

# 重新构建前端
bash rebuild_frontend.sh

# 更新并重启
bash update-and-restart.sh
```

---

## Docker 命令

### 容器管理

```bash
# 查看容器
docker compose ps
docker ps

# 启动服务
docker compose up -d

# 停止服务
docker compose stop

# 重启服务
docker compose restart

# 删除服务
docker compose down

# 删除服务和数据
docker compose down -v
```

### 日志查看

```bash
# 查看所有日志
docker compose logs -f

# 查看特定服务
docker compose logs -f backend-api
docker compose logs -f frontend
docker compose logs -f queue-worker

# 查看最近 100 行
docker compose logs --tail=100 backend-api
```

### 容器操作

```bash
# 进入容器
docker compose exec backend-api bash
docker compose exec frontend sh

# 执行命令
docker compose exec backend-api python check_deployment.py

# 查看资源使用
docker stats
```

### 扩展服务

```bash
# 扩展到 5 个实例
docker compose up -d --scale backend-api=5 --scale queue-worker=5

# 缩减到 2 个实例
docker compose up -d --scale backend-api=2 --scale queue-worker=2
```

---

## 数据库操作

### MySQL 连接

```bash
# 连接主库
mysql -h 127.0.0.1 -u qyd -p qyd

# 连接从库
mysql -h 192.168.13.7 -u qyd -p qyd

# 快速连接脚本
bash scripts/mysql/connect_mysql.sh
```

### 数据库管理

```bash
# 检查状态
bash scripts/mysql/check_mysql_status.sh

# 修复主从复制
bash scripts/mysql/fix_replication.sh

# 备份数据库
bash scripts/utils/backup_database.sh

# 恢复数据库
bash scripts/utils/restore_database.sh
```

### 数据库初始化

```bash
cd backend

# 初始化角色和管理员
python db/init_roles_and_admin.py

# 初始化路由权限
python db/init_routes.py

# 初始化 RBAC v2
python db/init_rbac_v2.py
```

### Redis 操作

```bash
# 连接 Redis
redis-cli -h 127.0.0.1 -p 6379 -a your_password

# Docker Redis
docker compose exec redis redis-cli -a redis_fNmAxZ

# 查看队列长度
redis-cli -a your_password LLEN project_account_queue

# 查看连接数
redis-cli -a your_password CLIENT LIST | wc -l

# 清空数据库
redis-cli -a your_password FLUSHDB
```

---

## 日志查看

### 应用日志

```bash
# 后端日志
tail -f backend/logs/api.log
tail -f backend/logs/app.log
tail -f backend/logs/database.log
tail -f backend/logs/scheduler.log

# Systemd 日志
sudo journalctl -u qyd-backend -f
sudo journalctl -u qyd-queue-worker -f

# 查看最近 100 行
sudo journalctl -u qyd-backend -n 100
```

### Nginx 日志

```bash
# 访问日志
sudo tail -f /var/log/nginx/access.log

# 错误日志
sudo tail -f /var/log/nginx/error.log
```

### 日志管理

```bash
# 清理日志
python backend/scripts/cleanup_logs.py

# 分析日志
python backend/scripts/analyze_logs.py

# 整理日志
python backend/scripts/organize_logs.py
```

---

## 测试命令

### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行特定测试
pytest tests/api/
pytest tests/integration/
pytest tests/performance/
pytest tests/unit/

# 运行单个测试文件
pytest tests/test_user.py

# 显示详细输出
pytest -v

# 显示打印输出
pytest -s
```

### API 测试

```bash
# 测试 API 接口
bash scripts/test/test_api_endpoints.sh

# 测试权限
bash scripts/test/test_user_permission.sh
bash scripts/test/test_project_permission.sh
bash scripts/test/test_server_permission.sh

# 测试批量操作
python scripts/test/test_batch_upsert.py
```

### 性能测试

```bash
# 压力测试（ab）
ab -n 10000 -c 100 http://localhost:6080/docs

# 压力测试（wrk）
wrk -t12 -c1000 -d60s http://localhost:6080/api/v1/health

# 队列性能测试
cd backend
python tests/performance/test_queue_performance.py
```

---

## 故障排查

### 诊断命令

```bash
# 诊断服务
bash diagnose_services.sh

# 诊断前端
bash diagnose_frontend.sh

# 检查数据库
python check_database.py

# 检查路由
bash check_routes.sh
```

### 调试脚本

```bash
# 检查 API 认证
python scripts/debug/check_api_auth.py

# 检查删除权限
python scripts/debug/check_delete_permissions.py

# 调试账号
python scripts/debug/debug_account.py

# 调试 Redis
python scripts/debug/debug_redis.py

# 调试数据库
python scripts/debug/debug_database.py
```

### 端口检查

```bash
# 查看端口占用
lsof -i :6080
lsof -i :5173
lsof -i :80

# 查看所有监听端口
netstat -tuln

# 杀死进程
kill -9 <PID>
```

### 进程检查

```bash
# 查看 Python 进程
ps aux | grep python

# 查看 Node 进程
ps aux | grep node

# 查看 Nginx 进程
ps aux | grep nginx

# 查看所有进程
htop
```

### 资源监控

```bash
# CPU 和内存
top
htop

# 磁盘使用
df -h

# 内存使用
free -h

# 网络连接
netstat -an | grep ESTABLISHED | wc -l

# 文件描述符
lsof | wc -l
```

---

## 环境变量

### 必需配置

```env
# MySQL
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=qyd
DB_PASSWORD=your_password
DB_NAME=qyd

# Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=redis_password

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars
```

### 性能配置

```env
# 标准性能
REDIS_QUEUE_BATCH_SIZE=200
REDIS_QUEUE_NUM_WORKERS=4

# 高性能
REDIS_QUEUE_BATCH_SIZE=300
REDIS_QUEUE_NUM_WORKERS=8

# 超高性能
REDIS_QUEUE_BATCH_SIZE=500
REDIS_QUEUE_NUM_WORKERS=12
```

### 读写分离

```env
# 启用读写分离
DB_READ_WRITE_SPLIT=1

# 从库配置
DB_SLAVE1_HOST=192.168.1.101
DB_SLAVE1_PORT=3306
DB_SLAVE2_HOST=192.168.1.102
DB_SLAVE2_PORT=3306
```

---

## 默认端口

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端（开发） | 5173 | Vite 开发服务器 |
| 前端（生产） | 80 | Nginx |
| 后端 API | 6080 | FastAPI |
| MySQL | 3306 | 数据库 |
| Redis | 6379 | 缓存/队列 |

---

## 默认账号

- **邮箱**: zhiyu
- **密码**: 2201101122@qq.com
- **角色**: ADMIN

> ⚠️ 首次登录后请立即修改密码！

---

## 常用 URL

### 本地开发

- 前端: http://localhost:5173
- 后端: http://localhost:6080
- API 文档: http://localhost:6080/docs
- ReDoc: http://localhost:6080/redoc

### Docker 部署

- 前端: http://localhost
- 后端: http://localhost:6080
- API 文档: http://localhost:6080/docs

### 生产环境

- 前端: http://your-domain.com
- 后端: http://your-domain.com:6080
- API 文档: http://your-domain.com:6080/docs

---

## 快速修复

### 端口被占用

```bash
# 查找进程
lsof -i :6080

# 杀死进程
kill -9 <PID>
```

### 数据库连接失败

```bash
# 测试连接
mysql -h 127.0.0.1 -u qyd -p qyd

# 检查配置
cat backend/.env | grep DB_

# 检查防火墙
sudo ufw allow 3306/tcp
```

### Redis 连接失败

```bash
# 测试连接
redis-cli -h 127.0.0.1 -p 6379 -a your_password ping

# 检查 Redis 状态
redis-cli INFO

# Docker Redis
docker compose ps redis
docker compose logs redis
```

### 前端无法访问

```bash
# 检查 Nginx
sudo nginx -t
sudo systemctl status nginx

# 重启 Nginx
sudo systemctl restart nginx

# 检查前端文件
ls -la frontend/dist/
```

### 服务无法启动

```bash
# 查看详细错误
sudo systemctl status qyd-backend
sudo journalctl -u qyd-backend -xe

# 查看应用日志
tail -f backend/logs/systemd-error.log

# 检查权限
ls -la /opt/zy/qyd_api/
```

---

## 相关文档

- [STARTUP_GUIDE.md](STARTUP_GUIDE.md) - 启动指南
- [scripts/SCRIPTS_INDEX.md](scripts/SCRIPTS_INDEX.md) - 脚本索引
- [docs/DOCUMENTATION_COMPLETE_INDEX.md](docs/DOCUMENTATION_COMPLETE_INDEX.md) - 文档索引

---

**最后更新**: 2026-01-26  
**版本**: v1.0.0

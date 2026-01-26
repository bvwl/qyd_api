# QYD 项目快速部署指南

适用于 Ubuntu Server 24.04，使用本地部署方式（前后端直接运行，Redis 使用 Docker 容器）。

## 🚀 一键部署

```bash
# 1. 安装环境（Python、Node.js、Redis 容器等）
sudo bash setup_environment.sh

# 2. 重新登录（使 Docker 权限生效）
exit
ssh user@server

# 3. 部署项目
cd /opt/zy/qyd_api
bash deploy_native.sh

# 4. 配置 Nginx
sudo cp /tmp/qyd_nginx.conf /etc/nginx/sites-available/qyd
sudo ln -sf /etc/nginx/sites-available/qyd /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

# 5. 安装并启动服务（开机自启动）
sudo cp /tmp/qyd-backend.service /etc/systemd/system/
sudo cp /tmp/qyd-queue-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable qyd-backend qyd-queue-worker
sudo systemctl start qyd-backend qyd-queue-worker

# 6. 查看状态
sudo systemctl status qyd-backend qyd-queue-worker
```

## 📋 详细步骤

### 步骤 1: 安装环境

```bash
cd /opt/zy/qyd_api
sudo bash setup_environment.sh
```

脚本会自动安装：
- ✅ Python 3.11
- ✅ Node.js 18
- ✅ Redis（Docker 容器）
- ✅ Nginx

**注意**：
- Docker 已安装，脚本会跳过 Docker 安装
- 安装完成后需要重新登录

### 步骤 2: 重新登录

```bash
exit
ssh user@server
```

这是为了使 Docker 权限生效（如果需要）。

### 步骤 3: 部署项目

```bash
cd /opt/zy/qyd_api
bash deploy_native.sh
```

脚本会自动：
- ✅ 检查环境
- ✅ 创建 Python 虚拟环境
- ✅ 安装后端依赖
- ✅ 安装前端依赖并构建
- ✅ 生成 Nginx 配置
- ✅ 生成 Systemd 服务配置
- ✅ 初始化数据库（可选）

**首次部署需要配置 .env**：

编辑 `backend/.env`，配置以下参数：

```env
# MySQL 主库
DB_HOST=192.168.1.100
DB_PORT=3306
DB_USER=qyd
DB_PASSWORD=your_mysql_password
DB_NAME=qyd

# MySQL 从库（可选）
DB_READ_WRITE_SPLIT=1
DB_SLAVE1_HOST=192.168.1.101
DB_SLAVE1_PORT=3306

# Redis（已自动配置）
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=见 /tmp/redis_password.txt

# JWT 密钥（至少32字符）
JWT_SECRET_KEY=your-secret-key-min-32-chars-here
```

### 步骤 4: 配置 Nginx

```bash
# 复制配置
sudo cp /tmp/qyd_nginx.conf /etc/nginx/sites-available/qyd

# 启用配置
sudo ln -sf /etc/nginx/sites-available/qyd /etc/nginx/sites-enabled/

# 删除默认配置
sudo rm -f /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl reload nginx
```

### 步骤 5: 配置开机自启动

```bash
# 复制服务文件
sudo cp /tmp/qyd-backend.service /etc/systemd/system/
sudo cp /tmp/qyd-queue-worker.service /etc/systemd/system/

# 重新加载 Systemd
sudo systemctl daemon-reload

# 启用开机自启动
sudo systemctl enable qyd-backend qyd-queue-worker

# 启动服务
sudo systemctl start qyd-backend qyd-queue-worker

# 查看状态
sudo systemctl status qyd-backend qyd-queue-worker
```

### 步骤 6: 验证部署

```bash
# 查看服务状态
sudo systemctl status qyd-backend qyd-queue-worker

# 查看日志
sudo journalctl -u qyd-backend -f

# 测试 API
curl http://localhost:6080/docs

# 测试前端
curl http://localhost
```

访问地址：
- **前端**: http://your-server-ip
- **后端**: http://your-server-ip:6080
- **API 文档**: http://your-server-ip:6080/docs

默认管理员账号：
- **邮箱**: zhiyu
- **密码**: 2201101122@qq.com

## 🔧 服务管理

### 启动/停止服务

```bash
# 启动
sudo systemctl start qyd-backend qyd-queue-worker

# 停止
sudo systemctl stop qyd-backend qyd-queue-worker

# 重启
sudo systemctl restart qyd-backend qyd-queue-worker

# 查看状态
sudo systemctl status qyd-backend qyd-queue-worker
```

### 查看日志

```bash
# Systemd 日志
sudo journalctl -u qyd-backend -f
sudo journalctl -u qyd-queue-worker -f

# 应用日志
tail -f /opt/zy/qyd_api/backend/logs/api.log
tail -f /opt/zy/qyd_api/backend/logs/app.log
tail -f /opt/zy/qyd_api/backend/logs/database.log
```

### Redis 管理

```bash
# 查看 Redis 容器状态
docker ps | grep redis

# 查看 Redis 日志
docker logs qyd-redis

# 连接 Redis
docker exec -it qyd-redis redis-cli -a $(cat /tmp/redis_password.txt | cut -d'=' -f2)

# 重启 Redis
docker restart qyd-redis

# 停止 Redis
docker stop qyd-redis

# 启动 Redis
docker start qyd-redis
```

### 更新代码

```bash
# 1. 拉取最新代码
cd /opt/zy/qyd_api
git pull

# 2. 更新后端
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 3. 更新前端
cd ../frontend
npm install
npx vite build

# 4. 重启服务
sudo systemctl restart qyd-backend qyd-queue-worker nginx
```

## 🐛 故障排查

### 服务无法启动

```bash
# 查看详细错误
sudo systemctl status qyd-backend
sudo journalctl -u qyd-backend -xe

# 查看应用日志
tail -f /opt/zy/qyd_api/backend/logs/systemd-error.log
```

### 端口被占用

```bash
# 查找占用 6080 端口的进程
sudo lsof -i :6080

# 杀死进程
sudo kill -9 <PID>
```

### Redis 连接失败

```bash
# 检查 Redis 容器
docker ps | grep redis

# 测试连接
docker exec qyd-redis redis-cli -a $(cat /tmp/redis_password.txt | cut -d'=' -f2) ping

# 查看 Redis 日志
docker logs qyd-redis
```

### 数据库连接失败

```bash
# 测试 MySQL 连接
mysql -h 192.168.1.100 -u qyd -p qyd

# 检查 .env 配置
cat /opt/zy/qyd_api/backend/.env | grep DB_
```

### 前端无法访问

```bash
# 检查 Nginx 配置
sudo nginx -t

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/error.log

# 检查前端文件
ls -la /opt/zy/qyd_api/frontend/dist/

# 重启 Nginx
sudo systemctl restart nginx
```

## 📊 性能优化

### 调整队列 Worker 数量

编辑 `backend/.env`：

```env
# 标准性能（2000条/秒）
REDIS_QUEUE_BATCH_SIZE=200
REDIS_QUEUE_NUM_WORKERS=4

# 高性能（6000条/秒）
REDIS_QUEUE_BATCH_SIZE=300
REDIS_QUEUE_NUM_WORKERS=8

# 超高性能（12000条/秒）
REDIS_QUEUE_BATCH_SIZE=500
REDIS_QUEUE_NUM_WORKERS=12
```

重启服务：

```bash
sudo systemctl restart qyd-queue-worker
```

### 启用读写分离

编辑 `backend/.env`：

```env
# 启用读写分离
DB_READ_WRITE_SPLIT=1

# 配置从库
DB_SLAVE1_HOST=192.168.1.101
DB_SLAVE1_PORT=3306
DB_SLAVE1_USER=qyd
DB_SLAVE1_PASSWORD=slave_password

DB_SLAVE2_HOST=192.168.1.102
DB_SLAVE2_PORT=3306
```

重启服务：

```bash
sudo systemctl restart qyd-backend qyd-queue-worker
```

## 🔒 安全建议

1. ✅ 修改默认管理员密码
2. ✅ 使用强密码作为 JWT_SECRET_KEY
3. ✅ 配置防火墙规则
4. ✅ 使用 HTTPS（配置 SSL 证书）
5. ✅ 定期更新依赖包
6. ✅ 定期备份数据库
7. ✅ 限制 Redis 访问（只允许本地）
8. ✅ 配置日志轮转
9. ✅ 监控服务状态
10. ✅ 定期检查日志

## 📚 相关文档

- [详细部署文档](NATIVE_DEPLOYMENT.md)
- [Docker 部署方案](DOCKER_DEPLOY_WITH_REDIS.md)
- [性能优化指南](docs/performance/SCALE_TO_10K_GUIDE.md)

---

**最后更新**: 2026-01-26  
**版本**: v1.2.5

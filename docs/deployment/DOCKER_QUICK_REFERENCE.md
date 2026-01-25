# Docker 部署快速参考

## 🚀 一键部署

```bash
bash docker-deploy.sh
```

## 📋 手动部署

```bash
# 1. 配置环境
cp .env.docker .env
vim .env

# 2. 构建镜像
docker-compose build

# 3. 初始化数据库
docker-compose run --rm backend-api python deploy_init.py

# 4. 启动服务
docker-compose up -d
```

## 🔑 默认账号

- **邮箱**: zhiyu
- **密码**: 2201101122@qq.com

## 🔗 访问地址

- 前端: http://localhost
- 后端: http://localhost:6080
- API 文档: http://localhost:6080/docs

## 📊 常用命令

### 服务管理

```bash
docker-compose up -d      # 启动
docker-compose stop       # 停止
docker-compose restart    # 重启
docker-compose down       # 删除
docker-compose ps         # 状态
```

### 日志查看

```bash
docker-compose logs -f                # 所有日志
docker-compose logs -f backend-api    # 后端日志
docker-compose logs -f queue-worker   # 队列日志
docker-compose logs -f frontend       # 前端日志
```

### 进入容器

```bash
docker-compose exec backend-api bash
docker-compose exec queue-worker bash
docker-compose exec frontend sh
```

### 执行命令

```bash
# 检查部署
docker-compose exec backend-api python check_deployment.py

# 数据库迁移
docker-compose exec backend-api aerich upgrade

# 重新初始化
docker-compose run --rm backend-api python deploy_init.py
```

## ⚙️ 环境变量

### 必需配置

```env
# MySQL
DB_HOST=host.docker.internal
DB_PASSWORD=your_password

# Redis
REDIS_HOST=host.docker.internal
REDIS_PASSWORD=your_password

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars
```

### 性能配置

```env
# 标准 (2000条/秒)
REDIS_QUEUE_BATCH_SIZE=200
REDIS_QUEUE_NUM_WORKERS=4

# 高性能 (6000条/秒)
REDIS_QUEUE_BATCH_SIZE=300
REDIS_QUEUE_NUM_WORKERS=8

# 超高性能 (12000条/秒)
REDIS_QUEUE_BATCH_SIZE=500
REDIS_QUEUE_NUM_WORKERS=12
```

## 🐛 故障排查

### 数据库连接失败

```bash
# 检查 MySQL
mysql -h localhost -u qyd -p

# 测试连接
docker-compose exec backend-api python -c "
import pymysql
conn = pymysql.connect(
    host='host.docker.internal',
    port=3306,
    user='qyd',
    password='password'
)
print('连接成功')
"
```

### Redis 连接失败

```bash
# 检查 Redis
redis-cli ping

# 测试连接
docker-compose exec backend-api python -c "
import redis
r = redis.Redis(host='host.docker.internal', port=6379)
print(r.ping())
"
```

### 端口被占用

```bash
# 查找占用进程
sudo lsof -i :80
sudo lsof -i :6080

# 修改端口（docker-compose.yml）
ports:
  - "8080:80"   # 前端
  - "8000:6080" # 后端
```

### 重新构建

```bash
# 清理并重建
docker-compose down
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

## 📚 详细文档

- [完整部署指南](DOCKER_DEPLOYMENT.md)
- [后端部署](backend/DEPLOYMENT_GUIDE.md)
- [性能优化](docs/performance/SCALE_TO_10K_GUIDE.md)

---

**提示**: 遇到问题先查看日志 `docker-compose logs -f`

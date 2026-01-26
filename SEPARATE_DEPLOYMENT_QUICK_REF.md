# 前后端分离部署快速参考

## 🚀 快速部署

### 后端服务器 (192.168.1.20)

```bash
# 1. 克隆代码
git clone <repo-url> /opt/qyd && cd /opt/qyd

# 2. 配置环境
cp .env.backend .env
vim .env  # 修改 DB_HOST, DB_PASSWORD, CORS_ORIGINS

# 3. 一键部署
chmod +x deploy-backend.sh && bash deploy-backend.sh
```

### 前端服务器 (192.168.1.10)

```bash
# 1. 克隆代码
git clone <repo-url> /opt/qyd && cd /opt/qyd

# 2. 配置环境
cp .env.frontend .env
vim .env  # 修改 VITE_API_BASE_URL

# 3. 一键部署
chmod +x deploy-frontend.sh && bash deploy-frontend.sh
```

## 📝 必须配置的参数

### 后端 (.env.backend)

```env
# MySQL 配置
DB_HOST=192.168.1.30
DB_PASSWORD=your_mysql_password

# Redis 配置（外部 Redis 服务器）
REDIS_HOST=192.168.1.20
REDIS_PORT=6379
REDIS_PASSWORD=redis_fNmAxZ

# JWT 密钥（至少32字符）
JWT_SECRET_KEY=your-secret-key-min-32-chars

# CORS（前端地址）
CORS_ORIGINS=http://192.168.1.10
```

### 前端 (.env.frontend)

```env
# 后端 API 地址
VITE_API_BASE_URL=http://192.168.1.20:6080
```

## 🔧 常用命令

### 后端

```bash
# 查看状态
docker-compose -f docker-compose.backend.yml ps

# 查看日志
docker-compose -f docker-compose.backend.yml logs -f

# 重启
docker-compose -f docker-compose.backend.yml restart

# 更新
git pull && docker-compose -f docker-compose.backend.yml build && docker-compose -f docker-compose.backend.yml up -d
```

### 前端

```bash
# 查看状态
docker-compose -f docker-compose.frontend.yml ps

# 查看日志
docker-compose -f docker-compose.frontend.yml logs -f

# 重启
docker-compose -f docker-compose.frontend.yml restart

# 更新
git pull && docker-compose -f docker-compose.frontend.yml build && docker-compose -f docker-compose.frontend.yml up -d
```

## 🐛 快速故障排查

### 前端无法访问后端

```bash
# 1. 测试后端连接
curl http://192.168.1.20:6080/docs

# 2. 检查 CORS 配置
docker-compose -f docker-compose.backend.yml exec backend-api env | grep CORS

# 3. 开放防火墙
sudo ufw allow from 192.168.1.10 to any port 6080

# 4. 重启后端
docker-compose -f docker-compose.backend.yml restart
```

### 后端无法连接 Redis

```bash
# 1. 测试 Redis 连接
redis-cli -h 192.168.1.20 -p 6379 -a redis_fNmAxZ ping

# 2. 检查 Redis 绑定地址
grep "^bind" /etc/redis/redis.conf

# 3. 开放防火墙（Redis 服务器）
sudo ufw allow from 192.168.1.20 to any port 6379

# 4. 重启 Redis
sudo systemctl restart redis
```

## 📊 访问地址

- **前端**: http://192.168.1.10
- **后端 API**: http://192.168.1.20:6080
- **API 文档**: http://192.168.1.20:6080/docs

## 🔐 默认账号

- **邮箱**: zhiyu
- **密码**: 2201101122@qq.com

⚠️ **首次登录后请立即修改密码！**

## 📚 详细文档

查看完整部署指南: [SEPARATE_DEPLOYMENT_GUIDE.md](SEPARATE_DEPLOYMENT_GUIDE.md)

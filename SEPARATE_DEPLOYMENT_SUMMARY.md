# 前后端分离部署实现总结

## ✅ 已完成的工作

本次为项目实现了完整的前后端分离部署方案，包括 Docker 部署和原生部署两种方式。

## 📁 新增文件清单

### 1. 部署配置文件

#### Docker Compose 配置

- **`docker-compose.backend.yml`**: 后端服务器专用配置
  - Backend API 服务
  - Queue Worker 服务
  - Redis 服务
  - 网络和卷配置

- **`docker-compose.frontend.yml`**: 前端服务器专用配置
  - Frontend (Nginx) 服务
  - 构建参数配置

#### 环境变量配置

- **`.env.backend`**: 后端服务器环境变量模板
  - 数据库配置
  - Redis 配置
  - JWT 配置
  - CORS 配置（包含前端地址）

- **`.env.frontend`**: 前端服务器环境变量模板
  - 后端 API 地址配置
  - 应用标题配置

### 2. 部署脚本

#### Docker 部署脚本

- **`deploy-backend.sh`**: 后端 Docker 一键部署脚本
  - 检查 Docker 环境
  - 配置环境变量
  - 构建镜像
  - 初始化数据库
  - 启动服务

- **`deploy-frontend.sh`**: 前端 Docker 一键部署脚本
  - 检查 Docker 环境
  - 配置环境变量
  - 构建镜像
  - 启动服务

#### 原生部署脚本

- **`deploy-backend-native.sh`**: 后端原生部署脚本
  - 检查 Python 环境
  - 安装配置 Redis
  - 创建虚拟环境
  - 安装依赖
  - 配置 Systemd 服务
  - 启动服务

- **`deploy-frontend-native.sh`**: 前端原生部署脚本
  - 检查 Node.js 环境
  - 安装配置 Nginx
  - 构建前端
  - 配置 Nginx
  - 启动服务

### 3. 部署文档

#### 主要文档

- **`SEPARATE_DEPLOYMENT_GUIDE.md`**: 前后端分离部署完整指南
  - 架构说明
  - Docker 部署详细步骤
  - 网络配置
  - 域名配置
  - HTTPS 配置
  - 常用命令
  - 故障排查
  - 性能优化
  - 安全建议

- **`SEPARATE_DEPLOYMENT_QUICK_REF.md`**: 快速参考指南
  - 快速部署命令
  - 必须配置的参数
  - 常用命令
  - 快速故障排查
  - 访问地址

- **`SEPARATE_DEPLOYMENT_NATIVE.md`**: 原生部署指南
  - 后端原生部署详细步骤
  - 前端原生部署详细步骤
  - Systemd 服务配置
  - Nginx 配置
  - 更新部署
  - 故障排查
  - 性能优化

- **`DEPLOYMENT_README.md`**: 部署文档索引
  - 所有部署方案对比
  - 快速选择指南
  - 部署架构对比
  - 部署文件说明
  - 常见问题

- **`SEPARATE_DEPLOYMENT_SUMMARY.md`**: 本文档，实现总结

## 🏗️ 部署架构

### 前后端分离架构

```
前端服务器 (192.168.1.10)     后端服务器 (192.168.1.20)
┌─────────────────┐           ┌─────────────────┐
│   Frontend      │           │  Backend API    │
│   (Nginx)       │◄──────────┤  (FastAPI)      │
│   Port: 80      │   CORS    │  Port: 6080     │
└─────────────────┘           │                 │
                              │  Queue Worker   │
                              │  (Python)       │
                              │                 │
                              │  Redis          │
                              │  Port: 6379     │
                              └────────┬────────┘
                                       │
                                ┌──────▼──────┐
                                │    MySQL    │
                                │ (外部服务)   │
                                └─────────────┘
```

### 部署优势

- ✅ **独立扩展**: 前后端可以独立扩展资源
- ✅ **故障隔离**: 一方故障不影响另一方
- ✅ **灵活部署**: 可以使用不同的服务器配置
- ✅ **安全性**: 后端可以部署在内网，只暴露必要的端口
- ✅ **负载均衡**: 可以部署多个后端实例

## 🚀 快速使用

### Docker 部署（推荐）

#### 后端服务器 (192.168.1.20)

```bash
# 1. 配置环境
cp .env.backend .env
vim .env  # 修改 DB_HOST, DB_PASSWORD, CORS_ORIGINS

# 2. 一键部署
chmod +x deploy-backend.sh
bash deploy-backend.sh
```

#### 前端服务器 (192.168.1.10)

```bash
# 1. 配置环境
cp .env.frontend .env
vim .env  # 修改 VITE_API_BASE_URL

# 2. 一键部署
chmod +x deploy-frontend.sh
bash deploy-frontend.sh
```

### 原生部署

#### 后端服务器

```bash
chmod +x deploy-backend-native.sh
bash deploy-backend-native.sh
```

#### 前端服务器

```bash
chmod +x deploy-frontend-native.sh
bash deploy-frontend-native.sh
```

## 📝 关键配置说明

### 后端配置 (.env.backend)

```env
# MySQL 配置（必须）
DB_HOST=192.168.1.30
DB_PASSWORD=your_mysql_password

# Redis 密码（必须）
REDIS_PASSWORD=redis_fNmAxZ

# JWT 密钥（必须，至少32字符）
JWT_SECRET_KEY=your-secret-key-min-32-chars

# CORS 配置（必须，前端服务器地址）
CORS_ORIGINS=http://192.168.1.10,http://192.168.1.10:80
```

### 前端配置 (.env.frontend)

```env
# 后端 API 地址（必须）
VITE_API_BASE_URL=http://192.168.1.20:6080
```

### 网络配置

#### 防火墙规则

**后端服务器**:
```bash
# 允许前端服务器访问 API
sudo ufw allow from 192.168.1.10 to any port 6080
```

**前端服务器**:
```bash
# 允许所有访问前端
sudo ufw allow 80
```

## 🔧 常用命令

### 后端服务器

```bash
# Docker 部署
docker-compose -f docker-compose.backend.yml ps      # 查看状态
docker-compose -f docker-compose.backend.yml logs -f # 查看日志
docker-compose -f docker-compose.backend.yml restart # 重启服务

# 原生部署
sudo systemctl status qyd-api        # 查看 API 状态
sudo systemctl status qyd-worker     # 查看 Worker 状态
sudo journalctl -u qyd-api -f        # 查看 API 日志
sudo systemctl restart qyd-api       # 重启 API
```

### 前端服务器

```bash
# Docker 部署
docker-compose -f docker-compose.frontend.yml ps      # 查看状态
docker-compose -f docker-compose.frontend.yml logs -f # 查看日志
docker-compose -f docker-compose.frontend.yml restart # 重启服务

# 原生部署
sudo systemctl status nginx          # 查看状态
sudo tail -f /var/log/nginx/error.log # 查看日志
sudo systemctl restart nginx         # 重启服务
```

## 🐛 常见问题

### 1. 前端无法访问后端

**原因**: CORS 配置不正确或防火墙阻止

**解决**:
```bash
# 1. 检查后端 CORS 配置
docker-compose -f docker-compose.backend.yml exec backend-api env | grep CORS

# 2. 开放防火墙
sudo ufw allow from 192.168.1.10 to any port 6080

# 3. 重启后端
docker-compose -f docker-compose.backend.yml restart
```

### 2. 后端无法连接数据库

**原因**: 数据库防火墙或绑定地址配置不正确

**解决**:
```bash
# 1. 测试数据库连接
mysql -h 192.168.1.30 -u qyd -p

# 2. 开放防火墙（数据库服务器）
sudo ufw allow from 192.168.1.20 to any port 3306

# 3. 检查 MySQL 绑定地址
# /etc/mysql/mysql.conf.d/mysqld.cnf
bind-address = 0.0.0.0
```

## 📊 性能优化

### 扩展后端实例

```bash
# 启动多个 API 实例
docker-compose -f docker-compose.backend.yml up -d --scale backend-api=3

# 启动多个 Worker 实例
docker-compose -f docker-compose.backend.yml up -d --scale queue-worker=3
```

### 调整队列配置

编辑 `.env.backend`:

```env
# 高性能配置
REDIS_QUEUE_BATCH_SIZE=500
REDIS_QUEUE_NUM_WORKERS=12
```

## 🔒 安全建议

1. ✅ 使用强密码作为 JWT_SECRET_KEY（至少32字符）
2. ✅ 限制 CORS_ORIGINS 为特定域名
3. ✅ 配置防火墙，只允许必要的访问
4. ✅ 使用 HTTPS 加密通信
5. ✅ 定期更新 Docker 镜像和系统
6. ✅ 限制容器资源使用
7. ✅ 定期备份数据库
8. ✅ 监控服务日志

## 📚 相关文档

- [完整部署指南](SEPARATE_DEPLOYMENT_GUIDE.md)
- [快速参考](SEPARATE_DEPLOYMENT_QUICK_REF.md)
- [原生部署指南](SEPARATE_DEPLOYMENT_NATIVE.md)
- [部署文档索引](DEPLOYMENT_README.md)
- [Docker 快速部署](DOCKER_QUICK_START.md)

## 🎯 下一步

1. 根据实际服务器 IP 修改配置文件
2. 选择合适的部署方式（Docker 或原生）
3. 按照对应的部署指南执行部署
4. 验证部署是否成功
5. 配置域名和 HTTPS（可选）
6. 配置监控和日志（可选）

## 📞 获取帮助

如遇到问题：

1. 查看对应的部署文档
2. 检查服务日志
3. 查看故障排查章节
4. 提交 Issue 到项目仓库

---

**创建时间**: 2026-01-27  
**版本**: v1.0.0

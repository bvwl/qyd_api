# 部署文档索引

本项目支持多种部署方式，请根据您的需求选择合适的部署方案。

## 📚 部署文档

### 1. 前后端分离部署（推荐）

适用于生产环境，前后端部署在不同服务器上。

#### Docker 部署

- **完整指南**: [SEPARATE_DEPLOYMENT_GUIDE.md](SEPARATE_DEPLOYMENT_GUIDE.md)
- **快速参考**: [SEPARATE_DEPLOYMENT_QUICK_REF.md](SEPARATE_DEPLOYMENT_QUICK_REF.md)
- **配置文件**:
  - 后端: `docker-compose.backend.yml` + `.env.backend`
  - 前端: `docker-compose.frontend.yml` + `.env.frontend`
- **部署脚本**:
  - 后端: `deploy-backend.sh`
  - 前端: `deploy-frontend.sh`

#### 原生部署

- **完整指南**: [SEPARATE_DEPLOYMENT_NATIVE.md](SEPARATE_DEPLOYMENT_NATIVE.md)
- **部署脚本**:
  - 后端: `deploy-backend-native.sh`
  - 前端: `deploy-frontend-native.sh`

### 2. 一体化部署

适用于开发环境或小型项目，前后端部署在同一服务器上。

#### Docker 部署

- **快速开始**: [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)
- **完整指南**: [docs/deployment/DOCKER_DEPLOYMENT.md](docs/deployment/DOCKER_DEPLOYMENT.md)
- **配置文件**: `docker-compose.yml` + `.env`
- **部署脚本**: `docker-deploy-fast.sh`

#### 原生部署

- **完整指南**: [NATIVE_DEPLOYMENT.md](NATIVE_DEPLOYMENT.md)
- **部署脚本**: `deploy_native.sh`

## 🚀 快速选择

### 我应该选择哪种部署方式？

| 场景 | 推荐方案 | 文档 |
|------|---------|------|
| 生产环境，需要高可用 | Docker 前后端分离 | [SEPARATE_DEPLOYMENT_GUIDE.md](SEPARATE_DEPLOYMENT_GUIDE.md) |
| 开发环境，快速测试 | Docker 一体化 | [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) |
| 不使用 Docker | 原生前后端分离 | [SEPARATE_DEPLOYMENT_NATIVE.md](SEPARATE_DEPLOYMENT_NATIVE.md) |
| 小型项目，单服务器 | Docker 一体化 | [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) |

## 📋 部署架构对比

### 前后端分离部署

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
                                └─────────────┘
```

**优势**:
- ✅ 独立扩展
- ✅ 故障隔离
- ✅ 灵活部署
- ✅ 更高安全性

### 一体化部署

```
单服务器 (192.168.1.10)
┌─────────────────────────┐
│  Frontend (Nginx)       │
│  Port: 80               │
├─────────────────────────┤
│  Backend API (FastAPI)  │
│  Port: 6080             │
├─────────────────────────┤
│  Queue Worker (Python)  │
├─────────────────────────┤
│  Redis                  │
│  Port: 6379             │
└────────────┬────────────┘
             │
      ┌──────▼──────┐
      │    MySQL    │
      └─────────────┘
```

**优势**:
- ✅ 部署简单
- ✅ 资源利用率高
- ✅ 适合小型项目

## 🔧 部署文件说明

### Docker Compose 文件

| 文件 | 用途 | 说明 |
|------|------|------|
| `docker-compose.yml` | 一体化部署 | 前后端 + Redis 在同一服务器 |
| `docker-compose.backend.yml` | 后端分离部署 | 只部署后端 + Redis |
| `docker-compose.frontend.yml` | 前端分离部署 | 只部署前端 |

### 环境变量文件

| 文件 | 用途 | 说明 |
|------|------|------|
| `.env` | 一体化部署 | 包含所有配置 |
| `.env.backend` | 后端分离部署 | 后端专用配置 |
| `.env.frontend` | 前端分离部署 | 前端专用配置 |
| `.env.docker` | Docker 部署模板 | 一体化部署模板 |

### 部署脚本

| 脚本 | 用途 | 说明 |
|------|------|------|
| `docker-deploy-fast.sh` | Docker 一体化部署 | 一键部署所有服务 |
| `deploy-backend.sh` | Docker 后端部署 | 部署后端服务 |
| `deploy-frontend.sh` | Docker 前端部署 | 部署前端服务 |
| `deploy-backend-native.sh` | 原生后端部署 | 不使用 Docker |
| `deploy-frontend-native.sh` | 原生前端部署 | 不使用 Docker |

## 📖 详细文档

### 部署指南

- [前后端分离部署指南](SEPARATE_DEPLOYMENT_GUIDE.md)
- [前后端分离快速参考](SEPARATE_DEPLOYMENT_QUICK_REF.md)
- [前后端分离原生部署](SEPARATE_DEPLOYMENT_NATIVE.md)
- [Docker 快速部署](DOCKER_QUICK_START.md)
- [Docker 完整部署](docs/deployment/DOCKER_DEPLOYMENT.md)
- [原生部署指南](NATIVE_DEPLOYMENT.md)

### 架构文档

- [部署架构说明](docs/deployment/DEPLOYMENT_ARCHITECTURE.md)
- [前端部署详解](docs/deployment/FRONTEND_DEPLOYMENT.md)
- [项目结构](.kiro/steering/structure.md)

### 性能优化

- [高并发部署](HIGH_CONCURRENCY_DEPLOYMENT.md)
- [性能优化指南](docs/performance/SCALE_TO_10K_GUIDE.md)
- [超高性能配置](docs/performance/ULTRA_HIGH_PERFORMANCE_GUIDE.md)

### 其他文档

- [快速开始](QUICK_START.md)
- [快速更新指南](QUICK_UPDATE_GUIDE.md)
- [部署检查清单](DEPLOYMENT_CHECKLIST.md)

## 🎯 快速开始

### Docker 前后端分离部署

#### 后端服务器

```bash
# 1. 配置环境
cp .env.backend .env
vim .env  # 修改配置

# 2. 一键部署
bash deploy-backend.sh
```

#### 前端服务器

```bash
# 1. 配置环境
cp .env.frontend .env
vim .env  # 修改后端地址

# 2. 一键部署
bash deploy-frontend.sh
```

### Docker 一体化部署

```bash
# 1. 配置环境
cp .env.docker .env
vim .env  # 修改配置

# 2. 一键部署
bash docker-deploy-fast.sh
```

## 🔍 常见问题

### 1. 如何选择部署方式？

- **生产环境**: 推荐 Docker 前后端分离部署
- **开发环境**: 推荐 Docker 一体化部署
- **不使用 Docker**: 选择原生部署

### 2. 前后端分离部署的优势？

- 独立扩展：前后端可以独立扩展资源
- 故障隔离：一方故障不影响另一方
- 灵活部署：可以使用不同的服务器配置
- 更高安全性：后端可以部署在内网

### 3. 如何更新部署？

#### Docker 部署

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose -f <compose-file> build
docker-compose -f <compose-file> up -d
```

#### 原生部署

```bash
# 后端
cd /opt/qyd/backend
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart qyd-api qyd-worker

# 前端
cd /opt/qyd/frontend
git pull
npm install
npm run build
sudo systemctl restart nginx
```

### 4. 如何查看日志？

#### Docker 部署

```bash
# 查看所有日志
docker-compose -f <compose-file> logs -f

# 查看特定服务
docker-compose -f <compose-file> logs -f backend-api
```

#### 原生部署

```bash
# 后端
sudo journalctl -u qyd-api -f
sudo journalctl -u qyd-worker -f

# 前端
sudo tail -f /var/log/nginx/error.log
```

## 📞 获取帮助

如遇到问题：

1. 查看对应的部署文档
2. 检查服务日志
3. 查看故障排查章节
4. 提交 Issue 到项目仓库

---

**最后更新**: 2026-01-27  
**版本**: v1.0.0

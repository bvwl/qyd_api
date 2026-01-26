# QYD 项目管理系统

一个基于 FastAPI + React + TypeScript 的全栈项目管理系统，提供用户管理、项目管理、服务器管理、邮箱管理等功能。支持RBAC权限控制、Redis队列批量处理、MySQL主从读写分离等企业级特性。

## ✨ 核心特性

- 🚀 **高性能**: 支持每秒处理2000-15000条数据（可扩展）
- 🔐 **安全认证**: JWT Token认证，bcrypt密码加密，AES-CBC敏感数据加密
- 👥 **RBAC权限**: 基于角色的访问控制，动态菜单
- 📊 **读写分离**: MySQL主从架构，提升数据库性能
- 🔄 **异步队列**: Redis队列批量处理，避免接口阻塞
- 📝 **完善日志**: 按模块分类，自动轮转压缩，90天保留期
- 📧 **邮件集成**: Outlook API集成，HTML邮件查看器
- 📱 **响应式UI**: 基于Ant Design 5，适配多种设备
- 🔒 **数据加密**: 项目账号敏感字段自动加密，基于权限解密

## 📋 目录

- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [启动指南](#启动指南)
- [主要功能](#主要功能)
- [性能配置](#性能配置)
- [项目结构](#项目结构)
- [API文档](#api文档)
- [开发指南](#开发指南)
- [部署指南](#部署指南)
- [脚本工具](#脚本工具)
- [文档索引](#文档索引)

## 🛠 技术栈

### 后端
- **框架**: FastAPI (异步Web框架)
- **数据库**: MySQL 8.0 + Tortoise ORM (异步ORM)
- **缓存/队列**: Redis 7.0
- **认证**: JWT (python-jose) + bcrypt
- **任务调度**: APScheduler
- **日志**: 自定义日志系统 (按模块分类、自动轮转压缩)
- **邮件集成**: Outlook API
- **容器化**: Docker + Docker Compose

### 前端
- **框架**: React 18 + TypeScript 5
- **UI库**: Ant Design 5
- **路由**: React Router v6
- **状态管理**: Zustand
- **HTTP客户端**: Axios
- **构建工具**: Vite 5
- **日期处理**: dayjs
- **样式**: Less + CSS Modules
- **容器化**: Docker (多阶段构建) + Nginx

### 部署架构

#### Docker 容器化部署（推荐）

```
┌─────────────────────────────────────────────────────────┐
│                      Docker 容器                         │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Frontend   │  │ Backend API  │  │Queue Worker  │ │
│  │   (Nginx)    │  │  (FastAPI)   │  │  (Python)    │ │
│  │   Port: 80   │  │  Port: 6080  │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
         ↓                  ↓                  ↓
    ┌─────────┐        ┌─────────┐        ┌─────────┐
    │  MySQL  │        │  Redis  │        │  Logs   │
    │ (外部)  │        │ (外部)  │        │ (挂载)  │
    └─────────┘        └─────────┘        └─────────┘
```

**特点**：
- 前端使用多阶段构建（Node.js 构建 → Nginx 服务）
- 后端和队列处理分离部署
- 支持连接外部 MySQL 和 Redis
- 日志持久化到宿主机

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- Redis 7.0+ (可选，用于队列处理)
- Docker 20.10+ 和 Docker Compose 2.0+ (Docker 部署)

## 📖 启动指南

根据不同场景选择合适的启动方式，详见 [STARTUP_GUIDE.md](STARTUP_GUIDE.md)

| 场景 | 文档 | 适用情况 | 推荐指数 |
|------|------|---------|---------|
| 开发环境 | [STARTUP_GUIDE.md](STARTUP_GUIDE.md#场景-1-开发环境) | 本地开发、调试 | ⭐⭐⭐⭐⭐ |
| Docker 快速部署 | [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) | 快速体验、测试 | ⭐⭐⭐⭐⭐ |
| 生产环境（本地） | [QUICK_START.md](QUICK_START.md) | 小型生产环境 | ⭐⭐⭐⭐ |
| 高并发生产 | [HIGH_CONCURRENCY_DEPLOYMENT.md](HIGH_CONCURRENCY_DEPLOYMENT.md) | 大型生产环境 | ⭐⭐⭐⭐⭐ |
| 仅启动后端 | [STARTUP_GUIDE.md](STARTUP_GUIDE.md#场景-5-仅启动后端) | 后端开发、API 测试 | ⭐⭐⭐ |
| 仅启动前端 | [STARTUP_GUIDE.md](STARTUP_GUIDE.md#场景-6-仅启动前端) | 前端开发、UI 调试 | ⭐⭐⭐ |

### 默认管理员账号

- **邮箱**: zhiyu
- **密码**: 2201101122@qq.com
- **角色**: ADMIN (管理员)

> ⚠️ 首次登录后请立即修改密码！

---

### 快速部署示例

#### Docker 部署（推荐）

```bash
# 一键部署
bash docker-deploy-fast.sh
```

详细文档：[DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)

#### 本地部署

```bash
# 一键部署
bash deploy_native.sh
```

详细文档：[QUICK_START.md](QUICK_START.md)

#### 高并发部署

```bash
# 高并发部署
bash deploy-high-concurrency.sh
```

详细文档：[HIGH_CONCURRENCY_DEPLOYMENT.md](HIGH_CONCURRENCY_DEPLOYMENT.md)

---

## 📦 主要功能

### 用户管理
- ✅ 用户注册/登录 (JWT认证)
- ✅ 用户列表管理 (CRUD)
- ✅ 角色管理 (ADMIN, GM, IT, MANUAL)
- ✅ 用户角色分配
- ✅ 路由权限管理 (RBAC)
- ✅ API Token管理 (支持10年长期Token)
- ✅ 操作日志记录 (记录操作人user_id)

### 项目管理
- ✅ 项目信息管理
- ✅ 项目账号管理 (支持批量操作)
- ✅ 项目账号敏感数据加密 (AES-CBC，基于权限解密)
- ✅ 项目钱包管理
- ✅ 项目余额管理 (自动计算变动)
- ✅ 项目统计和导出 (Excel)
- ✅ 多状态支持 (正常、维护、结束等)

### 服务器管理
- ✅ 服务器信息管理
- ✅ 国家/地区管理
- ✅ 服务器分组管理
- ✅ 服务器账号管理

### 邮箱管理
- ✅ 邮箱信息管理
- ✅ Outlook集成
- ✅ 邮件查看 (支持HTML渲染、搜索、缓存)
- ✅ 发送邮件功能
- ✅ 邮箱状态监控
- ✅ 8种邮箱类型支持

### 企业级特性
- ✅ **RBAC权限控制**: 基于角色的访问控制，动态菜单
- ✅ **数据加密**: 项目账号敏感字段AES-CBC加密，每个项目独立密钥
- ✅ **权限解密**: 只有项目所属人和ADMIN可以解密敏感数据
- ✅ **Redis队列**: 批量数据处理，避免接口阻塞
- ✅ **智能缓存**: Redis缓存优化，减少数据库查询
- ✅ **读写分离**: MySQL主从架构，提升性能
- ✅ **日志系统**: 按模块分类、自动轮转压缩、90天保留期
- ✅ **异常处理**: 统一的错误处理机制
- ✅ **高性能**: 支持2000-15000条/秒数据处理

## ⚡ 性能配置

系统支持多种性能配置，满足不同场景需求：

### 标准性能（2000条/秒）

适用于中小型应用，单队列进程处理。

```bash
cd backend
cp .env.high_performance .env
python start.py                    # HTTP服务
python start_queue_worker.py       # 队列处理
```

**配置要点**：
- 1个队列进程，8个workers
- 批处理大小：300
- 数据库连接池：40

**详细文档**: [docs/performance/QUEUE_SEPARATION_QUICK_START.md](docs/performance/QUEUE_SEPARATION_QUICK_START.md)

### 超高性能（10000+条/秒）

适用于大型应用，多队列进程并行处理。

```bash
cd backend
cp .env.ultra_high_performance .env
python start.py                    # HTTP服务
python start_queue_worker.py &     # 队列进程1
python start_queue_worker.py &     # 队列进程2
python start_queue_worker.py &     # 队列进程3
```

**配置要点**：
- 3个队列进程，每个12个workers
- 批处理大小：500
- 数据库连接池：80
- 推荐服务器：48核心，128GB内存

**详细文档**: [docs/performance/SCALE_TO_10K_GUIDE.md](docs/performance/SCALE_TO_10K_GUIDE.md)

### 性能对比

| 配置 | 队列进程 | Workers | 批处理 | 性能 | 适用场景 |
|------|---------|---------|--------|------|---------|
| 标准 | 1 | 8 | 300 | 2700条/秒 | 中小型应用 |
| 高性能 | 2 | 10 | 400 | 6000条/秒 | 中大型应用 |
| 超高性能 | 3 | 12 | 500 | 12000条/秒 | 大型应用 |
| 极限性能 | 5 | 12 | 800 | 20000条/秒 | 超大型应用 |

**快速参考**: [docs/performance/PERFORMANCE_QUICK_REFERENCE.md](docs/performance/PERFORMANCE_QUICK_REFERENCE.md)

## 📁 项目结构

```
qyd_api2/
├── backend/                    # 后端服务 (FastAPI + Python)
│   ├── app/                    # 应用代码
│   │   ├── apis/               # API路由
│   │   ├── core/               # 核心配置
│   │   ├── crud/               # 数据库操作
│   │   ├── models/             # 数据库模型
│   │   ├── schemas/            # Pydantic模型
│   │   ├── utils/              # 工具类
│   │   └── main.py             # 应用入口
│   ├── tests/                  # 测试文件 ✨
│   │   ├── api/                # API 测试
│   │   ├── integration/        # 集成测试
│   │   ├── performance/        # 性能测试
│   │   ├── unit/               # 单元测试
│   │   └── README.md           # 测试说明
│   ├── scripts/                # 脚本工具 ✨
│   │   ├── database/           # 数据库脚本
│   │   ├── xui/                # XUI 脚本
│   │   ├── test/               # 测试脚本
│   │   └── README.md           # 脚本说明
│   ├── docs/                   # 后端文档 ✨
│   │   ├── deployment/         # 部署文档
│   │   ├── migration/          # 迁移文档
│   │   ├── features/           # 功能文档
│   │   └── README.md           # 文档索引
│   ├── db/                     # 数据库初始化脚本
│   ├── examples/               # 示例代码
│   ├── logs/                   # 日志文件
│   ├── .env.example            # 环境变量示例
│   ├── .env.high_performance   # 高性能配置模板
│   ├── .env.ultra_high_performance  # 超高性能配置模板
│   ├── start.py                # HTTP服务启动脚本
│   ├── start_queue_worker.py   # 队列处理启动脚本
│   └── requirements.txt        # Python依赖
├── frontend/                   # 前端应用 (React + TypeScript)
│   ├── src/                    # 源代码
│   │   ├── api/                # API接口
│   │   ├── components/         # 公共组件
│   │   ├── views/              # 页面组件
│   │   ├── store/              # 状态管理
│   │   ├── router/             # 路由配置
│   │   └── utils/              # 工具函数
│   ├── tests/                  # 测试文件
│   └── package.json            # 依赖配置
├── docs/                       # 项目文档
│   ├── encryption/             # 加密功能文档
│   ├── logs/                   # 日志管理文档
│   ├── export/                 # 导出功能文档
│   ├── server/                 # 服务器管理文档
│   ├── mail/                   # 邮件功能文档
│   ├── performance/            # 性能优化文档
│   ├── guides/                 # 使用指南
│   ├── summaries/              # 功能总结
│   ├── api/                    # API文档
│   ├── features/               # 功能文档
│   ├── fixes/                  # 修复记录
│   ├── rbac/                   # RBAC设计文档
│   ├── project/                # 项目文档 ✨
│   ├── archived/               # 归档文档 ✨
│   └── DOCUMENTATION_INDEX.md  # 文档索引
├── scripts/                    # 项目级脚本
│   ├── mysql/                  # MySQL相关脚本
│   ├── test/                   # 测试脚本
│   ├── debug/                  # 调试脚本
│   ├── utils/                  # 工具脚本 ✨
│   └── SCRIPTS_README.md       # 脚本说明
├── PROJECT_ORGANIZATION_COMPLETE.md  # 文件整理报告 ✨ (已移至 docs/summaries/)
├── organize_all_files.sh       # 文件整理脚本 ✨
└── README.md                   # 项目说明文档
```

> ✨ 标记的目录为最近整理优化的部分（2026-01-26）

## 📚 API文档

启动后端服务后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:6080/docs
- **ReDoc**: http://localhost:6080/redoc

或在前端应用中使用内置的API测试工具（菜单：API文档）

## 🔧 开发指南

### 后端开发

详见 [backend/README.md](backend/README.md)

**关键规范**：
- 所有API必须添加JWT认证依赖
- 异常处理顺序：HTTPException → ValueError → Exception
- 使用读写分离工具：`db_read()` 和 `db_write()`
- 路由定义顺序：特定路径在前，动态路径在后

### 前端开发

详见 [frontend/README.md](frontend/README.md)

**关键规范**：
- 使用TypeScript定义类型
- API调用统一使用封装的request方法
- 使用权限组件控制UI显示
- 错误处理由拦截器统一处理

### 开发规范

详见 [.kiro/steering/conventions.md](.kiro/steering/conventions.md)

## 🚢 部署指南

### Docker 部署（推荐）

Docker 部署提供完整的容器化解决方案，支持前后端分离架构。

#### 快速部署

```bash
# 一键部署
bash docker-deploy.sh
```

#### 详细步骤

```bash
# 1. 配置环境变量
cp .env.docker .env
vim .env  # 配置 MySQL、Redis 等

# 2. 构建镜像
docker-compose build

# 3. 初始化数据库
docker-compose run --rm backend-api python deploy_init.py

# 4. 启动所有服务
docker-compose up -d

# 5. 查看服务状态
docker-compose ps
```

#### 服务管理

```bash
# 查看日志
docker-compose logs -f [service_name]

# 重启服务
docker-compose restart [service_name]

# 停止服务
docker-compose stop

# 删除服务（保留数据）
docker-compose down

# 删除服务和数据
docker-compose down -v
```

#### 容器说明

| 容器 | 说明 | 端口 | 镜像大小 |
|------|------|------|---------|
| frontend | Nginx + 静态文件 | 80 | ~30MB |
| backend-api | FastAPI 应用 | 6080 | ~500MB |
| queue-worker | Redis 队列处理 | - | ~500MB |

**前端容器特点**：
- 使用多阶段构建，第一阶段编译，第二阶段部署
- 最终镜像只包含 Nginx 和打包后的静态文件
- 体积小、启动快、性能优异

**详细文档**：
- [Docker 完整部署指南](docs/deployment/DOCKER_DEPLOYMENT.md)（60+ 页）
- [Docker 快速参考](docs/deployment/DOCKER_QUICK_REFERENCE.md)
- [Docker 部署方案总结](docs/deployment/DOCKER_SETUP_COMPLETE.md)

---

### 传统部署

#### 后端部署

```bash
cd backend

# 方式一：快速部署
bash quick_deploy.sh

# 方式二：手动部署
pip install -r requirements.txt
cp .env.example .env
vim .env
aerich init -t app.core.settings.TORTOISE_ORM
aerich init-db
python deploy_init.py
python start.py
```

#### 前端部署

```bash
cd frontend

# 构建生产版本
npm install
npm run build

# 部署 dist 目录到 Nginx
sudo cp -r dist/* /var/www/html/
```

**Nginx 配置示例**：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /var/www/html;
    index index.html;
    
    # 前端路由
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理
    location /v1/ {
        proxy_pass http://localhost:6080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

### 使用 Supervisor 管理进程（推荐）

适用于生产环境，自动重启和日志管理。

```bash
# 安装 Supervisor
sudo apt-get install supervisor

# 配置文件示例见：
# docs/performance/REDIS_QUEUE_SEPARATION_GUIDE.md

# 启动服务
sudo supervisorctl start qyd:*

# 查看状态
sudo supervisorctl status
```

---

### 性能优化部署

对于高性能需求（10000+条/秒），请参考：
- [超高性能部署指南](docs/performance/SCALE_TO_10K_GUIDE.md)
- [Redis队列分离部署](docs/performance/REDIS_QUEUE_SEPARATION_GUIDE.md)
- [性能配置快速参考](docs/performance/PERFORMANCE_QUICK_REFERENCE.md)

## 📖 文档

### 快速开始
- [STARTUP_GUIDE.md](STARTUP_GUIDE.md) - 启动指南（所有场景）⭐⭐⭐⭐⭐
- [QUICK_START.md](QUICK_START.md) - 本地快速部署
- [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) - Docker 快速部署

### 完整文档索引
- [docs/DOCUMENTATION_COMPLETE_INDEX.md](docs/DOCUMENTATION_COMPLETE_INDEX.md) - 完整文档索引⭐⭐⭐⭐⭐

### 部署文档
- [NATIVE_DEPLOYMENT.md](NATIVE_DEPLOYMENT.md) - 本地详细部署
- [HIGH_CONCURRENCY_DEPLOYMENT.md](HIGH_CONCURRENCY_DEPLOYMENT.md) - 高并发部署
- [docs/deployment/](docs/deployment/) - 部署文档目录

### 开发文档
- [.kiro/steering/conventions.md](.kiro/steering/conventions.md) - 开发规范⭐⭐⭐⭐⭐
- [.kiro/steering/structure.md](.kiro/steering/structure.md) - 项目结构
- [backend/README.md](backend/README.md) - 后端开发指南
- [frontend/README.md](frontend/README.md) - 前端开发指南

### 功能文档
- [docs/encryption/](docs/encryption/) - 加密功能文档
- [docs/logs/](docs/logs/) - 日志管理文档
- [docs/performance/](docs/performance/) - 性能优化文档
- [docs/rbac/](docs/rbac/) - RBAC 设计文档
- [docs/features/](docs/features/) - 功能文档目录

### 脚本工具
- [scripts/SCRIPTS_INDEX.md](scripts/SCRIPTS_INDEX.md) - 脚本工具索引⭐⭐⭐⭐⭐

---

## 🧪 测试

### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_user.py

# 性能测试
python test_queue_performance.py          # 标准测试（10000条）
python test_ultra_performance.py          # 超高性能测试（50000条）
```

### 前端测试

```bash
cd frontend

# 运行测试
npm run test

# 代码检查
npm run lint
```

## 🔒 安全建议

1. ✅ 使用强密码作为 `JWT_SECRET_KEY`（至少32字符）
2. ✅ 生产环境设置 `APP_DEBUG=0`
3. ✅ 限制 `CORS_ORIGINS` 为特定域名
4. ✅ 定期更新依赖包
5. ✅ 使用HTTPS部署
6. ✅ 定期备份数据库
7. ✅ 保护Redis密码，限制访问IP
8. ✅ 首次登录后立即修改管理员密码
9. ✅ 配置防火墙，只开放必要端口
10. ✅ 启用MySQL慢查询日志，监控性能

## 🛠 脚本工具

项目提供了丰富的脚本工具，详见 [scripts/SCRIPTS_INDEX.md](scripts/SCRIPTS_INDEX.md)

### 脚本分类

| 类型 | 位置 | 说明 |
|------|------|------|
| 部署脚本 | 根目录 | 环境安装、项目部署 |
| 服务管理 | 根目录 | 启动、重启、更新服务 |
| 数据库脚本 | `scripts/mysql/`, `backend/db/` | MySQL 管理、数据迁移 |
| 测试脚本 | `scripts/test/` | API 测试、权限测试 |
| 调试脚本 | `scripts/debug/` | 问题诊断、调试工具 |
| 工具脚本 | `scripts/utils/`, `backend/scripts/` | 备份、日志管理等 |

### 常用脚本

```bash
# 部署相关
bash setup_environment.sh          # 环境安装
bash deploy_native.sh              # 本地部署
bash docker-deploy-fast.sh         # Docker 快速部署

# 服务管理
bash start_all_services.sh         # 启动所有服务
bash restart_all_services.sh       # 重启所有服务
bash update-and-restart.sh         # 更新并重启

# 数据库管理
bash scripts/mysql/check_mysql_status.sh    # 检查 MySQL 状态
bash scripts/mysql/fix_replication.sh       # 修复主从复制

# 测试和调试
bash scripts/test/test_api_endpoints.sh     # 测试 API
python scripts/debug/check_api_auth.py      # 检查认证

# 工具
bash scripts/utils/backup_database.sh       # 备份数据库
python backend/scripts/cleanup_logs.py      # 清理日志
```

---

## 📚 文档索引

完整的文档索引和导航，详见 [docs/DOCUMENTATION_COMPLETE_INDEX.md](docs/DOCUMENTATION_COMPLETE_INDEX.md)

### 核心文档

| 文档 | 说明 | 推荐指数 |
|------|------|---------|
| [NAVIGATION_GUIDE.md](NAVIGATION_GUIDE.md) | 导航指南（按角色/任务） | ⭐⭐⭐⭐⭐ |
| [STARTUP_GUIDE.md](STARTUP_GUIDE.md) | 启动指南（所有场景） | ⭐⭐⭐⭐⭐ |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | 快速参考卡（常用命令） | ⭐⭐⭐⭐⭐ |
| [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) | Docker 快速部署 | ⭐⭐⭐⭐⭐ |
| [QUICK_START.md](QUICK_START.md) | 本地快速部署 | ⭐⭐⭐⭐ |
| [HIGH_CONCURRENCY_DEPLOYMENT.md](HIGH_CONCURRENCY_DEPLOYMENT.md) | 高并发部署 | ⭐⭐⭐⭐⭐ |

### 开发文档

| 文档 | 说明 | 推荐指数 |
|------|------|---------|
| [.kiro/steering/conventions.md](.kiro/steering/conventions.md) | 开发规范和最佳实践 | ⭐⭐⭐⭐⭐ |
| [.kiro/steering/structure.md](.kiro/steering/structure.md) | 项目结构说明 | ⭐⭐⭐⭐⭐ |
| [backend/README.md](backend/README.md) | 后端开发指南 | ⭐⭐⭐⭐⭐ |
| [frontend/README.md](frontend/README.md) | 前端开发指南 | ⭐⭐⭐⭐⭐ |

### 性能优化

| 文档 | 说明 | 推荐指数 |
|------|------|---------|
| [docs/performance/PERFORMANCE_QUICK_REFERENCE.md](docs/performance/PERFORMANCE_QUICK_REFERENCE.md) | 性能配置快速参考 | ⭐⭐⭐⭐⭐ |
| [docs/performance/SCALE_TO_10K_GUIDE.md](docs/performance/SCALE_TO_10K_GUIDE.md) | 扩展到 10000+ QPS | ⭐⭐⭐⭐⭐ |

### 功能文档

| 文档 | 说明 | 推荐指数 |
|------|------|---------|
| [docs/encryption/PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md](docs/encryption/PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md) | 加密功能快速参考 | ⭐⭐⭐⭐⭐ |
| [docs/logs/LOG_QUICK_REFERENCE.md](docs/logs/LOG_QUICK_REFERENCE.md) | 日志快速参考 | ⭐⭐⭐⭐⭐ |
| [docs/rbac/QUICK_START.md](docs/rbac/QUICK_START.md) | RBAC 快速开始 | ⭐⭐⭐⭐⭐ |

### 脚本工具

| 文档 | 说明 | 推荐指数 |
|------|------|---------|
| [scripts/SCRIPTS_INDEX.md](scripts/SCRIPTS_INDEX.md) | 脚本工具完整索引 | ⭐⭐⭐⭐⭐ |
| [backend/scripts/README.md](backend/scripts/README.md) | 后端脚本说明 | ⭐⭐⭐⭐ |

---

## 📊 监控和维护

### 日志管理

```bash
# 查看日志
tail -f backend/logs/api.log
tail -f backend/logs/app.log
tail -f backend/logs/database.log

# 清理旧日志（自动压缩）
# 日志系统会自动按小时轮转并压缩旧日志
```

### 性能监控

```bash
# 监控队列大小
redis-cli ZCARD qyd:project_account_keys_zset

# 监控数据库连接
mysql -e "SHOW PROCESSLIST;" | wc -l

# 监控Redis连接
redis-cli INFO clients | grep connected_clients

# 系统资源监控
htop
```

### 数据库备份

```bash
# 备份
mysqldump -u qyd -p qyd > backup_$(date +%Y%m%d).sql

# 恢复
mysql -u qyd -p qyd < backup_20260123.sql
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v1.2.0 (2026-01-26)

**Docker 部署方案**：
- ✅ 完整的 Docker 部署配置（前后端分离）
- ✅ 优化的 Dockerfile（多阶段构建）
- ✅ Docker Compose 配置（3个服务）
- ✅ 一键部署脚本 `docker-deploy.sh`
- ✅ Nginx 配置（前端服务）
- ✅ 环境变量模板 `.env.docker`
- ✅ 详细部署文档和快速参考
- ✅ 支持连接外部 MySQL 和 Redis
- ✅ 详见 [DOCKER_SETUP_COMPLETE.md](docs/deployment/DOCKER_SETUP_COMPLETE.md)

**部署优化**：
- ✅ 完善 requirements.txt，添加版本号和分类
- ✅ 新增快速部署脚本 `quick_deploy.sh`
- ✅ 新增部署初始化脚本 `deploy_init.py`
- ✅ 新增部署检查脚本 `check_deployment.py`
- ✅ 新增详细部署指南 `DEPLOYMENT_GUIDE.md`
- ✅ 使用 Aerich 管理数据库迁移
- ✅ Python 脚本自动导入初始数据
- ✅ 详见 [DEPLOYMENT_SUMMARY.md](docs/deployment/DEPLOYMENT_SUMMARY.md)

**项目整理**：
- ✅ 完成项目文件整理，优化目录结构
- ✅ 整理 71 个文件到对应目录
- ✅ 创建测试、脚本、文档索引文件
- ✅ 详见 [PROJECT_ORGANIZATION_COMPLETE.md](docs/summaries/PROJECT_ORGANIZATION_COMPLETE.md)

**功能更新**：
- ✅ 批量创建钱包功能开放给所有用户
- ✅ 详见 [WALLET_BATCH_CREATE_PERMISSION_UPDATE.md](docs/features/WALLET_BATCH_CREATE_PERMISSION_UPDATE.md)

**目录优化**：
- ✅ backend/tests/ - 测试文件按类型分类（api/integration/performance）
- ✅ backend/scripts/ - 脚本文件按功能分类（database/xui）
- ✅ backend/docs/ - 后端文档按主题分类（deployment/migration/features）
- ✅ docs/project/ - 项目级文档
- ✅ docs/archived/ - 归档文档
- ✅ scripts/utils/ - 工具脚本

### v1.1.0 (2026-01-25)

**新功能**：
- ✅ 项目账号敏感数据加密（AES-CBC，每个项目独立密钥）
- ✅ 基于权限的自动解密（只有项目所属人和ADMIN可以解密）
- ✅ Redis队列数据自动加密
- ✅ 日志系统优化（90天保留期，四层目录结构）
- ✅ 邮件菜单修复和优化

**安全增强**：
- ✅ 敏感字段递归加密（支持所有层级）
- ✅ 每个项目使用独立密钥
- ✅ 权限隔离，防止数据泄露

**文档更新**：
- ✅ 加密功能完整文档
- ✅ 日志管理文档
- ✅ 快速开始指南

### v1.0.0 (2026-01-23)

**新功能**：
- ✅ 完整的用户管理系统（CRUD、角色、权限）
- ✅ 项目管理（项目、账号、钱包、余额）
- ✅ 服务器管理（服务器、国家、分组、账号）
- ✅ 邮箱管理（邮箱、Outlook集成、邮件查看器）
- ✅ RBAC权限控制系统
- ✅ Redis队列批量处理
- ✅ MySQL主从读写分离
- ✅ JWT认证和API Token管理
- ✅ 完善的日志系统

**性能优化**：
- ✅ 队列处理和HTTP服务分离
- ✅ 支持2000-15000条/秒数据处理
- ✅ 智能缓存机制
- ✅ 数据库连接池优化

**文档完善**：
- ✅ 完整的API文档
- ✅ 性能优化指南
- ✅ 部署指南
- ✅ 开发规范

## 📄 许可证

[MIT License](LICENSE)

## 📧 联系方式

如有问题，请提交 Issue 或联系项目维护者。

---

**项目状态**: ✅ 生产就绪  
**最后更新**: 2026-01-26  
**版本**: v1.2.0

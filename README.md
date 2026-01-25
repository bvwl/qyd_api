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
- [主要功能](#主要功能)
- [性能配置](#性能配置)
- [项目结构](#项目结构)
- [API文档](#api文档)
- [开发指南](#开发指南)
- [部署指南](#部署指南)
- [文档](#文档)

## 🛠 技术栈

### 后端
- **框架**: FastAPI (异步Web框架)
- **数据库**: MySQL 8.0 + Tortoise ORM (异步ORM)
- **缓存/队列**: Redis 7.0
- **认证**: JWT (python-jose) + bcrypt
- **任务调度**: APScheduler
- **日志**: 自定义日志系统 (按模块分类、自动轮转压缩)
- **邮件集成**: Outlook API

### 前端
- **框架**: React 18 + TypeScript 5
- **UI库**: Ant Design 5
- **路由**: React Router v6
- **状态管理**: Zustand
- **HTTP客户端**: Axios
- **构建工具**: Vite 5
- **日期处理**: dayjs
- **样式**: Less + CSS Modules

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- Redis 7.0+ (可选，用于队列处理)

### Docker 部署（推荐）

#### 一键部署

```bash
# 1. 配置环境变量
cp .env.docker .env
vim .env  # 配置 MySQL 和 Redis 连接

# 2. 运行部署脚本
bash docker-deploy.sh
```

#### 手动部署

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

**访问地址**:
- 前端: http://localhost
- 后端: http://localhost:6080
- API 文档: http://localhost:6080/docs

详细文档：[DOCKER_DEPLOYMENT.md](docs/deployment/DOCKER_DEPLOYMENT.md) | [快速参考](docs/deployment/DOCKER_QUICK_REFERENCE.md)

---

### 后端部署

#### 方法一：快速部署（推荐）

```bash
cd backend
bash quick_deploy.sh
```

脚本会自动完成：
- ✅ 检查环境
- ✅ 创建虚拟环境
- ✅ 安装依赖
- ✅ 配置环境变量
- ✅ 初始化数据库
- ✅ 导入初始数据

#### 方法二：手动部署

```bash
cd backend

# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库、Redis等信息

# 3. 使用 Aerich 初始化数据库
aerich init -t app.core.settings.TORTOISE_ORM
aerich init-db

# 4. 导入初始数据
python deploy_init.py

# 5. 检查部署
python check_deployment.py

# 6. 启动服务
python start.py
```

详细部署文档：[backend/DEPLOYMENT_GUIDE.md](backend/DEPLOYMENT_GUIDE.md) | [部署总结](docs/deployment/DEPLOYMENT_SUMMARY.md)

后端服务将在 `http://localhost:6080` 启动

### 前端启动

```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev
```

前端应用将在 `http://localhost:3000` 启动

### 默认管理员账号

- **邮箱**: zhiyu
- **密码**: 2201101122@qq.com
- **角色**: ADMIN (管理员)

> ⚠️ 首次登录后请立即修改密码！

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

### 使用Docker部署

```bash
# 后端
cd backend
docker-compose up -d

# 前端
cd frontend
npm run build
# 将 dist/ 目录部署到Nginx或其他静态服务器
```

### 使用Supervisor管理进程（推荐）

适用于生产环境，自动重启和日志管理。

```bash
# 安装Supervisor
sudo apt-get install supervisor

# 配置文件示例见：
# docs/performance/REDIS_QUEUE_SEPARATION_GUIDE.md
```

### 性能优化部署

对于高性能需求（10000+条/秒），请参考：
- [超高性能部署指南](docs/performance/SCALE_TO_10K_GUIDE.md)
- [Redis队列分离部署](docs/performance/REDIS_QUEUE_SEPARATION_GUIDE.md)

## 📖 文档

### 快速开始
- [QUICK_START_GUIDE.md](docs/project/QUICK_START_GUIDE.md) - 快速开始指南（推荐）

### 加密功能文档 (`docs/encryption/`)

| 文档 | 说明 |
|------|------|
| [PROJECT_ACCOUNT_ENCRYPTION.md](docs/encryption/PROJECT_ACCOUNT_ENCRYPTION.md) | 项目账号加密详细文档 |
| [PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md](docs/encryption/PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md) | 加密功能快速参考 |
| [PROJECT_ACCOUNT_ENCRYPTION_FLOW.md](docs/encryption/PROJECT_ACCOUNT_ENCRYPTION_FLOW.md) | 加密流程图 |
| [SOCKS5_ACCOUNT_AES_ENCRYPTION.md](docs/encryption/SOCKS5_ACCOUNT_AES_ENCRYPTION.md) | SOCKS5账号加密 |

### 日志管理文档 (`docs/logs/`)

| 文档 | 说明 |
|------|------|
| [LOG_SYSTEM_COMPLETE.md](docs/logs/LOG_SYSTEM_COMPLETE.md) | 日志系统完整文档 |
| [LOG_QUICK_REFERENCE.md](docs/logs/LOG_QUICK_REFERENCE.md) | 日志快速参考 |
| [LOG_MANAGEMENT_UPDATE.md](docs/logs/LOG_MANAGEMENT_UPDATE.md) | 日志管理更新说明 |

### 性能优化文档 (`docs/performance/`)

| 文档 | 说明 |
|------|------|
| [QUEUE_SEPARATION_QUICK_START.md](docs/performance/QUEUE_SEPARATION_QUICK_START.md) | 队列分离快速开始 |
| [REDIS_QUEUE_SEPARATION_GUIDE.md](docs/performance/REDIS_QUEUE_SEPARATION_GUIDE.md) | Redis队列分离完整指南 |
| [SCALE_TO_10K_GUIDE.md](docs/performance/SCALE_TO_10K_GUIDE.md) | 扩展到10000+条/秒指南 |
| [PERFORMANCE_QUICK_REFERENCE.md](docs/performance/PERFORMANCE_QUICK_REFERENCE.md) | 性能配置快速参考 |
| [UVICORN_WORKERS_VS_REDIS_WORKERS.md](docs/performance/UVICORN_WORKERS_VS_REDIS_WORKERS.md) | Uvicorn Workers问题详解 |

### 导出功能文档 (`docs/export/`)

- 项目统计导出功能
- Excel导出实现
- 导出状态列和修复

### 使用指南 (`docs/guides/`)

- Redis队列使用指南
- Redis缓存逻辑说明
- 权限管理快速开始
- RBAC使用指南
- 邮件查看器快速开始
- 菜单绑定指南

### 功能文档 (`docs/features/`)

- 邮件查看器功能
- 钱包功能更新
- 项目用户管理
- 复制ID功能
- 项目账号功能总结
- 项目整理总结

### RBAC设计文档 (`docs/rbac/`)

- RBAC设计对比
- 企业级RBAC设计
- 现代RBAC设计
- 实用RBAC设计
- V1 vs V2对比

### 修复记录 (`docs/fixes/`)

详细的修复和更新记录，包括：
- JWT认证优化
- RBAC权限修复
- 日志系统更新
- 性能优化记录

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

项目提供了丰富的脚本工具，位于 `scripts/` 目录：

### MySQL脚本 (`scripts/mysql/`)
- `check_mysql_status.sh` - 检查MySQL状态
- `connect_mysql.sh` - 连接MySQL
- `restart_mysql.sh` - 重启MySQL
- `fix_replication.sh` - 修复主从复制
- `deploy_mysql_*.sh` - MySQL部署脚本

### 测试脚本 (`scripts/test/`)
- `test_api_endpoints.sh` - 测试API接口
- `test_*_permission.sh` - 测试权限功能
- `test_batch_upsert.py` - 测试批量操作

### 调试脚本 (`scripts/debug/`)
- `check_api_auth.py` - 检查API认证状态
- `check_delete_permissions.py` - 检查删除权限
- `debug_account.py` - 调试账号问题

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

# QYD 项目管理系统

一个基于 FastAPI + React + TypeScript 的全栈项目管理系统，提供用户管理、项目管理、服务器管理、邮箱管理等功能。支持RBAC权限控制、Redis队列批量处理、MySQL主从读写分离等企业级特性。

## 项目结构

```
qyd_api2/
├── backend/          # 后端服务 (FastAPI + Python)
│   ├── app/          # 应用代码
│   ├── db/           # 数据库初始化脚本
│   ├── scripts/      # 工具脚本
│   └── logs/         # 日志文件
├── frontend/         # 前端应用 (React + TypeScript + Ant Design)
│   ├── src/          # 源代码
│   └── tests/        # 测试文件
├── docs/             # 项目文档
│   ├── guides/       # 使用指南
│   ├── summaries/    # 功能总结
│   ├── api/          # API文档
│   ├── features/     # 功能文档
│   └── fixes/        # 修复记录
├── scripts/          # 项目级脚本
│   ├── mysql/        # MySQL相关脚本
│   ├── test/         # 测试脚本
│   ├── debug/        # 调试脚本
│   └── utils/        # 工具脚本
└── README.md         # 项目说明文档
```

## 技术栈

### 后端
- **框架**: FastAPI (异步Web框架)
- **数据库**: MySQL 8.0 + Tortoise ORM
- **缓存/队列**: Redis 7.0
- **认证**: JWT (JSON Web Token)
- **密码加密**: bcrypt
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

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- Redis 7.0+ (可选，用于队列处理)

### 后端启动

```bash
cd backend

# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库、Redis等信息

# 3. 初始化数据库
python db/init_roles_and_admin.py

# 4. 启动服务
python start.py
```

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

### 访问系统

打开浏览器访问 `http://localhost:3000`，使用默认管理员账号登录

## 默认账号

- **邮箱**: zhiyu
- **密码**: 2201101122@qq.com
- **角色**: ADMIN (管理员)

## 主要功能

### 用户管理
- ✅ 用户注册/登录 (JWT认证)
- ✅ 用户列表管理 (CRUD)
- ✅ 角色管理 (ADMIN, GM, IT, MANUAL)
- ✅ 用户角色分配
- ✅ 路由权限管理 (RBAC)
- ✅ API Token管理
- ✅ 操作日志记录

### 项目管理
- ✅ 项目信息管理
- ✅ 项目账号管理 (支持批量操作)
- ✅ 项目钱包管理
- ✅ 项目余额管理
- ✅ 多状态支持 (正常、维护、结束等)

### 服务器管理
- ✅ 服务器信息管理
- ✅ 国家/地区管理
- ✅ 服务器分组管理
- ✅ 服务器账号管理

### 邮箱管理
- ✅ 邮箱信息管理
- ✅ Outlook集成
- ✅ 邮件查看器 (支持HTML渲染、搜索、缓存)
- ✅ 邮箱状态监控
- ✅ 8种邮箱类型支持

### 企业级特性
- ✅ **RBAC权限控制**: 基于角色的访问控制
- ✅ **Redis队列**: 批量数据处理，避免接口阻塞
- ✅ **智能缓存**: Redis缓存优化，减少数据库查询
- ✅ **读写分离**: MySQL主从架构，提升性能
- ✅ **日志系统**: 按模块分类、自动轮转压缩
- ✅ **异常处理**: 统一的错误处理机制

### 其他功能
- ✅ 仪表盘数据统计
- ✅ 高级搜索 (支持时间范围过滤)
- ✅ 分页查询
- ✅ API接口测试工具
- ✅ 响应式布局

## API文档

启动后端服务后，访问以下地址查看API文档：

- Swagger UI: `http://localhost:6080/docs`
- ReDoc: `http://localhost:6080/redoc`

或在前端应用中使用内置的API测试工具（菜单：API文档）

## 开发指南

### 后端开发

详见 [backend/README.md](backend/README.md)

### 前端开发

详见 [frontend/README.md](frontend/README.md)

## 项目文档

文档按类型组织在 `docs/` 目录：

### 使用指南 (`docs/guides/`)
- Redis队列使用指南
- Redis缓存逻辑说明
- Redis管道分离设计
- 权限管理快速开始
- RBAC使用指南
- 邮件查看器快速开始
- 菜单绑定指南

### 功能总结 (`docs/summaries/`)
- Redis队列实现总结
- RBAC实现总结
- 权限管理总结
- 邮件查看器实现总结
- 批量操作总结
- 系统状态总结

### API文档 (`docs/api/`)
- API认证实现
- API错误处理

### 功能文档 (`docs/features/`)
- 邮件查看器功能
- 钱包功能更新
- 项目用户管理

### 修复记录 (`docs/fixes/`)
- 详细的修复和更新记录

## 测试

### 后端测试

```bash
cd backend
pytest
```

测试文件位于 `backend/tests/`

### 前端测试

```bash
cd frontend
npm run test
```

测试文件位于 `frontend/tests/`

## 核心特性详解

### 1. Redis队列批量处理

支持大批量数据的异步处理，避免接口长时间占用：

- **智能缓存检查**: 先检查Redis缓存，已处理的数据跳过
- **读写分离**: 使用从库查询，主库更新/创建
- **批量处理**: 可配置批量大小和工作线程数
- **独立管道**: 缓存操作和任务清理使用独立管道，失败不影响数据库操作
- **自动过期**: 缓存1小时自动过期

配置示例 (`.env`):
```env
REDIS_QUEUE_BATCH_SIZE=100        # 批量处理大小
REDIS_QUEUE_NUM_WORKERS=4         # 工作线程数
REDIS_QUEUE_CACHE_EXPIRE=3600     # 缓存过期时间(秒)
```

### 2. MySQL主从读写分离

支持一主多从架构，提升数据库性能：

- **主库**: 处理所有写操作 (INSERT, UPDATE, DELETE)
- **从库**: 处理所有读操作 (SELECT)
- **自动路由**: ORM自动根据操作类型选择数据库
- **连接池**: 自动管理数据库连接

配置示例 (`.env`):
```env
# 主库配置
DB_HOST=127.0.0.1
DB_PORT=3307
DB_USER=qyd
DB_PASSWORD=your_password
DB_NAME=qyd

# 从库配置
DB_SLAVE_HOSTS=127.0.0.1:3308,127.0.0.1:3309
```

### 3. RBAC权限控制

基于角色的访问控制系统：

- **4种角色**: ADMIN (管理员)、GM (项目管理员)、IT (技术人员)、MANUAL (手动操作员)
- **路由权限**: 动态菜单，根据角色显示不同菜单
- **API权限**: 所有API接口都需要JWT认证
- **删除保护**: 所有删除接口只有管理员可访问

### 4. 邮件查看器

集成Outlook邮件查看功能：

- **HTML渲染**: 安全渲染HTML邮件内容
- **本地缓存**: 10分钟本地缓存，减少API调用
- **搜索功能**: 支持文本搜索和正则表达式搜索
- **附件支持**: 显示附件列表和下载链接

### 5. 日志系统

完善的日志记录和管理：

- **按模块分类**: app.log, api.log, database.log, scheduler.log
- **自动轮转**: 按小时轮转日志文件
- **自动压缩**: 旧日志自动压缩为.gz格式
- **日志级别**: 支持DEBUG, INFO, WARNING, ERROR, CRITICAL

## 部署

### 后端部署

使用 Docker:

```bash
cd backend
docker-compose up -d
```

### 前端部署

```bash
cd frontend
npm run build
# 将 dist/ 目录部署到静态服务器
```

## 脚本工具

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

### 工具脚本 (`scripts/utils/`)
- `add_auth_to_apis.py` - 批量添加API认证
- `fix_*.py` - 各种修复工具
- `frontend_restart.sh` - 重启前端服务

## 安全建议

1. ✅ 使用强密码作为 `JWT_SECRET_KEY`
2. ✅ 生产环境设置 `DEBUG=False`
3. ✅ 限制 `CORS_ORIGINS` 为特定域名
4. ✅ 定期更新依赖包
5. ✅ 使用HTTPS部署
6. ✅ 定期备份数据库
7. ✅ 保护Redis密码，限制访问IP
8. ✅ 首次登录后立即修改管理员密码

## 许可证

[MIT License](LICENSE)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请联系项目维护者。

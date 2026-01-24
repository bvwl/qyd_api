# QYD 项目结构说明

## 📁 目录结构

```
qyd_api2/
├── backend/                          # 后端服务
│   ├── app/                          # 应用代码
│   │   ├── apis/                     # API路由
│   │   │   ├── deps.py               # 依赖注入（JWT认证）
│   │   │   └── v1/                   # API v1版本
│   │   │       ├── user/             # 用户管理API
│   │   │       ├── project/          # 项目管理API
│   │   │       ├── server/           # 服务器管理API
│   │   │       ├── mail/             # 邮箱管理API
│   │   │       └── rbac/             # RBAC权限API
│   │   ├── core/                     # 核心配置
│   │   │   ├── settings.py           # 配置管理（数据库、Redis等）
│   │   │   ├── database.py           # 数据库配置（读写分离）
│   │   │   ├── tools.py              # 工具函数（密码加密等）
│   │   │   └── verify.py             # 验证函数
│   │   ├── crud/                     # 数据库操作层
│   │   │   ├── user/                 # 用户相关CRUD
│   │   │   ├── project/              # 项目相关CRUD
│   │   │   ├── server/               # 服务器相关CRUD
│   │   │   └── mail/                 # 邮箱相关CRUD
│   │   ├── models/                   # 数据库模型
│   │   │   ├── base.py               # 基础模型
│   │   │   ├── user.py               # 用户模型
│   │   │   ├── project.py            # 项目模型
│   │   │   ├── server.py             # 服务器模型
│   │   │   ├── mail.py               # 邮箱模型
│   │   │   └── rbac_v2.py            # RBAC v2模型
│   │   ├── schemas/                  # Pydantic模型（请求/响应）
│   │   │   ├── base.py               # 基础Schema
│   │   │   ├── user/                 # 用户Schema
│   │   │   ├── project/              # 项目Schema
│   │   │   ├── server/               # 服务器Schema
│   │   │   └── mail/                 # 邮箱Schema
│   │   ├── utils/                    # 工具类
│   │   │   ├── jwt_tool.py           # JWT工具
│   │   │   ├── time_tool.py          # 时间处理
│   │   │   ├── logs.py               # 日志工具
│   │   │   ├── redis_queue.py        # Redis队列基类
│   │   │   ├── project_account_queue.py  # 项目账号队列
│   │   │   ├── data_permission.py    # 数据权限过滤
│   │   │   ├── decorators.py         # 自定义装饰器
│   │   │   ├── exceptions.py         # 自定义异常
│   │   │   ├── log_middleware.py     # 日志中间件
│   │   │   └── operation_log.py      # 操作日志
│   │   ├── clients/                  # 外部客户端
│   │   │   └── outlook.py            # Outlook客户端
│   │   ├── logs/                     # 日志配置
│   │   │   ├── README.md             # 日志系统说明
│   │   │   └── USAGE.md              # 使用指南
│   │   └── main.py                   # 应用入口
│   ├── db/                           # 数据库脚本
│   │   ├── init_roles_and_admin.py   # 初始化角色和管理员
│   │   ├── init_routes.py            # 初始化路由权限
│   │   ├── init_rbac_v2.py           # 初始化RBAC v2
│   │   └── README.md                 # 数据库初始化说明
│   ├── migrations/                   # 数据库迁移
│   ├── logs/                         # 日志文件目录
│   │   ├── api.log                   # API请求日志
│   │   ├── app.log                   # 应用日志
│   │   ├── database.log              # 数据库日志
│   │   └── scheduler.log             # 定时任务日志
│   ├── scripts/                      # 工具脚本
│   │   ├── add_jwt_to_apis.py        # 批量添加JWT认证
│   │   ├── analyze_logs.py           # 日志分析
│   │   ├── cleanup_logs.py           # 清理日志
│   │   └── verify_setup.py           # 验证配置
│   ├── tests/                        # 测试文件
│   │   ├── test_jwt.py               # JWT测试
│   │   ├── test_user.py              # 用户测试
│   │   ├── test_project.py           # 项目测试
│   │   └── test_server.py            # 服务器测试
│   ├── .env.example                  # 环境变量示例
│   ├── .env.high_performance         # 高性能配置模板
│   ├── .env.ultra_high_performance   # 超高性能配置模板
│   ├── requirements.txt              # Python依赖
│   ├── start.py                      # HTTP服务启动脚本
│   ├── start_queue_worker.py         # 队列处理启动脚本
│   ├── test_queue_performance.py     # 队列性能测试
│   ├── test_ultra_performance.py     # 超高性能测试
│   └── README.md                     # 后端说明文档
├── frontend/                         # 前端应用
│   ├── src/                          # 源代码
│   │   ├── api/                      # API接口封装
│   │   │   ├── index.ts              # Axios配置和拦截器
│   │   │   ├── user.ts               # 用户API
│   │   │   ├── project.ts            # 项目API
│   │   │   ├── server.ts             # 服务器API
│   │   │   ├── mail.ts               # 邮箱API
│   │   │   └── rbac.ts               # RBAC API
│   │   ├── components/               # 公共组件
│   │   │   ├── Layout/               # 布局组件
│   │   │   ├── ProtectedRoute/       # 路由守卫
│   │   │   ├── Permission/           # 权限组件
│   │   │   └── ApiTester/            # API测试工具
│   │   ├── views/                    # 页面组件
│   │   │   ├── Login/                # 登录页
│   │   │   ├── Dashboard/            # 仪表盘
│   │   │   ├── User/                 # 用户管理
│   │   │   │   ├── UserList/         # 用户列表
│   │   │   │   ├── RoleManage/       # 角色管理
│   │   │   │   ├── RouteManage/      # 路由管理
│   │   │   │   └── OperationLog/     # 操作日志
│   │   │   ├── Project/              # 项目管理
│   │   │   │   ├── ProjectList/      # 项目列表
│   │   │   │   ├── ProjectAccount/   # 项目账号
│   │   │   │   └── ProjectWallet/    # 项目钱包
│   │   │   ├── Server/               # 服务器管理
│   │   │   │   ├── ServerList/       # 服务器列表
│   │   │   │   ├── CountryManage/    # 国家管理
│   │   │   │   ├── GroupManage/      # 分组管理
│   │   │   │   └── ServerAccount/    # 服务器账号
│   │   │   ├── Mail/                 # 邮箱管理
│   │   │   │   ├── MailList/         # 邮箱列表
│   │   │   │   └── MailViewer/       # 邮件查看器
│   │   │   └── ApiDocs/              # API文档
│   │   ├── store/                    # 状态管理
│   │   │   └── useUserStore.ts       # 用户状态
│   │   ├── hooks/                    # 自定义Hooks
│   │   │   └── usePermission.ts      # 权限Hook
│   │   ├── utils/                    # 工具函数
│   │   │   ├── token.ts              # Token管理
│   │   │   ├── format.ts             # 格式化工具
│   │   │   └── constants.ts          # 常量定义
│   │   ├── types/                    # TypeScript类型
│   │   │   └── index.ts              # 类型定义
│   │   ├── router/                   # 路由配置
│   │   │   └── index.tsx             # 路由定义
│   │   ├── App.tsx                   # 应用入口
│   │   ├── main.tsx                  # 主入口
│   │   └── index.css                 # 全局样式
│   ├── tests/                        # 测试文件
│   ├── public/                       # 静态资源
│   ├── .env.development              # 开发环境配置
│   ├── .env.production               # 生产环境配置
│   ├── vite.config.ts                # Vite配置
│   ├── tsconfig.json                 # TypeScript配置
│   ├── package.json                  # 依赖配置
│   └── README.md                     # 前端说明文档
├── docs/                             # 项目文档
│   ├── performance/                  # 性能优化文档
│   │   ├── QUEUE_SEPARATION_QUICK_START.md
│   │   ├── REDIS_QUEUE_SEPARATION_GUIDE.md
│   │   ├── SCALE_TO_10K_GUIDE.md
│   │   ├── PERFORMANCE_QUICK_REFERENCE.md
│   │   └── ...
│   ├── guides/                       # 使用指南
│   │   ├── REDIS_QUEUE_GUIDE.md
│   │   ├── RBAC_README.md
│   │   ├── PERMISSION_QUICK_START.md
│   │   └── ...
│   ├── summaries/                    # 功能总结
│   ├── api/                          # API文档
│   ├── features/                     # 功能文档
│   ├── fixes/                        # 修复记录
│   ├── rbac/                         # RBAC设计文档
│   └── INDEX.md                      # 文档索引
├── scripts/                          # 项目级脚本
│   ├── mysql/                        # MySQL相关脚本
│   │   ├── check_mysql_status.sh
│   │   ├── deploy_mysql_single_server.sh
│   │   └── ...
│   ├── test/                         # 测试脚本
│   │   ├── test_api_endpoints.sh
│   │   ├── test_permission_apis.sh
│   │   └── ...
│   ├── debug/                        # 调试脚本
│   │   ├── check_api_auth.py
│   │   ├── debug_account.py
│   │   └── ...
│   └── utils/                        # 工具脚本
│       ├── add_auth_to_apis.py
│       ├── frontend_restart.sh
│       └── ...
├── .kiro/                            # Kiro配置
│   └── steering/                     # 开发规范
│       ├── conventions.md            # 开发规范
│       ├── structure.md              # 项目结构
│       ├── tech.md                   # 技术栈
│       └── product.md                # 产品说明
├── logs/                             # 项目级日志
├── README.md                         # 项目说明文档
└── PROJECT_STRUCTURE.md              # 本文档
```

## 📝 文件说明

### 后端核心文件

| 文件 | 说明 |
|------|------|
| `backend/app/main.py` | FastAPI应用入口，配置中间件、路由、生命周期 |
| `backend/app/apis/deps.py` | 依赖注入，提供JWT认证、权限检查等 |
| `backend/app/core/settings.py` | 配置管理，数据库、Redis、JWT等配置 |
| `backend/app/core/database.py` | 数据库配置，支持读写分离 |
| `backend/start.py` | HTTP服务启动脚本 |
| `backend/start_queue_worker.py` | 队列处理启动脚本（独立进程） |

### 前端核心文件

| 文件 | 说明 |
|------|------|
| `frontend/src/main.tsx` | React应用入口 |
| `frontend/src/App.tsx` | 应用根组件，配置路由 |
| `frontend/src/api/index.ts` | Axios配置，请求/响应拦截器 |
| `frontend/src/store/useUserStore.ts` | 用户状态管理（Zustand） |
| `frontend/src/router/index.tsx` | 路由配置 |

### 配置文件

| 文件 | 说明 |
|------|------|
| `backend/.env.example` | 环境变量示例 |
| `backend/.env.high_performance` | 高性能配置（2700条/秒） |
| `backend/.env.ultra_high_performance` | 超高性能配置（12000条/秒） |
| `frontend/.env.development` | 前端开发环境配置 |
| `frontend/.env.production` | 前端生产环境配置 |

### 文档文件

| 文件 | 说明 |
|------|------|
| `README.md` | 项目总览和快速开始 |
| `backend/README.md` | 后端开发指南 |
| `frontend/README.md` | 前端开发指南 |
| `docs/INDEX.md` | 文档索引 |
| `PROJECT_STRUCTURE.md` | 项目结构说明（本文档） |

## 🔍 按功能查找文件

### 用户管理

**后端**：
- API: `backend/app/apis/v1/user/`
- CRUD: `backend/app/crud/user/`
- Model: `backend/app/models/user.py`
- Schema: `backend/app/schemas/user/`

**前端**：
- 页面: `frontend/src/views/User/`
- API: `frontend/src/api/user.ts`

### 项目管理

**后端**：
- API: `backend/app/apis/v1/project/`
- CRUD: `backend/app/crud/project/`
- Model: `backend/app/models/project.py`
- Schema: `backend/app/schemas/project/`

**前端**：
- 页面: `frontend/src/views/Project/`
- API: `frontend/src/api/project.ts`

### RBAC权限

**后端**：
- API: `backend/app/apis/v1/rbac/`
- Model: `backend/app/models/rbac_v2.py`
- 工具: `backend/app/utils/rbac_v2.py`
- 数据权限: `backend/app/utils/data_permission.py`

**前端**：
- API: `frontend/src/api/rbac.ts`
- 组件: `frontend/src/components/Permission/`
- Hook: `frontend/src/hooks/usePermission.ts`

### Redis队列

**后端**：
- 基类: `backend/app/utils/redis_queue.py`
- 项目账号队列: `backend/app/utils/project_account_queue.py`
- 启动脚本: `backend/start_queue_worker.py`

**文档**：
- 使用指南: `docs/guides/REDIS_QUEUE_GUIDE.md`
- 性能分析: `docs/performance/REDIS_QUEUE_PERFORMANCE_ANALYSIS.md`

### 日志系统

**后端**：
- 工具: `backend/app/utils/logs.py`
- 中间件: `backend/app/utils/log_middleware.py`
- 操作日志: `backend/app/utils/operation_log.py`
- 配置: `backend/app/logs/`

**日志文件**：
- API日志: `backend/logs/api.log`
- 应用日志: `backend/logs/app.log`
- 数据库日志: `backend/logs/database.log`
- 定时任务日志: `backend/logs/scheduler.log`

## 🎯 开发流程

### 添加新功能

1. **后端**：
   - 在 `backend/app/models/` 创建数据库模型
   - 在 `backend/app/schemas/` 创建Pydantic模型
   - 在 `backend/app/crud/` 创建CRUD操作
   - 在 `backend/app/apis/v1/` 创建API路由
   - 添加JWT认证依赖

2. **前端**：
   - 在 `frontend/src/api/` 添加API接口
   - 在 `frontend/src/views/` 创建页面组件
   - 在 `frontend/src/router/` 配置路由
   - 使用 `<ProtectedRoute>` 包裹需要认证的页面

3. **文档**：
   - 在 `docs/features/` 添加功能文档
   - 更新 `docs/INDEX.md`

### 修复Bug

1. 在 `docs/fixes/` 创建修复文档
2. 记录问题、原因、解决方案
3. 更新相关代码
4. 添加测试用例

### 性能优化

1. 在 `docs/performance/` 创建优化文档
2. 记录优化前后的性能数据
3. 提供配置示例和使用指南

## 📊 代码统计

### 后端

- **Python文件**: 100+
- **API端点**: 80+
- **数据库模型**: 15+
- **工具类**: 20+

### 前端

- **TypeScript文件**: 80+
- **页面组件**: 30+
- **公共组件**: 15+
- **API接口**: 60+

### 文档

- **Markdown文件**: 80+
- **分类**: 7个
- **总字数**: 50万+

## 🔗 相关链接

- [项目README](README.md)
- [文档索引](docs/INDEX.md)
- [后端README](backend/README.md)
- [前端README](frontend/README.md)

---

**最后更新**: 2026-01-23  
**版本**: v1.0.0

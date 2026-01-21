# QYD 项目结构说明

## 整体结构

```
qyd_api2/
├── backend/              # 后端服务
│   ├── app/             # 应用代码
│   ├── db/              # 数据库脚本
│   ├── migrations/      # 数据库迁移
│   ├── logs/            # 日志文件
│   ├── scripts/         # 工具脚本
│   ├── tests/           # 测试和工具文件
│   ├── .env.example     # 环境变量示例
│   ├── requirements.txt # Python依赖
│   ├── start.py         # 启动脚本
│   └── README.md        # 后端文档
│
├── frontend/            # 前端应用
│   ├── src/            # 源代码
│   ├── public/         # 静态资源
│   ├── tests/          # 测试文件
│   ├── .env.development # 开发环境配置
│   ├── .env.production  # 生产环境配置
│   ├── package.json    # 依赖配置
│   └── README.md       # 前端文档
│
├── docs/               # 项目文档
│   ├── fixes/         # 修复记录
│   ├── README.md      # 文档索引
│   └── PROJECT_STRUCTURE.md  # 本文档
│
└── README.md          # 项目主文档
```

## 后端结构详解

### app/ - 应用核心

```
app/
├── apis/              # API路由层
│   ├── deps.py       # 依赖注入（JWT认证）
│   └── v1/           # API v1版本
│       ├── user/     # 用户模块
│       │   ├── auth.py      # 认证接口
│       │   ├── user.py      # 用户CRUD
│       │   ├── role.py      # 角色管理
│       │   ├── route.py     # 路由管理
│       │   ├── token.py     # Token管理
│       │   ├── log.py       # 日志管理
│       │   └── user_role.py # 用户角色关联
│       ├── project/  # 项目模块
│       │   ├── info.py      # 项目信息
│       │   ├── account.py   # 项目账号
│       │   ├── wallet.py    # 项目钱包
│       │   └── balance.py   # 项目余额
│       ├── server/   # 服务器模块
│       │   ├── info.py      # 服务器信息
│       │   ├── country.py   # 国家管理
│       │   ├── group.py     # 分组管理
│       │   └── account.py   # 服务器账号
│       └── mail/     # 邮箱模块
│           ├── info.py      # 邮箱信息
│           └── outlook.py   # Outlook集成
│
├── core/             # 核心配置
│   ├── settings.py   # 配置管理（数据库、JWT等）
│   ├── tools.py      # 工具函数（密码加密等）
│   └── verify.py     # 验证函数
│
├── crud/             # 数据库操作层
│   ├── user/        # 用户相关CRUD
│   ├── project/     # 项目相关CRUD
│   ├── server/      # 服务器相关CRUD
│   └── mail/        # 邮箱相关CRUD
│
├── models/          # 数据库模型
│   ├── base.py      # 基础模型
│   ├── user.py      # 用户模型
│   ├── project.py   # 项目模型
│   ├── server.py    # 服务器模型
│   └── mail.py      # 邮箱模型
│
├── schemas/         # Pydantic模型（请求/响应）
│   ├── base.py      # 基础Schema
│   ├── user/        # 用户Schema
│   ├── project/     # 项目Schema
│   ├── server/      # 服务器Schema
│   └── mail/        # 邮箱Schema
│
├── utils/           # 工具类
│   ├── jwt_tool.py  # JWT工具
│   ├── time_tool.py # 时间处理
│   ├── logs.py      # 日志工具
│   ├── decorators.py # 装饰器
│   ├── exceptions.py # 异常定义
│   └── ...
│
├── clients/         # 外部客户端
│   └── outlook.py   # Outlook客户端
│
├── logs/            # 日志配置
│   ├── README.md    # 日志说明
│   └── USAGE.md     # 使用指南
│
└── main.py          # 应用入口
```

### db/ - 数据库脚本

```
db/
├── init_roles_and_admin.py  # 初始化角色和管理员
├── init_roles_and_admin.sql # SQL版本
├── README.md                # 说明文档
└── INITIALIZATION_SUMMARY.md # 初始化总结
```

### tests/ - 测试文件

```
tests/
├── test_*.py              # 功能测试脚本
├── check_*.py             # 检查工具
├── fix_*.py               # 修复工具
└── *.sh                   # Shell脚本
```

## 前端结构详解

### src/ - 源代码

```
src/
├── api/              # API接口封装
│   ├── index.ts     # Axios配置和拦截器
│   ├── user.ts      # 用户API
│   ├── project.ts   # 项目API
│   ├── server.ts    # 服务器API
│   └── mail.ts      # 邮箱API
│
├── components/      # 公共组件
│   ├── Layout/      # 布局组件
│   │   └── index.tsx
│   ├── ProtectedRoute/  # 路由守卫
│   │   └── index.tsx
│   ├── ApiTester/   # API测试工具
│   │   └── index.tsx
│   ├── PageContainer/   # 页面容器
│   └── SearchForm/      # 搜索表单
│
├── views/           # 页面组件
│   ├── Login/       # 登录页
│   │   ├── index.tsx
│   │   └── index.less
│   ├── Dashboard/   # 仪表盘
│   │   └── index.tsx
│   ├── User/        # 用户管理
│   │   ├── UserList.tsx
│   │   ├── RoleList.tsx
│   │   ├── RouteList.tsx
│   │   ├── TokenList.tsx
│   │   └── LogList.tsx
│   ├── Project/     # 项目管理
│   │   ├── ProjectList.tsx
│   │   ├── ProjectAccount.tsx
│   │   ├── ProjectWallet.tsx
│   │   └── ProjectBalance.tsx
│   ├── Server/      # 服务器管理
│   │   ├── ServerList.tsx
│   │   ├── ServerAccount.tsx
│   │   ├── CountryList.tsx
│   │   └── GroupList.tsx
│   ├── Mail/        # 邮箱管理
│   │   └── MailList.tsx
│   └── ApiDocs/     # API文档
│       ├── UserApi.tsx
│       ├── UserCreate.tsx
│       ├── RoleApi.tsx
│       ├── ProjectApi.tsx
│       ├── ProjectAccountApi.tsx
│       ├── ServerApi.tsx
│       └── MailApi.tsx
│
├── store/           # 状态管理
│   └── useUserStore.ts  # 用户状态
│
├── utils/           # 工具函数
│   ├── token.ts     # Token管理
│   ├── format.ts    # 格式化工具
│   └── constants.ts # 常量定义
│
├── types/           # TypeScript类型
│   └── index.ts     # 类型定义
│
├── router/          # 路由配置
│   └── index.tsx
│
├── styles/          # 全局样式
│
├── App.tsx          # 应用入口
├── main.tsx         # 主入口
└── vite-env.d.ts    # Vite类型定义
```

### tests/ - 测试文件

```
tests/
├── *.html           # HTML测试页面
├── *.sh             # Shell脚本
├── *.js             # JavaScript工具
└── *.bat            # Windows批处理
```

## 文档结构

### docs/ - 项目文档

```
docs/
├── fixes/           # 修复记录（按时间顺序）
│   ├── JWT_AUTH_FIX.md
│   ├── SECURITY_FIX_PASSWORD_ENCRYPTION.md
│   ├── FRONTEND_COMPLETION_SUMMARY.md
│   ├── API_DOCS_MENU_SUMMARY.md
│   └── ...
│
├── README.md        # 文档索引
└── PROJECT_STRUCTURE.md  # 本文档
```

## 配置文件说明

### 后端配置

- `.env` - 环境变量（数据库、JWT等）
- `requirements.txt` - Python依赖
- `pyproject.toml` - 项目配置
- `pytest.ini` - 测试配置
- `compose.yml` - Docker配置

### 前端配置

- `.env.development` - 开发环境变量
- `.env.production` - 生产环境变量
- `package.json` - 依赖和脚本
- `vite.config.ts` - Vite配置
- `tsconfig.json` - TypeScript配置
- `eslint.config.js` - ESLint配置

## 数据流

### 请求流程

```
前端 → Axios拦截器 → 添加Token → 后端API
                                    ↓
                              JWT验证 (deps.py)
                                    ↓
                              API路由 (apis/)
                                    ↓
                              CRUD操作 (crud/)
                                    ↓
                              数据库模型 (models/)
                                    ↓
                              返回响应 (schemas/)
```

### 认证流程

```
1. 用户登录 → auth.py
2. 验证密码 → bcrypt
3. 生成JWT → jwt_tool.py
4. 返回Token → 前端
5. 存储Token → localStorage
6. 后续请求 → 自动添加Token
7. 验证Token → get_current_user (deps.py)
```

## 日志系统

### 日志分类

- `logs/app.log` - 应用日志
- `logs/api.log` - API请求日志
- `logs/database.log` - 数据库日志
- `logs/scheduler.log` - 定时任务日志

### 日志轮转

- 按小时轮转
- 自动压缩旧日志
- 保留最近7天

## 测试文件分类

### 后端测试

- `test_*.py` - 功能测试
- `check_*.py` - 检查工具
- `fix_*.py` - 修复工具
- `*.sh` - Shell脚本

### 前端测试

- `test-*.html` - HTML测试页面
- `*.sh` - Shell脚本
- `*.js` - JavaScript工具

## 开发工作流

1. **后端开发**: 修改 `app/` → 测试 → 提交
2. **前端开发**: 修改 `src/` → 测试 → 构建 → 提交
3. **文档更新**: 修改后在 `docs/fixes/` 添加记录
4. **测试**: 将测试文件放入 `tests/` 目录

## 部署结构

### 开发环境

```
localhost:3000 (前端) → localhost:6080 (后端) → MySQL
```

### 生产环境

```
Nginx (前端静态文件) → FastAPI (后端API) → MySQL
                                          → Redis (可选)
```

## 相关文档

- [主README](../README.md)
- [后端README](../backend/README.md)
- [前端README](../frontend/README.md)
- [文档索引](README.md)

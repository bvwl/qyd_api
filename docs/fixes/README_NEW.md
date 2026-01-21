# QYD API 后端服务

基于 **FastAPI + Tortoise ORM** 的后端 API 服务，提供用户管理、项目管理、服务器管理和邮箱管理功能。

**运行环境**: Python 3.11+  
**数据库**: MySQL 5.7+

---

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

关键配置项：
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` - 数据库连接
- `JWT_SECRET_KEY` - JWT 密钥（生产环境必须修改）
- `APP_HOST`, `APP_PORT` - 服务监听地址

### 3. 初始化数据库

```bash
# 初始化数据库表结构
./scripts/init_db.sh

# 初始化角色和管理员账户
python db/init_roles_and_admin.py
```

默认管理员账户：
- 邮箱：`zhiyu`
- 密码：`2201101122@qq.com`

### 4. 启动服务

```bash
python start.py
```

服务启动后访问：
- API 文档：http://127.0.0.1:6080/docs
- ReDoc 文档：http://127.0.0.1:6080/redoc

---

## 认证方式

系统支持两种认证方式：

### 1. JWT Token 认证（推荐）

**获取 Token**：
```bash
curl -X POST "http://127.0.0.1:6080/v1/user/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "zhiyu", "password": "2201101122@qq.com"}'
```

**使用 Token**：
```bash
curl -X GET "http://127.0.0.1:6080/v1/user/user" \
  -H "Authorization: Bearer <access_token>"
```

### 2. API Token 认证

**创建 API Token**：
1. 登录系统
2. 访问"用户管理 > Token 管理"
3. 创建新的 API Token

**使用 API Token**：
```bash
curl -X GET "http://127.0.0.1:6080/v1/user/user" \
  -H "API-TOKEN: <your_api_token>"
```

**注意**：
- 除了登录和注册接口，所有 API 都需要认证
- JWT Token 有过期时间，API Token 长期有效
- API Token 适合服务间调用，JWT Token 适合用户登录

---

## 目录结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── core/                # 核心配置
│   │   ├── settings.py      # 数据库配置
│   │   ├── tools.py         # 工具函数（密码加密等）
│   │   └── verify.py        # 验证函数
│   ├── models/              # 数据库模型
│   │   ├── base.py          # 基础模型
│   │   ├── user.py          # 用户模块模型
│   │   ├── project.py       # 项目模块模型
│   │   ├── server.py        # 服务器模块模型
│   │   └── mail.py          # 邮箱模块模型
│   ├── schemas/             # API 请求/响应模型
│   ├── crud/                # 数据库操作封装
│   ├── apis/                # API 路由
│   │   ├── deps.py          # 认证依赖
│   │   └── v1/              # API v1 版本
│   │       ├── user/        # 用户管理 API
│   │       ├── project/     # 项目管理 API
│   │       ├── server/      # 服务器管理 API
│   │       └── mail/        # 邮箱管理 API
│   ├── utils/               # 工具函数
│   │   ├── jwt_tool.py      # JWT 工具
│   │   ├── time_tool.py     # 时间工具
│   │   └── logs.py          # 日志工具
│   └── tests/               # 测试文件
├── db/                      # 数据库脚本
│   ├── init_roles_and_admin.py  # 初始化脚本
│   └── README.md
├── scripts/                 # 辅助脚本
│   ├── init_db.sh           # 初始化数据库
│   └── update_db.sh         # 更新数据库
├── migrations/              # 数据库迁移文件
├── .env                     # 环境变量配置
├── .env.example             # 环境变量模板
├── requirements.txt         # Python 依赖
├── start.py                 # 启动脚本
└── README.md                # 本文档
```

---

## API 模块

### 用户管理 (/v1/user)
- **auth** - 用户认证（登录、注册）
- **user** - 用户管理（CRUD）
- **role** - 角色管理（CRUD）
- **route** - 路由管理（CRUD）
- **token** - API Token 管理（CRUD）
- **log** - 操作日志（CRUD）
- **user_role** - 用户角色关联管理

### 项目管理 (/v1/project)
- **info** - 项目信息（CRUD）
- **account** - 项目账号（CRUD）
- **wallet** - 项目钱包（CRUD）
- **balance** - 项目余额（CRUD）

### 服务器管理 (/v1/server)
- **country** - 国家信息（CRUD）
- **group** - 分组信息（CRUD）
- **info** - 服务器信息（CRUD）
- **account** - 服务器账号（CRUD）

### 邮箱管理 (/v1/mail)
- **info** - 邮箱信息（CRUD）
- **outlook** - Outlook 操作（授权、发送、接收）

---

## 数据模型

### 用户模块
- `UserInfo` - 用户信息
- `UserRole` - 角色信息
- `FrontendRoute` - 前端路由/菜单
- `UserToken` - API Token
- `UserLog` - 操作日志

### 项目模块
- `ProjectInfo` - 项目信息
- `ProjectAccount` - 项目账号
- `ProjectWallet` - 项目钱包
- `ProjectBalance` - 项目余额

### 服务器模块
- `ServerCountry` - 国家信息
- `ServerGroup` - 分组信息
- `ServerInfo` - 服务器信息
- `ServerAccount` - 服务器账号

### 邮箱模块
- `EmailInfo` - 邮箱信息

---

## 权限系统

基于角色的访问控制（RBAC）：

### 默认角色
- **ADMIN** - 管理员（所有权限）
- **GM** - 项目管理员（项目和服务器管理）
- **IT** - IT 人员（服务器管理）
- **MANUAL** - 普通用户（基础权限）

### 权限验证

在 API 中使用不同的依赖函数：

```python
from app.apis.deps import get_current_user, get_admin_user, get_gm_user

# 基础认证（所有登录用户）
@app.get("")
async def gets(current_user: dict = Depends(get_current_user)):
    pass

# 管理员权限
@app.delete("/{id}")
async def delete(id: UUID, current_user: dict = Depends(get_admin_user)):
    pass

# GM 权限（ADMIN 或 GM）
@app.put("/{id}")
async def put(id: UUID, current_user: dict = Depends(get_gm_user)):
    pass
```

---

## 数据库迁移

使用 **aerich** 管理数据库迁移：

### 初始化
```bash
./scripts/init_db.sh
```

### 更新模型后迁移
```bash
./scripts/update_db.sh
```

### 手动迁移
```bash
# 生成迁移文件
aerich migrate

# 应用迁移
aerich upgrade

# 回滚迁移
aerich downgrade
```

---

## 环境变量说明

### 应用配置
- `APP_HOST` - 监听地址（默认：0.0.0.0）
- `APP_PORT` - 监听端口（默认：6080）
- `APP_DEBUG` - 调试模式（1/true/yes 启用热重载）
- `APP_WORKERS` - 工作进程数（默认：1）
- `LOG_LEVEL` - 日志级别（DEBUG/INFO/WARNING/ERROR）

### 数据库配置
- `DB_HOST` - 数据库主机
- `DB_PORT` - 数据库端口
- `DB_USER` - 数据库用户名
- `DB_PASSWORD` - 数据库密码
- `DB_NAME` - 数据库名称

### JWT 配置
- `JWT_SECRET_KEY` - JWT 密钥（必须修改）
- `JWT_ALGORITHM` - 加密算法（默认：HS256）
- `JWT_EXPIRE_MINUTES` - Token 过期时间（默认：1440 分钟）

### 功能开关
- `ENABLE_DOCS` - 启用 API 文档（0/1，生产环境建议关闭）
- `ENABLE_EMAIL_CHECK` - 启用邮箱状态检查定时任务（0/1）
- `CORS_ORIGINS` - CORS 允许的域名（逗号分隔）

### 定时任务配置
- `DB_CHECK_INTERVAL_MINUTES` - 数据库连接检查间隔（默认：30）
- `EMAIL_CHECK_INTERVAL_HOURS` - 邮箱状态检查间隔（默认：1）
- `SHUTDOWN_WAIT_SECONDS` - 关闭等待时间（默认：0.5）

---

## 开发指南

### 添加新的 API 模块

1. **创建模型** (`app/models/xxx.py`)
2. **创建 Schema** (`app/schemas/xxx/`)
3. **创建 CRUD** (`app/crud/xxx/`)
4. **创建 API** (`app/apis/v1/xxx/`)
5. **注册路由** (`app/apis/v1/__init__.py`)

### 代码规范

- 所有 API 端点必须添加认证（除登录/注册）
- 使用 `get_current_user` 进行基础认证
- 使用 `get_admin_user` 进行管理员权限验证
- 错误信息使用友好的中文提示
- 不要在错误信息中暴露技术细节

### 测试

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest app/tests/test_user.py

# 查看覆盖率
pytest --cov=app
```

---

## 常见问题

### 1. 数据库连接失败

检查 `.env` 中的数据库配置是否正确，确保 MySQL 服务正在运行。

### 2. JWT Token 过期

Token 默认 24 小时过期，可通过 `JWT_EXPIRE_MINUTES` 调整。

### 3. API 返回 401 Unauthorized

确保请求头中包含有效的认证信息（JWT Token 或 API Token）。

### 4. 端口被占用

修改 `.env` 中的 `APP_PORT` 或停止占用端口的进程。

### 5. 迁移失败

删除 `migrations/` 目录，重新运行 `./scripts/init_db.sh`。

---

## 生产环境部署

### 1. 安全配置

```env
# 生产环境配置
APP_DEBUG=0
ENABLE_DOCS=0
JWT_SECRET_KEY=<生成一个强密码>
CORS_ORIGINS=https://yourdomain.com
```

### 2. 使用 Gunicorn

```bash
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:6080
```

### 3. 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:6080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. 使用 Supervisor 管理进程

```ini
[program:qyd-api]
command=/path/to/venv/bin/gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:6080
directory=/path/to/backend
user=www-data
autostart=true
autorestart=true
```

---

## 更新日志

### 2026-01-21
- ✅ 添加 JWT 和 API Token 双重认证支持
- ✅ 统一错误处理，使用友好的错误信息
- ✅ 为所有 API 添加认证保护
- ✅ 优化数据库查询性能
- ✅ 完善文档和示例

### 2026-01-20
- ✅ 修复 Pydantic 循环引用问题
- ✅ 优化关联数据加载
- ✅ 完善 CRUD 层实现
- ✅ 添加数据库索引优化

---

## 技术栈

- **FastAPI** - 现代化的 Python Web 框架
- **Tortoise ORM** - 异步 ORM
- **MySQL** - 关系型数据库
- **JWT** - JSON Web Token 认证
- **bcrypt** - 密码加密
- **APScheduler** - 定时任务
- **uvicorn** - ASGI 服务器

---

## 许可证

MIT License

---

## 联系方式

如有问题或建议，请联系项目维护者。

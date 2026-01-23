# QYD 后端服务

基于 FastAPI 的高性能异步后端服务，提供完整的RESTful API。支持每秒处理2000-15000条数据，具备企业级特性。

## 技术栈

- **框架**: FastAPI (异步Web框架)
- **ORM**: Tortoise ORM (异步ORM)
- **数据库**: MySQL 8.0 (支持主从读写分离)
- **缓存/队列**: Redis 7.0
- **认证**: JWT (python-jose)
- **密码加密**: bcrypt
- **数据验证**: Pydantic
- **任务调度**: APScheduler
- **日志**: 自定义日志系统 (按模块分类、自动轮转压缩)
- **邮件集成**: Outlook API
- **API文档**: Swagger UI / ReDoc (自动生成)

## 项目结构

```
backend/
├── app/
│   ├── apis/              # API路由
│   │   ├── deps.py        # 依赖注入 (JWT认证)
│   │   └── v1/            # API v1版本
│   │       ├── user/      # 用户相关API
│   │       ├── project/   # 项目相关API
│   │       ├── server/    # 服务器相关API
│   │       └── mail/      # 邮箱相关API
│   ├── core/              # 核心配置
│   │   ├── settings.py    # 配置管理
│   │   ├── database.py    # 数据库配置 (支持读写分离)
│   │   ├── rd.py          # Redis配置
│   │   ├── tools.py       # 工具函数 (密码加密等)
│   │   └── verify.py      # 验证函数
│   ├── crud/              # 数据库操作层
│   ├── models/            # 数据库模型
│   ├── schemas/           # Pydantic模型 (请求/响应)
│   ├── utils/             # 工具类
│   │   ├── jwt_tool.py    # JWT工具
│   │   ├── time_tool.py   # 时间处理
│   │   ├── logs.py        # 日志工具
│   │   ├── redis_queue.py # Redis队列基类
│   │   └── project_account_queue.py  # 项目账号队列
│   ├── clients/           # 外部客户端 (Outlook等)
│   ├── logs/              # 日志配置
│   └── main.py            # 应用入口
├── db/                    # 数据库脚本
│   ├── init_roles_and_admin.py  # 初始化角色和管理员
│   ├── init_routes.py     # 初始化路由权限
│   └── README.md
├── migrations/            # 数据库迁移
├── logs/                  # 日志文件目录
├── tests/                 # 测试文件
├── scripts/               # 工具脚本
├── .env.example           # 环境变量示例
├── requirements.txt       # Python依赖
├── start.py              # 启动脚本
└── README.md             # 本文档
```

## 安装

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下内容：

```env
# 数据库配置 (主库)
DB_HOST=127.0.0.1
DB_PORT=3307
DB_USER=qyd
DB_PASSWORD=your_password_here
DB_NAME=qyd

# 从库配置 (可选，用于读写分离)
DB_SLAVE_HOSTS=127.0.0.1:3308,127.0.0.1:3309

# Redis配置 (可选，用于队列处理)
REDIS_HOST=127.0.0.1
REDIS_PORT=6378
REDIS_PASSWORD=redis_fNmAxZ
REDIS_DB=0

# Redis队列配置
REDIS_QUEUE_BATCH_SIZE=100        # 批量处理大小
REDIS_QUEUE_NUM_WORKERS=4         # 工作线程数
REDIS_QUEUE_CACHE_EXPIRE=3600     # 缓存过期时间(秒)

# JWT配置
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_DAYS=365

# 服务配置
HOST=0.0.0.0
PORT=6080
DEBUG=False
WORKERS=1

# CORS配置
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# 日志配置
LOG_LEVEL=INFO
```

### 3. 初始化数据库

```bash
# 创建数据库表
python -m aerich init -t app.core.settings.TORTOISE_ORM
python -m aerich init-db

# 初始化角色和管理员账号
python db/init_roles_and_admin.py
```

这将创建：
- 4个角色: ADMIN, GM, IT, MANUAL
- 1个管理员账号: zhiyu / 2201101122@qq.com

## 启动服务

### 开发模式（单进程）

```bash
python start.py
```

服务将在 `http://localhost:6080` 启动

配置 `.env`：
```bash
APP_WORKERS=1
ENABLE_QUEUE_WORKERS=1    # 开发环境可以启用队列处理
```

### 生产模式（分离队列处理）

#### 标准性能（2000条/秒）

```bash
# 配置环境
cp .env.high_performance .env

# 终端1：启动HTTP服务
python start.py

# 终端2：启动队列处理
python start_queue_worker.py
```

#### 超高性能（10000+条/秒）

```bash
# 配置环境
cp .env.ultra_high_performance .env

# 终端1：启动HTTP服务
python start.py

# 终端2-4：启动3个队列进程
python start_queue_worker.py &
python start_queue_worker.py &
python start_queue_worker.py &
```

#### 使用Supervisor管理（推荐）

```bash
# 安装Supervisor
sudo apt-get install supervisor

# 配置文件示例见：
# ../docs/performance/REDIS_QUEUE_SEPARATION_GUIDE.md

# 启动服务
sudo supervisorctl start qyd:*
```

### 使用Docker

```bash
docker-compose up -d
```

## API文档

启动服务后访问：

- **Swagger UI**: http://localhost:6080/docs
- **ReDoc**: http://localhost:6080/redoc

## 性能配置

系统支持多种性能配置：

### 配置文件

| 文件 | 性能 | 适用场景 |
|------|------|---------|
| `.env.example` | 基础 | 开发环境 |
| `.env.high_performance` | 2700条/秒 | 生产环境（标准） |
| `.env.ultra_high_performance` | 12000条/秒 | 生产环境（高负载） |

### 性能测试

```bash
# 标准测试（10000条数据）
python test_queue_performance.py

# 超高性能测试（50000条数据）
python test_ultra_performance.py

# 清理测试数据
python test_ultra_performance.py --cleanup
```

### 性能监控

```bash
# 监控队列大小
redis-cli ZCARD qyd:project_account_keys_zset

# 监控数据库连接
mysql -e "SHOW PROCESSLIST;" | wc -l

# 监控Redis连接
redis-cli INFO clients | grep connected_clients
```

详细的性能优化指南请参考：
- [队列分离快速开始](../docs/performance/QUEUE_SEPARATION_QUICK_START.md)
- [扩展到10000+条/秒](../docs/performance/SCALE_TO_10K_GUIDE.md)
- [性能快速参考](../docs/performance/PERFORMANCE_QUICK_REFERENCE.md)

## 核心功能

### 1. JWT认证

所有API（除了登录/注册）都需要JWT认证：

```python
# 在请求头中添加
Authorization: Bearer <your_jwt_token>
```

JWT Token包含：
- 用户ID
- 邮箱
- 角色列表
- 过期时间

### 2. 角色权限

系统支持4种角色：

- **ADMIN**: 管理员，拥有所有权限
- **GM**: 项目管理员
- **IT**: 技术人员
- **MANUAL**: 手动操作员（默认角色）

### 3. 密码加密

使用 bcrypt 加密密码：

```python
from app.core.tools import hashing

# 加密
hashed = hashing.hash("password")

# 验证
is_valid = hashing.verify("password", hashed)
```

### 4. 日志系统

日志按模块分类：

- `logs/app.log` - 应用日志
- `logs/api.log` - API请求日志
- `logs/database.log` - 数据库日志
- `logs/scheduler.log` - 定时任务日志

日志自动按小时轮转和压缩。

### 5. 异常处理

统一的异常处理顺序：

```python
try:
    # 业务逻辑
    pass
except HTTPException:  # 先捕获HTTPException
    raise
except ValueError as e:  # 参数错误 -> 400
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:  # 其他错误 -> 500
    raise HTTPException(status_code=500, detail=str(e))
```

### 6. 时间处理

支持多种时间格式：

- `YYYY-MM-DD`
- `YYYY-MM-DD HH:mm:ss`
- 13位时间戳

```python
from app.utils.time_tool import parse_time

# 自动解析
start_time = parse_time("2024-01-01")
end_time = parse_time("2024-12-31", is_end=True)  # 自动设置为23:59:59
```

### 7. Redis队列批量处理

支持大批量数据的异步处理：

```python
from app.utils.project_account_queue import project_account_queue

# 添加任务到队列
await project_account_queue.add_task({
    "project_id": "xxx",
    "account": "test",
    # ... 其他字段
})
```

特性：
- **智能缓存**: 先检查Redis缓存，已处理的数据跳过
- **读写分离**: 使用从库查询，主库更新/创建
- **批量处理**: 可配置批量大小和工作线程数
- **独立管道**: 缓存操作和任务清理使用独立管道
- **自动过期**: 缓存1小时自动过期

### 8. MySQL读写分离

系统支持一主多从架构：

- **主库**: 处理所有写操作 (INSERT, UPDATE, DELETE)
- **从库**: 处理所有读操作 (SELECT)
- **自动路由**: ORM自动根据操作类型选择数据库

配置方式：
```env
# 主库
DB_HOST=127.0.0.1
DB_PORT=3307

# 从库（多个用逗号分隔）
DB_SLAVE_HOSTS=127.0.0.1:3308,127.0.0.1:3309
```

在代码中使用：
```python
# 读操作（自动使用从库）
users = await User.all()

# 写操作（自动使用主库）
await User.create(email="test@example.com")

# 显式指定使用主库
users = await User.all().using_db(Tortoise.get_connection("default"))
```

## API规范

### 请求格式

```json
{
  "page": 1,
  "limit": 10,
  "res_count": true,
  "create_time_start": "2024-01-01",
  "create_time_end": "2024-12-31"
}
```

### 响应格式

成功响应：

```json
{
  "message": "成功",
  "count": 100,
  "num": 10,
  "items": [...]
}
```

错误响应：

```json
{
  "detail": "错误信息"
}
```

### HTTP状态码

- `200` - 成功
- `201` - 创建成功
- `400` - 参数错误
- `401` - 未认证
- `403` - 无权限
- `404` - 资源不存在或查询无数据
- `500` - 服务器错误

## 开发指南

### 添加新的API

1. 在 `app/models/` 创建数据库模型
2. 在 `app/schemas/` 创建Pydantic模型
3. 在 `app/crud/` 创建CRUD操作
4. 在 `app/apis/v1/` 创建API路由
5. 添加JWT认证依赖

示例：

```python
from fastapi import APIRouter, Depends
from app.apis.deps import get_current_user

router = APIRouter()

@router.get("/items")
async def get_items(
    current_user: dict = Depends(get_current_user)
):
    # 业务逻辑
    pass
```

### 数据库迁移

```bash
# 生成迁移文件
aerich migrate --name "description"

# 应用迁移
aerich upgrade
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_user.py

# 查看覆盖率
pytest --cov=app tests/
```

## 常见问题

### 1. 数据库连接失败

检查 `.env` 中的数据库配置是否正确，确保MySQL服务已启动。

### 2. JWT Token过期

默认Token有效期为365天，可在 `.env` 中修改 `JWT_ACCESS_TOKEN_EXPIRE_DAYS`。

### 3. CORS错误

在 `.env` 中添加前端地址到 `CORS_ORIGINS`。

### 4. 日志文件过大

日志自动按小时轮转，旧日志会被压缩。可以使用 `scripts/cleanup_logs.py` 清理旧日志。

## 性能优化

1. **数据库连接池**: Tortoise ORM自动管理
2. **异步处理**: 所有IO操作都是异步的
3. **查询优化**: 使用 `prefetch_related` 预加载关联数据
4. **日志轮转**: 防止日志文件过大
5. **定时任务**: 定期检查数据库连接

## 安全建议

1. ✅ 使用强密码作为 `JWT_SECRET_KEY`
2. ✅ 生产环境设置 `DEBUG=False`
3. ✅ 限制 `CORS_ORIGINS` 为特定域名
4. ✅ 定期更新依赖包
5. ✅ 使用HTTPS部署
6. ✅ 定期备份数据库

## 维护

### 日志管理

```bash
# 查看日志
tail -f logs/api.log

# 清理旧日志
python scripts/cleanup_logs.py
```

### 数据库备份

```bash
# 备份
mysqldump -u qyd -p qyd > backup.sql

# 恢复
mysql -u qyd -p qyd < backup.sql
```

## 相关链接

- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Tortoise ORM文档](https://tortoise.github.io/)
- [Pydantic文档](https://docs.pydantic.dev/)

## 更新日志

查看 `docs/fixes/` 目录了解详细的修复和更新记录。

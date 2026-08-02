# QYD 后端维护手册

QYD 后端是基于 FastAPI 的异步 API 服务，负责用户与权限、项目、服务器、邮箱、XUI、统计、导出和后台队列等业务。本项目已经上线；生产变更应经过备份、验证和可回滚发布，禁止直接在生产库试跑历史迁移或修复脚本。

## 技术栈

- Python 3.11
- FastAPI + Uvicorn
- Tortoise ORM + MySQL
- Redis（缓存与队列）
- APScheduler（进程内定时任务）
- JWT、bcrypt、AES
- Pytest

API 路由统一使用 `/v1` 前缀。服务启动后可访问 `/docs` 和 `/redoc`；生产是否开放由 `ENABLE_DOCS` 控制。

## 运行拓扑

生产环境由三个独立进程组成：

1. `python start.py`：FastAPI HTTP 服务。
2. `python start_queue_worker.py`：处理项目账号与项目提现 Redis 队列。
3. `python start_log_compressor.py`：独立压缩和清理日志。

API 服务还会启动 APScheduler，用于数据库连接保活，以及按配置执行邮箱状态检查和项目统计同步。

> 生产建议保持 `ENABLE_QUEUE_WORKERS=0`，由独立 Worker 消费队列。否则 API 内置 Worker 与独立 Worker 可能同时运行。

## 目录说明

```text
backend/
├── app/
│   ├── apis/          # FastAPI 路由与鉴权依赖
│   ├── clients/       # Outlook、钱包、XUI 等外部客户端
│   ├── core/          # 配置、数据库和通用校验
│   ├── crud/          # 数据访问层
│   ├── models/        # Tortoise ORM 模型
│   ├── schemas/       # 请求与响应模型
│   ├── utils/         # 队列、日志、加密、权限和统计工具
│   └── main.py        # FastAPI 应用入口
├── db/                # 历史 SQL/Python 数据库变更与初始化工具
├── migrations/        # Aerich 迁移
├── scripts/           # 运维与检查工具；执行前必须审阅
├── tests/             # 回归、集成和性能测试
├── Dockerfile
├── requirements.txt
├── start.py
├── start_queue_worker.py
└── start_log_compressor.py
```

## 本地开发

以下命令均在 `backend/` 目录执行。

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

编辑 `.env`，至少配置 MySQL、JWT 和 Redis。不要复制或提交生产环境的真实凭据。

启动 API：

```bash
python start.py
```

按需另开终端启动队列和日志压缩：

```bash
python start_queue_worker.py
python start_log_compressor.py
```

默认 API 地址为 `http://127.0.0.1:6080`。

## 配置

### HTTP 服务

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `APP_HOST` | `0.0.0.0` | 监听地址 |
| `APP_PORT` | `6080` | 监听端口 |
| `APP_DEBUG` | `0` | 是否启用 reload |
| `WORKERS` / `APP_WORKERS` | `1` | Uvicorn 进程数，`WORKERS` 优先 |
| `APP_LIMIT_CONCURRENCY` | `10000` | 并发连接限制 |
| `APP_BACKLOG` | `4096` | Socket backlog |
| `APP_TIMEOUT_KEEP_ALIVE` | `5` | Keep-Alive 秒数 |
| `ENABLE_DOCS` | `1` | 是否开放 Swagger/ReDoc |
| `CORS_ORIGINS` | `*` | 允许的来源，多个值用逗号分隔 |

生产环境应设置明确的 `CORS_ORIGINS`，并使用至少 32 位、随机生成的 `JWT_SECRET_KEY`。

### MySQL

主库使用 `DB_HOST`、`DB_PORT`、`DB_USER`、`DB_PASSWORD`、`DB_NAME`。连接池由 `DB_MINSIZE`、`DB_MAXSIZE`、`DB_POOL_RECYCLE` 和 `DB_CONNECT_TIMEOUT` 控制。

设置 `DB_READ_WRITE_SPLIT=1` 后，可通过 `DB_SLAVE1_*`、`DB_SLAVE2_*` 配置两个从库。写操作始终走主库，读操作在健康从库间轮询并在异常时回退主库。

### Redis 与队列

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `REDIS_ENABLED` | `1` | 是否启用 Redis |
| `REDIS_HOST` / `REDIS_PORT` | `127.0.0.1:6379` | Redis 地址 |
| `REDIS_PASSWORD` / `REDIS_DB` | 空 / `0` | 认证和数据库 |
| `REDIS_KEY_PREFIX` | `qyd:` | Key 前缀 |
| `REDIS_QUEUE_BATCH_SIZE` | `200` | 单批处理量 |
| `REDIS_QUEUE_NUM_WORKERS` | `4` | 每个队列进程内的并发数 |
| `QUEUE_WORKER_PROCESSES` | `1` | 独立队列进程数 |

实际并发会随 `QUEUE_WORKER_PROCESSES × REDIS_QUEUE_NUM_WORKERS` 放大。调整前必须同时评估数据库连接池、Redis 连接数和外部接口限流。

### 定时任务与日志

- `DB_CHECK_INTERVAL_MINUTES`：数据库保活周期。
- `ENABLE_EMAIL_CHECK`、`EMAIL_CHECK_INTERVAL_HOURS`：邮箱状态检查。
- `ENABLE_STATS_SYNC`、`STATS_SYNC_INTERVAL_MINUTES`：项目统计同步。
- `LOG_LEVEL`：日志级别。
- `LOG_COMPRESS_INTERVAL_HOURS`、`LOG_RETENTION_DAYS`、`LOG_COMPRESS_ON_STARTUP`：独立日志压缩进程。

> `WORKERS>1` 时，每个 API 进程都会创建 APScheduler，可能重复执行定时任务。提高 API Worker 数前，应先把定时任务迁到单独进程或保证任务具备分布式互斥。

## Docker 部署

仓库根目录提供应用栈 `docker-compose.yml`，也提供前后端分离的 Compose 文件。MySQL 和 Redis 均为外部服务，Compose 不会创建或管理它们；启动前必须正确配置 `DB_*` 与 `REDIS_*`。发布前先确认线上实际使用的文件，不要混用两套拓扑。以下 Docker 命令均在仓库根目录执行。

只做配置校验：

```bash
docker compose config --quiet
```

完整栈构建和启动：

```bash
docker compose build
docker compose up -d
```

后端分离部署：

```bash
docker compose -f docker-compose.backend.yml build
docker compose -f docker-compose.backend.yml up -d
```

注意事项：

- 当前 Docker 健康检查访问 `/docs`。若生产设置 `ENABLE_DOCS=0`，应先把健康检查改为独立健康端点，否则容器会被判为不健康。
- 确认 `logs/`、`static/` 和数据库导出目录使用持久化卷或宿主机备份；重建容器前先验证数据不会随容器丢失。
- 不要在未审阅的情况下运行名称含 `reset`、`cleanup`、`fix`、`migrate` 的历史脚本。

## 数据库变更

已上线数据库禁止使用“自动建表”代替迁移。每次模型或 Schema 调整至少执行：

1. 记录当前数据库版本与目标变更。
2. 完成全量或可验证备份。
3. 在生产副本上验证迁移和回滚。
4. 审阅 SQL 的锁表、默认值、索引和数据转换影响。
5. 在维护窗口执行，并观察 API、Worker 与数据库指标。
6. 保留上一个应用镜像和对应数据库回滚方案。

`db/` 中同时存在 SQL 与 Python 历史迁移，且当前 Aerich 迁移基线不完整。在重建可靠迁移基线并核对线上 Schema 前，不得整体删除或批量执行这些文件。

## 验证

测试可能连接数据库、Redis 或外部服务，只能使用隔离环境和测试凭据：

```bash
python -m pytest tests
```

发布后的最低验证项：

- API 进程、队列 Worker、日志压缩进程均健康。
- 登录、权限菜单和一个只读业务接口正常。
- MySQL 主库/从库与 Redis 连接正常。
- 项目账号、项目提现队列无持续积压。
- 定时任务没有因多 Worker 重复执行。
- 日志、上传文件与数据库导出落在持久化路径。

## 安全与回滚

- 禁止提交 `.env`、JWT、数据库/Redis 密码、Bearer Token 或管理员初始密码。
- 所有 `/v1` API（登录等公开接口除外）使用 `Authorization: Bearer <token>`。
- 若仓库历史中出现过真实凭据，仅删除文件不够，必须轮换线上凭据。
- 发布前记录当前 Commit、镜像标签和数据库版本。
- 应用问题优先回滚到上一镜像；数据库已变更时严格使用已验证的反向迁移或备份恢复方案。

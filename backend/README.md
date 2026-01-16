# QYD API 后端服务（backend）

本目录为 QYD API 的后端服务代码，基于 **FastAPI + Tortoise ORM** 实现，主要提供：

- 服务器相关管理接口（国家、分组、服务器信息、代理账号等）
- 邮箱相关管理接口（邮箱信息、授权记录）
- 邮箱发送/授权等客户端能力（`app/clients/mail.py`）

运行环境：**Python 3.11+**（建议）  
依赖管理：使用 `requirements.txt` 手动安装

---

## 1. 目录结构概览

仅列出与后端开发直接相关的核心目录：

- `app/`
  - `main.py`：FastAPI 应用入口（包含路由注册、全局异常处理、数据库生命周期管理）
  - `core/`：核心配置
    - `settings.py`：Tortoise ORM 配置、数据库连接信息等
  - `models/`：Tortoise ORM 模型定义
    - `server.py`：服务器国家、分组、服务器信息、代理账号等模型
    - `mail.py`：邮箱信息、邮箱授权模型
  - `schemas/`：Pydantic 请求/响应模型
    - `server/`：服务器相关的 Create/Update/Out/OutList 模型
    - `mail/`：邮箱相关的 Create/Update/Out/OutList 模型及枚举
  - `crud/`：各模型对应的 CRUD 封装
    - `base.py`：通用 CRUD 基类（统一列表查询、分页、关联处理、upsert 等）
    - `server/`：服务器相关 CRUD（国家、分组、服务器信息、代理账号）
    - `mail/`：邮箱信息、邮箱授权 CRUD
  - `apis/v1/`：对外 HTTP 接口（按业务模块拆分）
    - `server/`：服务器相关接口
    - `mail/`：邮箱相关接口
  - `clients/`
    - `mail.py`：邮箱客户端封装（授权、收发邮件等逻辑）
  - `utils/`：通用工具
    - `time_tool.py`：时间解析、时区处理（接口里的 `parse_time` 使用）
    - `exceptions.py`：自定义异常
    - `logs.py`：日志封装
    - `retry.py`：重试工具
    - `redis_tool.py`：Redis 相关封装
  - `tests/`
    - `api_requests_test.py`：接口测试样例（可作为 Postman/接口调用的参考）
- `migrations/`：数据库迁移脚本（由 aerich 生成）
- `scripts/`：辅助脚本
  - `init_db.sh`：初始化数据库（建表）
  - `update_db.sh`：更新数据库（迁移）
- `start.py`：本地启动脚本（封装 uvicorn 运行参数）
- `.env`：环境变量配置（数据库连接、监听地址等）

---

## 2. 快速启动

### 2.1 安装依赖

在 `backend/` 目录下执行：

```bash
pip install -r requirements.txt
```

> 依赖中包含了 FastAPI、Tortoise ORM、uvicorn、APScheduler、DrissionPage 等。

### 2.2 配置环境变量

在 `backend/` 目录下创建或修改 `.env` 文件（已有则按需修改），典型配置示例：

```env
APP_HOST=0.0.0.0
APP_PORT=6070
APP_DEBUG=1

# 数据库相关（示例，具体以 app.core.settings.TORTOISE_ORM 为准）
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=qyd
```

`start.py` 中的 `run_server` 会优先从 `.env` 加载环境变量：

- 未设置时，默认监听 `0.0.0.0:6070`
- `APP_DEBUG` 存在时，会打开 `reload` 热重载

### 2.3 启动服务

在 `backend/` 目录下执行：

```bash
python start.py
```

或直接使用 uvicorn（需保证 `PYTHONPATH` 指向 `backend`）：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 6070 --reload
```

服务启动后，即可访问：

- 接口文档（默认）：`http://127.0.0.1:6070/docs`
- 或者：`http://127.0.0.1:6070/redoc`

---

## 3. 数据库迁移（Tortoise ORM + aerich）

本项目使用 **aerich** 管理数据库迁移，配置入口在：

- `pyproject.toml` 中的 `[tool.aerich]`
- `tortoise_orm = "app.core.settings.TORTOISE_ORM"`

### 3.1 初始化数据库

在第一次运行前，执行：

```bash
./scripts/init_db.sh
```

该脚本通常会执行类似（仅示意）：

```bash
aerich init-db
```

用于创建基础表结构。

### 3.2 执行迁移更新

当模型（`app/models/*.py`）发生变化，需要更新数据库结构时，执行：

```bash
./scripts/update_db.sh
```

该脚本通常会依次执行（仅示意）：

```bash
aerich migrate
aerich upgrade
```

用于生成迁移文件并应用到数据库。

---

## 4. 核心设计说明（简要）

### 4.1 分层结构

- **models**：保存数据库结构和关系，使用 Tortoise ORM 定义。
- **schemas**：HTTP 层的入参/出参模型：
  - Create / Update：请求体结构。
  - Out / OutList：响应封装，包含列表总数、条目数量等。
- **crud**：
  - `CRUDBase` 封装了通用的增删改查、分页、count、upsert。
  - 具体业务 CRUD（例如 `server/info.py`、`mail/info.py`）通过：
    - 配置 `QUERY_FIELD_RULES`/`QUERY_FIELD_MAP`：控制查询行为（模糊、精确、时间范围等）。
    - 配置 `RELATED_FIELDS`：控制外键写入（例如 `group_id -> group`）。
    - 按需重写 `_before_create/_before_update/_handle_related_fields` 做业务校验和关联处理。
- **apis/v1**：只负责：
  - 解析 HTTP 参数（Query/Body/Path）；
  - 调用 CRUD 层；
  - 统一异常转换为 `HTTPException`。

### 4.2 查询与过滤

- 通用过滤通过 `CRUDBase._build_query` 实现：
  - `QUERY_FIELD_RULES`：声明哪些字段可被查询，以及使用何种查询方式（`exact/contains/gte/...`）；
  - `QUERY_FIELD_MAP`：将参数名映射到真实字段（例如 `create_time_start -> create_time`）。
- 时间范围查询在各 CRUD 子类中统一支持：
  - 常见参数：`create_time_start/create_time_end`、`update_time_start/update_time_end`；
  - API 层使用 `utils.time_tool.parse_time` 将字符串/时间戳转换为 `datetime`。

### 4.3 邮箱业务的一点特殊逻辑

在 `app/crud/mail/info.py` 中：

- `EMAIL_TYPE_CONDITIONS` 通过 `(ip_is_null, token_is_null)` 的组合来表达 `email_type`：
  - `ip_ok/ip_not`：对应 `server_info_id` 是否为空；
  - `token_ok/token_not`：对应 `access_token` 是否为空；
  - 组合枚举则同时对两者进行过滤。
- `_apply_email_type_filter` 将这些枚举映射为具体的 ORM 查询条件，供列表和 count 复用。

---

## 5. 测试与调试建议

目前仓库中已包含基础的接口请求示例：

- `app/tests/api_requests_test.py`

建议的调试方式：

1. 启动服务后，先通过 `/docs` 直接调试 API，观察请求/响应结构；
2. 若引入 `pytest`，可在根目录或 `backend/` 目录下执行：

   ```bash
   pytest
   ```

   （具体测试框架可根据你后续的选择在此基础上扩展）

---

## 6. 后续扩展建议

- 新增业务模块时，建议沿用当前结构：
  - 在 `models/` 中新增模型；
  - 在 `schemas/xxx/` 中新增对应的 Create/Update/Out/OutList；
  - 在 `crud/xxx/` 中创建 CRUD 子类，继承 `CRUDBase` 并配置查询规则；
  - 在 `apis/v1/xxx/` 中新增路由，使用统一的异常处理方式。
- 所有新增函数，建议保持已有风格：  
  函数级中文注释简要说明“用途 + 入参 + 关键逻辑”，方便以后快速浏览回忆。

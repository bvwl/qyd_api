# QYD API 后端服务（backend）

本目录为 QYD API 的后端服务代码，基于 **FastAPI + Tortoise ORM** 实现，主要提供：

- 用户管理接口（用户、角色、权限、日志、Token）
- 项目管理接口（项目信息、账号、钱包、余额）
- 服务器管理接口（国家、分组、服务器信息、代理账号）
- 邮箱管理接口（邮箱信息、Outlook 授权/收发邮件）
- 基于角色的访问控制（RBAC）权限管理
- 定时任务（APScheduler）自动检查邮箱状态

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
    - `base.py`：基础模型（包含 UUID 主键、创建/更新时间）
    - `user.py`：用户、角色、日志、Token、前端路由模型
    - `project.py`：项目信息、账号、钱包、余额模型
    - `server.py`：服务器国家、分组、服务器信息、代理账号模型
    - `mail.py`：邮箱信息模型
  - `schemas/`：Pydantic 请求/响应模型
    - `base.py`：基础响应模型（BaseOut）
    - `user/`：用户相关的 Create/Update/Out/OutList 模型
      - `info.py`：用户信息 Schema
      - `role.py`：角色 Schema
      - `route.py`：前端路由 Schema
      - `token.py`：Token Schema
      - `log.py`：操作日志 Schema
    - `project/`：项目相关的 Create/Update/Out/OutList 模型
      - `info.py`：项目信息 Schema
      - `account.py`：项目账号 Schema
      - `wallet.py`：项目钱包 Schema
      - `balance.py`：项目余额 Schema
    - `server/`：服务器相关的 Create/Update/Out/OutList 模型
      - `country.py`：国家信息 Schema
      - `group.py`：分组信息 Schema
      - `info.py`：服务器信息 Schema
      - `account.py`：服务器账号 Schema
    - `mail/`：邮箱相关的 Create/Update/Out/OutList 模型及枚举
      - `info.py`：邮箱信息 Schema（包含 EmailType 枚举）
      - `outlook.py`：Outlook 操作 Schema
  - `crud/`：各模型对应的 CRUD 封装
    - `base.py`：通用 CRUD 基类（统一列表查询、分页、关联处理、upsert 等）
    - `user/`：用户相关 CRUD
      - `user.py`：用户信息 CRUD
      - `role.py`：角色 CRUD
      - `route.py`：前端路由 CRUD
      - `token.py`：Token CRUD
      - `log.py`：操作日志 CRUD
      - `permission.py`：权限 CRUD（占位）
    - `project/`：项目相关 CRUD
      - `info.py`：项目信息 CRUD
      - `account.py`：项目账号 CRUD
      - `wallet.py`：项目钱包 CRUD
      - `balance.py`：项目余额 CRUD
    - `server/`：服务器相关 CRUD
      - `country.py`：国家信息 CRUD
      - `group.py`：分组信息 CRUD
      - `info.py`：服务器信息 CRUD
      - `account.py`：服务器账号 CRUD
    - `mail/`：邮箱相关 CRUD
      - `info.py`：邮箱信息 CRUD
  - `apis/v1/`：对外 HTTP 接口（按业务模块拆分）
    - `user/`：用户相关接口
      - `auth.py`：用户认证接口
      - `user.py`：用户管理接口
      - `role.py`：角色管理接口
      - `route.py`：路由管理接口
      - `token.py`：Token 管理接口
      - `log.py`：日志管理接口
    - `project/`：项目相关接口
      - `info.py`：项目信息接口
      - `account.py`：项目账号接口
      - `wallet.py`：项目钱包接口
      - `balance.py`：项目余额接口
    - `server/`：服务器相关接口
      - `country.py`：国家信息接口
      - `group.py`：分组信息接口
      - `info.py`：服务器信息接口
      - `account.py`：服务器账号接口
    - `mail/`：邮箱相关接口
      - `info.py`：邮箱信息接口
      - `outlook.py`：Outlook 操作接口
  - `clients/`
    - `outlook.py`：Outlook 邮箱客户端封装（OAuth2 授权、收发邮件等逻辑）
  - `utils/`：通用工具
    - `time_tool.py`：时间解析、时区处理（接口里的 `parse_time` 使用）
    - `exceptions.py`：自定义异常
    - `logs.py`：日志封装
    - `retry.py`：重试工具
    - `redis_tool.py`：Redis 相关封装
    - `decorators.py`：装饰器工具
    - `req.py`：HTTP 请求工具
  - `tests/`：测试文件
    - `api_requests_test.py`：接口测试样例（可作为 Postman/接口调用的参考）
    - `test_user.py`：用户模块测试
    - `test_project.py`：项目模块测试
    - `test_server.py`：服务器模块测试
    - `test_mail.py`：邮箱模块测试
    - `user_requests_test.py`：用户请求测试
    - `run_all_tests.py`：运行所有测试
- `migrations/`：数据库迁移脚本（由 aerich 生成）
  - `models/`：迁移版本文件
- `scripts/`：辅助脚本
  - `init_db.sh`：初始化数据库（建表）
  - `update_db.sh`：更新数据库（迁移）
- `start.py`：本地启动脚本（封装 uvicorn 运行参数）
- `verify_setup.py`：项目完整性验证脚本（验证所有模块是否正确配置）
- `OPTIMIZATION_SUMMARY.md`：代码优化总结（详细的优化说明）
- `BEFORE_AFTER_COMPARISON.md`：优化前后对比（直观的对比展示）
- `.env`：环境变量配置（数据库连接、监听地址等）
- `.env.example`：环境变量配置模板
- `requirements.txt`：Python 依赖包列表
- `pyproject.toml`：项目配置（aerich 配置）
- `pytest.ini`：pytest 配置

---

## 2. 快速启动

### 2.0 启动前检查清单

在启动服务前，请确保：

- [ ] Python 3.11+ 已安装
- [ ] MySQL 数据库已安装并运行
- [ ] 已创建数据库（默认名称：qyd）
- [ ] 已配置 `.env` 文件（数据库连接信息）
- [ ] 已安装所有依赖（`pip install -r requirements.txt`）

**快速验证：**

运行验证脚本检查项目配置是否正确：

```bash
python scripts/verify_setup.py
```

该脚本会验证：
- ✅ 所有模型是否正确导入
- ✅ 所有 CRUD 模块是否正确配置
- ✅ 所有 API 路由是否正确注册
- ✅ FastAPI 应用是否可以正常启动

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
APP_PORT=6080
APP_DEBUG=1

# 数据库相关（示例，具体以 app.core.settings.TORTOISE_ORM 为准）
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=qyd
```

`start.py` 中的 `run_server` 会优先从 `.env` 加载环境变量：

- 未设置时，默认监听 `0.0.0.0:6080`
- `APP_DEBUG` 存在时，会打开 `reload` 热重载

### 2.3 启动服务

在 `backend/` 目录下执行：

```bash
python start.py
```

或直接使用 uvicorn（需保证 `PYTHONPATH` 指向 `backend`）：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 6080 --reload
```

服务启动后，即可访问：

- 接口文档（默认）：`http://127.0.0.1:6080/docs`
- 或者：`http://127.0.0.1:6080/redoc`

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

## 4. 核心设计说明

### 4.1 数据模型设计

#### 4.1.1 用户模块（user.py）

**核心模型：**

- `UserInfo`：用户信息
  - 字段：email（邮箱）、password（密码加密）、nickname（昵称）、avatar（头像）、status（状态）
  - 状态枚举：`UserStatus`（1:正常, 2:停用, 3:锁定, 4:封禁）
  - 多对多关联：roles（角色）、projects（项目）

- `UserRole`：用户角色
  - 字段：name（角色名称）、code（角色标识）、description（角色描述）
  - 多对多关联：users（用户）、routes（前端路由）

- `FrontendRoute`：前端路由/菜单
  - 字段：name、path、component、title、icon、sort、redirect、is_hidden、is_cache、is_affix、status
  - 支持树形结构：parent（父级路由）、children（子路由）
  - 多对多关联：roles（角色）

- `UserToken`：用户访问令牌
  - 字段：token、status
  - 外键关联：user（所属用户）

- `UserLog`：用户操作日志
  - 字段：action（操作类型）、description（操作描述）、ip、user_agent
  - 外键关联：user（所属用户）

#### 4.1.2 项目模块（project.py）

**核心模型：**

- `ProjectInfo`：项目信息
  - 字段：name（项目名称）、status（状态）、content（项目内容）
  - 状态枚举：`ProjectStatus`（1:正常, 2:未编写, 3:编写中, 4:项目结束, 5:项目跑路, 6:项目维护, 7:未分配, 8:账号不支持, 9:IP不支持）
  - 多对多关联：users（项目成员）

- `ProjectAccount`：项目账号
  - 字段：account、password、status、account_type、data（扩展数据）
  - 状态枚举：`Status`（1:正常, 2:异常）
  - 账号类型枚举：`AccountType`（1:邮箱, 2:钱包, 3:x, 4:其他1, 5:其他2）
  - 外键关联：project（所属项目）、server（关联服务器）、wallet（关联钱包）

- `ProjectWallet`：项目钱包
  - 字段：private_key（私钥）、public_key（公钥）、mnemonic（助记词）、chain（链）、remark（备注）

- `ProjectBalance`：项目余额
  - 字段：balance（余额）、variable（变动余额）、history（历史余额）
  - 一对一关联：account（关联账号）

#### 4.1.3 服务器模块（server.py）

**核心模型：**

- `ServerCountry`：国家信息
  - 字段：short_name（国家简称）、name（国家名称）、status

- `ServerGroup`：分组信息
  - 字段：name（分组名称）、status
  - 外键关联：country（所属国家）

- `ServerInfo`：服务器信息
  - 字段：host、ssh_port、password、status、domain、is_sale、port
  - 销售状态枚举：`IsSale`（1:是, 2:否）
  - 外键关联：group（所属分组）

- `ServerAccount`：服务器账号
  - 字段：username、password
  - 一对一关联：user（关联用户信息）

#### 4.1.4 邮箱模块（mail.py）

**核心模型：**

- `EmailInfo`：邮箱信息
  - 字段：email、password、auxiliary_email、auxiliary_email_password、client_id、access_token、refresh_token、status
  - 外键关联：server（代理信息）

### 4.2 枚举类型设计

所有枚举统一使用 `IntEnum`（整数枚举），便于前端处理和数据库存储：

- 在模型中使用 `fields.IntEnumField(EnumClass)` 定义
- 在 Schema 中直接引用模型定义的枚举类型
- 枚举值为整数，注释说明对应含义

### 4.3 数据库索引设计

#### 4.3.1 索引类型与声明方式

**单字段索引：使用 `index=True`**
```python
class User(BaseModel):
    email = fields.CharField(max_length=128, unique=True)  # unique 自动创建索引
    username = fields.CharField(max_length=64, index=True)  # ✅ 单字段索引
```

**复合索引：使用 `Meta.indexes`**
```python
class User(BaseModel):
    status = fields.IntField()
    
    class Meta:
        indexes = [
            ("status", "create_time"),  # ✅ 复合索引
            # 不要重复声明已有 index=True 的字段
        ]
```

**自动索引（无需手动声明）：**
- 主键（`pk=True`）
- 唯一约束（`unique=True`）
- 外键（`ForeignKeyField`）
- BaseModel 的 `create_time`（已有 `index=True`）

#### 4.3.2 索引优化原则

1. **基于实际查询模式**：根据 CRUD 层的查询条件创建索引
2. **复合索引优先**：将常用的查询条件组合成复合索引
3. **高选择性字段在前**：`(user_id, status)` 优于 `(status, user_id)`
4. **避免冗余索引**：不要重复声明已有的索引
5. **左前缀原则**：复合索引 `(A, B, C)` 可用于 `WHERE A` 和 `WHERE A AND B`

#### 4.3.3 各模块索引配置

**用户模块：**
```python
# UserRole
indexes = [
    ("code",),              # 唯一查询（已有 unique=True，此处为示例）
    ("name",),              # 模糊查询
]

# UserInfo
indexes = [
    ("status", "create_time"),  # 按状态和时间查询
]

# UserToken
indexes = [
    ("user_id", "status", "create_time"),  # 按用户和状态查询
    ("status", "create_time"),             # 按状态查询
]

# UserLog
indexes = [
    ("user_id", "create_time"),            # 按用户查询（最常用）
    ("user_id", "action", "create_time"),  # 按用户和操作类型
    ("action", "create_time"),             # 按操作类型
]

# FrontendRoute
indexes = [
    ("status", "parent_id", "sort"),  # 按状态和父级查询
    ("parent_id", "sort"),            # 树形结构查询
    ("path",),                        # 按路径查询
    ("name",),                        # 按名称查询
]
```

**项目模块：**
```python
# ProjectInfo
indexes = [
    ("status", "create_time"),  # 按状态和时间查询
]

# ProjectAccount
indexes = [
    ("project_id", "status", "account_type"),  # 按项目查询
    ("status", "account_type", "create_time"), # 按状态和类型
    ("server_id", "status"),                   # 按服务器
    ("wallet_id",),                            # 按钱包
]

# ProjectWallet
indexes = [
    ("chain", "create_time"),  # 按链查询
]

# ProjectBalance
indexes = [
    ("account_id", "create_time"),  # 按账号查询
]
```

**服务器模块：**
```python
# ServerCountry
indexes = [
    ("status", "create_time"),  # 按状态和时间
]

# ServerGroup
indexes = [
    ("country_id", "status", "create_time"),  # 按国家查询
    ("status", "create_time"),                # 按状态查询
]

# ServerInfo
indexes = [
    ("status", "is_sale", "create_time"),  # 按状态和销售状态
    ("group_id", "status"),                # 按分组查询
]

# ServerAccount
indexes = [
    ("user_id", "create_time"),  # 按用户查询
]
```

**邮箱模块：**
```python
# EmailInfo
indexes = [
    ("status", "server_id", "create_time"),  # EmailType 过滤（最重要）
    ("status", "create_time"),               # 按状态查询
    ("server_id", "status"),                 # 按服务器查询
    ("update_time",),                        # 定时任务查询
]
```

#### 4.3.4 性能提升预期

- **邮箱列表查询**：50-80% 提升（EmailType 过滤优化）
- **用户日志查询**：60-90% 提升（复合索引覆盖）
- **项目账号查询**：40-70% 提升（多场景支持）
- **路由树查询**：30-50% 提升（父子关系优化）

#### 4.3.5 索引使用示例

```python
# 示例 1：邮箱 EmailType 过滤
# 查询：status=1 AND server_id IS NOT NULL ORDER BY create_time DESC
# 使用索引：("status", "server_id", "create_time")
EmailInfo.filter(status=1, server_id__isnull=False).order_by('-create_time')

# 示例 2：用户日志查询
# 查询：user_id=? AND action=? ORDER BY create_time DESC
# 使用索引：("user_id", "action", "create_time")
UserLog.filter(user_id=user_id, action=action).order_by('-create_time')

# 示例 3：路由树查询
# 查询：parent_id=? ORDER BY sort ASC
# 使用索引：("parent_id", "sort")
FrontendRoute.filter(parent_id=parent_id).order_by('sort')
```

### 4.4 多对多关联设计

多对多关联遵循以下规则：

- 在一侧定义 `ManyToManyField`，指定中间表名称（through 参数）
- 在另一侧只声明类型注解 `ManyToManyRelation`
- 使用 `TYPE_CHECKING` 避免循环导入

**示例关联：**

- 用户 ↔ 角色：`user_role_rel` 中间表
- 角色 ↔ 路由：`role_route_rel` 中间表
- 项目 ↔ 用户：`project_user_rel` 中间表

### 4.5 关联数据加载规范

**单个对象查询：**
- 使用 `fetch_related()` 加载关联数据
- 示例：`await obj.fetch_related('user', 'roles')`

**列表查询：**
- 使用 `prefetch_related()` 预加载关联数据，避免 N+1 查询问题
- 示例：`await query.prefetch_related('user', 'roles')`

**嵌套关联：**
- 使用双下划线语法加载嵌套关联
- 示例：`await query.prefetch_related('group', 'group__country')`

**关键区别：**
- `fetch_related`：用于已加载的单个对象
- `prefetch_related`：用于查询集（QuerySet），一次性预加载所有对象的关联数据
- 不要在 `get_or_none()` 后链式调用 `prefetch_related()`

**各模块关联加载示例：**

```python
# Mail 模块
await EmailInfo.all().prefetch_related('server')

# Project 模块
await ProjectInfo.all().prefetch_related('users')
await ProjectAccount.all().prefetch_related('project', 'server', 'wallet')
await ProjectBalance.all().prefetch_related('account')

# Server 模块
await ServerCountry.all().prefetch_related('server_groups')
await ServerGroup.all().prefetch_related('country')
await ServerInfo.all().prefetch_related('group', 'group__country')
await ServerAccount.all().prefetch_related('user')

# User 模块
await UserInfo.all().prefetch_related('roles', 'projects')
await UserRole.all().prefetch_related('users', 'routes')
await FrontendRoute.all().prefetch_related('parent', 'children', 'roles')
await UserToken.all().prefetch_related('user')
await UserLog.all().prefetch_related('user')
```

### 4.6 RBAC 权限控制设计

基于角色的访问控制（Role-Based Access Control）：

```
用户（UserInfo）
    ↓ 多对多
角色（UserRole）
    ↓ 多对多
路由（FrontendRoute）
```

- 用户可以拥有多个角色
- 角色可以关联多个前端路由/菜单
- 通过角色间接控制用户可访问的路由
- 路由支持树形结构，可构建多级菜单

### 4.7 分层结构

- **models**：保存数据库结构和关系，使用 Tortoise ORM 定义。
- **schemas**：HTTP 层的入参/出参模型：
  - Create / Update：请求体结构。
  - Out / OutList：响应封装，包含列表总数、条目数量等。
  - 关联对象：直接引入对应的 Base 模型，不使用 Lite 精简模型。
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

### 4.8 Schema 设计规范

**基础规范：**

- `Base`：包含模型的基础字段（不包含 ID、时间戳、关联对象）
- `Create`：继承 Base，添加外键 ID 字段和关联 ID 列表
- `Update`：所有字段可选，支持部分更新
- `Out`：包含完整信息（ID、时间戳、关联对象）
- `OutList`：包含 message、count、num、items

**关联字段顺序：**

1. 先定义外键 ID 字段（如 `project_id`）
2. 后定义关联对象字段（如 `project: ProjectInfoBase`）

**关联对象引用：**

- 直接引入对应模块的 `Base` 模型
- 不使用 `Lite` 精简模型
- 示例：`from app.schemas.project.info import Base as ProjectInfoBase`

**时间字段序列化：**

- 使用 `@field_serializer` 统一格式化为中国时区
- 格式：`%Y-%m-%d %H:%M:%S`

### 4.9 查询与过滤

- 通用过滤通过 `CRUDBase._build_query` 实现：
  - `QUERY_FIELD_RULES`：声明哪些字段可被查询，以及使用何种查询方式（`exact/contains/gte/...`）；
  - `QUERY_FIELD_MAP`：将参数名映射到真实字段（例如 `create_time_start -> create_time`）。
- 时间范围查询在各 CRUD 子类中统一支持：
  - 常见参数：`create_time_start/create_time_end`、`update_time_start/update_time_end`；
  - API 层使用 `utils.time_tool.parse_time` 将字符串/时间戳转换为 `datetime`。

### 4.10 邮箱业务的一点特殊逻辑

在 `app/crud/mail/info.py` 中：

- `EMAIL_TYPE_CONDITIONS` 通过 `(ip_is_null, token_is_null)` 的组合来表达 `email_type`：
  - `ip_ok/ip_not`：对应 `server_info_id` 是否为空；
  - `token_ok/token_not`：对应 `access_token` 是否为空；
  - 组合枚举则同时对两者进行过滤。
- `_apply_email_type_filter` 将这些枚举映射为具体的 ORM 查询条件，供列表和 count 复用。
- 列表查询 `get_multi` 在无数据时统一抛出 `404`，便于前端通过 HTTP 状态码判断“是否查到数据”（200 为正常，有数据；404 为无数据）。
- 邮箱列表接口对敏感字段做了脱敏处理：
  - `password` / `auxiliary_email_password` 在列表返回中会被置空；
  - 嵌套的 `server_info.ssh_port` 在列表返回中会被置为 `null`。

### 4.11 Outlook 授权与收发邮件

相关位置：

- 客户端：`app/clients/outlook.py`（封装 Azure OAuth2 PKCE 流程 + Microsoft Graph API 调用）
- 接口层：`app/apis/v1/mail/outlook.py`
- Schema：`app/schemas/mail/outlook.py`

主要能力：

- 生成微软 OAuth2 授权 URL（PKCE 模式），前端引导用户授权；
- 使用授权回调 URL 换取 `access_token` / `refresh_token` 并落库；
- 使用 Outlook 帐号发送邮件；
- 从垃圾箱/收件箱中获取指定发件人的邮件：
  - 会优先检查垃圾邮件箱，尝试把误判的邮件移回收件箱；
  - 然后再从收件箱中按发件人邮箱过滤并返回内容。
- 刷新 Token 时内置重试逻辑：当请求连续多次返回 5xx 时，会把对应邮箱状态标记为异常（5），方便后续排查。

### 4.12 定时任务与自动邮箱状态检查

相关位置：

- APScheduler 初始化与调度：`app/main.py`
- 邮箱状态检查逻辑：`app/apis/v1/mail/outlook.py` 中：
  - `check_and_update_emails_logic`
  - `auto_check_email_status`

说明：

- `check_and_update_emails_logic`：根据传入的时间范围、状态、邮箱类型等条件查询邮箱，并调用 Outlook 客户端尝试收取一封测试邮件，进而将邮箱状态更新为“正常/异常”。
- `auto_check_email_status`：用于定时任务调用，自动检查 N 天前未更新的正常邮箱状态：
  - 使用 `CN_TZ` 计算 N 天前的时间点，并转换为 13 位时间戳；
  - 固定筛选“状态正常 + IP/TOKEN 均正常”的邮箱；
  - 将更新时间早于该时间点的邮箱交给 `check_and_update_emails_logic` 做实际检查与状态更新。
- 在 `main.py` 中已经预留了以“每小时执行一次”的方式注册该任务的代码（目前默认注释，如需启用只需解除注释）。

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

## 6. 常用接口使用示例

下面示例默认后端监听在 `http://127.0.0.1:6070`。

### 6.1 邮箱列表查询（支持筛选 / 404 区分“无数据”）

接口：`GET /v1/mail/info`

示例请求（查询状态正常且 IP、TOKEN 均正常的邮箱，按创建时间倒序第一页，每页 10 条，同时返回总数）：

```bash
curl "http://127.0.0.1:6070/v1/mail/info?status=1&email_type=ip_ok_token_ok&order_by=-create_time&res_count=true&page=1&limit=10"
```

返回示例：

```json
{
  "message": "成功",
  "count": 1891,
  "num": 10,
  "items": [
    {
      "email": "xxx@outlook.com",
      "password": "",
      "auxiliary_email": "xxx@0n.lv",
      "auxiliary_email_password": "",
      "client_id": "8ca2df50-512f-495e-83f6-faa83b574bab",
      "access_token": "...",
      "refresh_token": "...",
      "status": 1,
      "message": "成功",
      "id": "09a71d1f-e66c-4d9d-89f1-12308a46450b",
      "create_time": "2026-01-15 17:17:52",
      "update_time": "2026-01-16 16:03:07",
      "server_info_id": "909463f8-9655-41db-9e62-332892e21b4d",
      "server_info": {
        "host": "92.113.143.209",
        "ssh_port": null,
        "password": null,
        "status": 1,
        "domain": "zd8.0n.lv",
        "is_sale": 1,
        "port": 32123
      },
      "proxy_type": "socks5",
      "proxy_url": "socks5://username:password@zd8.0n.lv:32123"
    }
  ]
}
```

注意：

- 当无任何数据符合条件时，接口会返回 `404` 状态码（HTTP 层），方便前端统一用“200=查到数据、404=未查到数据”的规则处理。
- 列表中的敏感字段已脱敏：`password` / `auxiliary_email_password` 为空字符串，`server_info.ssh_port` 为 `null`。

### 6.2 批量调整邮箱状态

接口：`POST /v1/mail/info/status/batch-update`

示例（将所有状态为 4 的邮箱改为 1）：

```bash
curl -X POST "http://127.0.0.1:6070/v1/mail/info/status/batch-update" \
  -H "Content-Type: application/json" \
  -d '{"from_status": 4, "to_status": 1}'
```

返回示例：

```json
{
  "message": "成功",
  "count": 123
}
```

### 6.3 Outlook 授权流程

#### 6.3.1 获取授权 URL

接口：`GET /v1/mail/outlook/auth/url`

```bash
curl "http://127.0.0.1:6070/v1/mail/outlook/auth/url?email=xxx@outlook.com"
```

返回示例：

```json
{
  "url": "https://login.microsoftonline.com/...",
  "verifier": "随机字符串"
}
```

前端应：

- 使用 `url` 打开浏览器让用户登录并授权；
- 在用户授权完成后，复制浏览器地址栏中的完整回调 URL；
- 将回调 URL 和 `verifier` 一起传给下一个接口。

#### 6.3.2 使用回调 URL 换取 Token

接口：`POST /v1/mail/outlook/auth/token`

```bash
curl -X POST "http://127.0.0.1:6070/v1/mail/outlook/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "xxx@outlook.com",
    "url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?code=...",
    "verifier": "上一步返回的 verifier"
  }'
```

成功时会在数据库中写入 `access_token` / `refresh_token`，并返回：

```json
{
  "message": "获取Token成功",
  "count": 1
}
```

### 6.4 使用 Outlook 发送邮件

接口：`POST /v1/mail/outlook/send`

```bash
curl -X POST "http://127.0.0.1:6070/v1/mail/outlook/send" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "xxx@outlook.com",
    "to_email": "target@example.com",
    "subject": "测试邮件",
    "content": "你好，这是一封测试邮件。",
    "content_type": "Text"
  }'
```

成功时返回：

```json
{
  "message": "成功",
  "count": 1
}
```

### 6.5 获取指定发件人的邮件

接口：`POST /v1/mail/outlook/messages`

```bash
curl -X POST "http://127.0.0.1:6070/v1/mail/outlook/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "xxx@outlook.com",
    "from_email": "sender@example.com",
    "num": 1,
    "top": 10
  }'
```

返回示例：

```json
{
  "code": 1,
  "message": "获取成功",
  "data": [
    {
      "from_email": "sender@example.com",
      "title": "测试标题",
      "content": "邮件正文 HTML 或文本内容"
    }
  ]
}
```

当未找到符合条件的邮件或调用失败时，返回：

```json
{
  "code": 0,
  "message": "获取失败或无邮件",
  "data": []
}
```

---

## 7. 后续扩展建议

- 新增业务模块时，建议沿用当前结构：
  - 在 `models/` 中新增模型；
  - 在 `schemas/xxx/` 中新增对应的 Create/Update/Out/OutList；
  - 在 `crud/xxx/` 中创建 CRUD 子类，继承 `CRUDBase` 并配置查询规则；
  - 在 `apis/v1/xxx/` 中新增路由，使用统一的异常处理方式。
- 所有新增函数，建议保持已有风格：  
  函数级中文注释简要说明“用途 + 入参 + 关键逻辑”，方便以后快速浏览回忆。

---

## 8. 数据模型关系图

```
用户模块：
UserInfo (用户)
    ├─ 多对多 ─> UserRole (角色)
    │              └─ 多对多 ─> FrontendRoute (前端路由/菜单)
    ├─ 多对多 ─> ProjectInfo (项目)
    ├─ 一对多 ─> UserToken (Token)
    ├─ 一对多 ─> UserLog (操作日志)
    └─ 一对一 ─> ServerAccount (服务器账号)

项目模块：
ProjectInfo (项目信息)
    ├─ 多对多 ─> UserInfo (项目成员)
    └─ 一对多 ─> ProjectAccount (项目账号)
                    ├─ 外键 ─> ServerInfo (关联服务器)
                    ├─ 外键 ─> ProjectWallet (关联钱包)
                    └─ 一对一 ─> ProjectBalance (余额)

服务器模块：
ServerCountry (国家)
    └─ 一对多 ─> ServerGroup (分组)
                    └─ 一对多 ─> ServerInfo (服务器信息)
                                    ├─ 一对多 ─> EmailInfo (邮箱)
                                    └─ 一对多 ─> ProjectAccount (项目账号)

邮箱模块：
EmailInfo (邮箱信息)
    └─ 外键 ─> ServerInfo (代理服务器)
```

---

## 9. 枚举类型参考

### 用户模块

- `UserStatus`（用户状态）：1-正常, 2-停用, 3-锁定, 4-封禁
- `Status`（通用状态）：1-正常, 2-异常

### 项目模块

- `ProjectStatus`（项目状态）：1-正常, 2-未编写, 3-编写中, 4-项目结束, 5-项目跑路, 6-项目维护, 7-未分配, 8-账号不支持, 9-IP不支持
- `AccountType`（账号类型）：1-邮箱, 2-钱包, 3-x, 4-其他1, 5-其他2
- `Status`（通用状态）：1-正常, 2-异常

### 服务器模块

- `Status`（通用状态）：1-正常, 2-异常
- `IsSale`（是否销售）：1-是, 2-否

### 邮箱模块

- `Status`（通用状态）：1-正常, 2-异常


---

## 10. API 接口完整列表

### 10.1 用户模块 (/v1/user)

#### 用户认证 (/auth)
- 用户登录、注册、Token 验证等

#### 用户管理 (/user)
- `POST /v1/user/user` - 创建用户
- `GET /v1/user/user/{id}` - 获取用户信息
- `GET /v1/user/user` - 获取用户列表
- `PUT /v1/user/user/{id}` - 更新用户信息
- `DELETE /v1/user/user/{id}` - 删除用户
- `POST /v1/user/user/upsert` - 创建或更新用户

#### 角色管理 (/role)
- `POST /v1/user/role` - 创建角色
- `GET /v1/user/role/{id}` - 获取角色信息
- `GET /v1/user/role` - 获取角色列表
- `PUT /v1/user/role/{id}` - 更新角色信息
- `DELETE /v1/user/role/{id}` - 删除角色
- `POST /v1/user/role/upsert` - 创建或更新角色

#### 路由管理 (/route)
- `POST /v1/user/route` - 创建路由
- `GET /v1/user/route/{id}` - 获取路由信息
- `GET /v1/user/route` - 获取路由列表
- `PUT /v1/user/route/{id}` - 更新路由信息
- `DELETE /v1/user/route/{id}` - 删除路由
- `POST /v1/user/route/upsert` - 创建或更新路由

#### Token 管理 (/token)
- `POST /v1/user/token` - 创建 Token
- `GET /v1/user/token/{id}` - 获取 Token 信息
- `GET /v1/user/token` - 获取 Token 列表
- `PUT /v1/user/token/{id}` - 更新 Token 信息
- `DELETE /v1/user/token/{id}` - 删除 Token
- `POST /v1/user/token/upsert` - 创建或更新 Token

#### 日志管理 (/log)
- `POST /v1/user/log` - 创建日志
- `GET /v1/user/log/{id}` - 获取日志信息
- `GET /v1/user/log` - 获取日志列表
- `PUT /v1/user/log/{id}` - 更新日志信息
- `DELETE /v1/user/log/{id}` - 删除日志

### 10.2 项目模块 (/v1/project)

#### 项目信息 (/info)
- `POST /v1/project/info` - 创建项目
- `GET /v1/project/info/{id}` - 获取项目信息
- `GET /v1/project/info` - 获取项目列表
- `PUT /v1/project/info/{id}` - 更新项目信息
- `DELETE /v1/project/info/{id}` - 删除项目
- `POST /v1/project/info/upsert` - 创建或更新项目

#### 项目账号 (/account)
- `POST /v1/project/account` - 创建项目账号
- `GET /v1/project/account/{id}` - 获取项目账号信息
- `GET /v1/project/account` - 获取项目账号列表
- `PUT /v1/project/account/{id}` - 更新项目账号信息
- `DELETE /v1/project/account/{id}` - 删除项目账号
- `POST /v1/project/account/upsert` - 创建或更新项目账号

#### 项目钱包 (/wallet)
- `POST /v1/project/wallet` - 创建项目钱包
- `GET /v1/project/wallet/{id}` - 获取项目钱包信息
- `GET /v1/project/wallet` - 获取项目钱包列表
- `PUT /v1/project/wallet/{id}` - 更新项目钱包信息
- `DELETE /v1/project/wallet/{id}` - 删除项目钱包
- `POST /v1/project/wallet/upsert` - 创建或更新项目钱包

#### 项目余额 (/balance)
- `POST /v1/project/balance` - 创建项目余额
- `GET /v1/project/balance/{id}` - 获取项目余额信息
- `GET /v1/project/balance` - 获取项目余额列表
- `PUT /v1/project/balance/{id}` - 更新项目余额信息
- `DELETE /v1/project/balance/{id}` - 删除项目余额
- `POST /v1/project/balance/upsert` - 创建或更新项目余额

### 10.3 服务器模块 (/v1/server)

#### 国家信息 (/country)
- `POST /v1/server/country` - 创建国家信息
- `GET /v1/server/country/{id}` - 获取国家信息
- `GET /v1/server/country` - 获取国家列表
- `PUT /v1/server/country/{id}` - 更新国家信息
- `DELETE /v1/server/country/{id}` - 删除国家信息
- `POST /v1/server/country/upsert` - 创建或更新国家信息

#### 分组信息 (/group)
- `POST /v1/server/group` - 创建分组信息
- `GET /v1/server/group/{id}` - 获取分组信息
- `GET /v1/server/group` - 获取分组列表
- `PUT /v1/server/group/{id}` - 更新分组信息
- `DELETE /v1/server/group/{id}` - 删除分组信息
- `POST /v1/server/group/upsert` - 创建或更新分组信息

#### 服务器信息 (/info)
- `POST /v1/server/info` - 创建服务器信息
- `GET /v1/server/info/{id}` - 获取服务器信息
- `GET /v1/server/info` - 获取服务器列表
- `PUT /v1/server/info/{id}` - 更新服务器信息
- `DELETE /v1/server/info/{id}` - 删除服务器信息
- `POST /v1/server/info/upsert` - 创建或更新服务器信息

#### 服务器账号 (/account)
- `POST /v1/server/account` - 创建服务器账号
- `GET /v1/server/account/{id}` - 获取服务器账号信息
- `GET /v1/server/account` - 获取服务器账号列表
- `PUT /v1/server/account/{id}` - 更新服务器账号信息
- `DELETE /v1/server/account/{id}` - 删除服务器账号
- `POST /v1/server/account/upsert` - 创建或更新服务器账号

### 10.4 邮箱模块 (/v1/mail)

#### 邮箱信息 (/info)
- `POST /v1/mail/info` - 创建邮箱信息
- `GET /v1/mail/info/{id}` - 获取邮箱信息
- `GET /v1/mail/info` - 获取邮箱列表（支持 EmailType 过滤）
- `PUT /v1/mail/info/{id}` - 更新邮箱信息
- `DELETE /v1/mail/info/{id}` - 删除邮箱信息
- `POST /v1/mail/info/upsert` - 创建或更新邮箱信息
- `POST /v1/mail/info/status/batch-update` - 批量更新邮箱状态

#### Outlook 操作 (/outlook)
- `GET /v1/mail/outlook/auth/url` - 获取 OAuth2 授权 URL
- `POST /v1/mail/outlook/auth/token` - 使用授权码换取 Token
- `POST /v1/mail/outlook/send` - 发送邮件
- `POST /v1/mail/outlook/messages` - 获取指定发件人的邮件
- `POST /v1/mail/outlook/check` - 检查并更新邮箱状态

---

## 11. 最近更新记录

### 2026-01-21 - 代码优化和配置增强

**优化内容：**

1. **start.py 优化**
   - ✅ 修复 `APP_DEBUG` 环境变量判断逻辑（支持 0/1/true/false/yes/no）
   - ✅ 添加日志系统配置（`setup_logging`）
   - ✅ 所有 uvicorn 参数可通过环境变量配置
   - ✅ 启动时输出关键配置信息

2. **main.py 优化**
   - ✅ 移除未使用的导入（`signal`, `sys`）
   - ✅ 使用 `logging` 替代 `print`，支持日志级别控制
   - ✅ 添加 FastAPI 应用元数据（title, description, version）
   - ✅ CORS 配置可通过环境变量控制（支持多域名）
   - ✅ API 文档可通过环境变量启用/禁用
   - ✅ 定时任务配置可通过环境变量控制
   - ✅ 优雅关闭等待时间可配置
   - ✅ 移除重复的 `if __name__ == '__main__'` 块

3. **配置文件优化**
   - ✅ 重构 `.env` 文件，添加详细注释和分类
   - ✅ 创建 `.env.example` 模板文件
   - ✅ 新增配置项：
     - `LOG_LEVEL`: 日志级别控制
     - `ENABLE_DOCS`: API 文档开关
     - `CORS_ORIGINS`: CORS 域名配置
     - `APP_WORKERS`: 工作进程数
     - `ENABLE_EMAIL_CHECK`: 邮箱检查开关
     - `DB_CHECK_INTERVAL_MINUTES`: 数据库检查间隔
     - `EMAIL_CHECK_INTERVAL_HOURS`: 邮箱检查间隔
     - `SHUTDOWN_WAIT_SECONDS`: 关闭等待时间

4. **安全性提升**
   - ✅ 生产环境可禁用 API 文档
   - ✅ CORS 可配置具体允许的域名
   - ✅ 所有敏感配置通过环境变量管理

**优化效果：**
- 更好的日志管理和调试能力
- 更灵活的配置管理
- 更安全的生产环境部署
- 更清晰的代码结构

### 2026-01-21 - 修复 Pydantic 循环引用问题

**问题描述：**
访问 `/openapi.json` 或 `/docs` 时出现 500 错误：
```
PydanticUserError: `TypeAdapter[...]` is not fully defined; 
you should define `...` and all referenced types, then call `.rebuild()` on the instance.
```

**根本原因：**
Schema 模型之间存在循环引用，导致 Pydantic 无法完全构建模型：
1. `user.info.Out` 引用 `project.info.Base`（通过 `projects` 字段）
2. `project.info.Out` 引用 `user.info.Base`（通过 `users` 字段）
3. `user.role.Out` 引用 `user.info.Base`（通过 `users` 字段）
4. `user.info.Out` 引用 `user.role.Base`（通过 `roles` 字段）

**修复内容：**
1. **移除循环引用字段**：
   - `user/info.py`: 移除 `Out.projects` 字段（未使用）
   - `user/role.py`: 移除 `Out.users` 字段（未使用）

2. **测试配置优化**：
   - 添加 `conftest.py` 配置 pytest 事件循环
   - 更新 `pytest.ini` 添加 `asyncio_mode = auto`
   - 添加 `pytest-asyncio` 依赖

**验证结果：**
- ✅ OpenAPI schema 正常生成
- ✅ Swagger UI 可访问（http://127.0.0.1:6080/docs）
- ✅ API 端点正常工作
- ✅ 用户注册/登录接口测试通过

**最佳实践：**
- 避免在输出模型中包含双向关联
- 使用 `TYPE_CHECKING` 处理前向引用
- 如需双向关联，考虑使用独立的详情接口

### 2026-01-21 - 修复事件循环关闭错误

**问题描述：**
应用关闭时出现 `RuntimeError: Event loop is closed` 错误，导致数据库连接无法正确清理。

**根本原因：**
1. `main.py` 中存在重复的调度器实例创建（两次 `scheduler = AsyncIOScheduler()`）
2. `keep_db_connection_alive` 函数被重复定义
3. 数据库连接在事件循环关闭后才尝试清理，导致 `aiomysql` 连接析构时出错

**修复内容：**
1. 移除重复的调度器实例创建
2. 移除重复的函数定义
3. 优化关闭顺序：
   - 先关闭调度器（避免任务还在运行）
   - 等待 0.5 秒让任务完成
   - 再关闭数据库连接
4. 改进错误处理和日志输出

**验证结果：**
- ✅ 应用可以正常启动和关闭
- ✅ 数据库连接正确清理
- ✅ 无事件循环关闭错误

### 2026-01-20 - CRUD 和 API 完善

**修复内容：**

1. **关联加载优化**
   - 统一使用 `prefetch_related()` 进行列表查询的关联预加载
   - 避免 N+1 查询问题，显著提升性能
   - 修正了所有模块的关联加载方式

2. **用户模块 CRUD 修复**
   - 修正 `UserLog` 的 action 字段过滤（从字符串改为整数）
   - 修正 `UserToken` 的字段名（token、status）
   - 修正 `UserRole` 和 `FrontendRoute` 的多对多关联处理
   - 移除不需要的关联（tokens、logs、server_account）

3. **Schema 循环导入修复**
   - 使用 `TYPE_CHECKING` 解决 `user/info.py` 和 `project/info.py` 的循环导入
   - 使用 `TYPE_CHECKING` 解决 `user/info.py` 和 `user/role.py` 的循环导入
   - 使用字符串类型注解（forward reference）避免运行时导入

4. **新增 API 接口**
   - 创建 `backend/app/apis/v1/user/role.py` - 角色管理 API
   - 创建 `backend/app/apis/v1/user/route.py` - 路由管理 API
   - 创建 `backend/app/apis/v1/user/token.py` - Token 管理 API
   - 创建 `backend/app/apis/v1/user/log.py` - 日志管理 API
   - 更新路由注册，所有 API 正常工作

5. **验证结果**
   - ✅ 所有模块的 CRUD 关联加载正确
   - ✅ 所有 API 路由成功注册（共 93 个路由）
   - ✅ 应用可以正常启动，无导入错误
   - ✅ 测试套件可以正常收集（53 个测试用例）

---

## 12. 开发规范总结

### 12.1 枚举类型规范

- 模型层枚举使用 `IntEnum`（数据库存储整数）
- 业务层枚举（如 `EmailType`）使用 `StrEnum`（API 查询参数，方便测试）
- 枚举值：模型层用整数，业务层用大写字符串

### 12.2 关联加载规范

- 单个对象查询：使用 `fetch_related`
- 列表查询：使用 `prefetch_related` 避免 N+1 问题
- 不要在 `get_or_none()` 后链式调用 `prefetch_related`
- 不要在开头和结尾重复调用 `prefetch_related`

### 12.3 多对多关联规范

- 在一侧定义 `ManyToManyField`，指定 `through` 中间表
- 在另一侧只声明类型注解 `ManyToManyRelation`
- 使用 `TYPE_CHECKING` 避免循环导入

### 12.4 Schema 设计规范

- 不使用 `Lite` 精简模型，直接引入对应的 `Base`
- 关联字段顺序：先 ID 字段，后关联对象
- 外键处理：在 create/upsert 中使用 `exclude` 正确处理
- 使用 `TYPE_CHECKING` 避免循环导入

### 12.5 模型名称规范

- 用户角色：`UserRole` 不是 `Role`
- 用户令牌：`UserToken` 不是 `Token`
- 前端路由：`FrontendRoute` 不是 `Route`

---

## 13. 故障排查

### 13.1 循环导入问题

**症状：** `ImportError: cannot import name 'Base' from partially initialized module`

**解决方案：**
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.xxx import Base as XxxBase

# 在类型注解中使用字符串引用
field: List["XxxBase"] = Field(...)
```

### 13.2 关联数据未加载

**症状：** 访问关联对象时报错或返回空

**解决方案：**
- 列表查询：确保使用 `prefetch_related('relation_name')`
- 单个查询：确保使用 `await obj.fetch_related('relation_name')`

### 13.3 N+1 查询问题

**症状：** 列表查询时数据库查询次数过多

**解决方案：**
- 将循环中的 `fetch_related` 改为查询时的 `prefetch_related`
- 示例：`await query.prefetch_related('user', 'roles')`

### 13.4 Pydantic 循环引用错误

**症状：** 
- 访问 `/openapi.json` 或 `/docs` 时返回 500 错误
- 错误信息：`PydanticUserError: TypeAdapter[...] is not fully defined`

**常见原因：**
1. Schema 模型之间存在双向引用
2. 输出模型（Out）包含了相互引用的关联字段
3. 例如：User.projects 引用 Project，Project.users 引用 User

**解决方案：**
1. **移除不必要的关联字段**（推荐）：
   ```python
   # 移除前
   class UserOut(Base):
       roles: List[RoleBase] = Field(...)
       projects: List[ProjectBase] = Field(...)  # ❌ 循环引用
   
   # 移除后
   class UserOut(Base):
       roles: List[RoleBase] = Field(...)
       # projects 字段已移除
   ```

2. **使用独立的详情接口**：
   - 列表接口：只返回基础信息
   - 详情接口：返回完整的关联信息
   
3. **使用 TYPE_CHECKING**（如果必须保留）：
   ```python
   from typing import TYPE_CHECKING
   
   if TYPE_CHECKING:
       from app.schemas.project.info import Base as ProjectBase
   
   class UserOut(Base):
       projects: List["ProjectBase"] = Field(...)
   ```

4. **调用 model_rebuild()**（最后手段）：
   ```python
   # 在所有模型定义完成后
   UserOut.model_rebuild()
   ProjectOut.model_rebuild()
   ```

**验证方法：**
```bash
# 测试 OpenAPI schema 生成
curl http://127.0.0.1:6080/openapi.json

# 访问 Swagger UI
open http://127.0.0.1:6080/docs
```

### 13.5 事件循环关闭错误

**症状：** `RuntimeError: Event loop is closed` 或 `Exception ignored in: <function Connection.__del__>`

**常见原因：**
1. 重复创建调度器或其他异步资源
2. 数据库连接在事件循环关闭后才清理
3. 关闭顺序不正确

**解决方案：**
1. 确保全局只创建一次调度器实例
2. 在 `lifespan` 的 `finally` 块中正确关闭资源
3. 关闭顺序：先关闭调度器 → 等待任务完成 → 关闭数据库连接
4. 使用 `scheduler.shutdown(wait=False)` 避免阻塞
5. 添加适当的等待时间（如 `await asyncio.sleep(0.5)`）让任务完成

**示例代码：**
```python
async def shutdown_handler():
    print('开始优雅关闭...')
    
    # 1. 先关闭调度器
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
    
    # 2. 等待任务完成
    await asyncio.sleep(0.5)
    
    # 3. 关闭数据库连接
    await Tortoise.close_connections()
```

## 15. 代码质量验证

### 15.1 模型验证

所有模型已通过导入测试：
- ✅ 用户模块：UserInfo, UserRole, UserToken, UserLog, FrontendRoute
- ✅ 项目模块：ProjectInfo, ProjectAccount, ProjectWallet, ProjectBalance
- ✅ 服务器模块：ServerCountry, ServerGroup, ServerInfo, ServerAccount
- ✅ 邮箱模块：EmailInfo

### 15.2 CRUD 验证

所有 CRUD 模块已通过导入测试：
- ✅ 用户模块：user_crud, role_crud, route_crud, token_crud, log_crud
- ✅ 项目模块：project_info_crud, project_account_crud, project_wallet_crud, project_balance_crud
- ✅ 服务器模块：server_country_crud, server_group_crud, server_info_crud, server_account_crud
- ✅ 邮箱模块：email_info_crud

### 15.3 API 验证

所有 API 路由已正确注册（共 93 个路由）：
- ✅ 用户模块：/v1/user/* (auth, user, role, route, token, log)
- ✅ 项目模块：/v1/project/* (info, account, wallet, balance)
- ✅ 服务器模块：/v1/server/* (country, group, info, account)
- ✅ 邮箱模块：/v1/mail/* (info, outlook)

### 15.4 关联加载验证

所有模块的关联加载已优化：
- ✅ 单个对象查询使用 `fetch_related()`
- ✅ 列表查询使用 `prefetch_related()` 避免 N+1 问题
- ✅ 嵌套关联使用双下划线语法
- ✅ 多对多关联正确处理

### 15.5 索引优化验证

所有模型的索引配置已优化：
- ✅ 单字段索引使用 `index=True`
- ✅ 复合索引使用 `Meta.indexes`
- ✅ 避免重复声明已有的索引
- ✅ 高选择性字段在前

### 15.6 应用启动验证

- ✅ 应用可以正常导入
- ✅ 无循环导入错误
- ✅ 无重复资源创建
- ✅ 事件循环正确管理

---

## 16. 快速参考

### 16.1 常用命令

```bash
# 验证项目配置
python scripts/verify_setup.py

# 初始化数据库
bash scripts/init_db.sh

# 更新数据库结构
bash scripts/update_db.sh

# 启动服务（开发模式）
python start.py

# 启动服务（生产模式）
uvicorn app.main:app --host 0.0.0.0 --port 6080

# 运行测试
pytest app/tests/ -v
```

### 16.2 环境变量

在 `.env` 文件中配置（参考 `.env.example` 模板）：

```env
# ==========================================
# 应用配置
# ==========================================
APP_HOST=0.0.0.0
APP_PORT=6080
APP_DEBUG=0                    # 0=生产模式, 1=调试模式（启用热重载）
APP_WORKERS=1                  # 工作进程数（生产环境可增加）

# 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# API 文档: 1=启用, 0=禁用（生产环境建议禁用）
ENABLE_DOCS=1

# CORS 配置（多个域名用逗号分隔，* 表示允许所有）
# 生产环境建议指定具体域名
CORS_ORIGINS=*

# ==========================================
# 服务器性能配置
# ==========================================
APP_LIMIT_CONCURRENCY=10000    # 最大并发连接数
APP_BACKLOG=4096               # 待处理连接队列大小
APP_TIMEOUT_KEEP_ALIVE=5       # Keep-Alive 超时时间（秒）

# ==========================================
# 数据库配置
# ==========================================
DB_ENGINE=tortoise.backends.mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=qyd
DB_PASSWORD=your_password
DB_NAME=qyd
DB_MINSIZE=20                  # 连接池最小连接数
DB_MAXSIZE=80                  # 连接池最大连接数
DB_ECHO=0                      # 是否打印 SQL 语句
DB_POOL_RECYCLE=3600           # 连接回收时间（秒）
DB_CONNECT_TIMEOUT=10          # 连接超时时间（秒）

# ==========================================
# 定时任务配置
# ==========================================
DB_CHECK_INTERVAL_MINUTES=30   # 数据库连接检查间隔（分钟）
ENABLE_EMAIL_CHECK=0           # 是否启用邮箱状态自动检查
EMAIL_CHECK_INTERVAL_HOURS=1   # 邮箱状态检查间隔（小时）

# ==========================================
# 优雅关闭配置
# ==========================================
SHUTDOWN_WAIT_SECONDS=0.5      # 关闭时等待任务完成的时间（秒）
```

**配置说明：**

- **开发环境**：设置 `APP_DEBUG=1` 启用热重载，`LOG_LEVEL=DEBUG` 查看详细日志
- **生产环境**：设置 `APP_DEBUG=0`，`ENABLE_DOCS=0` 禁用 API 文档，`CORS_ORIGINS` 指定具体域名
- **性能调优**：根据服务器配置调整 `DB_MINSIZE`、`DB_MAXSIZE`、`APP_WORKERS` 等参数

### 16.3 项目结构速查

```
backend/
├── app/
│   ├── main.py              # 应用入口
│   ├── models/              # 数据模型
│   ├── schemas/             # API Schema
│   ├── crud/                # 数据库操作
│   ├── apis/v1/             # API 路由
│   ├── clients/             # 外部客户端
│   ├── core/                # 核心配置
│   ├── utils/               # 工具函数
│   └── tests/               # 测试文件
├── migrations/              # 数据库迁移
├── scripts/                 # 辅助脚本
│   ├── verify_setup.py      # 验证脚本
│   ├── check_db_tables.py   # 检查数据库表
│   ├── test_db_connection.py # 测试数据库连接
│   ├── cleanup_logs.py      # 清理日志
│   ├── analyze_logs.py      # 分析日志
│   └── *.sh                 # Shell 脚本
├── examples/                # 示例代码
├── start.py                 # 启动脚本
└── requirements.txt         # 依赖列表
```

### 16.4 API 文档地址

启动服务后访问：

- Swagger UI: `http://127.0.0.1:6080/docs`
- ReDoc: `http://127.0.0.1:6080/redoc`

---

## 17. 日志系统

### 17.1 日志系统概述

项目已集成完整的日志系统，支持：
- ✅ 每个模块独立日志文件
- ✅ 每2小时自动滚动，保留30天
- ✅ 自动压缩旧日志（节省80-90%空间）
- ✅ 自动清理超过30天的日志
- ✅ 多进程安全写入
- ✅ 敏感信息自动过滤
- ✅ API 请求自动记录

### 17.2 快速使用

#### 基础日志记录

```python
from app.utils.logs import getLogger

logger = getLogger('user')
logger.info("用户登录成功")
logger.error("操作失败", exc_info=True)
```

#### API 日志记录

```python
from app.utils.logs import getLogger, log_api_call

logger = getLogger('api')
log_api_call(
    logger=logger,
    user_id="user123",
    endpoint="/api/v1/users",
    method="GET",
    params={"id": 123},
    response_status=200,
    client_ip="192.168.1.100"
)
```

#### 使用装饰器

```python
from app.utils.log_decorator import log_function_call, log_exception

@log_function_call(logger_name="user", log_args=True)
async def create_user(username: str):
    return {"id": 1, "username": username}

@log_exception(logger_name="error")
def risky_operation():
    # 异常会自动记录
    pass
```

### 17.3 日志文件结构

```
logs/
├── api.log                     # API 请求日志（自动记录）
├── app.log                     # 应用日志
├── scheduler.log               # 定时任务日志
├── database.log                # 数据库日志
├── user.log                    # 用户模块日志
├── project.log                 # 项目模块日志
├── server.log                  # 服务器模块日志
├── mail.log                    # 邮箱模块日志
├── user.log.2026-01-21_00      # 滚动日志（未压缩）
└── user.log.2026-01-20_22.gz   # 压缩日志
```

### 17.4 日志管理命令

```bash
# 测试日志系统
python app/tests/test_logging_system.py

# 运行示例
python examples/log_usage_examples.py

# 清理日志（保留30天）
python scripts/cleanup_logs.py

# 分析日志
python scripts/analyze_logs.py

# 使用管理脚本
./scripts/log_manager.sh help
./scripts/log_manager.sh view      # 实时查看
./scripts/log_manager.sh analyze   # 分析统计
./scripts/log_manager.sh clean     # 清理旧日志
```

### 17.5 查看日志

```bash
# 实时查看日志
tail -f logs/api.log

# 查看多个日志
tail -f logs/{user,project,api}.log

# 查看压缩日志
zless logs/user.log.2026-01-20_22.gz

# 搜索日志
grep "错误" logs/user.log
zgrep "错误" logs/user.log.*.gz
```

### 17.6 定时清理

使用 crontab 设置定时清理：

```bash
# 编辑 crontab
crontab -e

# 每天凌晨3点清理日志
0 3 * * * cd /path/to/backend && python scripts/cleanup_logs.py
```

### 17.7 日志模块命名规范

```python
# 应用层
app_logger = getLogger('app')
api_logger = getLogger('api')

# 业务模块
user_logger = getLogger('user')
project_logger = getLogger('project')
server_logger = getLogger('server')
mail_logger = getLogger('mail')

# 数据层
user_crud_logger = getLogger('user_crud')
db_logger = getLogger('database')

# 系统层
scheduler_logger = getLogger('scheduler')
error_logger = getLogger('error')
```

---

## 18. API 404 处理

### 18.1 统一的空结果处理

所有列表查询接口在没有数据时统一返回 HTTP 404 错误，而不是返回空数组。

**修改前：**
```json
HTTP 200 OK
{
  "message": "成功",
  "count": -1,
  "num": 0,
  "items": []
}
```

**修改后：**
```json
HTTP 404 Not Found
{
  "detail": "未查询到数据"
}
```

### 18.2 受影响的接口

所有列表查询接口：
- `GET /v1/mail/info`
- `GET /v1/project/account`
- `GET /v1/project/balance`
- `GET /v1/project/info`
- `GET /v1/project/wallet`
- `GET /v1/server/account`
- `GET /v1/server/country`
- `GET /v1/server/group`
- `GET /v1/server/info`
- `GET /v1/user/log`
- `GET /v1/user/role`
- `GET /v1/user/route`
- `GET /v1/user/token`
- `GET /v1/user`

### 18.3 前端适配建议

```javascript
// 推荐的前端处理方式
try {
  const response = await fetch('/v1/server/account');
  if (response.status === 404) {
    // 显示空状态或"未找到数据"
    showEmptyState();
    return;
  }
  const data = await response.json();
  // 处理数据
  displayData(data.items);
} catch (error) {
  // 处理错误
  handleError(error);
}
```

---

## 19. 联系与贡献

如有问题或建议，请联系项目维护者。

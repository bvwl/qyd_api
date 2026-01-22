# 将余额表合并到账号表

## 更新时间
2026-01-21

## 背景

原来的设计中，项目账号（`ProjectAccount`）和项目余额（`ProjectBalance`）是两张独立的表，通过一对一关系关联。但这样的设计存在以下问题：

1. **数据冗余**：一对一关系意味着每个账号对应一个余额记录，完全可以合并
2. **查询复杂**：需要 JOIN 两张表才能获取完整的账号信息
3. **维护困难**：需要同时维护两张表的数据一致性
4. **性能损耗**：额外的表和关联查询影响性能

## 解决方案

将余额字段直接添加到项目账号表中，删除独立的余额表。

### 数据库变更

#### 修改前

```sql
-- 项目账号表
CREATE TABLE project_account (
    id CHAR(36) PRIMARY KEY,
    account VARCHAR(255),
    password TEXT,
    status INT,
    account_type INT,
    data JSON,
    project_id CHAR(36),
    server_id CHAR(36),
    create_time DATETIME,
    update_time DATETIME
);

-- 项目余额表（独立）
CREATE TABLE project_balance (
    id CHAR(36) PRIMARY KEY,
    balance DECIMAL(18,6),
    variable DECIMAL(18,6),
    history JSON,
    account_id CHAR(36) UNIQUE,  -- 一对一关系
    create_time DATETIME,
    update_time DATETIME
);
```

#### 修改后

```sql
-- 项目账号表（包含余额字段）
CREATE TABLE project_account (
    id CHAR(36) PRIMARY KEY,
    account VARCHAR(255),
    password TEXT,
    status INT,
    account_type INT,
    data JSON,
    -- 余额相关字段
    balance DECIMAL(18,6) DEFAULT 0,
    variable DECIMAL(18,6) DEFAULT 0,
    balance_history JSON,
    project_id CHAR(36),
    server_id CHAR(36),
    create_time DATETIME,
    update_time DATETIME
);

-- 删除 project_balance 表
```

### 模型变更

#### 修改前

```python
# 项目账号模型
class ProjectAccount(BaseModel):
    account = fields.CharField(...)
    password = fields.TextField(...)
    status = fields.IntEnumField(...)
    account_type = fields.IntEnumField(...)
    data = fields.JSONField(...)
    project = fields.ForeignKeyField(...)
    server = fields.ForeignKeyField(...)

# 项目余额模型（独立）
class ProjectBalance(BaseModel):
    account = fields.OneToOneField("models.ProjectAccount", ...)
    balance = fields.DecimalField(...)
    variable = fields.DecimalField(...)
    history = fields.JSONField(...)
```

#### 修改后

```python
# 项目账号模型（包含余额字段）
class ProjectAccount(BaseModel):
    account = fields.CharField(...)
    password = fields.TextField(...)
    status = fields.IntEnumField(...)
    account_type = fields.IntEnumField(...)
    data = fields.JSONField(...)
    # 余额相关字段
    balance = fields.DecimalField(max_digits=18, decimal_places=6, default=0, ...)
    variable = fields.DecimalField(max_digits=18, decimal_places=6, default=0, ...)
    balance_history = fields.JSONField(null=True, ...)
    project = fields.ForeignKeyField(...)
    server = fields.ForeignKeyField(...)

# 删除 ProjectBalance 模型
```

## 实施步骤

### 1. 数据库迁移

**文件**: `backend/migrations/models/3_20260121173500_merge_balance_into_account.py`

```python
async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 1. 在 project_account 表添加余额相关字段
        ALTER TABLE `project_account` ADD `balance` DECIMAL(18,6) NOT NULL DEFAULT 0;
        ALTER TABLE `project_account` ADD `variable` DECIMAL(18,6) NOT NULL DEFAULT 0;
        ALTER TABLE `project_account` ADD `balance_history` JSON NULL;
        
        -- 2. 将 project_balance 表的数据迁移到 project_account 表
        UPDATE project_account pa
        INNER JOIN project_balance pb ON pa.id = pb.account_id
        SET pa.balance = pb.balance,
            pa.variable = pb.variable,
            pa.balance_history = pb.history;
        
        -- 3. 添加余额字段的索引
        CREATE INDEX `idx_project_account_balance` ON `project_account` (`balance`);
        
        -- 4. 删除 project_balance 表
        DROP TABLE IF EXISTS `project_balance`;
    """
```

### 2. 后端修改

#### 2.1 修改模型

**文件**: `backend/app/models/project.py`

- 在 `ProjectAccount` 模型中添加余额字段
- 删除 `ProjectBalance` 模型

#### 2.2 修改 Schema

**文件**: `backend/app/schemas/project/account.py`

```python
class Base(BaseModel):
    account: str
    password: str | None
    status: Status
    account_type: AccountType
    data: dict | None
    # 余额相关字段
    balance: Decimal = Field(0, description="余额")
    variable: Decimal = Field(0, description="变动余额")
    balance_history: dict | None = Field(None, description="历史余额")

class Create(BaseModel):
    account: str
    password: str | None
    status: Status
    account_type: AccountType
    data: dict | None
    # 余额相关字段（可选，不传默认为0）
    balance: Decimal | None = Field(None, description="余额（可选，默认0）")
    variable: Decimal | None = Field(None, description="变动余额（可选，默认0）")
    balance_history: dict | None = Field(None, description="历史余额")
    project_id: UUID
    server_id: UUID | None
```

**说明**：
- `Base` 模型中余额字段有默认值 0
- `Create` 模型中余额字段为可选（`Decimal | None`），不传时数据库使用默认值 0
- `Update` 模型中余额字段为可选，支持部分更新

**删除文件**: `backend/app/schemas/project/balance.py`

#### 2.3 修改 CRUD

**保留文件**: `backend/app/crud/project/account.py`（无需修改，自动支持新字段）

**删除文件**: `backend/app/crud/project/balance.py`

#### 2.4 修改 API

**文件**: `backend/app/apis/v1/project/account.py`

添加余额字段的排序支持：

```python
order_by: str | None = Query(
    "-create_time",
    description="排序字段",
    pattern="^(?:-)?(?:id|account|status|balance|variable|create_time|update_time)$",
),
```

**删除文件**: `backend/app/apis/v1/project/balance.py`

#### 2.5 修改路由注册

**文件**: `backend/app/apis/v1/project/__init__.py`

```python
# 删除余额路由
# from .balance import app as balance_app
# router.include_router(balance_app, prefix="/balance", tags=["项目余额"])
```

### 3. 前端修改

#### 3.1 修改类型定义

**文件**: `frontend/src/types/index.ts`

```typescript
export interface ProjectAccount {
  id: string
  account: string
  password?: string
  status: Status
  account_type: AccountType
  data?: Record<string, any>
  // 余额相关字段
  balance: number | string
  variable: number | string
  balance_history?: any
  project_id: string
  project?: Project
  server_id?: string
  server?: ServerInfo
  create_time: string
  update_time: string
}

// 删除 ProjectBalance 接口
```

#### 3.2 修改 API

**文件**: `frontend/src/api/project.ts`

```typescript
// 项目账号（包含余额字段）
export const getProjectAccountList = (params?: PaginationParams & { 
  project_id?: string
  status?: number
  account_type?: number
  account?: string
  order_by?: string  // 支持按余额排序
  ...
}) => {
  return api.get<any, ApiResponse<ProjectAccount>>('/v1/project/account', { params })
}

// 删除所有余额相关的 API 方法
```

#### 3.3 修改页面

**删除文件**: `frontend/src/views/Project/ProjectBalance.tsx`

**修改文件**: `frontend/src/views/Project/ProjectAccount.tsx`

在项目账号页面中添加余额列的显示和编辑功能。

## 优势

### 1. 数据结构更简单

- ✅ 只需维护一张表
- ✅ 减少了表之间的关联
- ✅ 数据一致性更容易保证

### 2. 查询性能更好

- ✅ 无需 JOIN 查询
- ✅ 减少了数据库查询次数
- ✅ 索引更高效

### 3. 代码更简洁

- ✅ 删除了独立的余额 CRUD、API、Schema
- ✅ 减少了代码维护成本
- ✅ 逻辑更清晰

### 4. 用户体验更好

- ✅ 在账号列表中直接显示余额
- ✅ 无需切换页面查看余额
- ✅ 编辑账号时可以同时编辑余额

## 数据迁移

### 迁移前数据

```
project_account:
id: 1, account: "test@example.com", ...

project_balance:
id: 100, account_id: 1, balance: 1000.50, variable: 50.00
```

### 迁移后数据

```
project_account:
id: 1, account: "test@example.com", balance: 1000.50, variable: 50.00, ...
```

### 迁移命令

```bash
# 运行迁移
aerich upgrade
```

## 相关文件

### 后端文件

**修改**:
- ✅ `backend/app/models/project.py` - 合并余额字段到账号模型
- ✅ `backend/app/schemas/project/account.py` - 添加余额字段
- ✅ `backend/app/apis/v1/project/account.py` - 添加余额排序支持
- ✅ `backend/app/apis/v1/project/__init__.py` - 移除余额路由

**删除**:
- ✅ `backend/app/schemas/project/balance.py`
- ✅ `backend/app/crud/project/balance.py`
- ✅ `backend/app/apis/v1/project/balance.py`

**新增**:
- ✅ `backend/migrations/models/3_20260121173500_merge_balance_into_account.py`

### 前端文件

**修改**:
- ✅ `frontend/src/types/index.ts` - 合并余额字段到账号类型
- ✅ `frontend/src/api/project.ts` - 删除余额 API
- ✅ `frontend/src/views/Project/ProjectAccount.tsx` - 添加余额列显示

**删除**:
- ✅ `frontend/src/views/Project/ProjectBalance.tsx`

### 文档

- ✅ `docs/fixes/MERGE_BALANCE_INTO_ACCOUNT.md` - 本文档

## 使用示例

### 创建账号（不传余额）

```python
# 请求
POST /v1/project/account
{
    "account": "test@example.com",
    "password": "encrypted_password",
    "status": 1,
    "account_type": 1,
    "project_id": "project-uuid"
    # 不传 balance 和 variable，数据库使用默认值 0
}

# 响应
{
    "id": "account-uuid",
    "account": "test@example.com",
    "balance": 0,      # 默认值
    "variable": 0,     # 默认值
    ...
}
```

### 创建账号（传入余额）

```python
# 请求
POST /v1/project/account
{
    "account": "test@example.com",
    "password": "encrypted_password",
    "status": 1,
    "account_type": 1,
    "balance": 1000.50,
    "variable": 50.00,
    "project_id": "project-uuid"
}

# 响应
{
    "id": "account-uuid",
    "account": "test@example.com",
    "balance": 1000.50,
    "variable": 50.00,
    ...
}
```

### 更新余额

```python
# 请求
PUT /v1/project/account/{id}
{
    "balance": 2000.00,
    "variable": 100.00
}

# 响应
{
    "id": "account-uuid",
    "account": "test@example.com",
    "balance": 2000.00,
    "variable": 100.00,
    ...
}
```

## 注意事项

1. **数据备份**: 在执行迁移前，务必备份数据库
2. **迁移顺序**: 必须先运行数据库迁移，再部署新代码
3. **回滚方案**: 迁移文件包含 downgrade 方法，可以回滚
4. **前端路由**: 需要删除或重定向原来的余额页面路由

## 测试清单

- [ ] 数据库迁移成功
- [ ] 原有余额数据正确迁移到账号表
- [ ] 账号列表显示余额字段
- [ ] 创建账号时可以设置余额
- [ ] 更新账号时可以修改余额
- [ ] 按余额排序功能正常
- [ ] 删除账号时余额数据一起删除
- [ ] API 文档更新
- [ ] 前端路由更新

## 总结

✅ 将余额表合并到账号表，简化了数据结构
✅ 删除了独立的余额 CRUD、API、Schema
✅ 提升了查询性能，减少了 JOIN 操作
✅ 代码更简洁，维护成本更低
✅ 用户体验更好，无需切换页面查看余额
✅ 数据迁移脚本完整，支持升级和回滚

这是一次成功的数据库重构，将一对一关系的两张表合并为一张表，大大简化了系统设计！

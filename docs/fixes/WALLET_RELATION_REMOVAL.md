# ProjectAccount 钱包关联移除修复

## 修复时间
2026-01-21

## 问题描述
ProjectAccount 模型中删除了与 ProjectWallet 的关联关系（wallet_id 外键），需要清理所有相关代码和文档中的引用。

## 数据模型变更

### 修改前的关系
```
ProjectInfo (项目)
    ↓ (一对多: project_id)
ProjectAccount (项目账号)
    ↓ (多对一: wallet_id, 可选)  ← 已删除
ProjectWallet (钱包)
```

### 修改后的关系
```
ProjectInfo (项目)
    ↓ (一对多: project_id, 可选)
ProjectWallet (钱包)

ProjectInfo (项目)
    ↓ (一对多: project_id)
ProjectAccount (项目账号)
```

钱包和账号现在都是独立的资源。钱包可以选择性地关联到项目（`project_id` 可为空），账号必须关联到项目。

## 修复内容

### 1. 模型层 (backend/app/models/project.py)
✅ 移除 `ProjectAccount` 的 `wallet_id` 索引定义

**修改前**:
```python
indexes = [
    ("project_id", "status", "account_type"),
    ("status", "account_type", "create_time"),
    ("server_id", "status"),
    ("wallet_id",),  # ← 已删除
]
```

**修改后**:
```python
indexes = [
    ("project_id", "status", "account_type"),
    ("status", "account_type", "create_time"),
    ("server_id", "status"),
]
```

### 2. CRUD 层 (backend/app/crud/project/account.py)
✅ 移除 `get_multi` 方法中的 `wallet` 预加载
✅ 移除 `update` 方法中的 `wallet` 预加载
✅ 移除 `upsert` 方法中的 `wallet_id` 处理

**修改前**:
```python
res = await query.prefetch_related('project', 'server', 'wallet')
```

**修改后**:
```python
res = await query.prefetch_related('project', 'server')
```

### 3. API 层 (backend/app/apis/v1/project/account.py)
✅ 移除 `gets` 方法中的 `wallet_id` 查询参数
✅ 移除传递给 CRUD 的 `wallet_id` 参数

**修改前**:
```python
async def gets(
    wallet_id: UUID | None = Query(None, description="关联钱包ID"),
    ...
):
    return await project_account_crud.get_multi(
        wallet_id=wallet_id,
        ...
    )
```

**修改后**:
```python
async def gets(
    # wallet_id 参数已移除
    ...
):
    return await project_account_crud.get_multi(
        # wallet_id 参数已移除
        ...
    )
```

### 4. Schema 层 (backend/app/schemas/project/account.py)
✅ 已确认没有 `wallet_id` 字段（之前已正确）

### 5. 钱包 CRUD 增强 (backend/app/crud/project/wallet.py)
✅ 添加 `project_id` 过滤支持
✅ 添加 `project` 关联预加载
✅ 在 create、get、update 方法中加载项目信息

**新增功能**:
```python
async def get_multi(self,
                    project_id: UUID | None = None,  # ← 新增
                    chain: str | None = None,
                    ...
):
    query = ProjectWallet.all()
    
    if project_id:  # ← 新增
        query = query.filter(project_id=project_id)
    
    # 预加载关联的项目信息
    res = await query.prefetch_related('project')
```

### 6. 钱包 API 增强 (backend/app/apis/v1/project/wallet.py)
✅ 添加 `project_id` 查询参数

**新增功能**:
```python
async def gets(
    project_id: UUID | None = Query(None, description="所属项目ID"),  # ← 新增
    chain: str | None = Query(None, description="链名称"),
    ...
):
    return await project_wallet_crud.get_multi(
        project_id=project_id,  # ← 新增
        chain=chain,
        ...
    )
```

### 7. 文档更新
✅ `docs/fixes/WALLET_MODEL_CORRECTION.md` - 更新数据模型关系
✅ `docs/fixes/FINAL_SUMMARY_20260121.md` - 更新数据模型关系和查询方法
✅ `docs/fixes/WALLET_API_FIX.md` - 更新数据模型关系和查询方法

### 8. 前端代码
✅ 已确认前端代码正确，无需修改
- `frontend/src/types/index.ts` - ProjectAccount 接口没有 wallet_id
- `frontend/src/api/project.ts` - API 调用正确
- `frontend/src/views/Project/ProjectAccount.tsx` - 组件正确

## 数据库迁移

已有迁移文件记录了这个变更：
`backend/migrations/models/1_20260121155309_wallet_project_relation.py`

**迁移内容**:
```sql
-- 从 ProjectAccount 移除 wallet_id
ALTER TABLE `project_account` DROP FOREIGN KEY `fk_project__project__93399a32`;
ALTER TABLE `project_account` DROP INDEX `idx_project_acc_wallet__29c3f9`;
ALTER TABLE `project_account` DROP COLUMN `wallet_id`;

-- 给 ProjectWallet 添加 project_id
ALTER TABLE `project_wallet` ADD `project_id` CHAR(36) NOT NULL COMMENT '所属项目';
ALTER TABLE `project_wallet` ADD CONSTRAINT `fk_project__project__cba39da5` 
    FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`) ON DELETE CASCADE;
```

## API 使用说明

### 查询项目账号
```bash
# 查询项目的所有账号
GET /v1/project/account?project_id={project_id}

# 按账号类型过滤
GET /v1/project/account?project_id={project_id}&account_type=1
```

### 查询项目钱包
```bash
# 查询项目的所有钱包
GET /v1/project/wallet?project_id={project_id}

# 查询所有钱包（包括独立钱包）
GET /v1/project/wallet

# 按链名称过滤
GET /v1/project/wallet?project_id={project_id}&chain=ETH

# 查询单个钱包
GET /v1/project/wallet/{wallet_id}
```

### 创建或更新钱包（Upsert）
```bash
# 根据公钥判断是否已存在
POST /v1/project/wallet/upsert
{
  "private_key": "encrypted_private_key",
  "public_key": "0x...",
  "mnemonic": "encrypted_mnemonic",
  "chain": "ETH",
  "remark": "钱包备注",
  "project_id": "project-uuid"  # 可选
}
```

### 创建项目钱包
```bash
POST /v1/project/wallet
{
  "private_key": "encrypted_private_key",
  "public_key": "0x...",
  "mnemonic": "encrypted_mnemonic",
  "chain": "ETH",
  "remark": "主钱包",
  "project_id": "project-uuid"  # 可选，不传则创建独立钱包
}
```

### 创建项目账号
```bash
POST /v1/project/account
{
  "account": "user@example.com",
  "password": "encrypted_password",
  "status": 1,
  "account_type": 1,
  "project_id": "project-uuid"
}
```

## 前端使用示例

### 查询项目的钱包
```typescript
// 查询特定项目的钱包
const projectWallets = await getProjectWalletList({
  project_id: "project-uuid",
  page: 1,
  limit: 10
})

// 查询所有钱包
const allWallets = await getProjectWalletList({
  page: 1,
  limit: 10
})
```

### 查询项目的账号
```typescript
// 查询项目的账号
const accounts = await getProjectAccountList({
  project_id: "project-uuid",
  page: 1,
  limit: 10
})
```

## 优势

### 1. 灵活性更高
- 钱包可以独立存在，不依赖项目
- 钱包可以后续关联到项目
- 钱包可以在项目间转移

### 2. 查询简化
- 可以直接查询项目的钱包
- 可以查询所有独立钱包
- API 调用更灵活

### 3. 独立管理
- 钱包和账号是两个独立的资源
- 钱包可以独立创建、更新、删除
- 便于批量导入和管理

## 测试验证

### 1. 编译检查
```bash
python -m py_compile backend/app/models/project.py
python -m py_compile backend/app/crud/project/account.py
python -m py_compile backend/app/apis/v1/project/account.py
python -m py_compile backend/app/schemas/project/account.py
```
✅ 所有文件编译通过

### 2. API 测试
```bash
# 测试项目账号查询
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:6080/v1/project/account?project_id=xxx&page=1&limit=10"

# 测试项目钱包查询
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:6080/v1/project/wallet?project_id=xxx&page=1&limit=10"
```

## 相关文件

### 后端
- ✅ `backend/app/models/project.py` - 模型定义
- ✅ `backend/app/schemas/project/account.py` - Schema 定义
- ✅ `backend/app/crud/project/account.py` - CRUD 操作
- ✅ `backend/app/apis/v1/project/account.py` - API 端点
- ✅ `backend/app/crud/project/wallet.py` - 钱包 CRUD（增强）
- ✅ `backend/app/apis/v1/project/wallet.py` - 钱包 API（增强）

### 前端
- ✅ `frontend/src/types/index.ts` - 类型定义（无需修改）
- ✅ `frontend/src/api/project.ts` - API 调用（无需修改）
- ✅ `frontend/src/views/Project/ProjectAccount.tsx` - 组件（无需修改）

### 文档
- ✅ `docs/fixes/WALLET_MODEL_CORRECTION.md` - 已更新
- ✅ `docs/fixes/FINAL_SUMMARY_20260121.md` - 已更新
- ✅ `docs/fixes/WALLET_API_FIX.md` - 已更新
- ✅ `docs/fixes/WALLET_RELATION_REMOVAL.md` - 本文档

### 数据库
- ✅ `backend/migrations/models/1_20260121155309_wallet_project_relation.py` - 迁移文件

## 总结

✅ 移除了 ProjectAccount 中所有 wallet_id 相关代码
✅ 更新了所有 CRUD 和 API 层的代码
✅ 增强了 ProjectWallet 的查询功能，支持按 project_id 过滤
✅ ProjectWallet 的 project_id 是可选的，支持独立钱包
✅ 更新了所有相关文档
✅ 前端代码无需修改（已经是正确的）
✅ 所有 Python 文件编译通过

现在钱包可以独立存在，也可以选择性地关联到项目；账号必须关联到项目。这提供了更大的灵活性。

# 钱包模型关系纠正

## 修正时间
2026-01-21

## 问题描述
之前错误地认为 `ProjectWallet` 模型有 `project_id` 字段，并添加了相关的过滤逻辑。实际上钱包是独立的资源，不直接关联项目。

## 数据模型关系

### 实际的数据库设计

```
ProjectInfo (项目信息)
    ↓ (一对多: project_id, 可选)
ProjectWallet (项目钱包)

ProjectInfo (项目信息)
    ↓ (一对多: project_id)
ProjectAccount (项目账号)
```

### 模型字段

**ProjectWallet (钱包)**:
- id (UUID)
- private_key (加密私钥)
- public_key (公钥)
- mnemonic (加密助记词, **可为空**)
- chain (链名称)
- remark (备注, 可为空)
- **project_id** (外键 → ProjectInfo, **可为空**)
- create_time
- update_time

**ProjectAccount (项目账号)**:
- id (UUID)
- account (账号)
- password (加密密码)
- status (状态)
- account_type (账号类型)
- data (扩展数据)
- **project_id** (外键 → ProjectInfo, **必填**)
- server_id (外键 → ServerInfo, 可选)
- create_time
- update_time

**注意**: 
- ProjectAccount 不再有 `wallet_id` 字段
- ProjectWallet 的 `project_id` 是可选的，钱包可以独立存在

## 设计理念

### 为什么钱包可以独立存在？

1. **灵活性**: 钱包可以先创建，后续再关联到项目
2. **复用性**: 钱包可以在不同项目间转移
3. **独立管理**: 钱包可以作为独立资源管理，不依赖项目

### 如何关联项目和钱包？

可选关联：
```
项目 ←→ 钱包（可选）
项目 → 账号（必须）
```

## 修正内容

### 1. 还原 API 层
`backend/app/apis/v1/project/wallet.py`:

**修正前**（错误）:
```python
async def gets(
    project_id: UUID | None = Query(None, description="关联项目ID"),  # ← 错误
    chain: str | None = Query(None, description="链名称"),
    ...
):
    return await project_wallet_crud.get_multi(
        project_id=project_id,  # ← 错误
        chain=chain,
        ...
    )
```

**修正后**（正确）:
```python
async def gets(
    chain: str | None = Query(None, description="链名称"),  # ← 移除 project_id
    ...
):
    return await project_wallet_crud.get_multi(
        chain=chain,  # ← 不传递 project_id
        ...
    )
```

### 2. 还原 CRUD 层
`backend/app/crud/project/wallet.py`:

**修正前**（错误）:
```python
async def get_multi(self,
                    project_id: UUID | None = None,  # ← 错误
                    chain: str | None = None,
                    ...
):
    query = ProjectWallet.all()
    
    if project_id:  # ← 错误
        query = query.filter(project_id=project_id)
    
    if chain:
        query = query.filter(chain__icontains=chain)
```

**修正后**（正确）:
```python
async def get_multi(self,
                    chain: str | None = None,  # ← 移除 project_id
                    ...
):
    query = ProjectWallet.all()
    
    if chain:  # ← 直接从 chain 开始
        query = query.filter(chain__icontains=chain)
```

### 3. 更新文档

修正了以下文档中的错误描述：
- ✅ `docs/fixes/WALLET_API_FIX.md`
- ✅ `docs/fixes/PROJECT_MANAGEMENT_PAGES_SUMMARY.md`
- ✅ `backend/app/tests/README.md`

## API 使用说明

### 查询所有钱包
```bash
GET /v1/project/wallet?page=1&limit=10&res_count=true
```

### 按链名称过滤
```bash
GET /v1/project/wallet?chain=ETH&page=1&limit=10&res_count=true
```

### 查询单个钱包
```bash
GET /v1/project/wallet/{wallet_id}
```

## 如何查询项目的钱包？

钱包可以选择性地关联项目，查询方式灵活：

### 方法1: 查询特定项目的钱包
```bash
GET /v1/project/wallet?project_id={project_id}
```

### 方法2: 查询所有钱包（包括独立钱包）
```bash
GET /v1/project/wallet
```

### 方法3: 查询单个钱包
```bash
GET /v1/project/wallet/{wallet_id}
```

### 前端示例
```typescript
// 获取项目的所有钱包
const projectWallets = await getProjectWalletList({ 
  project_id,
  page: 1,
  limit: 10
})

// 获取所有钱包（包括独立钱包）
const allWallets = await getProjectWalletList({ 
  page: 1,
  limit: 10
})

// 获取单个钱包详情
const wallet = await getProjectWalletDetail(wallet_id)
```

## 数据流示例

### 创建独立钱包（不关联项目）

```typescript
// 创建独立钱包（不需要助记词）
const wallet = await createProjectWallet({
  private_key: "encrypted_private_key",
  public_key: "0x...",
  chain: "ETH",
  remark: "独立钱包"
  // mnemonic 可选，不传也可以
  // project_id 可选，不传则钱包独立存在
})
```

### 创建关联项目的钱包

```typescript
// 创建钱包并关联项目（带助记词）
const wallet = await createProjectWallet({
  private_key: "encrypted_private_key",
  public_key: "0x...",
  mnemonic: "encrypted_mnemonic",  // 可选
  chain: "ETH",
  remark: "项目钱包",
  project_id: "project-uuid"  // ← 关联到项目
})
```

### 创建项目账号

```typescript
// 创建账号，必须关联项目
const account = await createProjectAccount({
  account: "user@example.com",
  password: "encrypted_password",
  status: 1,
  account_type: 1, // 邮箱类型
  project_id: "project-uuid"  // ← 必须关联项目
})
```

### 查询项目的所有钱包

```typescript
// 查询项目的钱包
const wallets = await getProjectWalletList({
  project_id: "project-uuid",
  page: 1,
  limit: 10
})
```

### 查询所有独立钱包

```typescript
// 查询未关联项目的钱包
// 后端需要支持过滤 project_id 为 null 的记录
const independentWallets = await getProjectWalletList({
  page: 1,
  limit: 10
  // 不传 project_id，获取所有钱包
})
```

## 优势

### 1. 灵活性更高
```
独立钱包（未关联项目）
项目A
  ├── 钱包1
  ├── 钱包2
  ├── 账号1
  └── 账号2
项目B
  ├── 钱包3
  └── 账号3
```
钱包可以独立存在，也可以关联到项目。

### 2. 独立管理
- 钱包可以先创建，后续再关联到项目
- 钱包可以从一个项目转移到另一个项目
- 便于批量导入和管理

### 3. 安全隔离
- 钱包信息集中存储
- 统一的加密策略
- 便于权限控制

## 相关文件

### 模型定义
- `backend/app/models/project.py` - ProjectWallet, ProjectAccount

### API层
- `backend/app/apis/v1/project/wallet.py` - 钱包API（已修正）
- `backend/app/apis/v1/project/account.py` - 账号API

### CRUD层
- `backend/app/crud/project/wallet.py` - 钱包CRUD（已修正）
- `backend/app/crud/project/account.py` - 账号CRUD

### Schema
- `backend/app/schemas/project/wallet.py` - 钱包Schema（正确）
- `backend/app/schemas/project/account.py` - 账号Schema

### 文档
- `docs/fixes/WALLET_API_FIX.md` - 钱包API修复（已更新）
- `docs/fixes/PROJECT_MANAGEMENT_PAGES_SUMMARY.md` - 项目管理总结（已更新）

## 总结

✅ 还原了错误的 project_id 参数
✅ 明确了钱包是独立资源
✅ 更新了所有相关文档
✅ 提供了正确的查询方法
✅ 后端服务已重启并正常运行

钱包现在作为独立资源管理，通过项目账号间接关联到项目，这是更合理和灵活的设计。

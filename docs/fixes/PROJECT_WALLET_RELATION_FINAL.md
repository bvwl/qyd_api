# 项目钱包关联关系最终修复

## 修复时间
2026-01-21

## 数据模型关系

### 最终的数据模型关系
```
ProjectInfo (项目信息)
    ↓ (一对多: project_id, 可选)
ProjectWallet (项目钱包)

ProjectInfo (项目信息)
    ↓ (一对多: project_id, 必须)
ProjectAccount (项目账号)
```

### 关键特性
- **ProjectWallet**: `project_id` 是**可选的**（`null=True`），钱包可以独立存在
- **ProjectAccount**: `project_id` 是**必须的**，账号必须关联到项目
- **ProjectAccount** 不再有 `wallet_id` 字段

## 修改内容

### 1. Schema 层 (backend/app/schemas/project/wallet.py)

✅ **Create 模型** - project_id 可选
```python
class Create(Base):
    """
    创建项目钱包请求模型
    """
    project_id: UUID | None = Field(None, description="所属项目ID")
```

✅ **Update 模型** - project_id 可选
```python
class Update(BaseModel):
    """
    更新项目钱包请求模型，支持部分更新
    """
    private_key: str | None = Field(None, description="私钥（AES加密）")
    public_key: str | None = Field(None, description="公钥")
    mnemonic: str | None = Field(None, description="助记词（AES加密）")
    chain: str | None = Field(None, description="链")
    remark: str | None = Field(None, description="备注")
    project_id: UUID | None = Field(None, description="所属项目ID")
```

✅ **Out 模型** - 包含可选的项目信息
```python
class Out(Base):
    """
    项目钱包输出模型
    """
    message: str = Field("成功", description="提示信息")
    id: UUID = Field(..., description="钱包ID")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")
    
    project_id: UUID | None = Field(None, description="所属项目ID")
    project: ProjectInfoBase | None = Field(None, description="项目信息")
```

### 2. CRUD 层 (backend/app/crud/project/wallet.py)

✅ **create 方法** - 预加载项目信息
```python
async def create(self, item: Create) -> Out:
    res = await ProjectWallet.create(**item.model_dump())
    if not res:
        raise HTTPException(status_code=500, detail='创建失败')
    await res.fetch_related('project')
    return Out.model_validate(res)
```

✅ **get 方法** - 预加载项目信息
```python
async def get(self, id: UUID) -> Out:
    res = await ProjectWallet.get_or_none(id=id)
    if not res:
        raise HTTPException(status_code=404, detail='数据不存在')
    await res.fetch_related('project')
    return Out.model_validate(res)
```

✅ **get_multi 方法** - 支持按 project_id 过滤
```python
async def get_multi(self,
                    project_id: UUID | None = None,  # ← 支持过滤
                    chain: str | None = None,
                    ...
):
    query = ProjectWallet.all()
    
    if project_id:
        query = query.filter(project_id=project_id)
    
    if chain:
        query = query.filter(chain__icontains=chain)
    
    # 预加载关联的项目信息
    res = await query.prefetch_related('project')
    ...
```

✅ **update 方法** - 预加载项目信息
```python
async def update(self, id: UUID, item: Update) -> Out:
    res = await ProjectWallet.get_or_none(id=id)
    if not res:
        raise HTTPException(status_code=404, detail='数据不存在')
    
    update_data = item.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail='没有更新数据')
    
    await res.update_from_dict(update_data)
    await res.save()
    await res.fetch_related('project')
    
    return Out.model_validate(res)
```

✅ **upsert 方法** - 预加载项目信息
```python
async def upsert(self, item: Create) -> Out:
    record, created = await ProjectWallet.get_or_create(
        defaults=item.model_dump(),
        public_key=item.public_key
    )
    
    if not created:
        update_data = item.model_dump(exclude_unset=True)
        if update_data:
            await record.update_from_dict(update_data)
            await record.save()
    
    await record.fetch_related('project')
    return Out.model_validate(record)
```

### 3. API 层 (backend/app/apis/v1/project/wallet.py)

✅ **gets 方法** - 支持按 project_id 查询
```python
@app.get("", response_model=OutList, description="获取项目钱包列表")
async def gets(
    project_id: UUID | None = Query(None, description="所属项目ID"),  # ← 支持过滤
    chain: str | None = Query(None, description="链名称"),
    ...
):
    return await project_wallet_crud.get_multi(
        project_id=project_id,
        chain=chain,
        ...
    )
```

✅ **post_or_put 方法** - 创建或更新（Upsert）
```python
@app.post("/upsert", response_model=Out, description="创建或更新项目钱包")
async def post_or_put(
    item: Create = Body(..., description="创建或更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建或更新项目钱包（根据公钥唯一性）
    
    如果公钥已存在，则更新该钱包信息；否则创建新钱包
    """
    return await project_wallet_crud.upsert(item)
```

### 4. 模型层 (backend/app/models/project.py)

✅ **ProjectWallet 模型** - project 字段可为空
```python
class ProjectWallet(BaseModel):
    """
    项目钱包
    """
    private_key = fields.TextField(description="私钥（AES加密）")
    public_key = fields.TextField(description="公钥")
    mnemonic = fields.TextField(description="助记词（AES加密）")
    chain = fields.CharField(max_length=255, description="链")
    remark = fields.CharField(max_length=255, null=True, description="备注")

    # 和项目信息关联（可选）
    project = fields.ForeignKeyField(
        "models.ProjectInfo", 
        null=True,  # ← 可为空
        related_name="wallets", 
        description="所属项目"
    )
```

✅ **ProjectAccount 模型** - 移除了 wallet_id 索引
```python
class Meta:
    indexes = [
        ("project_id", "status", "account_type"),
        ("status", "account_type", "create_time"),
        ("server_id", "status"),
        # wallet_id 索引已移除
    ]
```

## API 使用说明

### 创建独立钱包（不关联项目）
```bash
POST /v1/project/wallet
{
  "private_key": "encrypted_private_key",
  "public_key": "0x...",
  "chain": "ETH",
  "remark": "独立钱包"
  # mnemonic 可选，不传也可以
  # project_id 可选，不传则创建独立钱包
}
```

### 创建关联项目的钱包
```bash
POST /v1/project/wallet
{
  "private_key": "encrypted_private_key",
  "public_key": "0x...",
  "mnemonic": "encrypted_mnemonic",  # 可选
  "chain": "ETH",
  "remark": "项目钱包",
  "project_id": "project-uuid"  # ← 关联到项目
}
```

### 查询特定项目的钱包
```bash
GET /v1/project/wallet?project_id={project_id}&page=1&limit=10&res_count=true
```

### 查询所有钱包（包括独立钱包）
```bash
GET /v1/project/wallet?page=1&limit=10&res_count=true
```

### 按链名称过滤
```bash
GET /v1/project/wallet?chain=ETH&page=1&limit=10
```

### 查询单个钱包
```bash
GET /v1/project/wallet/{wallet_id}
```

### 更新钱包（可以修改项目关联）
```bash
PUT /v1/project/wallet/{wallet_id}
{
  "project_id": "new-project-uuid",  # 可以修改关联的项目
  "remark": "更新备注"
}
```

### 将钱包从项目中解除关联
```bash
PUT /v1/project/wallet/{wallet_id}
{
  "project_id": null  # 设置为 null 解除关联
}
```

### 创建或更新钱包（Upsert）
```bash
POST /v1/project/wallet/upsert
{
  "private_key": "encrypted_private_key",
  "public_key": "0x...",  # 根据公钥判断是否已存在
  "mnemonic": "encrypted_mnemonic",
  "chain": "ETH",
  "remark": "钱包备注",
  "project_id": "project-uuid"  # 可选
}
```

如果公钥已存在，则更新该钱包信息；否则创建新钱包。

## 前端使用示例

### TypeScript 类型定义
```typescript
export interface ProjectWallet {
  id: string
  private_key: string
  public_key: string
  mnemonic: string
  chain: string
  remark?: string
  project_id?: string  // ← 可选
  project?: Project    // ← 可选
  create_time: string
  update_time: string
}
```

### 创建独立钱包
```typescript
const wallet = await createProjectWallet({
  private_key: "encrypted_private_key",
  public_key: "0x...",
  mnemonic: "encrypted_mnemonic",
  chain: "ETH",
  remark: "独立钱包"
  // 不传 project_id
})
```

### 创建项目钱包
```typescript
const wallet = await createProjectWallet({
  private_key: "encrypted_private_key",
  public_key: "0x...",
  mnemonic: "encrypted_mnemonic",
  chain: "ETH",
  remark: "项目钱包",
  project_id: "project-uuid"
})
```

### 查询项目的钱包
```typescript
const projectWallets = await getProjectWalletList({
  project_id: "project-uuid",
  page: 1,
  limit: 10,
  res_count: true
})
```

### 查询所有钱包
```typescript
const allWallets = await getProjectWalletList({
  page: 1,
  limit: 10,
  res_count: true
})
```

### 将钱包关联到项目
```typescript
await updateProjectWallet(walletId, {
  project_id: "project-uuid"
})
```

### 解除钱包的项目关联
```typescript
await updateProjectWallet(walletId, {
  project_id: null
})
```

### 创建或更新钱包（Upsert）
```typescript
// 如果公钥已存在则更新，否则创建
const wallet = await upsertProjectWallet({
  private_key: "encrypted_private_key",
  public_key: "0x...",  // 根据公钥判断唯一性
  mnemonic: "encrypted_mnemonic",
  chain: "ETH",
  remark: "钱包备注",
  project_id: "project-uuid"  // 可选
})
```

## 使用场景

### 场景1: 独立钱包管理
```
1. 创建独立钱包（不关联项目）
2. 批量导入钱包
3. 后续根据需要关联到项目
```

### 场景2: 项目钱包管理
```
1. 创建项目
2. 为项目创建钱包（直接关联）
3. 查询项目的所有钱包
```

### 场景3: 钱包转移
```
1. 钱包从项目A解除关联
2. 钱包关联到项目B
```

### 场景4: 钱包池管理
```
1. 维护一个独立钱包池
2. 根据需要分配给不同项目
3. 项目结束后回收到钱包池
```

## 优势

### 1. 灵活性
- 钱包可以独立存在，不依赖项目
- 钱包可以在项目间转移
- 支持钱包池管理模式

### 2. 可扩展性
- 便于批量导入钱包
- 支持钱包的动态分配
- 便于钱包的集中管理

### 3. 向后兼容
- 支持原有的项目关联模式
- 同时支持新的独立钱包模式
- 不影响现有功能

## 数据库迁移

### 迁移文件1: 钱包项目关联
`backend/migrations/models/1_20260121155309_wallet_project_relation.py`

```sql
-- 从 ProjectAccount 移除 wallet_id
ALTER TABLE `project_account` DROP FOREIGN KEY `fk_project__project__93399a32`;
ALTER TABLE `project_account` DROP INDEX `idx_project_acc_wallet__29c3f9`;
ALTER TABLE `project_account` DROP COLUMN `wallet_id`;

-- 给 ProjectWallet 添加 project_id（可为空）
ALTER TABLE `project_wallet` ADD `project_id` CHAR(36) COMMENT '所属项目';
ALTER TABLE `project_wallet` ADD CONSTRAINT `fk_project__project__cba39da5` 
    FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`) ON DELETE CASCADE;
```

注意：`project_id` 字段没有 `NOT NULL` 约束，因此可以为空。

### 迁移文件2: 助记词可空
`backend/migrations/models/2_20260121163732_wallet_mnemonic_nullable.py`

```sql
-- 修改 project_wallet 表的 mnemonic 字段为可空
ALTER TABLE `project_wallet` MODIFY COLUMN `mnemonic` LONGTEXT COMMENT '助记词（AES加密）';
```

注意：`mnemonic` 字段移除了 `NOT NULL` 约束，因为不是所有钱包都有助记词。

## 测试验证

### 1. 编译检查
```bash
python -m py_compile backend/app/schemas/project/wallet.py
python -m py_compile backend/app/crud/project/wallet.py
python -m py_compile backend/app/apis/v1/project/wallet.py
```
✅ 所有文件编译通过

### 2. API 测试
```bash
# 创建独立钱包
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"private_key":"xxx","public_key":"0x...","mnemonic":"xxx","chain":"ETH"}' \
  "http://127.0.0.1:6080/v1/project/wallet"

# 创建项目钱包
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"private_key":"xxx","public_key":"0x...","mnemonic":"xxx","chain":"ETH","project_id":"project-uuid"}' \
  "http://127.0.0.1:6080/v1/project/wallet"

# Upsert 钱包（根据公钥判断）
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"private_key":"xxx","public_key":"0x...","mnemonic":"xxx","chain":"ETH","project_id":"project-uuid"}' \
  "http://127.0.0.1:6080/v1/project/wallet/upsert"

# 查询项目钱包
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:6080/v1/project/wallet?project_id=project-uuid"

# 查询所有钱包
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:6080/v1/project/wallet"
```

## 相关文件

### 后端
- ✅ `backend/app/models/project.py` - 模型定义
- ✅ `backend/app/schemas/project/wallet.py` - Schema 定义
- ✅ `backend/app/crud/project/wallet.py` - CRUD 操作
- ✅ `backend/app/apis/v1/project/wallet.py` - API 端点
- ✅ `backend/app/schemas/project/account.py` - 账号 Schema（已移除 wallet_id）
- ✅ `backend/app/crud/project/account.py` - 账号 CRUD（已移除 wallet 预加载）
- ✅ `backend/app/apis/v1/project/account.py` - 账号 API（已移除 wallet_id 参数）

### 前端
- ✅ `frontend/src/types/index.ts` - 类型定义（无需修改）
- ✅ `frontend/src/api/project.ts` - API 调用（无需修改）

### 文档
- ✅ `docs/fixes/WALLET_MODEL_CORRECTION.md` - 已更新
- ✅ `docs/fixes/FINAL_SUMMARY_20260121.md` - 已更新
- ✅ `docs/fixes/WALLET_API_FIX.md` - 已更新
- ✅ `docs/fixes/WALLET_RELATION_REMOVAL.md` - 已更新
- ✅ `docs/fixes/PROJECT_WALLET_RELATION_FINAL.md` - 本文档

### 数据库
- ✅ `backend/migrations/models/1_20260121155309_wallet_project_relation.py` - 钱包项目关联迁移
- ✅ `backend/migrations/models/2_20260121163732_wallet_mnemonic_nullable.py` - 助记词可空迁移

## 总结

✅ ProjectWallet 的 `project_id` 是可选的，支持独立钱包
✅ 所有 CRUD 方法都正确预加载项目信息
✅ API 支持按 `project_id` 过滤查询
✅ 添加了 `/upsert` 接口，根据公钥判断创建或更新
✅ Schema 正确定义了可选的项目关联
✅ ProjectAccount 完全移除了 wallet_id 相关代码
✅ 所有文档已更新
✅ 前端代码无需修改
✅ 所有 Python 文件编译通过

现在系统支持两种钱包管理模式：
1. **独立钱包模式**：钱包不关联项目，可以独立管理
2. **项目钱包模式**：钱包关联到项目，便于项目管理

钱包 API 完整功能：
- `POST /v1/project/wallet` - 创建钱包
- `GET /v1/project/wallet/{id}` - 获取单个钱包
- `GET /v1/project/wallet` - 查询钱包列表（支持 project_id 过滤）
- `PUT /v1/project/wallet/{id}` - 更新钱包
- `DELETE /v1/project/wallet/{id}` - 删除钱包
- `POST /v1/project/wallet/upsert` - 创建或更新钱包（根据公钥唯一性）

这提供了最大的灵活性，满足不同的使用场景。

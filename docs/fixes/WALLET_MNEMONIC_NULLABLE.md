# 项目钱包助记词字段改为可空

## 修改时间
2026-01-21

## 问题描述
不是所有钱包都有助记词（mnemonic），例如：
- 通过私钥导入的钱包
- 硬件钱包
- 某些类型的智能合约钱包

但当前模型中 `mnemonic` 字段是必填的，这不合理。

## 解决方案

### 1. 修改模型 (backend/app/models/project.py)

```python
class ProjectWallet(BaseModel):
    """
    项目钱包
    """
    private_key = fields.TextField(description="私钥（AES加密）")
    public_key = fields.TextField(description="公钥")
    mnemonic = fields.TextField(null=True, description="助记词（AES加密）")  # ← 添加 null=True
    chain = fields.CharField(max_length=255, description="链")
    remark = fields.CharField(max_length=255, null=True, description="备注")
    project = fields.ForeignKeyField("models.ProjectInfo", null=True, related_name="wallets", description="所属项目")
```

### 2. 修改 Schema (backend/app/schemas/project/wallet.py)

```python
class Base(BaseModel):
    """
    项目钱包基础模型
    """
    private_key: str = Field(..., description="私钥（AES加密）")
    public_key: str = Field(..., description="公钥")
    mnemonic: str | None = Field(None, description="助记词（AES加密）")  # ← 改为可选
    chain: str = Field(..., description="链")
    remark: str | None = Field(None, description="备注")
```

### 3. 数据库迁移

创建迁移文件：`backend/migrations/models/2_20260121163732_wallet_mnemonic_nullable.py`

```python
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 修改 project_wallet 表的 mnemonic 字段为可空
        ALTER TABLE `project_wallet` MODIFY COLUMN `mnemonic` LONGTEXT COMMENT '助记词（AES加密）';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 恢复 project_wallet 表的 mnemonic 字段为非空
        ALTER TABLE `project_wallet` MODIFY COLUMN `mnemonic` LONGTEXT NOT NULL COMMENT '助记词（AES加密）';"""
```

## 使用场景

### 场景1: 创建有助记词的钱包
```bash
POST /v1/project/wallet
{
  "private_key": "encrypted_private_key",
  "public_key": "0x...",
  "mnemonic": "encrypted_mnemonic",  # 有助记词
  "chain": "ETH",
  "project_id": "project-uuid"
}
```

### 场景2: 创建无助记词的钱包（私钥导入）
```bash
POST /v1/project/wallet
{
  "private_key": "encrypted_private_key",
  "public_key": "0x...",
  # 不传 mnemonic
  "chain": "ETH",
  "project_id": "project-uuid"
}
```

### 场景3: 硬件钱包
```bash
POST /v1/project/wallet
{
  "private_key": "",  # 硬件钱包可能不暴露私钥
  "public_key": "0x...",
  # 不传 mnemonic
  "chain": "ETH",
  "remark": "Ledger 硬件钱包"
}
```

## 前端使用

### TypeScript 类型定义
```typescript
export interface ProjectWallet {
  id: string
  private_key: string
  public_key: string
  mnemonic?: string  // ← 可选
  chain: string
  remark?: string
  project_id?: string
  project?: Project
  create_time: string
  update_time: string
}
```

### 创建钱包示例
```typescript
// 有助记词的钱包
const walletWithMnemonic = await createProjectWallet({
  private_key: "encrypted_private_key",
  public_key: "0x...",
  mnemonic: "encrypted_mnemonic",
  chain: "ETH"
})

// 无助记词的钱包（私钥导入）
const walletWithoutMnemonic = await createProjectWallet({
  private_key: "encrypted_private_key",
  public_key: "0x...",
  // 不传 mnemonic
  chain: "ETH"
})
```

## 字段说明

### 必填字段
- `private_key`: 私钥（加密存储）
- `public_key`: 公钥（用于唯一性判断）
- `chain`: 链名称（如 ETH, BSC, Polygon 等）

### 可选字段
- `mnemonic`: 助记词（加密存储）- **新改为可选**
- `remark`: 备注
- `project_id`: 所属项目ID

## 数据完整性

虽然 `mnemonic` 是可选的，但建议：

1. **有助记词的钱包**：尽量保存助记词，便于恢复
2. **私钥导入的钱包**：可以不保存助记词
3. **硬件钱包**：通常不需要保存助记词和私钥

## 迁移步骤

### 1. 应用迁移
```bash
# 进入后端目录
cd backend

# 应用迁移
aerich upgrade
```

### 2. 验证迁移
```bash
# 连接数据库
mysql -u root -p

# 查看表结构
USE your_database;
DESC project_wallet;

# 验证 mnemonic 字段的 Null 列应该是 YES
```

### 3. 测试
```bash
# 测试创建无助记词的钱包
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "private_key": "encrypted_key",
    "public_key": "0x123abc",
    "chain": "ETH",
    "remark": "私钥导入的钱包"
  }' \
  "http://127.0.0.1:6080/v1/project/wallet"
```

## 相关文件

- ✅ `backend/app/models/project.py` - 模型定义
- ✅ `backend/app/schemas/project/wallet.py` - Schema 定义
- ✅ `backend/migrations/models/2_20260121163732_wallet_mnemonic_nullable.py` - 迁移文件
- ✅ `docs/fixes/WALLET_MNEMONIC_NULLABLE.md` - 本文档
- ✅ `docs/fixes/PROJECT_WALLET_RELATION_FINAL.md` - 已更新
- ✅ `docs/fixes/WALLET_MODEL_CORRECTION.md` - 已更新

## 总结

✅ 模型中 `mnemonic` 字段改为可空（`null=True`）
✅ Schema 中 `mnemonic` 字段改为可选（`str | None`）
✅ 创建了数据库迁移文件
✅ 更新了相关文档
✅ 代码编译通过

现在钱包模型更加灵活，支持：
- 有助记词的钱包（通过助记词生成）
- 无助记词的钱包（私钥导入）
- 硬件钱包等特殊类型

这更符合实际使用场景！

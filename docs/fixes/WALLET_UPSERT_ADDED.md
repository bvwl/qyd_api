# 项目钱包添加 Upsert 接口

## 修改时间
2026-01-21

## 问题描述
项目钱包 API 缺少 upsert（创建或更新）接口，与其他模块不一致。

## 解决方案

### 添加 API 接口

在 `backend/app/apis/v1/project/wallet.py` 中添加了 upsert 接口：

```python
@app.post("/upsert", response_model=Out, description="创建或更新项目钱包", summary="创建或更新项目钱包")
async def post_or_put(
    item: Create = Body(..., description="创建或更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建或更新项目钱包（根据公钥唯一性）
    
    如果公钥已存在，则更新该钱包信息；否则创建新钱包
    """
    try:
        return await project_wallet_crud.upsert(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### CRUD 方法

CRUD 层已有 upsert 方法（`backend/app/crud/project/wallet.py`）：

```python
async def upsert(self, item: Create) -> Out:
    record, created = await ProjectWallet.get_or_create(
        defaults=item.model_dump(),
        public_key=item.public_key  # 根据公钥判断唯一性
    )
    
    if not created:
        update_data = item.model_dump(exclude_unset=True)
        if update_data:
            await record.update_from_dict(update_data)
            await record.save()
    
    await record.fetch_related('project')
    return Out.model_validate(record)
```

## 使用说明

### API 调用

```bash
POST /v1/project/wallet/upsert
Authorization: Bearer {token}
Content-Type: application/json

{
  "private_key": "encrypted_private_key",
  "public_key": "0x123...",  # 根据此字段判断唯一性
  "mnemonic": "encrypted_mnemonic",
  "chain": "ETH",
  "remark": "主钱包",
  "project_id": "project-uuid"  # 可选
}
```

### 行为说明

1. **如果公钥已存在**：更新该钱包的其他信息（私钥、助记词、链、备注、项目关联等）
2. **如果公钥不存在**：创建新的钱包记录

### 使用场景

#### 场景1: 批量导入钱包
```bash
# 多次调用 upsert，相同公钥会更新而不是重复创建
for wallet in wallets:
    POST /v1/project/wallet/upsert
    {
      "public_key": wallet.public_key,
      "private_key": wallet.private_key,
      ...
    }
```

#### 场景2: 更新钱包项目关联
```bash
# 如果钱包已存在，更新其项目关联
POST /v1/project/wallet/upsert
{
  "public_key": "0x123...",  # 已存在的公钥
  "project_id": "new-project-uuid"  # 更新项目关联
}
```

#### 场景3: 确保钱包存在
```bash
# 不确定钱包是否已存在，使用 upsert 确保存在
POST /v1/project/wallet/upsert
{
  "public_key": "0x123...",
  "private_key": "...",
  "mnemonic": "...",
  "chain": "ETH"
}
```

## 前端使用

### API 函数（需要添加）

在 `frontend/src/api/project.ts` 中添加：

```typescript
export const upsertProjectWallet = (data: Partial<ProjectWallet>) => {
  return api.post<any, ProjectWallet>('/v1/project/wallet/upsert', data)
}
```

### 使用示例

```typescript
// 创建或更新钱包
const wallet = await upsertProjectWallet({
  public_key: "0x123...",
  private_key: "encrypted_private_key",
  mnemonic: "encrypted_mnemonic",
  chain: "ETH",
  remark: "主钱包",
  project_id: "project-uuid"  // 可选
})

// 批量导入钱包
for (const walletData of importedWallets) {
  await upsertProjectWallet(walletData)
}
```

## 与其他模块对比

现在项目钱包 API 与其他模块保持一致：

| 模块 | Upsert 接口 | 唯一性判断字段 |
|------|------------|--------------|
| 项目信息 | ✅ `/v1/project/info/upsert` | name |
| 项目账号 | ✅ `/v1/project/account/upsert` | account + project_id |
| 项目钱包 | ✅ `/v1/project/wallet/upsert` | public_key |
| 用户信息 | ✅ `/v1/user/user/upsert` | email |
| 角色信息 | ✅ `/v1/user/role/upsert` | code |
| 服务器信息 | ✅ `/v1/server/info/upsert` | host |
| 邮箱信息 | ✅ `/v1/mail/info/upsert` | email |

## 完整的钱包 API 列表

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/v1/project/wallet` | 创建钱包 |
| GET | `/v1/project/wallet/{id}` | 获取单个钱包 |
| GET | `/v1/project/wallet` | 查询钱包列表 |
| PUT | `/v1/project/wallet/{id}` | 更新钱包 |
| DELETE | `/v1/project/wallet/{id}` | 删除钱包 |
| POST | `/v1/project/wallet/upsert` | 创建或更新钱包 ✨ |

## 测试验证

```bash
# 测试 upsert - 创建新钱包
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "private_key": "encrypted_key",
    "public_key": "0x123abc",
    "mnemonic": "encrypted_mnemonic",
    "chain": "ETH",
    "remark": "测试钱包"
  }' \
  "http://127.0.0.1:6080/v1/project/wallet/upsert"

# 测试 upsert - 更新已存在的钱包
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "public_key": "0x123abc",
    "remark": "更新后的备注",
    "project_id": "project-uuid"
  }' \
  "http://127.0.0.1:6080/v1/project/wallet/upsert"
```

## 相关文件

- ✅ `backend/app/apis/v1/project/wallet.py` - 添加了 upsert 接口
- ✅ `backend/app/crud/project/wallet.py` - upsert 方法已存在
- ✅ `docs/fixes/PROJECT_WALLET_RELATION_FINAL.md` - 已更新
- ✅ `docs/fixes/WALLET_RELATION_REMOVAL.md` - 已更新
- ✅ `docs/fixes/WALLET_UPSERT_ADDED.md` - 本文档

## 总结

✅ 添加了 `/v1/project/wallet/upsert` 接口
✅ 根据公钥（public_key）判断唯一性
✅ 支持创建新钱包或更新已存在的钱包
✅ 与其他模块的 upsert 接口保持一致
✅ 代码编译通过
✅ 文档已更新

现在项目钱包模块的 API 功能完整，与其他模块保持一致！

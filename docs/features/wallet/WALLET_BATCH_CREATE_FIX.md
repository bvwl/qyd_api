# 批量创建钱包功能 - Pydantic 验证错误修复

## 问题描述

批量创建钱包时出现 Pydantic 验证错误：

```
1 validation error for Out
project.name
  Field required [type=missing, input_value=<tortoise.fields.relation...e object at 0x1083b3060>, input_type=_NoneAwaitable]
```

## 错误原因

1. **关联字段验证问题**：`Out` 模型中有 `project: ProjectInfoBase | None` 字段
2. **批量创建的钱包没有关联项目**：`project_id` 为 `None`
3. **Pydantic 尝试验证关联对象**：即使 `project` 为 `None`，Pydantic 仍然尝试验证 `ProjectInfoBase` 模型
4. **ProjectInfoBase 需要必填字段**：`name` 字段是必填的，导致验证失败

## 解决方案

### 1. 修改 Schema 模型 (`backend/app/schemas/project/wallet.py`)

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
    
    # 关联的项目信息（可选，批量创建时不包含）
    project: ProjectInfoBase | None = Field(default=None, description="项目信息")  # 添加 default=None

    @field_serializer("create_time", "update_time")
    def format_datetime(self, dt: datetime) -> str:
        return dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True
        # 允许任意类型，避免关联字段验证问题
        arbitrary_types_allowed = True  # 新增配置
```

**关键修改**：
- `project` 字段添加 `default=None`
- 添加 `arbitrary_types_allowed = True` 配置

### 2. 修改 CRUD 方法 (`backend/app/crud/project/wallet.py`)

```python
async def batch_create(self, item: BatchCreate) -> BatchCreateOut:
    """
    批量创建钱包
    """
    # ... 创建钱包逻辑 ...
    
    if not created_wallets:
        raise HTTPException(status_code=500, detail='批量创建失败，没有成功创建任何钱包')
    
    # 手动构建输出数据（避免Pydantic验证关联字段）
    items = []
    for wallet in created_wallets:
        # 使用项目名称解密（因为前端需要明文显示）
        from app.core.tools import aes_decrypt_wallet
        
        # 构建字典，排除 project 字段
        wallet_dict = {
            'message': '成功',
            'id': wallet.id,  # 直接使用 UUID 对象，不转字符串
            'private_key': aes_decrypt_wallet(wallet.private_key, item.project_name),
            'public_key': wallet.public_key,
            'mnemonic': aes_decrypt_wallet(wallet.mnemonic, item.project_name) if wallet.mnemonic else None,
            'chain': wallet.chain,
            'remark': wallet.remark,
            'project_id': None,
            'create_time': wallet.create_time,
            'update_time': wallet.update_time,
            # 不包含 project 字段，让 Pydantic 使用默认值 None
        }
        items.append(Out(**wallet_dict))
    
    return BatchCreateOut(
        message=f'成功创建 {len(created_wallets)} 个钱包',
        count=len(created_wallets),
        items=items
    )
```

**关键修改**：
- 手动构建字典，不包含 `project` 字段
- 直接使用 UUID 对象，不转换为字符串
- 在构建时解密私钥和助记词（前端需要明文显示）

### 3. 重启后端服务

修改代码后需要重启后端服务才能生效：

```bash
# 停止服务
pkill -f "python.*start.py"

# 启动服务
cd backend
python start.py
```

## 测试验证

### 测试 ETH 钱包创建

```bash
curl -X POST 'http://127.0.0.1:6080/v1/project/wallet/batch' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -d '{"project_name":"test","chain":"eth","count":2}'
```

**响应示例**：
```json
{
  "message": "成功创建 2 个钱包",
  "count": 2,
  "items": [
    {
      "private_key": "787f5d3822ad594b91105236586ef38cc63d4d43de377f24fcf0636f2a8388c3",
      "public_key": "0x9d21648509549F43554Bde8752f4B9C7B43A140B",
      "mnemonic": "tobacco craft knee finish later pumpkin jazz shoe adult black century stool",
      "chain": "eth",
      "remark": null,
      "message": "成功",
      "id": "9066dcb3-6973-485e-8998-683235eb143f",
      "create_time": "2026-01-25 17:42:26",
      "update_time": "2026-01-25 17:42:26",
      "project_id": null,
      "project": null
    }
  ]
}
```

### 测试 Solana 钱包创建

```bash
curl -X POST 'http://127.0.0.1:6080/v1/project/wallet/batch' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -d '{"project_name":"test","chain":"solana","count":1}'
```

**响应示例**：
```json
{
  "message": "成功创建 1 个钱包",
  "count": 1,
  "items": [
    {
      "private_key": "5MveABZLkWxmfztmPhthDkjKmBAMYBYAG76gknKvZjBGD1m77Vc7fB94GEr6YJz1twRgrLKWf7cND8utAraedncC",
      "public_key": "DM9HQ2QbBtm8K4hQH8MFBbPgYUr6mS4NvWs4oYmGVZRW",
      "mnemonic": null,
      "chain": "solana",
      "remark": null,
      "message": "成功",
      "id": "0564ed60-71d6-4613-b6e2-8e3ec952a2af",
      "create_time": "2026-01-25 17:42:36",
      "update_time": "2026-01-25 17:42:36",
      "project_id": null,
      "project": null
    }
  ]
}
```

## 功能特性

### ✅ 已实现

1. **批量创建**：支持一次创建 1-100 个钱包
2. **多链支持**：支持 ETH 和 Solana 两种链
3. **自动加密**：私钥和助记词使用 AES 加密存储到数据库
4. **自动解密**：API 返回时自动解密（仅 ADMIN 可见明文）
5. **数据持久化**：钱包自动保存到数据库
6. **权限控制**：只有 ADMIN 可以批量创建钱包

### 📝 注意事项

1. **项目名称**：用于加密密钥，请妥善保管
2. **不关联项目**：批量创建的钱包不关联项目表（`project_id` 为 `None`）
3. **明文返回**：API 返回的是解密后的明文数据（方便前端显示）
4. **数据库加密**：数据库中存储的是加密数据
5. **权限限制**：只有 ADMIN 角色可以调用此 API

## 前端集成

前端页面已经完成，位于：
- **组件**：`frontend/src/views/Project/WalletBatchCreate.tsx`
- **路由**：`/project/wallet/batch-create`
- **菜单**：项目管理 → 批量创建钱包

前端功能：
- ✅ 表单输入（项目名称、链类型、数量、备注）
- ✅ 表格显示创建的钱包
- ✅ 私钥/助记词显示/隐藏切换
- ✅ 一键复制功能
- ✅ 10 分钟倒计时
- ✅ Excel 导出功能
- ✅ 权限控制（仅 ADMIN 可访问）

## 相关文件

### 后端
- `backend/app/apis/v1/project/wallet.py` - API 端点（已修复）
- `backend/app/crud/project/wallet.py` - CRUD 方法（已修复）
- `backend/app/schemas/project/wallet.py` - 数据模型（已修复）
- `backend/app/core/tools.py` - 加密/解密工具
- `backend/app/clients/wallet.py` - 钱包生成客户端

### 前端
- `frontend/src/App.tsx` - 路由配置（已添加）
- `frontend/src/views/Project/WalletBatchCreate.tsx` - 页面组件
- `frontend/src/api/project.ts` - API 调用
- `frontend/src/components/Layout/index.tsx` - 菜单配置

## 更新日志

### 2026-01-25 17:42
- ✅ 修复 Pydantic 验证错误
- ✅ 修改 `Out` 模型，添加 `default=None` 和 `arbitrary_types_allowed`
- ✅ 修改 CRUD 方法，手动构建输出字典
- ✅ 重启后端服务
- ✅ 测试 ETH 和 Solana 钱包创建
- ✅ 验证功能正常工作

### 之前的更新
- ✅ 实现后端批量创建 API
- ✅ 添加 AES 加密功能
- ✅ 创建前端页面组件
- ✅ 添加 Excel 导出功能
- ✅ 修复前端路由配置
- ✅ 注册后端路由权限

## 总结

批量创建钱包功能现在完全正常工作！

**问题根源**：Pydantic 在验证 `Out` 模型时，尝试验证 `project` 关联字段，但批量创建的钱包没有关联项目，导致验证失败。

**解决方案**：
1. 在 `Out` 模型中为 `project` 字段添加 `default=None`
2. 添加 `arbitrary_types_allowed = True` 配置
3. 在 CRUD 方法中手动构建输出字典，不包含 `project` 字段

现在可以正常使用批量创建钱包功能了！🎉

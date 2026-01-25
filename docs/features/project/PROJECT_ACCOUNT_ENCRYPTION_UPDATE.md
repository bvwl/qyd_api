# 项目账号加密方式更新

## 更新时间
2026-01-25

## 更新内容

### 1. 加密密钥生成方式变更

**之前的方式（基于项目名称）：**
- 密钥（key）: MD5(项目名称 + "9527")
- 初始化向量（IV）: MD5("9527" + 项目名称) 取前16字节
- 问题：需要查询关联的项目信息才能加密/解密

**新的方式（基于项目账号）：**
- 密钥（key）: MD5(项目账号 + "9527")
- 初始化向量（IV）: MD5("9527" + 项目账号) 取前16字节
- 优势：不需要查询关联的项目信息，直接使用账号即可

### 2. 新增 password 字段加密

**之前：**
- 只加密 `data` 字段中的 `private_key` 和 `mnemonic`
- `password` 字段（与 `data` 同级）未加密

**现在：**
- 继续加密 `data` 字段中的 `private_key` 和 `mnemonic`
- 新增 `password` 字段加密（与 `data` 同级）

## 修改的文件

### 1. 核心加密工具 (`backend/app/core/tools.py`)

```python
def aes_encrypt_project(plaintext: str, account: str) -> str:
    """
    使用AES加密项目敏感数据
    - key: MD5(账号 + "9527")
    - iv: MD5("9527" + 账号) 取前16位
    """
    # 生成密钥：MD5(账号 + "9527")
    key_string = f"{account}9527"
    key = hashlib.md5(key_string.encode('utf-8')).digest()
    
    # 生成IV：MD5("9527" + 账号) 取前16位
    iv_string = f"9527{account}"
    iv = hashlib.md5(iv_string.encode('utf-8')).digest()[:16]
    
    # ... 加密逻辑
```

### 2. 项目加密工具 (`backend/app/utils/project_crypto.py`)

**新增函数：**
- `encrypt_password(password: str, account: str) -> str`: 加密 password 字段
- `decrypt_password(encrypted_password: str, account: str) -> str`: 解密 password 字段

**更新函数：**
- `encrypt_sensitive_fields(data, account)`: 参数从 `project_name` 改为 `account`
- `decrypt_sensitive_fields(data, account)`: 参数从 `project_name` 改为 `account`

### 3. 项目账号队列 (`backend/app/utils/project_account_queue.py`)

**更新 `add_to_queue` 方法：**
```python
async def add_to_queue(self, account: str, project_name: str, data: dict, **kwargs):
    # 使用 account 而不是 project_name 进行加密
    if data:
        data = encrypt_sensitive_fields(data, account)
    
    # 新增 password 字段加密
    password = kwargs.get('password')
    if password:
        kwargs['password'] = encrypt_password(password, account)
```

### 4. 项目账号 CRUD (`backend/app/crud/project/account.py`)

**更新所有方法使用 account 进行加密/解密：**

#### create 方法
```python
async def create(self, item: Create) -> Out:
    account = item.account
    
    # 加密 data 字段
    if 'data' in filtered_item and filtered_item['data']:
        filtered_item['data'] = encrypt_sensitive_fields(filtered_item['data'], account)
    
    # 加密 password 字段
    if 'password' in filtered_item and filtered_item['password']:
        filtered_item['password'] = encrypt_password(filtered_item['password'], account)
```

#### get 方法
```python
async def get(self, id: UUID, user_id: str | None = None, user_roles: list[str] | None = None) -> Out:
    # 解密 data 字段
    if result.data:
        result.data = decrypt_sensitive_fields(result.data, res.account)
    
    # 解密 password 字段
    if result.password:
        result.password = decrypt_password(result.password, res.account)
```

#### get_multi 方法
```python
async def get_multi(...) -> OutList:
    for obj in res:
        # 解密 data 字段
        if item.data:
            item.data = decrypt_sensitive_fields(item.data, obj.account)
        
        # 解密 password 字段
        if item.password:
            item.password = decrypt_password(item.password, obj.account)
```

#### update 方法
```python
async def update(self, id: UUID, item: Update) -> Out:
    account = res.account
    
    # 加密 data 字段
    if 'data' in update_data and update_data['data']:
        update_data['data'] = encrypt_sensitive_fields(update_data['data'], account)
    
    # 加密 password 字段
    if 'password' in update_data and update_data['password']:
        update_data['password'] = encrypt_password(update_data['password'], account)
```

#### upsert 方法
```python
async def upsert(self, item: Create) -> Out:
    account = item.account
    
    # 加密 data 字段
    if 'data' in update_data and update_data['data']:
        update_data['data'] = encrypt_sensitive_fields(update_data['data'], account)
    
    # 加密 password 字段
    if 'password' in update_data and update_data['password']:
        update_data['password'] = encrypt_password(update_data['password'], account)
```

## 加密字段说明

### data 字段（递归加密）
在 `data` 字段的所有层级中，以下字段会被加密：
- `private_key`: 私钥
- `mnemonic`: 助记词

**示例：**
```json
{
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",  // 不加密
  "private_key": "0x4c0883a69102937d...",  // 加密
  "mnemonic": "abandon abandon abandon...",  // 加密
  "balance": "100.5",  // 不加密
  "nested": {
    "chain": "Ethereum",  // 不加密
    "private_key": "nested_key",  // 加密
    "other_field": "value"  // 不加密
  },
  "list_data": [
    {
      "name": "wallet1",  // 不加密
      "private_key": "key1",  // 加密
      "mnemonic": "mnemonic1"  // 加密
    }
  ]
}
```

### password 字段（与 data 同级）
整个 `password` 字段会被加密。

## 权限控制

解密权限判断逻辑（`check_user_can_decrypt`）：
1. **管理员（ADMIN）**：可以解密所有项目的敏感数据
2. **项目所属人**：可以解密自己项目的敏感数据
3. **其他用户**：无法解密，返回加密状态的数据

## 测试验证

### 测试文件
- `backend/test_encryption_simple.py`: 简单加密测试（不需要数据库）
- `backend/test_account_encryption_update.py`: 完整CRUD测试（需要数据库）

### 运行测试
```bash
# 简单测试（推荐）
cd backend
python test_encryption_simple.py

# 完整测试（需要数据库运行）
cd backend
python test_account_encryption_update.py
```

### 测试结果
```
✅ 所有测试通过！

总结:
1. ✅ 加密密钥已改为基于账号（账号+9527）
2. ✅ IV已改为基于账号（9527+账号）
3. ✅ password字段支持加密
4. ✅ data字段中的private_key和mnemonic支持递归加密
5. ✅ 不同账号产生不同的加密结果
6. ✅ 非敏感字段不会被加密
7. ✅ 所有加密数据可以正确解密
```

## 优势

### 1. 性能提升
- **之前**：每次加密/解密都需要查询项目信息（额外的数据库查询）
- **现在**：直接使用账号，无需额外查询

### 2. 代码简化
- **之前**：需要 `await res.fetch_related('project')` 获取项目信息
- **现在**：直接使用 `res.account` 或 `item.account`

### 3. 更好的隔离性
- 每个账号使用独立的密钥
- 即使是同一个项目的不同账号，密钥也不同
- 提高了安全性

## 注意事项

### 1. 数据迁移
如果数据库中已有使用旧加密方式的数据，需要进行数据迁移：
1. 读取旧数据（使用项目名称解密）
2. 使用新方式重新加密（使用账号加密）
3. 更新数据库

### 2. 兼容性
- 新旧加密方式不兼容
- 旧数据无法使用新方式解密
- 需要统一迁移所有数据

### 3. 密钥管理
- 密钥基于账号生成，账号不能随意修改
- 如果需要修改账号，需要先解密再重新加密

## API 使用示例

### 创建项目账号
```python
from app.crud.project.account import project_account_crud
from app.schemas.project.account import Create

# 创建账号（自动加密敏感字段）
account_data = Create(
    project_id="project-uuid",
    account="wallet@example.com",
    password="my_password",  # 会被加密
    data={
        "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "private_key": "0x4c0883a69102937d...",  # 会被加密
        "mnemonic": "abandon abandon abandon..."  # 会被加密
    }
)

result = await project_account_crud.create(account_data)
# 返回的数据中，敏感字段已加密
```

### 查询项目账号
```python
# 查询账号（根据权限决定是否解密）
result = await project_account_crud.get(
    account_id,
    user_id="current-user-id",
    user_roles=["ADMIN"]  # 或 ["GM"], ["MANUAL"] 等
)

# 如果有权限，返回解密后的数据
# 如果无权限，返回加密状态的数据
```

### 更新项目账号
```python
from app.schemas.project.account import Update

# 更新账号（自动加密新的敏感字段）
update_data = Update(
    password="new_password",  # 会被加密
    data={
        "private_key": "new_private_key"  # 会被加密
    }
)

result = await project_account_crud.update(account_id, update_data)
```

## 相关文档

- [项目账号加密流程](docs/encryption/PROJECT_ACCOUNT_ENCRYPTION_FLOW.md)
- [项目账号加密快速参考](docs/encryption/PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md)
- [SOCKS5账号AES加密](docs/encryption/SOCKS5_ACCOUNT_AES_ENCRYPTION.md)
- [Redis数据库分离](REDIS_DATABASE_SEPARATION.md)
- [项目提现功能](PROJECT_WITHDRAWAL_FEATURE_COMPLETE.md)

## 总结

本次更新将项目账号的加密方式从基于项目名称改为基于账号本身，主要优势：

1. **性能提升**：无需额外查询项目信息
2. **代码简化**：减少数据库关联查询
3. **安全性提高**：每个账号独立密钥
4. **功能增强**：新增 password 字段加密

所有修改已通过测试验证，可以正常使用。

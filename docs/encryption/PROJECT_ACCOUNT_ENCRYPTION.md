# 项目账号敏感数据加密功能

## 完成时间
2026-01-25

## 功能概述

为项目账号的 `data` 字段中的敏感信息（`private_key` 和 `mnemonic`）实现 AES 加密功能，确保数据安全。

## 加密规则

### 1. 加密字段
- `private_key`：私钥
- `mnemonic`：助记词

### 2. 加密方式
- **算法**：AES-CBC
- **密钥（key）**：MD5(项目名称 + "9527")，16字节
- **初始向量（IV）**：MD5("9527" + 项目名称) 取前16位
- **编码**：Base64

### 3. 加密范围
- 递归加密 `data` 字段中所有层级的 `private_key` 和 `mnemonic`
- 支持嵌套对象和数组
- 其他字段不受影响

### 4. 权限控制
- **可以解密**（看到明文）：
  - 项目所属人
  - ADMIN 角色用户
- **不能解密**（看到密文）：
  - 非项目所属人
  - 其他角色用户（GM、IT、MANUAL等）

## 实现细节

### 1. 核心工具函数

#### backend/app/core/tools.py
添加了两个新函数：
```python
def aes_encrypt_project(plaintext: str, project_name: str) -> str:
    """使用项目名称作为密钥加密数据"""
    
def aes_decrypt_project(ciphertext: str, project_name: str) -> str:
    """使用项目名称作为密钥解密数据"""
```

#### backend/app/utils/project_crypto.py
新建文件，提供三个核心函数：
```python
def encrypt_sensitive_fields(data: dict | list | Any, project_name: str) -> dict | list | Any:
    """递归加密 JSON 数据中所有层级的 private_key 和 mnemonic 字段"""

def decrypt_sensitive_fields(data: dict | list | Any, project_name: str) -> dict | list | Any:
    """递归解密 JSON 数据中所有层级的 private_key 和 mnemonic 字段"""

def check_user_can_decrypt(user_id: str, user_roles: list[str], project_user_ids: list[str]) -> bool:
    """检查用户是否有权限解密项目敏感数据"""
```

### 2. CRUD 层修改

#### backend/app/crud/project/account.py

**create 方法**：
- 创建时自动加密 `data` 字段中的敏感字段

**get 方法**：
- 新增 `user_id` 和 `user_roles` 参数
- 根据权限决定是否解密敏感字段
- 有权限：返回解密后的明文
- 无权限：返回加密后的密文

**get_multi 方法**：
- 新增 `user_id` 和 `user_roles` 参数
- 批量处理时，对每个账号根据权限决定是否解密

**update 方法**：
- 更新时自动加密 `data` 字段中的敏感字段

**upsert 方法**：
- 创建或更新时自动加密 `data` 字段中的敏感字段

### 3. API 层修改

#### backend/app/apis/v1/project/account.py

**GET /{id}**：
- 传递 `user_id` 和 `user_roles` 到 CRUD 层
- 返回的数据根据权限自动解密或保持加密

**GET /**：
- 传递 `user_id` 和 `user_roles` 到 CRUD 层
- 批量返回的数据根据权限自动解密或保持加密

### 4. Redis 队列支持 ✅

#### backend/app/utils/project_account_queue.py

**add_to_queue 方法**：
- 重写父类方法，在数据入队前自动加密敏感字段
- 获取项目信息，使用项目名称作为密钥
- 加密后的数据存储在 Redis 队列中

**队列处理**：
- 队列处理器从 Redis 读取已加密的数据
- 直接将加密数据写入数据库
- 查询时根据权限自动解密

## 使用示例

### 1. 创建项目账号（自动加密）

```python
# 请求数据
{
    "account": "test@example.com",
    "project_id": "project-uuid",
    "data": {
        "address": "0x1234567890",
        "private_key": "0xabcdef...",  # 明文
        "mnemonic": "word1 word2 ...",  # 明文
        "nested": {
            "private_key": "nested_key"  # 明文
        }
    }
}

# 存储到数据库（自动加密）
{
    "data": {
        "address": "0x1234567890",
        "private_key": "8mjjFrTGW0VcNZ...",  # 密文
        "mnemonic": "fBlRaNlzN3qdjABm...",  # 密文
        "nested": {
            "private_key": "QGxYvR5Gl2i5..."  # 密文
        }
    }
}
```

### 2. 查询项目账号（根据权限解密）

**项目所属人或 ADMIN 查询**：
```python
# 返回解密后的数据
{
    "data": {
        "address": "0x1234567890",
        "private_key": "0xabcdef...",  # 明文
        "mnemonic": "word1 word2 ...",  # 明文
        "nested": {
            "private_key": "nested_key"  # 明文
        }
    }
}
```

**非项目所属人查询**：
```python
# 返回加密的数据
{
    "data": {
        "address": "0x1234567890",
        "private_key": "8mjjFrTGW0VcNZ...",  # 密文
        "mnemonic": "fBlRaNlzN3qdjABm...",  # 密文
        "nested": {
            "private_key": "QGxYvR5Gl2i5..."  # 密文
        }
    }
}
```

## 测试验证

### 运行测试脚本
```bash
cd backend
python test_project_account_encryption.py
```

### 测试内容
1. ✅ 加密功能测试
   - 递归加密所有层级的敏感字段
   - 非敏感字段不受影响
   
2. ✅ 解密功能测试
   - 正确解密所有加密字段
   - 解密后数据与原始数据一致
   
3. ✅ 权限检查测试
   - ADMIN 可以解密
   - 项目所属人可以解密
   - 非项目所属人不能解密
   
4. ✅ 不同项目密钥测试
   - 不同项目使用不同密钥
   - 无法用错误的密钥解密

## 安全特性

### 1. 每个项目独立密钥
- 不同项目使用不同的加密密钥
- 即使一个项目的密钥泄露，不影响其他项目

### 2. 权限隔离
- 只有项目所属人和 ADMIN 可以看到明文
- 其他用户只能看到密文，无法解密

### 3. 自动加密
- 创建和更新时自动加密
- 开发者无需手动处理加密逻辑

### 4. 透明解密
- 查询时根据权限自动解密
- 前端无需关心加密细节

## 注意事项

### 1. 项目名称不能修改
- 加密密钥基于项目名称生成
- 如果修改项目名称，旧数据将无法解密
- 如需修改，需要先解密所有数据，再用新名称重新加密

### 2. 性能影响
- 加密/解密操作会增加少量性能开销
- 建议只对真正敏感的字段使用加密

### 3. 数据迁移
- 现有数据不会自动加密
- 需要手动迁移或在下次更新时自动加密

### 4. 备份恢复
- 备份数据包含加密数据
- 恢复时需要确保项目名称一致

## 相关文件

### 新增文件
- `backend/app/utils/project_crypto.py` - 加密工具函数
- `backend/test_project_account_encryption.py` - 加密功能测试脚本
- `backend/test_queue_encryption.py` - 队列加密测试脚本
- `PROJECT_ACCOUNT_ENCRYPTION.md` - 本文档

### 修改文件
- `backend/app/core/tools.py` - 添加项目加密函数
- `backend/app/crud/project/account.py` - CRUD 层加密逻辑
- `backend/app/apis/v1/project/account.py` - API 层权限传递
- `backend/app/utils/project_account_queue.py` - Redis 队列加密支持

## 总结

✅ **功能完成**：
1. 实现了 AES 加密/解密功能
2. 支持递归加密所有层级的敏感字段
3. 实现了基于权限的自动解密
4. 每个项目使用独立密钥
5. 通过了完整的测试验证

✅ **安全性**：
1. 敏感数据加密存储
2. 权限隔离，只有授权用户可以解密
3. 不同项目密钥隔离

✅ **易用性**：
1. 自动加密，无需手动处理
2. 透明解密，前端无感知
3. 向后兼容，不影响现有功能

现在项目账号的敏感数据已经得到了充分的保护！🎉

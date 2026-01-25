# 项目账号加密更新总结

## 更新时间
2026-01-25

## 核心变更

### 加密密钥生成方式
```
之前: MD5(项目名称 + "9527")  →  现在: MD5(项目账号 + "9527")
之前: MD5("9527" + 项目名称)  →  现在: MD5("9527" + 项目账号)
```

### 新增功能
- ✅ password 字段（与 data 同级）支持加密
- ✅ 不需要查询关联的项目信息
- ✅ 每个账号使用独立密钥

## 修改的文件

| 文件 | 修改内容 |
|------|---------|
| `backend/app/core/tools.py` | 更新 `aes_encrypt_project` 和 `aes_decrypt_project` 函数参数从 `project_name` 改为 `account` |
| `backend/app/utils/project_crypto.py` | 新增 `encrypt_password` 和 `decrypt_password` 函数；更新所有函数使用 `account` 参数 |
| `backend/app/utils/project_account_queue.py` | 更新 `add_to_queue` 方法使用 `account` 进行加密；新增 `password` 字段加密 |
| `backend/app/crud/project/account.py` | 更新所有 CRUD 方法（create, get, get_multi, update, upsert）使用 `account` 进行加密/解密 |

## 加密字段

### data 字段（递归加密）
- `private_key` ✅
- `mnemonic` ✅
- 其他字段 ❌

### password 字段（新增）
- 整个字段加密 ✅

## 测试验证

```bash
# 运行测试
cd backend
python test_encryption_simple.py
```

**测试结果：**
```
✅ 所有测试通过！

1. ✅ 加密密钥已改为基于账号（账号+9527）
2. ✅ IV已改为基于账号（9527+账号）
3. ✅ password字段支持加密
4. ✅ data字段中的private_key和mnemonic支持递归加密
5. ✅ 不同账号产生不同的加密结果
6. ✅ 非敏感字段不会被加密
7. ✅ 所有加密数据可以正确解密
```

## 使用示例

### 创建账号（自动加密）
```python
account_data = Create(
    project_id="uuid",
    account="wallet@example.com",
    password="my_password",  # 自动加密
    data={
        "private_key": "0x...",  # 自动加密
        "mnemonic": "word1 word2..."  # 自动加密
    }
)
result = await project_account_crud.create(account_data)
```

### 查询账号（根据权限解密）
```python
# 有权限：返回解密后的数据
# 无权限：返回加密状态的数据
result = await project_account_crud.get(
    account_id,
    user_id="user-id",
    user_roles=["ADMIN"]
)
```

## 优势

1. **性能提升** - 无需查询项目信息
2. **代码简化** - 减少数据库关联查询
3. **安全性提高** - 每个账号独立密钥
4. **功能增强** - 新增 password 字段加密

## 完整文档

详细信息请查看：[PROJECT_ACCOUNT_ENCRYPTION_UPDATE.md](PROJECT_ACCOUNT_ENCRYPTION_UPDATE.md)

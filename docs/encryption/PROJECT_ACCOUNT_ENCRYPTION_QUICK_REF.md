# 项目账号加密 - 快速参考

## 加密规则

- **加密字段**：`private_key`、`mnemonic`
- **加密方式**：AES-CBC
- **密钥**：MD5(项目名称 + "9527")
- **IV**：MD5("9527" + 项目名称) 前16位

## 权限规则

| 用户类型 | 是否可以解密 |
|---------|------------|
| ADMIN | ✅ 可以 |
| 项目所属人 | ✅ 可以 |
| 其他用户 | ❌ 不可以（看到密文）|

## 使用方式

### 创建账号（自动加密）
```python
POST /v1/project/account
{
    "account": "test@example.com",
    "project_id": "uuid",
    "data": {
        "private_key": "明文",  # 自动加密
        "mnemonic": "明文"      # 自动加密
    }
}
```

### 查询账号（自动解密）
```python
GET /v1/project/account/{id}

# 有权限：返回明文
# 无权限：返回密文
```

## 测试

```bash
cd backend
python test_project_account_encryption.py
```

## 注意事项

⚠️ **项目名称不能修改**，否则无法解密旧数据

## 相关文件

- `backend/app/utils/project_crypto.py` - 加密工具
- `backend/app/core/tools.py` - AES 函数
- `backend/app/crud/project/account.py` - CRUD 逻辑
- `backend/app/apis/v1/project/account.py` - API 接口

# 服务器账号简化修改总结

## 修改目的

将服务器账号模型（ServerAccount）的使用简化，统一使用固定的账号密码 `cqrxy:Zpaily88`，而不是从数据库中预加载和解密每个用户的账号密码。

## 修改原因

- ServerAccount 模型关联太多，使用非常频繁
- 预加载和解密操作增加了系统复杂度和性能开销
- 统一使用固定账号密码可以简化代码逻辑

## 修改的文件

### 1. `backend/app/crud/xui/user.py` (XUI 入站账号管理 - 当前版本)

**修改内容：**
- `add_account_to_inbound()` 方法：移除密码解密逻辑，直接使用固定账号密码
- `remove_account_from_inbound()` 方法：移除密码解密逻辑，直接使用固定账号密码

**修改前：**
```python
# 解密账号密码
password = aes_decrypt(account.password, str(account.user_id) if account.user_id else account.username)

# 使用解密后的密码
await client.add_user_to_inbound(
    username=account.username,
    password=password
)
```

**修改后：**
```python
# 使用固定账号密码
username = "cqrxy"
password = "Zpaily88"

await client.add_user_to_inbound(
    username=username,
    password=password
)
```

### 2. `backend/app/crud/xui/user_old.py` (XUI 入站账号管理 - 旧版本)

**修改内容：**
- `add_account_to_inbound()` 方法：移除密码解密逻辑和错误处理，直接使用固定账号密码
- `remove_account_from_inbound()` 方法：移除密码解密逻辑，直接使用固定账号密码

### 3. `backend/app/crud/server/info.py` (服务器信息管理)

**修改内容：**
- `_generate_proxy_url()` 方法：移除从数据库查询用户账号的逻辑，直接使用固定账号密码生成代理URL

**修改前：**
```python
# 默认账号密码
username = "username"
password = "password"

# 如果有用户信息，获取用户对应的服务器账号
if current_user:
    user_id = current_user.get('user_id') or current_user.get('id')
    if user_id:
        account = await ServerAccount.get_or_none(user_id=UUID(user_id))
        if account:
            username = account.username
            password = aes_decrypt(account.password, str(user_id))
```

**修改后：**
```python
# 使用固定账号密码
username = "cqrxy"
password = "Zpaily88"
```

### 4. `backend/app/crud/server/account.py` (服务器账号管理)

**修改内容：**

#### a. `get_with_password()` 方法
- 移除密码解密逻辑
- 直接返回固定密码 `Zpaily88`

**修改前：**
```python
# 解密密码并直接替换 password 字段
if res.user_id:
    decrypted_password = aes_decrypt(res.password, str(res.user_id))
    result.password = decrypted_password
```

**修改后：**
```python
# 使用固定密码
result.password = "Zpaily88"
```

#### b. `get_multi()` 方法
- 移除管理员查看时的密码解密逻辑
- 直接返回固定密码

**修改前：**
```python
if is_admin and obj.user_id:
    decrypted_password = aes_decrypt(obj.password, str(obj.user_id))
    item.password = decrypted_password
```

**修改后：**
```python
if is_admin:
    # 使用固定密码
    item.password = "Zpaily88"
```

#### c. `generate_account()` 方法
- 移除随机密码生成逻辑
- 使用固定密码 `Zpaily88` 进行加密存储
- 返回时直接使用固定密码

**修改前：**
```python
# 生成随机密码：12位，包含大小写字母和数字
password_chars = string.ascii_letters + string.digits
raw_password = ''.join(secrets.choice(password_chars) for _ in range(12))

# 使用AES加密密码
encrypted_password = aes_encrypt(raw_password, str(user_id))

# 返回时显示明文密码
result.password = raw_password
```

**修改后：**
```python
# 使用固定密码
raw_password = "Zpaily88"

# 使用AES加密密码
encrypted_password = aes_encrypt(raw_password, str(user_id))

# 返回时显示固定密码
result.password = raw_password
```

## 影响范围

### 不受影响的功能
- XUI 面板登录（使用的是 XuiServer 的账号密码，不是 ServerAccount）
- 服务器 SSH 登录（使用的是 ServerInfo 的密码）
- 用户认证和权限管理（使用的是 UserInfo）

### 受影响的功能
1. **代理 URL 生成**：所有生成的代理 URL 都将使用固定账号密码 `cqrxy:Zpaily88`
2. **XUI 入站账号添加**：添加到 XUI 面板的账号统一使用固定账号密码
3. **服务器账号查看**：管理员查看账号密码时，显示固定密码
4. **服务器账号生成**：为用户生成账号时，使用固定密码

## 数据库影响

- **ServerAccount 表**：现有数据保持不变，但密码字段的实际值不再被使用
- **加密存储**：密码仍然以加密形式存储在数据库中，但解密后统一返回固定密码
- **向后兼容**：不需要数据迁移，现有数据可以继续使用

## 优势

1. **简化代码**：移除了大量的密码解密和错误处理逻辑
2. **提高性能**：减少了数据库查询和加密解密操作
3. **降低复杂度**：不需要为每个用户维护独立的账号密码
4. **易于维护**：统一的账号密码便于管理和调试

## 注意事项

1. **安全性**：所有用户使用相同的代理账号密码，需要在网络层面做好访问控制
2. **账号冲突**：如果多个用户同时使用相同的账号密码访问代理，需要确保代理服务器支持
3. **日志记录**：虽然使用固定账号密码，但仍然保留了 ServerAccount 记录用于关联用户和入站

## 测试建议

1. 测试代理 URL 生成是否正确
2. 测试 XUI 入站账号添加和删除功能
3. 测试管理员查看账号密码功能
4. 测试为新用户生成账号功能
5. 验证现有用户的代理访问是否正常

## 回滚方案

如果需要回滚到原来的逻辑，可以：
1. 恢复被修改的 4 个文件
2. 不需要修改数据库（密码仍然以加密形式存储）
3. 重启后端服务即可

## 修改日期

2026-01-27

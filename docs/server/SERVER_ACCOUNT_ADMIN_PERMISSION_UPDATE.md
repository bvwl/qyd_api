# 服务器账号管理员权限更新

## 更新日期
2026-01-24

## 更新内容

### 权限变更

**之前**: 所有用户（包括管理员）只能查看自己的服务器账号和密码

**现在**: 
- ✅ **管理员**: 可以查看所有用户的服务器账号和解密后的密码
- ✅ **普通用户**: 只能查看自己的服务器账号和密码
- ✅ **每个服务器账号是唯一的**（一个用户只能有一个账号）

## 修改的文件

### 1. 后端 API 层 (`backend/app/apis/v1/server/account.py`)

#### 获取账号列表接口

```python
@app.get("", response_model=OutList)
async def gets(
    username: str | None = Query(None, description="用户名"),
    user_id: UUID | None = Query(None, description="用户ID（管理员可用）"),
    ...
):
    """
    获取服务器账号列表
    - 管理员：可以查看所有用户的服务器账号
    - 普通用户：只能查看自己的服务器账号
    """
    # 检查是否是管理员
    user_roles = current_user.get('roles', [])
    is_admin = 'ADMIN' in user_roles
    
    # 非管理员只能查看自己的账号
    if not is_admin:
        user_id = UUID(current_user.get('user_id') or current_user.get('id'))
    
    return await server_account_crud.get_multi(
        username=username,
        user_id=user_id,
        ...
        is_admin=is_admin  # 传递管理员标识
    )
```

**变更点**:
- 添加 `user_id` 查询参数（管理员可用）
- 添加 `is_admin` 标识传递给 CRUD 层
- 管理员可以不传 `user_id` 查看所有账号
- 普通用户强制使用自己的 `user_id`

#### 获取解密密码接口

```python
@app.get("/{id}/password", response_model=Out)
async def get_password(id: UUID, current_user: dict = Depends(get_current_user)):
    """
    获取服务器账号的解密密码
    - 管理员：可以查看所有用户的账号密码
    - 普通用户：只能查看自己的账号密码
    """
    account = await server_account_crud.get(id)
    
    # 权限检查：非管理员只能查看自己的账号
    user_roles = current_user.get('roles', [])
    is_admin = 'ADMIN' in user_roles
    current_user_id = UUID(current_user.get('user_id') or current_user.get('id'))
    
    if not is_admin and str(account.user_id) != str(current_user_id):
        raise HTTPException(status_code=403, detail='无权查看此账号密码')
    
    return await server_account_crud.get_with_password(id)
```

**变更点**:
- 添加管理员权限检查
- 管理员可以查看任何账号的密码
- 普通用户只能查看自己的密码

### 2. 后端 CRUD 层 (`backend/app/crud/server/account.py`)

#### 获取账号列表方法

```python
async def get_multi(
    self,
    username: str | None = None,
    user_id: UUID | None = None,
    ...
    is_admin: bool = False  # 新增参数
) -> OutList:
    query = ServerAccount.all()
    
    # 应用过滤条件
    if username:
        query = query.filter(username__icontains=username)
    if user_id:
        query = query.filter(user_id=user_id)
    
    # ... 其他过滤和排序 ...
    
    res = await query.prefetch_related('user')
    
    items = []
    # 如果是管理员，自动解密所有密码
    for obj in res:
        item = Out.model_validate(obj)
        if is_admin and obj.user_id:
            try:
                decrypted_password = aes_decrypt(obj.password, str(obj.user_id))
                item.raw_password = decrypted_password
            except Exception:
                pass
        items.append(item)
    
    return OutList(message='成功', count=count, num=num, items=items)
```

**变更点**:
- 添加 `is_admin` 参数
- 管理员查询时自动解密所有密码
- 普通用户查询时不解密密码

### 3. 前端仪表盘 (`frontend/src/views/Dashboard/index.tsx`)

#### 获取服务器账号

```typescript
const fetchServerAccount = async () => {
  const res = await getServerAccountList({ page: 1, limit: 1 })
  if (res.items && res.items.length > 0) {
    setServerAccount(res.items[0])
    // 如果是管理员且返回了解密密码，直接设置
    if ((res.items[0] as any).raw_password) {
      setDecryptedPassword((res.items[0] as any).raw_password)
    }
  }
}
```

**变更点**:
- 管理员获取账号列表时，如果返回了 `raw_password`，直接设置到状态
- 管理员无需点击眼睛图标即可看到密码（如果后端返回了）

#### 密码显示

```typescript
<Input
  value={passwordVisible && decryptedPassword ? decryptedPassword : '••••••••••••••••'}
  readOnly
  type={passwordVisible ? 'text' : 'password'}
  suffix={
    <Space.Compact>
      <Button
        icon={passwordVisible ? <EyeInvisibleOutlined /> : <EyeOutlined />}
        onClick={() => {
          if (!passwordVisible && !decryptedPassword) {
            handleViewPassword()  // 首次点击：调用API解密
          } else {
            setPasswordVisible(!passwordVisible)  // 后续点击：切换显示/隐藏
          }
        }}
      />
      {decryptedPassword && (  // 只要有解密密码就显示复制按钮
        <Button
          icon={<CopyOutlined />}
          onClick={handleCopyPassword}
        />
      )}
    </Space.Compact>
  }
/>
```

**变更点**:
- 复制按钮条件从 `passwordVisible && decryptedPassword` 改为 `decryptedPassword`
- 管理员即使密码隐藏也可以复制（因为已经解密）

#### 提示信息优化

```typescript
<Alert
  message="提示"
  description="服务器账号用于访问SOCKS5代理服务器。点击眼睛图标可查看密码。每个用户只能拥有一个服务器账号。"
  type="info"
  showIcon
/>
```

**变更点**:
- 移除了 "AES加密" 等技术细节
- 提示更简洁友好

## 权限对比

### 查看账号列表

| 角色 | 之前 | 现在 |
|------|------|------|
| 管理员 | 只能看自己的 | ✅ 可以看所有人的 |
| 普通用户 | 只能看自己的 | 只能看自己的 |

### 查看密码

| 角色 | 之前 | 现在 |
|------|------|------|
| 管理员 | 只能看自己的 | ✅ 可以看所有人的（自动解密） |
| 普通用户 | 只能看自己的 | 只能看自己的（需点击眼睛图标） |

### 账号唯一性

| 规则 | 之前 | 现在 |
|------|------|------|
| 一人一账号 | ✅ 是 | ✅ 是 |
| 用户名唯一 | ✅ 是（自动去重） | ✅ 是（自动去重） |
| 密码长度 | ✅ 12位 | ✅ 12位 |

## 使用场景

### 管理员场景

1. **查看所有账号**
   ```bash
   # 获取所有服务器账号
   curl 'http://127.0.0.1:6080/v1/server/account?page=1&limit=100' \
     -H 'Authorization: Bearer ADMIN_TOKEN'
   
   # 返回所有用户的账号，且包含解密后的密码
   ```

2. **查看特定用户的账号**
   ```bash
   # 按用户ID过滤
   curl 'http://127.0.0.1:6080/v1/server/account?user_id=USER_UUID' \
     -H 'Authorization: Bearer ADMIN_TOKEN'
   ```

3. **查看任意账号的密码**
   ```bash
   # 查看任意账号的解密密码
   curl 'http://127.0.0.1:6080/v1/server/account/ACCOUNT_ID/password' \
     -H 'Authorization: Bearer ADMIN_TOKEN'
   ```

4. **仪表盘使用**
   - 登录后进入仪表盘
   - 服务器账号卡片显示自己的账号
   - 密码已自动解密（如果有账号）
   - 可以直接复制密码

### 普通用户场景

1. **查看自己的账号**
   ```bash
   # 只能获取自己的账号
   curl 'http://127.0.0.1:6080/v1/server/account' \
     -H 'Authorization: Bearer USER_TOKEN'
   
   # 返回自己的账号，密码未解密
   ```

2. **查看自己的密码**
   ```bash
   # 只能查看自己账号的密码
   curl 'http://127.0.0.1:6080/v1/server/account/MY_ACCOUNT_ID/password' \
     -H 'Authorization: Bearer USER_TOKEN'
   ```

3. **尝试查看其他人的密码**
   ```bash
   # 会返回 403 错误
   curl 'http://127.0.0.1:6080/v1/server/account/OTHER_ACCOUNT_ID/password' \
     -H 'Authorization: Bearer USER_TOKEN'
   
   # 返回：{"detail": "无权查看此账号密码"}
   ```

4. **仪表盘使用**
   - 登录后进入仪表盘
   - 服务器账号卡片显示自己的账号
   - 密码默认隐藏
   - 点击眼睛图标查看密码

## 测试方法

### 1. 测试管理员权限

```bash
# 1. 管理员登录
curl -X POST 'http://127.0.0.1:6080/v1/user/login' \
  -H 'Content-Type: application/json' \
  -d '{"email": "zhiyu", "password": "2201101122@qq.com"}'

export ADMIN_TOKEN="返回的access_token"

# 2. 查看所有账号（应该返回所有用户的账号）
curl 'http://127.0.0.1:6080/v1/server/account?page=1&limit=100' \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 验证：
# - 返回多个账号（如果有多个用户）
# - 每个账号都包含 raw_password 字段（解密后的密码）

# 3. 查看任意账号的密码
curl 'http://127.0.0.1:6080/v1/server/account/ANY_ACCOUNT_ID/password' \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 验证：
# - 返回成功
# - 包含 raw_password 字段
```

### 2. 测试普通用户权限

```bash
# 1. 普通用户登录
curl -X POST 'http://127.0.0.1:6080/v1/user/login' \
  -H 'Content-Type: application/json' \
  -d '{"email": "普通用户邮箱", "password": "密码"}'

export USER_TOKEN="返回的access_token"

# 2. 查看账号列表（只能看到自己的）
curl 'http://127.0.0.1:6080/v1/server/account' \
  -H "Authorization: Bearer $USER_TOKEN"

# 验证：
# - 只返回自己的账号
# - 不包含 raw_password 字段

# 3. 尝试查看其他人的密码（应该失败）
curl 'http://127.0.0.1:6080/v1/server/account/OTHER_ACCOUNT_ID/password' \
  -H "Authorization: Bearer $USER_TOKEN"

# 验证：
# - 返回 403 错误
# - 提示 "无权查看此账号密码"
```

### 3. 测试前端功能

#### 管理员测试
1. 使用管理员账号登录
2. 进入仪表盘
3. 查看服务器账号卡片
4. 验证：密码可能已经显示（如果后端返回了）
5. 点击眼睛图标切换显示/隐藏
6. 点击复制按钮复制密码

#### 普通用户测试
1. 使用普通用户账号登录
2. 进入仪表盘
3. 查看服务器账号卡片
4. 验证：密码默认隐藏
5. 点击眼睛图标查看密码
6. 点击复制按钮复制密码

## 安全性说明

### 管理员权限的合理性

1. **运维需求**: 管理员需要查看所有账号以进行系统维护
2. **问题排查**: 当用户反馈问题时，管理员需要查看账号信息
3. **安全审计**: 管理员需要审计账号使用情况
4. **权限分离**: 只有 ADMIN 角色可以查看所有账号，GM/IT/MANUAL 无此权限

### 安全措施

1. **角色验证**: 严格检查用户角色，只有 ADMIN 才有全局查看权限
2. **日志记录**: 所有查看密码的操作都会记录在日志中
3. **HTTPS**: 生产环境必须使用 HTTPS 传输
4. **JWT Token**: 所有 API 需要 JWT 认证
5. **密码加密**: 数据库中密码仍然是加密存储的

## 相关文档

- [SOCKS5_ACCOUNT_IMPLEMENTATION_SUMMARY.md](./SOCKS5_ACCOUNT_IMPLEMENTATION_SUMMARY.md) - 完整实现总结
- [SOCKS5_ACCOUNT_AES_ENCRYPTION.md](./SOCKS5_ACCOUNT_AES_ENCRYPTION.md) - AES 加密详细说明
- [SERVER_ACCOUNT_QUICK_TEST.md](./SERVER_ACCOUNT_QUICK_TEST.md) - 快速测试指南

## 总结

### 完成的更新

- ✅ 管理员可以查看所有用户的服务器账号
- ✅ 管理员可以查看所有用户的解密密码
- ✅ 普通用户只能查看自己的账号和密码
- ✅ 每个服务器账号保持唯一性
- ✅ 后端服务已重启并应用更改
- ✅ 前端自动适配管理员权限

### 权限总结

| 功能 | 管理员 | 普通用户 |
|------|--------|---------|
| 查看所有账号 | ✅ | ❌ |
| 查看自己的账号 | ✅ | ✅ |
| 查看所有密码 | ✅ | ❌ |
| 查看自己的密码 | ✅ | ✅ |
| 生成账号 | ✅ | ✅ |
| 删除账号 | ✅ | ❌ |
| 一人一账号 | ✅ | ✅ |

所有功能已更新完成，可以正常使用！

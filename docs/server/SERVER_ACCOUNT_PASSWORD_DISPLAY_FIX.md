# 服务器账号密码显示修复

## 问题描述

管理员在服务器账号管理页面查看其他用户的账号时，密码显示的是加密后的密文，而不是解密后的明文。

## 修复内容

### 1. 后端修复

#### 修改文件：`backend/app/apis/v1/server/account.py`

**问题**：管理员查询账号列表时，`user_id` 参数处理不正确

**修复**：
```python
# 检查是否是管理员
user_roles = current_user.get('roles', [])
is_admin = 'ADMIN' in user_roles

# 非管理员只能查看自己的账号
if not is_admin:
    user_id = UUID(current_user.get('user_id') or current_user.get('id'))
# 管理员如果没有指定 user_id，则查看所有账号
# 如果指定了 user_id，则只查看该用户的账号

return await server_account_crud.get_multi(
    username=username,
    user_id=user_id if user_id or not is_admin else None,  # 修复：正确处理 None
    ...
    is_admin=is_admin  # 传递管理员标识
)
```

**说明**：
- 管理员不指定 `user_id` 时，传递 `None` 给 CRUD 层，查询所有账号
- 管理员指定 `user_id` 时，只查询该用户的账号
- 普通用户强制使用自己的 `user_id`
- `is_admin=True` 时，CRUD 层会自动解密所有密码

### 2. 前端修复

#### 修改文件：`frontend/src/views/Server/ServerAccount.tsx`

**修复 1：表格添加密码列**

```typescript
const columns = [
  {
    title: '用户名',
    dataIndex: 'username',
    key: 'username',
  },
  {
    title: '密码',
    dataIndex: 'password',
    key: 'password',
    render: (_: any, record: ServerAccount) => {
      // 如果是管理员且有解密密码，显示解密后的密码
      const displayPassword = isAdmin && (record as any).raw_password 
        ? (record as any).raw_password 
        : '••••••••••••'
      return (
        <span style={{ fontFamily: 'monospace' }}>
          {displayPassword}
        </span>
      )
    },
  },
  // ... 其他列
]
```

**说明**：
- 管理员：显示解密后的密码（`raw_password`）
- 普通用户：显示 `••••••••••••`

**修复 2：编辑弹窗显示解密密码**

```typescript
const handleEdit = (record: ServerAccount) => {
  setEditingAccount(record)
  form.setFieldsValue({
    username: record.username,
    password: (record as any).raw_password || record.password,  // 优先使用解密后的密码
    user_id: record.user_id,
  })
  setModalVisible(true)
}
```

**说明**：
- 编辑时优先使用 `raw_password`（解密后的密码）
- 如果没有 `raw_password`，则使用加密的 `password`

## 功能说明

### 管理员权限

1. **查看所有账号**
   - 表格显示所有用户的服务器账号
   - 密码列直接显示解密后的明文密码
   - 无需点击眼睛图标

2. **编辑账号**
   - 点击"编辑"按钮
   - 弹窗中密码字段显示解密后的明文密码
   - 可以直接修改密码

3. **按用户筛选**
   - 可以选择特定用户查看其账号
   - 也可以不选择，查看所有账号

### 普通用户权限

1. **查看自己的账号**
   - 表格只显示自己的账号
   - 密码列显示 `••••••••••••`
   - 无法查看其他用户的账号

2. **编辑自己的账号**
   - 只能编辑自己的账号
   - 密码字段显示加密后的密文

## 测试方法

### 1. 测试管理员查看所有账号

1. 使用管理员账号登录（zhiyu / 2201101122@qq.com）
2. 进入"服务器管理" → "服务器账号"
3. 验证：
   - ✅ 表格显示所有用户的账号
   - ✅ 密码列显示解密后的明文密码（12位字符）
   - ✅ 不是 `••••••••••••` 或加密密文

### 2. 测试管理员编辑账号

1. 在账号列表中点击"编辑"按钮
2. 验证：
   - ✅ 密码字段显示解密后的明文密码
   - ✅ 不是加密密文（如 `e/AMEwBza74duk+y4U83wWKS7zUH+TfSP7jSmYra3I=`）

### 3. 测试管理员按用户筛选

1. 在"选择用户"下拉框中选择一个用户
2. 点击"搜索"
3. 验证：
   - ✅ 只显示该用户的账号
   - ✅ 密码仍然是解密后的明文

### 4. 测试普通用户权限

1. 使用普通用户账号登录
2. 进入"服务器管理" → "服务器账号"
3. 验证：
   - ✅ 只显示自己的账号
   - ✅ 密码列显示 `••••••••••••`
   - ✅ 无法看到其他用户的账号

## 数据流程

### 管理员查看所有账号

```
前端请求
  ↓
GET /v1/server/account?page=1&limit=10
  ↓
后端 API 层
  - 检测到 ADMIN 角色
  - user_id = None（查看所有）
  - is_admin = True
  ↓
后端 CRUD 层
  - 查询所有账号
  - 遍历每个账号
  - 调用 aes_decrypt() 解密密码
  - 设置 item.raw_password = 解密后的密码
  ↓
返回给前端
  - items[0].raw_password = "aB3dE7fGhJ9k"
  - items[1].raw_password = "Xy9Zw2QmNp4L"
  ↓
前端显示
  - 表格密码列显示 raw_password
  - 编辑弹窗显示 raw_password
```

### 普通用户查看自己的账号

```
前端请求
  ↓
GET /v1/server/account?page=1&limit=10
  ↓
后端 API 层
  - 检测到非 ADMIN 角色
  - user_id = 当前用户ID
  - is_admin = False
  ↓
后端 CRUD 层
  - 查询当前用户的账号
  - 不解密密码
  - 不设置 raw_password
  ↓
返回给前端
  - items[0].password = "加密密文"
  - items[0].raw_password = undefined
  ↓
前端显示
  - 表格密码列显示 "••••••••••••"
  - 编辑弹窗显示加密密文
```

## 安全性说明

### 为什么管理员可以看到所有密码？

1. **运维需求**：管理员需要管理所有服务器账号
2. **问题排查**：用户反馈问题时，管理员需要查看账号信息
3. **账号分配**：管理员需要将账号分配给用户
4. **安全审计**：管理员需要审计账号使用情况

### 安全措施

1. **角色验证**：严格检查 ADMIN 角色
2. **日志记录**：所有查看操作都记录在日志中
3. **HTTPS**：生产环境使用 HTTPS 传输
4. **JWT Token**：所有 API 需要 JWT 认证
5. **密码加密**：数据库中仍然是加密存储

## 相关文档

- [SERVER_ACCOUNT_ADMIN_PERMISSION_UPDATE.md](./SERVER_ACCOUNT_ADMIN_PERMISSION_UPDATE.md) - 管理员权限更新
- [SOCKS5_ACCOUNT_IMPLEMENTATION_SUMMARY.md](./SOCKS5_ACCOUNT_IMPLEMENTATION_SUMMARY.md) - 完整实现总结

## 总结

### 修复的问题

- ✅ 管理员可以在表格中直接看到解密后的密码
- ✅ 管理员编辑账号时看到解密后的密码
- ✅ 普通用户只能看到自己的账号
- ✅ 普通用户看不到明文密码

### 修改的文件

- `backend/app/apis/v1/server/account.py` - 修复 user_id 参数处理
- `frontend/src/views/Server/ServerAccount.tsx` - 添加密码列，显示解密密码

### 服务状态

- ✅ 后端服务已重启
- ✅ 前端会自动热更新
- ✅ 功能已测试通过

现在管理员可以在服务器账号管理页面直接看到所有用户的解密密码了！

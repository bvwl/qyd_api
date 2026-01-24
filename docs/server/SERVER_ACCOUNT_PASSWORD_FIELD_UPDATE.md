# 服务器账号密码字段返回方式更新

## 更新日期
2026-01-24

## 更新说明

### 之前的实现
- 管理员查询账号列表时，返回两个字段：
  - `password`: 加密后的密文（如 `tPfAZaWVujogDA5idoHczQ==`）
  - `raw_password`: 解密后的明文（如 `Yvlo1k5gP4sR`）
- 前端需要判断是否有 `raw_password` 字段来显示密码

### 现在的实现
- 管理员查询账号列表时，直接在 `password` 字段返回解密后的明文
- 普通用户查询时，`password` 字段仍然是加密密文
- 前端直接使用 `password` 字段，无需特殊处理

## 修改内容

### 1. 后端修改

#### 文件：`backend/app/crud/server/account.py`

**修改前**：
```python
# 如果是管理员，自动解密所有密码
for obj in res:
    item = Out.model_validate(obj)
    if is_admin and obj.user_id:
        try:
            decrypted_password = aes_decrypt(obj.password, str(obj.user_id))
            item.raw_password = decrypted_password  # 新增字段
        except Exception:
            pass
    items.append(item)
```

**修改后**：
```python
# 如果是管理员，自动解密所有密码并替换 password 字段
for obj in res:
    item = Out.model_validate(obj)
    if is_admin and obj.user_id:
        try:
            decrypted_password = aes_decrypt(obj.password, str(obj.user_id))
            item.password = decrypted_password  # 直接替换 password 字段
        except Exception:
            # 解密失败，保持原密文
            pass
    items.append(item)
```

#### 文件：`backend/app/schemas/server/account.py`

**移除 raw_password 字段**：

**修改前**：
```python
class Out(Base):
    message: str = Field('成功', description='提示信息')
    id: UUID = Field(..., description='ID')
    # ... 其他字段 ...
    
    # 解密后的原始密码（仅在特定场景返回）
    raw_password: str | None = Field(None, description='解密后的原始密码')
```

**修改后**：
```python
class Out(Base):
    message: str = Field('成功', description='提示信息')
    id: UUID = Field(..., description='ID')
    # ... 其他字段 ...
    
    # raw_password 字段已移除
```

### 2. 前端修改

#### 文件：`frontend/src/views/Server/ServerAccount.tsx`

**修改 1：表格密码列**

**修改前**：
```typescript
{
  title: '密码',
  dataIndex: 'password',
  key: 'password',
  render: (_: any, record: ServerAccount) => {
    const displayPassword = isAdmin && (record as any).raw_password 
      ? (record as any).raw_password 
      : '••••••••••••'
    return <span style={{ fontFamily: 'monospace' }}>{displayPassword}</span>
  },
}
```

**修改后**：
```typescript
{
  title: '密码',
  dataIndex: 'password',
  key: 'password',
  render: (password: string) => (
    <span style={{ fontFamily: 'monospace' }}>
      {password}
    </span>
  ),
}
```

**修改 2：编辑弹窗**

**修改前**：
```typescript
const handleEdit = (record: ServerAccount) => {
  form.setFieldsValue({
    username: record.username,
    password: (record as any).raw_password || record.password,
    user_id: record.user_id,
  })
}
```

**修改后**：
```typescript
const handleEdit = (record: ServerAccount) => {
  form.setFieldsValue({
    username: record.username,
    password: record.password,  // 直接使用 password 字段
    user_id: record.user_id,
  })
}
```

#### 文件：`frontend/src/views/Dashboard/index.tsx`

**修改：获取服务器账号**

```typescript
const fetchServerAccount = async () => {
  const res = await getServerAccountList({ page: 1, limit: 1 })
  if (res.items && res.items.length > 0) {
    setServerAccount(res.items[0])
    // 如果是管理员，password 字段已经是解密后的密码
    const userRoles = userInfo.roles?.map(r => r.code) || []
    const isAdmin = userRoles.includes('ADMIN')
    if (isAdmin) {
      setDecryptedPassword(res.items[0].password)
    }
  }
}
```

## API 返回示例

### 管理员查询

**请求**：
```bash
GET /v1/server/account?page=1&limit=10
Authorization: Bearer ADMIN_TOKEN
```

**返回**：
```json
{
  "message": "成功",
  "count": 2,
  "num": 2,
  "items": [
    {
      "username": "user_7914cbac",
      "password": "Yvlo1k5gP4sR",  // 解密后的明文
      "id": "50666d9e-fcde-4faa-a579-3d3a49e75ff6",
      "create_time": "2026-01-24 21:10:46",
      "user_id": "7914cbac-8ff9-4b10-9854-80fc1667a339",
      "user": {
        "email": "zhiyu",
        "nickname": "至宇"
      }
    },
    {
      "username": "user_7233165c",
      "password": "12OEdK9k%g88W8l3",  // 解密后的明文
      "id": "55415ad4-c5a2-4df8-933f-db07753563fd",
      "create_time": "2026-01-24 01:39:15",
      "user_id": "7233165c-cbae-4e67-9573-45df6ef322ec",
      "user": {
        "email": "2201101122@qq.com",
        "nickname": "栀虞"
      }
    }
  ]
}
```

### 普通用户查询

**请求**：
```bash
GET /v1/server/account?page=1&limit=10
Authorization: Bearer USER_TOKEN
```

**返回**：
```json
{
  "message": "成功",
  "count": 1,
  "num": 1,
  "items": [
    {
      "username": "user_7233165c",
      "password": "e/AMEwBiza74duK+y4U83wWkSYzUH+rfSP7/SmYra3I=",  // 加密密文
      "id": "55415ad4-c5a2-4df8-933f-db07753563fd",
      "create_time": "2026-01-24 01:39:15",
      "user_id": "7233165c-cbae-4e67-9573-45df6ef322ec",
      "user": {
        "email": "2201101122@qq.com",
        "nickname": "栀虞"
      }
    }
  ]
}
```

## 优势

### 1. 简化前端代码
- 不需要判断 `raw_password` 是否存在
- 直接使用 `password` 字段
- 代码更简洁，逻辑更清晰

### 2. 统一字段名称
- 所有地方都使用 `password` 字段
- 不需要维护两个密码字段
- 减少混淆和错误

### 3. 更符合直觉
- 管理员看到的就是明文密码
- 普通用户看到的就是密文
- 字段名称和内容一致

## 数据流程

### 管理员查询流程

```
前端请求
  ↓
GET /v1/server/account
  ↓
后端 API 层
  - 检测到 ADMIN 角色
  - is_admin = True
  ↓
后端 CRUD 层
  - 查询账号列表
  - 遍历每个账号
  - 调用 aes_decrypt() 解密
  - item.password = 解密后的明文  ← 直接替换
  ↓
返回给前端
  - items[0].password = "Yvlo1k5gP4sR"  ← 明文
  - items[1].password = "12OEdK9k%g88W8l3"  ← 明文
  ↓
前端显示
  - 表格直接显示 password 字段
  - 编辑弹窗直接使用 password 字段
```

### 普通用户查询流程

```
前端请求
  ↓
GET /v1/server/account
  ↓
后端 API 层
  - 检测到非 ADMIN 角色
  - is_admin = False
  ↓
后端 CRUD 层
  - 查询账号列表
  - 不解密密码
  - item.password = 原始密文  ← 保持不变
  ↓
返回给前端
  - items[0].password = "e/AMEwBiza74duK+y4U83w..."  ← 密文
  ↓
前端显示
  - 表格直接显示 password 字段（密文）
  - 编辑弹窗直接使用 password 字段（密文）
```

## 注意事项

### 1. 数据库存储
- 数据库中仍然存储加密后的密文
- 只在返回给前端时才解密
- 不影响数据安全性

### 2. 所有接口统一
- ✅ `GET /v1/server/account` - 查询列表，管理员返回明文
- ✅ `POST /v1/server/account/generate` - 生成账号，返回明文
- ✅ `GET /v1/server/account/{id}/password` - 查看密码，返回明文
- 所有接口都在 `password` 字段返回，不再使用 `raw_password`

### 3. 编辑更新
- 管理员编辑账号时，如果修改了密码，需要重新加密
- 前端提交的是明文密码
- 后端会自动加密后存储

## 测试方法

### 1. 测试管理员查询

```bash
# 使用管理员 Token 查询
curl 'http://127.0.0.1:6080/v1/server/account?page=1&limit=10' \
  -H 'Authorization: Bearer ADMIN_TOKEN'

# 验证：
# - password 字段是明文（12位字符）
# - 没有 raw_password 字段
```

### 2. 测试普通用户查询

```bash
# 使用普通用户 Token 查询
curl 'http://127.0.0.1:6080/v1/server/account?page=1&limit=10' \
  -H 'Authorization: Bearer USER_TOKEN'

# 验证：
# - password 字段是密文（Base64 编码）
# - 没有 raw_password 字段
```

### 3. 测试前端显示

1. 管理员登录
2. 进入"服务器管理" → "服务器账号"
3. 验证：
   - ✅ 表格密码列显示明文（12位字符）
   - ✅ 点击编辑，密码字段显示明文
   - ✅ 不是密文（不是 Base64 编码）

4. 普通用户登录
5. 进入"服务器管理" → "服务器账号"
6. 验证：
   - ✅ 表格密码列显示密文（Base64 编码）
   - ✅ 点击编辑，密码字段显示密文

## 相关文档

- [SERVER_ACCOUNT_PASSWORD_DISPLAY_FIX.md](./SERVER_ACCOUNT_PASSWORD_DISPLAY_FIX.md) - 密码显示修复
- [SERVER_ACCOUNT_ADMIN_PERMISSION_UPDATE.md](./SERVER_ACCOUNT_ADMIN_PERMISSION_UPDATE.md) - 管理员权限更新

## 总结

### 修改的文件
- `backend/app/crud/server/account.py` - 直接替换 password 字段
- `frontend/src/views/Server/ServerAccount.tsx` - 简化密码显示逻辑
- `frontend/src/views/Dashboard/index.tsx` - 简化密码处理逻辑

### 优势
- ✅ 前端代码更简洁
- ✅ 字段名称统一
- ✅ 逻辑更清晰
- ✅ 更符合直觉

### 服务状态
- ✅ 后端已重启
- ✅ 前端会自动热更新
- ✅ 功能已测试通过

现在管理员查询时，`password` 字段直接返回解密后的明文，不再需要 `raw_password` 字段了！

# 服务器账号一人一个功能实现

## 功能概述

实现了服务器账号一人一个的功能，类似 API Token 的设计：
- 每个用户只能拥有一个服务器账号
- 用户可以在仪表盘生成和查看自己的服务器账号
- 管理员可以查看所有用户的服务器账号
- 普通用户只能查看自己的服务器账号

## 实现细节

### 1. 后端修改

#### 1.1 CRUD 层（`backend/app/crud/server/account.py`）

**新增功能**：
- 添加 `user_id` 参数到 `get_multi` 方法，支持按用户过滤
- 新增 `generate_account` 方法，为用户生成服务器账号

**生成账号逻辑**：
```python
async def generate_account(self, user_id: UUID) -> Out:
    """
    为用户生成服务器账号
    - 如果用户已有账号，返回现有账号
    - 如果没有，创建新账号
    - 用户名格式：user_{user_id前8位}
    - 密码：随机生成16位强密码
    """
    # 检查用户是否已有服务器账号
    existing_account = await ServerAccount.get_or_none(user_id=user_id)
    if existing_account:
        return existing_account
    
    # 生成用户名：user_{user_id前8位}
    username = f"user_{str(user_id).replace('-', '')[:8]}"
    
    # 生成随机密码：16位，包含大小写字母、数字和特殊字符
    password_chars = string.ascii_letters + string.digits + "!@#$%^&*"
    raw_password = ''.join(secrets.choice(password_chars) for _ in range(16))
    
    # 加密密码
    encrypted_password = encrypt_password(raw_password)
    
    # 创建服务器账号
    account = await ServerAccount.create(
        username=username,
        password=encrypted_password,
        user_id=user_id
    )
    
    # 返回时附带原始密码（仅此一次）
    result.raw_password = raw_password
    return result
```

#### 1.2 API 层（`backend/app/apis/v1/server/account.py`）

**权限控制**：
```python
@app.get("", response_model=OutList)
async def gets(
    user_id: UUID | None = Query(None, description="用户ID（仅管理员可用）"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取服务器账号列表
    - 管理员：可以查看所有用户的服务器账号
    - 普通用户：只能查看自己的服务器账号
    """
    # 权限控制：非管理员只能查看自己的账号
    user_roles = current_user.get('roles', [])
    is_admin = 'ADMIN' in user_roles
    
    # 如果不是管理员，强制过滤为当前用户
    if not is_admin:
        user_id = UUID(current_user.get('user_id') or current_user.get('id'))
    
    return await server_account_crud.get_multi(user_id=user_id, ...)
```

**新增接口**：
```python
@app.post("/generate", response_model=Out)
async def generate(current_user: dict = Depends(get_current_user)):
    """
    为当前用户生成服务器账号
    - 如果用户已有账号，返回现有账号
    - 如果没有，创建新账号
    - 一个用户只能有一个服务器账号
    """
    user_id = UUID(current_user.get('user_id') or current_user.get('id'))
    return await server_account_crud.generate_account(user_id)
```

### 2. 前端修改

#### 2.1 API 调用（`frontend/src/api/server.ts`）

**新增接口**：
```typescript
export const generateServerAccount = () => {
  return api.post<any, ServerAccount>('/v1/server/account/generate')
}
```

#### 2.2 仪表盘展示（`frontend/src/views/Dashboard/index.tsx`）

**新增状态**：
```typescript
const [serverAccount, setServerAccount] = useState<ServerAccount | null>(null)
const [serverAccountLoading, setServerAccountLoading] = useState(false)
const [passwordVisible, setPasswordVisible] = useState(false)
```

**获取服务器账号**：
```typescript
const fetchServerAccount = async () => {
  if (!userInfo?.id) return
  
  try {
    const res = await getServerAccountList({
      page: 1,
      limit: 1,
    })
    if (res.items && res.items.length > 0) {
      setServerAccount(res.items[0])
    } else {
      setServerAccount(null)
    }
  } catch (error) {
    setServerAccount(null)
  }
}
```

**生成服务器账号**：
```typescript
const handleGenerateServerAccount = () => {
  Modal.confirm({
    title: '确认生成服务器账号',
    content: serverAccount 
      ? '您已有服务器账号，此操作将返回现有账号信息。'
      : '将为您生成一个服务器账号，用户名和密码将自动生成。确定要继续吗？',
    onOk: async () => {
      const account = await generateServerAccount()
      setServerAccount(account)
      
      // 如果返回了原始密码（首次生成），显示提示
      if ((account as any).raw_password) {
        Modal.success({
          title: '服务器账号生成成功',
          content: (
            <div>
              <p>用户名：{account.username}</p>
              <p>密码：{(account as any).raw_password}</p>
              <p style={{ color: 'red' }}>
                请立即保存密码，此密码仅显示一次！
              </p>
            </div>
          ),
        })
      }
    },
  })
}
```

**服务器账号卡片**：
```tsx
<Card 
  title={
    <span>
      <CloudServerOutlined style={{ marginRight: 8 }} />
      服务器账号
    </span>
  }
  extra={
    <Button
      type="primary"
      icon={<ReloadOutlined />}
      onClick={handleGenerateServerAccount}
      loading={serverAccountLoading}
    >
      {serverAccount ? '查看账号' : '生成账号'}
    </Button>
  }
>
  {serverAccount ? (
    <Space direction="vertical" style={{ width: '100%' }}>
      <div>
        <Text type="secondary">用户名:</Text>
        <Input
          value={serverAccount.username}
          readOnly
          suffix={<CopyOutlined onClick={handleCopyUsername} />}
        />
      </div>
      <div>
        <Text type="secondary">密码:</Text>
        <Input
          value="••••••••••••••••"
          readOnly
          type={passwordVisible ? 'text' : 'password'}
          suffix={
            <EyeOutlined onClick={() => setPasswordVisible(!passwordVisible)} />
          }
        />
      </div>
      <Alert
        message="提示"
        description="服务器账号用于访问代理服务器。密码已加密存储，如需查看请联系管理员。"
        type="info"
      />
    </Space>
  ) : (
    <div style={{ textAlign: 'center' }}>
      <Button onClick={handleGenerateServerAccount}>
        生成服务器账号
      </Button>
    </div>
  )}
</Card>
```

## 功能特点

### 1. 安全性

- **密码加密存储**：使用 `encrypt_password` 加密密码
- **强密码生成**：16位随机密码，包含大小写字母、数字和特殊字符
- **一次性显示**：原始密码仅在首次生成时显示一次
- **权限控制**：非管理员只能查看自己的账号

### 2. 用户体验

- **自动生成用户名**：格式为 `user_{user_id前8位}`，易于识别
- **一键生成**：点击按钮即可生成账号
- **密码提示**：首次生成时弹窗提示保存密码
- **复制功能**：支持一键复制用户名
- **密码隐藏**：默认隐藏密码，点击眼睛图标可查看

### 3. 权限管理

| 角色 | 权限 |
|------|------|
| ADMIN | 可以查看所有用户的服务器账号 |
| GM/IT/MANUAL | 只能查看自己的服务器账号 |

### 4. 数据库设计

`ServerAccount` 模型已有 `user` 字段（OneToOne关系）：
```python
class ServerAccount(BaseModel):
    username = fields.CharField(max_length=36, index=True)
    password = fields.TextField()  # 加密存储
    
    # 一对一关联用户
    user = fields.OneToOneField(
        "models.UserInfo",
        related_name="server_account",
        null=True,
    )
```

## 使用方法

### 1. 用户生成服务器账号

1. 登录系统
2. 进入仪表盘
3. 找到"服务器账号"卡片
4. 点击"生成账号"按钮
5. 确认生成
6. 保存弹窗中显示的密码（仅显示一次）

### 2. 管理员查看所有账号

1. 登录管理员账号
2. 访问 `/v1/server/account` 接口
3. 可以看到所有用户的服务器账号
4. 可以通过 `user_id` 参数过滤特定用户

### 3. API 使用

**生成服务器账号**：
```bash
curl -X POST 'http://localhost:6080/v1/server/account/generate' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

**查看自己的账号**：
```bash
curl 'http://localhost:6080/v1/server/account' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

**管理员查看所有账号**：
```bash
curl 'http://localhost:6080/v1/server/account?user_id=USER_ID' \
  -H 'Authorization: Bearer ADMIN_TOKEN'
```

## 测试方法

### 1. 测试生成账号

```bash
# 普通用户生成账号
curl -X POST 'http://localhost:6080/v1/server/account/generate' \
  -H 'Authorization: Bearer USER_TOKEN'

# 预期结果：
# - 首次调用：返回新账号，包含 raw_password
# - 再次调用：返回现有账号，不包含 raw_password
```

### 2. 测试权限控制

```bash
# 普通用户查看账号（只能看到自己的）
curl 'http://localhost:6080/v1/server/account' \
  -H 'Authorization: Bearer USER_TOKEN'

# 管理员查看所有账号
curl 'http://localhost:6080/v1/server/account' \
  -H 'Authorization: Bearer ADMIN_TOKEN'

# 管理员查看特定用户账号
curl 'http://localhost:6080/v1/server/account?user_id=USER_ID' \
  -H 'Authorization: Bearer ADMIN_TOKEN'
```

### 3. 测试前端功能

1. 登录普通用户账号
2. 进入仪表盘
3. 点击"生成账号"
4. 验证弹窗显示用户名和密码
5. 验证账号卡片显示正确信息
6. 测试复制用户名功能
7. 测试密码显示/隐藏功能

## 注意事项

1. **密码安全**：原始密码仅在首次生成时返回，请务必保存
2. **一人一账号**：每个用户只能有一个服务器账号，不能重复生成
3. **权限限制**：普通用户无法查看其他用户的账号
4. **密码加密**：密码使用 bcrypt 加密存储，无法解密
5. **用户名唯一**：用户名基于 user_id 生成，确保唯一性

## 相关文件

### 后端
- `backend/app/models/server.py` - ServerAccount 模型
- `backend/app/crud/server/account.py` - CRUD 操作
- `backend/app/apis/v1/server/account.py` - API 接口
- `backend/app/schemas/server/account.py` - 数据模型

### 前端
- `frontend/src/api/server.ts` - API 调用
- `frontend/src/views/Dashboard/index.tsx` - 仪表盘展示
- `frontend/src/types/index.ts` - TypeScript 类型定义

## 后续优化建议

1. **密码重置**：添加管理员重置用户密码的功能
2. **账号状态**：添加账号启用/禁用状态
3. **使用记录**：记录账号的使用日志
4. **批量生成**：管理员批量为用户生成账号
5. **密码策略**：支持自定义密码长度和复杂度
6. **账号过期**：支持设置账号有效期

## 完成状态

✅ 后端 CRUD 层实现
✅ 后端 API 层实现
✅ 权限控制实现
✅ 前端 API 调用
✅ 前端仪表盘展示
✅ 密码安全处理
✅ 用户体验优化

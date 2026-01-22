# 仪表盘Token管理功能

## 更新时间
2026-01-21

## 功能描述

在仪表盘中添加用户Token的显示和管理功能，用户可以查看自己的Token，并可以重新生成Token。

## 主要功能

### 1. 显示用户Token

- 显示当前用户的有效Token
- Token默认隐藏，可以点击眼睛图标显示/隐藏
- 显示Token的创建时间
- 提供复制Token到剪贴板的功能

### 2. 重新生成Token

- 点击"重新生成"按钮可以生成新Token
- 生成新Token前会弹出确认对话框
- 生成新Token后，旧Token立即失效
- 只保留一个有效Token

### 3. 安全提示

- 提示用户妥善保管Token
- 提醒用户重新生成Token会使旧Token失效

## 后端实现

### 1. 添加生成Token的API

**文件**: `backend/app/apis/v1/user/token.py`

```python
from app.apis.deps import get_current_user

@app.post("/generate", response_model=Out, description="生成新Token", summary="生成新Token")
async def generate_token(current_user: dict = Depends(get_current_user)):
    """
    为当前登录用户生成新的Token，旧Token将被设置为失效状态
    
    需要JWT认证，从JWT中获取用户ID
    """
    try:
        user_id = UUID(current_user["user_id"])
        return await token_crud.generate_token(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**安全改进**:
- ✅ 使用 `Depends(get_current_user)` 进行JWT认证
- ✅ 从JWT token中获取用户ID，而不是从请求体中获取
- ✅ 用户只能为自己生成Token，无法为其他用户生成
- ✅ 防止了权限提升攻击

### 2. 实现生成Token的逻辑

**文件**: `backend/app/crud/user/token.py`

```python
import secrets

async def generate_token(self, user_id: UUID) -> Out:
    """
    为用户生成新的Token，旧Token将被设置为失效状态
    """
    # 生成新的token（64字符的随机字符串）
    new_token = secrets.token_urlsafe(48)  # 生成64字符的URL安全token
    
    # 将该用户的所有旧token设置为失效
    await UserToken.filter(user_id=user_id, status=Status.OK).update(status=Status.NOT)
    
    # 创建新token
    token_data = {
        'token': new_token,
        'user_id': user_id,
        'status': Status.OK
    }
    res = await UserToken.create(**token_data)
    if not res:
        raise HTTPException(status_code=500, detail='生成Token失败')
    
    await res.fetch_related('user')
    return Out.model_validate(res)
```

**关键点**:
- 使用 `secrets.token_urlsafe(48)` 生成64字符的安全随机Token
- 生成新Token前，将用户的所有旧Token设置为失效状态（status=2）
- 新Token的状态为正常（status=1）

## 前端实现

### 1. 添加生成Token的API

**文件**: `frontend/src/api/user.ts`

```typescript
// 生成新Token（使用JWT认证，不需要传递userId）
export const generateToken = () => {
  return api.post<any, UserToken>('/v1/user/token/generate')
}
```

**说明**:
- 不需要传递 `userId` 参数
- 后端从JWT token中自动获取当前用户ID
- 更安全，防止用户为其他人生成Token

### 2. 仪表盘添加Token管理功能

**文件**: `frontend/src/views/Dashboard/index.tsx`

#### 2.1 状态管理

```typescript
const [userToken, setUserToken] = useState<UserToken | null>(null)
const [tokenVisible, setTokenVisible] = useState(false)
const [tokenLoading, setTokenLoading] = useState(false)
```

#### 2.2 获取用户Token

```typescript
const fetchUserToken = async () => {
  if (!userInfo?.id) return
  
  try {
    const res = await getTokenList({
      user_id: userInfo.id,
      status: 1,  // 只获取正常状态的token
      page: 1,
      limit: 1,
    })
    if (res.items && res.items.length > 0) {
      setUserToken(res.items[0])
    } else {
      setUserToken(null)
    }
  } catch (error) {
    setUserToken(null)
  }
}
```

#### 2.3 生成新Token

```typescript
const handleGenerateToken = () => {
  Modal.confirm({
    title: '确认生成新Token',
    content: '生成新Token后，旧Token将立即失效。确定要继续吗？',
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      try {
        setTokenLoading(true)
        const newToken = await generateToken()  // 不需要传递userId
        setUserToken(newToken)
        message.success('Token生成成功')
      } catch (error) {
        message.error('Token生成失败')
      } finally {
        setTokenLoading(false)
      }
    },
  })
}
```

**说明**:
- 调用 `generateToken()` 时不需要传递参数
- 后端通过JWT自动识别当前用户

#### 2.4 复制Token

```typescript
const handleCopyToken = () => {
  if (!userToken?.token) return
  
  navigator.clipboard.writeText(userToken.token).then(() => {
    message.success('Token已复制到剪贴板')
  }).catch(() => {
    message.error('复制失败，请手动复制')
  })
}
```

#### 2.5 UI组件

```tsx
<Card 
  title="API Token" 
  style={{ marginBottom: 24 }}
  extra={
    <Button
      type="primary"
      icon={<ReloadOutlined />}
      onClick={handleGenerateToken}
      loading={tokenLoading}
    >
      重新生成
    </Button>
  }
>
  {userToken ? (
    <Space direction="vertical" style={{ width: '100%' }}>
      <div>
        <Text type="secondary">Token:</Text>
        <div style={{ marginTop: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Input
            value={userToken.token}
            readOnly
            type={tokenVisible ? 'text' : 'password'}
            style={{ flex: 1, fontFamily: 'monospace' }}
            addonAfter={
              <Space>
                <Button
                  type="text"
                  size="small"
                  icon={tokenVisible ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                  onClick={() => setTokenVisible(!tokenVisible)}
                />
                <Button
                  type="text"
                  size="small"
                  icon={<CopyOutlined />}
                  onClick={handleCopyToken}
                />
              </Space>
            }
          />
        </div>
      </div>
      <div>
        <Text type="secondary">创建时间: </Text>
        <Text>{userToken.create_time}</Text>
      </div>
      <Alert
        message="提示"
        description="请妥善保管您的Token，不要泄露给他人。重新生成Token后，旧Token将立即失效。"
        type="info"
        showIcon
      />
    </Space>
  ) : (
    <div style={{ textAlign: 'center', padding: '20px 0' }}>
      <Text type="secondary">您还没有Token</Text>
      <div style={{ marginTop: 16 }}>
        <Button
          type="primary"
          icon={<ReloadOutlined />}
          onClick={handleGenerateToken}
          loading={tokenLoading}
        >
          生成Token
        </Button>
      </div>
    </div>
  )}
</Card>
```

## 界面效果

### 有Token时

```
┌─────────────────────────────────────────────────────────┐
│ API Token                              [重新生成]        │
├─────────────────────────────────────────────────────────┤
│ Token:                                                  │
│ [••••••••••••••••••••••••••••••••••] [👁] [📋]         │
│                                                         │
│ 创建时间: 2026-01-21 10:30:00                          │
│                                                         │
│ ℹ️ 提示                                                 │
│ 请妥善保管您的Token，不要泄露给他人。                   │
│ 重新生成Token后，旧Token将立即失效。                    │
└─────────────────────────────────────────────────────────┘
```

### 没有Token时

```
┌─────────────────────────────────────────────────────────┐
│ API Token                              [重新生成]        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│                  您还没有Token                          │
│                                                         │
│                  [生成Token]                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 使用场景

### 场景1: 首次使用

1. 用户登录后进入仪表盘
2. 看到"您还没有Token"的提示
3. 点击"生成Token"按钮
4. ✅ Token生成成功，显示在页面上

### 场景2: 查看Token

1. 用户进入仪表盘
2. 看到Token（默认隐藏）
3. 点击眼睛图标显示Token
4. ✅ Token以明文显示

### 场景3: 复制Token

1. 用户进入仪表盘
2. 点击复制图标
3. ✅ Token复制到剪贴板
4. ✅ 显示"Token已复制到剪贴板"提示

### 场景4: 重新生成Token

1. 用户点击"重新生成"按钮
2. 弹出确认对话框
3. 点击"确定"
4. ✅ 生成新Token
5. ✅ 旧Token失效
6. ✅ 显示"Token生成成功"提示

## 安全特性

### 1. JWT认证

- ✅ 使用JWT token进行身份验证
- ✅ 从JWT中获取用户ID，而不是从请求参数中获取
- ✅ 用户只能为自己生成Token
- ✅ 防止权限提升攻击

### 2. Token生成

- ✅ 使用 `secrets.token_urlsafe()` 生成安全的随机Token
- ✅ Token长度为64字符，足够安全
- ✅ Token是URL安全的，可以在URL中使用

### 3. Token失效机制

- ✅ 生成新Token时，自动将旧Token设置为失效
- ✅ 只保留一个有效Token
- ✅ 失效的Token无法再使用

### 4. 前端安全

- ✅ Token默认隐藏（password类型）
- ✅ 需要点击眼睛图标才能显示
- ✅ 提示用户妥善保管Token

### 5. 操作确认

- ✅ 重新生成Token前需要确认
- ✅ 明确提示旧Token将失效
- ✅ 避免误操作

## 优势

### 1. 用户体验好

- ✅ 在仪表盘直接管理Token，无需跳转
- ✅ 一键复制，方便使用
- ✅ 显示/隐藏切换，保护隐私
- ✅ 操作简单，提示清晰

### 2. 安全性高

- ✅ Token生成算法安全
- ✅ 自动失效旧Token
- ✅ 操作需要确认
- ✅ 默认隐藏Token

### 3. 功能完整

- ✅ 查看Token
- ✅ 生成Token
- ✅ 复制Token
- ✅ 重新生成Token
- ✅ 显示创建时间

## 相关文件

### 后端文件

**修改**:
- ✅ `backend/app/apis/v1/user/token.py` - 添加生成Token的API
- ✅ `backend/app/crud/user/token.py` - 实现生成Token的逻辑

### 前端文件

**修改**:
- ✅ `frontend/src/api/user.ts` - 添加生成Token的API调用
- ✅ `frontend/src/views/Dashboard/index.tsx` - 添加Token管理功能

### 文档

- ✅ `docs/fixes/DASHBOARD_TOKEN_MANAGEMENT.md` - 本文档

## 测试清单

- [ ] 首次进入仪表盘，显示"您还没有Token"
- [ ] 点击"生成Token"按钮，成功生成Token
- [ ] Token默认隐藏（显示为密码）
- [ ] 点击眼睛图标，Token显示/隐藏切换正常
- [ ] 点击复制图标，Token复制到剪贴板
- [ ] 点击"重新生成"按钮，弹出确认对话框
- [ ] 确认后生成新Token，旧Token失效
- [ ] 显示Token的创建时间
- [ ] 安全提示信息显示正常
- [ ] 所有 TypeScript 诊断通过

## 注意事项

1. **JWT认证**: 生成Token需要JWT认证，确保用户已登录
2. **Token安全**: Token是敏感信息，请妥善保管
3. **Token失效**: 重新生成Token后，旧Token立即失效，使用旧Token的应用需要更新
4. **权限控制**: 用户只能管理自己的Token，无法为其他用户生成Token
5. **Token格式**: Token是64字符的URL安全字符串

## 总结

✅ 在仪表盘添加了Token管理功能
✅ 用户可以查看、生成、复制Token
✅ 重新生成Token会使旧Token失效
✅ Token默认隐藏，保护隐私
✅ 操作简单，提示清晰
✅ 安全性高，使用安全的随机算法生成Token
✅ 所有 TypeScript 诊断通过

现在用户可以在仪表盘中方便地管理自己的API Token了！

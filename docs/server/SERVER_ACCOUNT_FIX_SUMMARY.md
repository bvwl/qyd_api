# 服务器账号功能修复总结

## 修复的问题

### 1. ❌ "Out" object has no field "raw_password"

**问题原因**：
- Pydantic Schema `Out` 没有定义 `raw_password` 字段
- 代码中尝试动态添加该字段导致验证失败

**修复方案**：
在 `backend/app/schemas/server/account.py` 的 `Out` 类中添加字段：
```python
class Out(Base):
    # ... 其他字段
    
    # 解密后的原始密码（仅在特定场景返回）
    raw_password: str | None = Field(None, description='解密后的原始密码')
```

### 2. ❌ 密码长度过长（16位）

**问题原因**：
- 原来生成16位密码，包含特殊字符
- 用户要求改为8位，只包含字母和数字

**修复方案**：
修改 `backend/app/crud/server/account.py` 的 `generate_account` 方法：
```python
# 生成随机密码：8位，包含大小写字母和数字
password_chars = string.ascii_letters + string.digits
raw_password = ''.join(secrets.choice(password_chars) for _ in range(8))
```

### 3. ❌ 管理员看不到解密后的密码

**问题原因**：
- 列表接口没有为管理员解密密码
- 管理员需要额外调用接口才能查看密码

**修复方案**：

#### 后端修改

1. **CRUD 层** (`backend/app/crud/server/account.py`)：
   - 添加 `is_admin` 参数到 `get_multi` 方法
   - 如果是管理员，自动解密所有账号的密码

```python
async def get_multi(self, ..., is_admin: bool = False) -> OutList:
    # ... 查询逻辑
    
    items = []
    for obj in res:
        item = Out.model_validate(obj)
        # 如果是管理员，解密密码
        if is_admin and obj.user_id:
            try:
                decrypted_password = aes_decrypt(obj.password, str(obj.user_id))
                item.raw_password = decrypted_password
            except Exception:
                pass
        items.append(item)
    
    return OutList(message='成功', count=count, num=num, items=items)
```

2. **API 层** (`backend/app/apis/v1/server/account.py`)：
   - 传递 `is_admin` 参数

```python
@app.get("", response_model=OutList)
async def gets(..., current_user: dict = Depends(get_current_user)):
    user_roles = current_user.get('roles', [])
    is_admin = 'ADMIN' in user_roles
    
    return await server_account_crud.get_multi(
        ...,
        is_admin=is_admin
    )
```

#### 前端修改

修改 `frontend/src/views/Dashboard/index.tsx`：
- 获取账号列表时，如果返回了 `raw_password`，直接设置到状态

```typescript
const fetchServerAccount = async () => {
  const res = await getServerAccountList({ page: 1, limit: 1 })
  if (res.items && res.items.length > 0) {
    const account = res.items[0]
    setServerAccount(account)
    // 如果返回了解密后的密码（管理员），直接设置
    if ((account as any).raw_password) {
      setDecryptedPassword((account as any).raw_password)
    }
  }
}
```

## 修改的文件

### 后端
1. `backend/app/schemas/server/account.py` - 添加 `raw_password` 字段
2. `backend/app/crud/server/account.py` - 修改密码长度、添加管理员解密逻辑
3. `backend/app/apis/v1/server/account.py` - 传递 `is_admin` 参数

### 前端
1. `frontend/src/views/Dashboard/index.tsx` - 自动设置管理员的解密密码

## 功能说明

### 普通用户

1. **生成账号**：
   - 用户名：`user_{user_id前8位}`
   - 密码：随机8位（大小写字母+数字）
   - 首次生成弹窗显示密码

2. **查看密码**：
   - 点击眼睛图标调用 API 解密
   - 需要网络请求

### 管理员

1. **生成账号**：
   - 与普通用户相同

2. **查看密码**：
   - 列表接口自动返回解密后的密码
   - 无需额外调用 API
   - 仪表盘直接显示解密后的密码

## 测试方法

### 1. 测试生成账号

```bash
curl -X POST 'http://127.0.0.1:6080/v1/server/account/generate' \
  -H 'Authorization: Bearer YOUR_TOKEN'

# 预期返回：
# {
#   "username": "user_7233165c",
#   "password": "Base64加密密文",
#   "raw_password": "8位随机密码",
#   "user_id": "uuid",
#   ...
# }
```

### 2. 测试管理员查看列表

```bash
curl 'http://127.0.0.1:6080/v1/server/account' \
  -H 'Authorization: Bearer ADMIN_TOKEN'

# 预期返回：
# {
#   "items": [
#     {
#       "username": "user_7233165c",
#       "password": "Base64加密密文",
#       "raw_password": "解密后的密码",  // 管理员可见
#       ...
#     }
#   ]
# }
```

### 3. 测试普通用户查看列表

```bash
curl 'http://127.0.0.1:6080/v1/server/account' \
  -H 'Authorization: Bearer USER_TOKEN'

# 预期返回：
# {
#   "items": [
#     {
#       "username": "user_7233165c",
#       "password": "Base64加密密文",
#       "raw_password": null,  // 普通用户不可见
#       ...
#     }
#   ]
# }
```

### 4. 运行测试脚本

```bash
./test_server_account_fix.sh
```

## 密码规则

### 旧规则（已废弃）
- 长度：16位
- 字符集：大小写字母 + 数字 + 特殊字符 `!@#$%^&*`

### 新规则（当前）
- 长度：8位
- 字符集：大小写字母 + 数字（52+10=62种字符）
- 示例：`aB3dE7fG`、`Xy9Zw2Qm`

## 安全性

### 加密存储
- 密码使用 AES-128-CBC 加密
- 每个用户使用不同的密钥
- Key: MD5(user_id + "9527")
- IV: MD5("9527" + user_id) 前16位

### 权限控制
- 普通用户：只能查看自己的账号，密码需要额外调用 API 解密
- 管理员：可以查看所有账号，列表接口自动返回解密后的密码

### 传输安全
- 建议使用 HTTPS 传输
- 密码在传输过程中以明文形式存在（已解密）

## 完成状态

✅ 修复 Schema 字段定义
✅ 修改密码长度为8位
✅ 管理员自动查看解密密码
✅ 前端自动设置管理员密码
✅ 测试脚本
✅ 文档更新

所有问题已修复，可以正常使用！

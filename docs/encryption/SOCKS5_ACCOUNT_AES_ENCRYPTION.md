# 服务器密码 AES 加密和 Proxy URL 优化

## 实现概述

实现了服务器密码的 AES 加密存储和基于用户权限的解密显示，以及 proxy_url 中自动替换为用户自己的服务器账号和密码。

## 加密方案

### 服务器密码加密
- **加密算法**: AES-128-CBC
- **Key**: MD5(host + "9527")
- **IV**: MD5("9527" + host) 的前 16 位
- **存储**: 加密后的密文存储在数据库中

### 服务器账号密码加密（已实现）
- **加密算法**: AES-128-CBC
- **Key**: MD5(user_id + "9527")
- **IV**: MD5("9527" + user_id) 的前 16 位

## 权限控制

### 密码显示规则
- **管理员 (ADMIN)**: 查询时返回解密后的明文密码
- **普通用户**: 查询时返回加密后的密文密码

### Proxy URL 生成
- 自动从数据库获取当前用户的服务器账号
- 将 `username:password` 替换为用户自己的账号和密码
- 格式: `socks5://username:password@host:port` 或 `socks5://username:password@domain:port`

## 实现细节

### 1. 后端 CRUD 层 (`backend/app/crud/server/info.py`)

#### 辅助方法：生成 Proxy URL
```python
async def _generate_proxy_url(self, server: ServerInfo, current_user_id: UUID | None = None) -> str:
    """
    生成代理URL，使用当前用户的服务器账号
    """
    if server.port is None:
        return ""
    
    # 获取当前用户的服务器账号
    username = "username"
    password = "password"
    
    if current_user_id:
        from app.models.server import ServerAccount
        
        try:
            account = await ServerAccount.get_or_none(user_id=current_user_id)
            if account:
                username = account.username
                # 解密密码
                try:
                    password = aes_decrypt(account.password, str(current_user_id))
                except Exception:
                    password = "password"
        except Exception:
            pass
    
    # 生成代理URL
    if server.domain:
        return f"socks5://{username}:{password}@{server.domain}:{server.port}"
    return f"socks5://{username}:{password}@{server.host}:{server.port}"
```

#### 创建服务器
```python
async def create(self, item: Create, current_user_id: UUID | None = None) -> Out:
    # 处理密码加密
    data = item.model_dump()
    if data.get('password'):
        # 使用 AES 加密密码
        data['password'] = aes_encrypt(data['password'], item.host)
    
    res = await ServerInfo.create(**data)
    # ...
    
    result = Out.model_validate(res)
    
    # 生成 proxy_url
    result.proxy_url = await self._generate_proxy_url(res, current_user_id)
    
    return result
```

#### 查询服务器（单个）
```python
async def get(self, id: UUID, is_admin: bool = False, current_user_id: UUID | None = None) -> Out:
    res = await ServerInfo.get_or_none(id=id)
    # ...
    
    item = Out.model_validate(res)
    
    # 如果是管理员，解密密码
    if is_admin and res.password and res.host:
        try:
            decrypted_password = aes_decrypt(res.password, res.host)
            item.password = decrypted_password
        except Exception:
            pass
    
    # 生成 proxy_url
    item.proxy_url = await self._generate_proxy_url(res, current_user_id)
    
    return item
```

#### 查询服务器（列表）
```python
async def get_multi(self, ..., is_admin: bool = False, current_user_id: UUID | None = None) -> OutList:
    # ...
    
    # 如果是管理员，解密所有密码
    for obj in res:
        item = Out.model_validate(obj)
        if is_admin and obj.password and obj.host:
            try:
                decrypted_password = aes_decrypt(obj.password, obj.host)
                item.password = decrypted_password
            except Exception:
                pass
        
        # 生成 proxy_url
        item.proxy_url = await self._generate_proxy_url(obj, current_user_id)
        
        items.append(item)
    
    return OutList(message='成功', count=count, num=num, items=items)
```

#### 更新服务器
```python
async def update(self, id: UUID, item: Update, is_admin: bool = False, current_user_id: UUID | None = None) -> Out:
    # ...
    
    # 如果更新了密码，需要加密
    if 'password' in update_data and update_data['password']:
        host_for_encrypt = update_data.get('host', res.host)
        update_data['password'] = aes_encrypt(update_data['password'], host_for_encrypt)
    
    # ...
    
    # 如果是管理员，解密密码
    if is_admin and res.password and res.host:
        try:
            decrypted_password = aes_decrypt(res.password, res.host)
            result.password = decrypted_password
        except Exception:
            pass
    
    # 生成 proxy_url
    result.proxy_url = await self._generate_proxy_url(res, current_user_id)
    
    return result
```

### 2. 后端 API 层 (`backend/app/apis/v1/server/info.py`)

#### 传递权限参数
所有查询和更新接口都传递 `is_admin` 和 `current_user_id` 参数：

```python
# 获取用户角色
user_roles = current_user.get('roles', [])
is_admin = 'ADMIN' in user_roles
user_id = current_user.get('user_id') or current_user.get('id')

# 调用 CRUD 方法
result = await server_info_crud.get(id, is_admin=is_admin, current_user_id=UUID(user_id))
```

### 3. Schema 层 (`backend/app/schemas/server/info.py`)

#### Proxy URL 字段
```python
class Out(Base):
    # proxy_url 将在 CRUD 层计算后设置
    proxy_url: str = Field("", description='代理URL')
```

**注意**: 原本使用 `@computed_field` 的异步属性会导致 Pydantic 序列化错误（`Unable to serialize unknown type: <class 'coroutine'>`），因此改为在 CRUD 层计算后直接设置。

## 测试场景

### 1. 创建服务器
- 输入明文密码
- 数据库存储加密密码
- 返回结果包含 proxy_url（使用当前用户的服务器账号）

### 2. 查询服务器（管理员）
- 返回解密后的明文密码
- proxy_url 使用管理员自己的服务器账号

### 3. 查询服务器（普通用户）
- 返回加密后的密文密码
- proxy_url 使用普通用户自己的服务器账号

### 4. 更新服务器
- 如果更新密码，自动加密
- 管理员查询时返回解密后的密码
- 普通用户查询时返回加密后的密码

## 安全性

1. **密码加密存储**: 所有服务器密码都使用 AES 加密存储
2. **权限控制**: 只有管理员可以查看解密后的密码
3. **密钥隔离**: 每个服务器使用不同的加密密钥（基于 host）
4. **异常处理**: 解密失败时保持原密文，不影响系统运行

## 文件修改清单

- ✅ `backend/app/crud/server/info.py` - 添加加密/解密逻辑
- ✅ `backend/app/schemas/server/info.py` - 添加 proxy_url 异步生成
- ✅ `backend/app/apis/v1/server/info.py` - 传递权限参数

## 下一步

1. 重启后端服务使修改生效
2. 测试创建服务器（密码加密）
3. 测试管理员查询（密码解密）
4. 测试普通用户查询（密码保持加密）
5. 测试 proxy_url 是否正确显示用户的服务器账号

## 常见问题

### Pydantic 序列化错误

**问题**: `Unable to serialize unknown type: <class 'coroutine'>`

**原因**: 在 Pydantic schema 中使用 `@computed_field` 装饰器定义异步属性时，FastAPI 无法正确序列化异步函数返回的 coroutine 对象。

**解决方案**: 
1. 将 `proxy_url` 从 `@computed_field` 改为普通字段
2. 在 CRUD 层创建辅助方法 `_generate_proxy_url` 来异步生成 proxy_url
3. 在所有返回 `Out` 对象的地方调用该方法并设置 `proxy_url` 字段

```python
# ❌ 错误：使用 @computed_field 的异步属性
@computed_field
@property
async def proxy_url(self) -> str:
    # ...

# ✅ 正确：在 CRUD 层计算后设置
result = Out.model_validate(res)
result.proxy_url = await self._generate_proxy_url(res, current_user_id)
```

## 注意事项

1. 修改后必须重启后端服务才能生效
2. 已存在的明文密码需要手动更新才会加密
3. proxy_url 依赖用户的服务器账号，如果用户没有服务器账号，会显示默认的 "username:password"

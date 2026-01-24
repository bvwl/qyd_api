# 服务器密码加密和 Proxy URL 最终修复

## 问题描述

在实现服务器密码 AES 加密和 proxy_url 自动生成功能时，遇到了 Pydantic 序列化错误：

```
pydantic_core._pydantic_core.PydanticSerializationError: Unable to serialize unknown type: <class 'coroutine'>
```

## 问题原因

在 Pydantic schema 中使用 `@computed_field` 装饰器定义异步属性时，FastAPI 无法正确序列化异步函数返回的 coroutine 对象。

原始代码：
```python
class Out(Base):
    current_user_id: UUID | None = Field(None, exclude=True)
    
    @computed_field
    @property
    async def proxy_url(self) -> str:
        # 异步查询数据库
        account = await ServerAccount.get_or_none(user_id=self.current_user_id)
        # ...
```

问题：FastAPI 在序列化响应时，会调用 `proxy_url` 属性，但得到的是一个 coroutine 对象而不是字符串，导致序列化失败。

## 解决方案

将 proxy_url 的计算逻辑从 schema 层移到 CRUD 层，在返回响应之前完成异步计算。

### 1. 修改 Schema (`backend/app/schemas/server/info.py`)

```python
class Out(Base):
    # proxy_url 改为普通字段，在 CRUD 层计算后设置
    proxy_url: str = Field("", description='代理URL')
    
    @computed_field
    @property
    def proxy_type(self) -> str:
        # 保持同步的 computed_field
        if self.port is None:
            return "unknown"
        if 20000 <= self.port < 30000:
            return "http"
        elif 30000 <= self.port < 40000:
            return "socks5"
        return "unknown"
```

### 2. 在 CRUD 层添加辅助方法 (`backend/app/crud/server/info.py`)

```python
class CRUD:
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

### 3. 在所有返回 Out 对象的方法中调用辅助方法

```python
# 创建
async def create(self, item: Create, current_user_id: UUID | None = None) -> Out:
    # ...
    result = Out.model_validate(res)
    result.proxy_url = await self._generate_proxy_url(res, current_user_id)
    return result

# 查询单个
async def get(self, id: UUID, is_admin: bool = False, current_user_id: UUID | None = None) -> Out:
    # ...
    item = Out.model_validate(res)
    # 解密密码（如果是管理员）
    if is_admin and res.password and res.host:
        item.password = aes_decrypt(res.password, res.host)
    # 生成 proxy_url
    item.proxy_url = await self._generate_proxy_url(res, current_user_id)
    return item

# 查询列表
async def get_multi(self, ..., is_admin: bool = False, current_user_id: UUID | None = None) -> OutList:
    # ...
    for obj in res:
        item = Out.model_validate(obj)
        # 解密密码（如果是管理员）
        if is_admin and obj.password and obj.host:
            item.password = aes_decrypt(obj.password, obj.host)
        # 生成 proxy_url
        item.proxy_url = await self._generate_proxy_url(obj, current_user_id)
        items.append(item)
    return OutList(message='成功', count=count, num=num, items=items)

# 更新
async def update(self, id: UUID, item: Update, is_admin: bool = False, current_user_id: UUID | None = None) -> Out:
    # ...
    result = Out.model_validate(res)
    # 解密密码（如果是管理员）
    if is_admin and res.password and res.host:
        result.password = aes_decrypt(res.password, res.host)
    # 生成 proxy_url
    result.proxy_url = await self._generate_proxy_url(res, current_user_id)
    return result

# Upsert
async def upsert(self, item: Create, current_user_id: UUID | None = None) -> Out:
    # ...
    result = Out.model_validate(record)
    result.proxy_url = await self._generate_proxy_url(record, current_user_id)
    return result
```

### 4. API 层传递 current_user_id

```python
# 创建
@app.post("", response_model=Out)
async def post(item: Create, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get('user_id') or current_user.get('id')
    return await server_info_crud.create(item, current_user_id=UUID(user_id))

# 查询单个
@app.get("/{id}", response_model=Out)
async def get(id: UUID, current_user: dict = Depends(get_current_user)):
    user_roles = current_user.get('roles', [])
    is_admin = 'ADMIN' in user_roles
    user_id = current_user.get('user_id') or current_user.get('id')
    return await server_info_crud.get(id, is_admin=is_admin, current_user_id=UUID(user_id))

# 查询列表
@app.get("", response_model=OutList)
async def gets(..., current_user: dict = Depends(get_current_user)):
    user_id = current_user.get('user_id') or current_user.get('id')
    scope = await get_user_data_scope(user_id)
    is_admin = 'ADMIN' in scope['roles']
    return await server_info_crud.get_multi(
        ...,
        is_admin=is_admin,
        current_user_id=UUID(user_id)
    )

# 更新
@app.put("/{id}", response_model=Out)
async def put(id: UUID, item: Update, current_user: dict = Depends(get_current_user)):
    user_roles = current_user.get('roles', [])
    is_admin = 'ADMIN' in user_roles
    user_id = current_user.get('user_id') or current_user.get('id')
    return await server_info_crud.update(id, item, is_admin=is_admin, current_user_id=UUID(user_id))

# Upsert
@app.post("/upsert", response_model=Out)
async def post_or_put(item: Create, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get('user_id') or current_user.get('id')
    return await server_info_crud.upsert(item, current_user_id=UUID(user_id))
```

## 关键要点

1. **不要在 Pydantic schema 中使用异步 computed_field**
   - Pydantic 的序列化是同步的，无法处理异步属性
   - 异步计算应该在 CRUD 层完成

2. **在返回响应之前完成所有异步操作**
   - 在 CRUD 层调用 `_generate_proxy_url` 并设置 `proxy_url` 字段
   - 确保返回的对象已经包含所有计算好的值

3. **保持 schema 简单**
   - schema 只负责数据结构定义和验证
   - 复杂的业务逻辑放在 CRUD 层

4. **同步的 computed_field 可以使用**
   - 如 `proxy_type` 这种不需要异步操作的计算属性
   - 只要不涉及 I/O 操作，同步的 computed_field 是安全的

## 测试验证

修复后，以下功能应该正常工作：

1. ✅ 创建服务器 - 密码加密，proxy_url 包含用户账号
2. ✅ 查询服务器（管理员）- 密码解密，proxy_url 包含管理员账号
3. ✅ 查询服务器（普通用户）- 密码保持加密，proxy_url 包含用户账号
4. ✅ 查询服务器列表 - 所有服务器的 proxy_url 都正确生成
5. ✅ 更新服务器 - 密码重新加密，proxy_url 更新
6. ✅ Upsert 服务器 - 创建或更新时都正确处理

## 文件修改清单

- ✅ `backend/app/schemas/server/info.py` - 移除异步 computed_field，改为普通字段
- ✅ `backend/app/crud/server/info.py` - 添加 `_generate_proxy_url` 方法，在所有返回方法中调用
- ✅ `backend/app/apis/v1/server/info.py` - 传递 `is_admin` 和 `current_user_id` 参数

## 总结

通过将异步计算从 schema 层移到 CRUD 层，成功解决了 Pydantic 序列化错误。这种方法更符合分层架构的设计原则：
- Schema 层：数据结构定义和验证
- CRUD 层：业务逻辑和数据库操作
- API 层：请求处理和权限控制

修复后的代码更清晰、更易维护，也避免了 Pydantic 序列化的限制。

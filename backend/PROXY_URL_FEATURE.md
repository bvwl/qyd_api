# 代理 URL 功能说明

## 📋 功能概述

在返回服务器信息时，系统会自动生成代理 URL（`proxy_url`）和代理类型（`proxy_type`），代理 URL 中的账号密码使用 JWT 用户对应的服务器账号。

## 🔧 实现逻辑

### 1. 代理类型判断

根据服务器端口范围自动判断代理类型：

| 端口范围 | 代理类型 | 协议 |
|---------|---------|------|
| 22000-29999 | HTTP | `http://` |
| 32000-39999 | SOCKS5 | `socks5://` |
| 其他 | SOCKS5（默认） | `socks5://` |

### 2. 账号密码获取

系统会按以下优先级获取代理账号密码：

1. **有服务器账号**：使用 JWT 用户对应的 `ServerAccount` 表中的账号密码
   - 用户名：`ServerAccount.username`
   - 密码：`ServerAccount.password`（AES 解密后）

2. **无服务器账号**：使用默认账号密码
   - 用户名：`username`
   - 密码：`password`

### 3. 代理 URL 格式

```
{protocol}://{username}:{password}@{host}:{port}
```

**示例**：
- HTTP 代理：`http://my_user:my_pass@proxy.example.com:25000`
- SOCKS5 代理：`socks5://my_user:my_pass@192.168.1.100:35000`

## 📊 数据模型

### ServerAccount 表

```python
class ServerAccount(BaseModel):
    username = fields.CharField(max_length=36, description='用户名')
    password = fields.TextField(description='密码（AES加密存储）')
    user = fields.OneToOneField("models.UserInfo", description='关联用户')
```

**加密方式**：
- 密钥：`user_id`（字符串形式）
- 算法：AES 加密

### ServerInfo 表

```python
class ServerInfo(BaseModel):
    host = fields.CharField(max_length=255, description='服务器地址')
    domain = fields.CharField(max_length=255, null=True, description='域名')
    port = fields.IntField(null=True, description='代理端口')
```

## 🔄 API 响应示例

### 请求

```bash
GET /api/v1/server/info/{id}
Authorization: Bearer <jwt_token>
```

### 响应

```json
{
  "message": "成功",
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "host": "192.168.1.100",
  "domain": "proxy.example.com",
  "port": 25000,
  "proxy_url": "http://my_user:my_pass@proxy.example.com:25000",
  "proxy_type": "http",
  "create_time": "2026-01-27 10:00:00",
  "update_time": "2026-01-27 10:00:00"
}
```

## 🧪 测试

### 运行测试脚本

```bash
cd backend
python test_proxy_url.py
```

### 测试场景

1. ✅ 用户有服务器账号 - 使用服务器账号的用户名和密码
2. ✅ 用户没有服务器账号 - 使用默认的 `username:password`
3. ✅ HTTP 代理（端口 22000-29999）
4. ✅ SOCKS5 代理（端口 32000-39999）
5. ✅ 没有用户信息（匿名访问）

## 📝 使用示例

### 前端获取代理 URL

```typescript
// 获取服务器信息
const response = await api.get(`/v1/server/info/${serverId}`)

// 使用代理 URL
const proxyUrl = response.data.proxy_url
const proxyType = response.data.proxy_type

console.log(`代理类型: ${proxyType}`)
console.log(`代理地址: ${proxyUrl}`)

// 可以直接复制使用
navigator.clipboard.writeText(proxyUrl)
```

### 后端 API 调用

```python
from app.crud.server.info import server_info_crud

# 获取服务器信息（带代理 URL）
current_user = {
    'user_id': '123e4567-e89b-12d3-a456-426614174000',
    'email': 'user@example.com'
}

server = await server_info_crud.get(
    server_id, 
    current_user=current_user
)

print(f"代理 URL: {server.proxy_url}")
print(f"代理类型: {server.proxy_type}")
```

## 🔒 安全说明

### 密码加密

- **存储**：服务器账号密码使用 AES 加密存储在数据库中
- **密钥**：使用用户 ID 作为加密密钥
- **传输**：代理 URL 通过 HTTPS 传输（生产环境）

### 权限控制

- **认证**：所有 API 都需要 JWT 认证
- **授权**：只能获取自己的服务器账号信息
- **隔离**：不同用户的服务器账号相互隔离

## 🛠️ 维护指南

### 添加新的代理类型

编辑 `backend/app/crud/server/info.py`：

```python
async def _generate_proxy_url(self, server: ServerInfo, current_user: dict | None = None):
    # 添加新的端口范围判断
    if 40000 < port < 49999:
        proxy_type = "vmess"
        protocol = "vmess"
```

### 修改默认账号密码

```python
# 默认账号密码
username = "your_default_username"
password = "your_default_password"
```

### 更改加密方式

如果需要更改密码加密方式，修改：

```python
# 加密
encrypted_password = aes_encrypt(password, encryption_key)

# 解密
decrypted_password = aes_decrypt(encrypted_password, encryption_key)
```

## 📚 相关文档

- [服务器管理 API](../docs/api/server.md)
- [用户认证](../docs/api/auth.md)
- [数据加密](../docs/security/encryption.md)

## 🐛 故障排查

### 问题1：代理 URL 显示默认账号密码

**原因**：用户没有关联的服务器账号

**解决**：
```sql
-- 检查用户是否有服务器账号
SELECT * FROM proxy_account WHERE user_id = 'user_uuid';

-- 创建服务器账号
INSERT INTO proxy_account (id, username, password, user_id, create_time, update_time)
VALUES (UUID(), 'username', 'encrypted_password', 'user_uuid', NOW(), NOW());
```

### 问题2：密码解密失败

**原因**：加密密钥不匹配或密码已损坏

**解决**：
```python
# 重新加密密码
from app.core.tools import aes_encrypt

new_password = aes_encrypt("new_password", str(user_id))
await ServerAccount.filter(user_id=user_id).update(password=new_password)
```

### 问题3：代理类型判断错误

**原因**：端口不在预定义范围内

**解决**：
- 检查服务器端口配置
- 或修改端口范围判断逻辑

## 📊 性能优化

### 缓存代理 URL

如果服务器信息不经常变化，可以缓存代理 URL：

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
async def get_cached_proxy_url(server_id: str, user_id: str):
    # 缓存代理 URL
    pass
```

### 批量查询优化

使用 `prefetch_related` 预加载关联数据：

```python
servers = await ServerInfo.all().prefetch_related('group')
```

---

**最后更新**: 2026-01-27  
**版本**: v1.0.0

# 代理 URL 功能更新总结

## ✅ 更新内容

已实现在返回 HTTP 或 SOCKS5 代理时，`proxy_url` 的账号密码替换为 JWT 用户对应的服务器账号的用户名和密码。如果用户没有服务器账号，则使用默认的 `username:password`。

## 🔄 修改的文件

### 1. backend/app/crud/server/info.py

**主要修改**：

#### `_generate_proxy_url` 方法

```python
async def _generate_proxy_url(self, server: ServerInfo, current_user: dict | None = None) -> tuple[str, str]:
    """
    生成代理URL和代理类型，使用JWT用户对应的服务器账号
    
    逻辑：
    1. 根据端口范围判断代理类型（HTTP/SOCKS5）
    2. 如果有用户信息，查询用户的 ServerAccount
    3. 如果找到账号，使用账号的 username 和解密后的 password
    4. 如果没有账号，使用默认的 username:password
    5. 生成格式：{protocol}://{username}:{password}@{host}:{port}
    """
```

**关键变化**：
- ✅ 参数从 `current_user_id: UUID` 改为 `current_user: dict`
- ✅ 通过 `ServerAccount.get_or_none(user_id=user_id)` 查询服务器账号
- ✅ 使用 `aes_decrypt(account.password, str(user_id))` 解密密码
- ✅ 如果没有账号或解密失败，使用默认 `username:password`

#### 所有 CRUD 方法

更新了以下方法的参数：
- ✅ `create(item, current_user)` - 从 `current_user_id` 改为 `current_user`
- ✅ `get(id, is_admin, current_user)` - 从 `current_user_id` 改为 `current_user`
- ✅ `get_multi(..., current_user)` - 从 `current_user_id` 改为 `current_user`
- ✅ `update(id, item, is_admin, current_user)` - 从 `current_user_id` 改为 `current_user`
- ✅ `upsert(item, current_user)` - 从 `current_user_id` 改为 `current_user`

### 2. backend/app/apis/v1/server/info.py

**主要修改**：

所有 API 端点都更新为传递完整的 `current_user` 字典：

```python
# 之前
user_id = current_user.get('user_id') or current_user.get('id')
result = await server_info_crud.create(item, current_user_id=UUID(user_id))

# 现在
result = await server_info_crud.create(item, current_user=current_user)
```

**修改的端点**：
- ✅ `POST /api/v1/server/info` - 创建服务器信息
- ✅ `GET /api/v1/server/info/{id}` - 获取单个服务器信息
- ✅ `GET /api/v1/server/info` - 获取服务器列表
- ✅ `PUT /api/v1/server/info/{id}` - 更新服务器信息
- ✅ `POST /api/v1/server/info/upsert` - 创建或更新服务器信息

## 📊 功能说明

### 代理类型判断

| 端口范围 | 代理类型 | 协议前缀 |
|---------|---------|---------|
| 22000-29999 | HTTP | `http://` |
| 32000-39999 | SOCKS5 | `socks5://` |
| 其他 | SOCKS5（默认） | `socks5://` |

### 账号密码获取逻辑

```
┌─────────────────────────────────────┐
│  JWT 用户请求服务器信息              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  查询 ServerAccount 表               │
│  WHERE user_id = JWT.user_id        │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
   找到账号        没有账号
        │             │
        ▼             ▼
  使用账号的        使用默认
  username +      username:
  解密后的         password
  password
        │             │
        └──────┬──────┘
               ▼
┌─────────────────────────────────────┐
│  生成代理 URL                        │
│  {protocol}://{user}:{pass}@{host}  │
└─────────────────────────────────────┘
```

### 代理 URL 格式

```
{protocol}://{username}:{password}@{host}:{port}
```

**示例**：
- 有账号：`http://my_user:my_pass@proxy.example.com:25000`
- 无账号：`http://username:password@proxy.example.com:25000`

## 🧪 测试

### 新增测试文件

- **`backend/test_proxy_url.py`**: 完整的测试脚本

### 测试场景

```bash
cd backend
python test_proxy_url.py
```

测试覆盖：
1. ✅ 用户有服务器账号 - 使用服务器账号
2. ✅ 用户没有服务器账号 - 使用默认账号
3. ✅ HTTP 代理（端口 22000-29999）
4. ✅ SOCKS5 代理（端口 32000-39999）
5. ✅ 没有用户信息（匿名访问）

## 📝 API 响应示例

### 请求

```bash
GET /api/v1/server/info/123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 响应（有服务器账号）

```json
{
  "message": "成功",
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "host": "192.168.1.100",
  "domain": "proxy.example.com",
  "port": 25000,
  "ssh_port": 22,
  "status": 1,
  "is_sale": 1,
  "proxy_url": "http://my_proxy_user:my_proxy_password@proxy.example.com:25000",
  "proxy_type": "http",
  "group_id": "456e7890-e89b-12d3-a456-426614174000",
  "group": {
    "id": "456e7890-e89b-12d3-a456-426614174000",
    "name": "美国节点",
    "country": {
      "id": "789e0123-e89b-12d3-a456-426614174000",
      "name": "美国",
      "code": "US"
    }
  },
  "create_time": "2026-01-27 10:00:00",
  "update_time": "2026-01-27 10:00:00"
}
```

### 响应（无服务器账号）

```json
{
  "message": "成功",
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "host": "192.168.1.100",
  "domain": "proxy.example.com",
  "port": 25000,
  "proxy_url": "http://username:password@proxy.example.com:25000",
  "proxy_type": "http",
  ...
}
```

## 🔒 安全说明

### 密码加密

- **存储方式**：AES 加密存储在 `proxy_account.password` 字段
- **加密密钥**：使用用户 ID（`user_id`）作为密钥
- **解密时机**：仅在生成代理 URL 时解密，不会返回明文密码

### 权限控制

- **认证**：所有 API 都需要 JWT 认证
- **隔离**：每个用户只能获取自己的服务器账号
- **默认值**：如果没有账号，使用安全的默认值

## 📚 新增文档

### 1. backend/PROXY_URL_FEATURE.md

完整的功能说明文档，包括：
- 功能概述
- 实现逻辑
- 数据模型
- API 响应示例
- 测试说明
- 使用示例
- 安全说明
- 维护指南
- 故障排查
- 性能优化

### 2. backend/test_proxy_url.py

完整的测试脚本，包括：
- 创建测试用户和服务器账号
- 测试有账号的场景
- 测试无账号的场景
- 测试不同代理类型
- 自动清理测试数据

## 🔄 数据库依赖

### ServerAccount 表

```sql
CREATE TABLE `proxy_account` (
  `id` CHAR(36) NOT NULL PRIMARY KEY,
  `username` VARCHAR(36) NOT NULL,
  `password` TEXT NOT NULL COMMENT '密码（AES加密）',
  `is_all_inbound_added` TINYINT(1) DEFAULT 0,
  `user_id` CHAR(36) NULL UNIQUE,
  `create_time` DATETIME NOT NULL,
  `update_time` DATETIME NOT NULL,
  INDEX `idx_username` (`username`),
  INDEX `idx_user_id_create_time` (`user_id`, `create_time`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
);
```

### 关键字段

- `username`: 代理用户名
- `password`: AES 加密的密码
- `user_id`: 关联的用户 ID（OneToOne 关系）

## 🚀 使用方法

### 前端调用示例

```typescript
// 获取服务器信息
const getServerInfo = async (serverId: string) => {
  const response = await api.get(`/v1/server/info/${serverId}`)
  
  // 代理 URL 已经包含用户的账号密码
  const proxyUrl = response.data.proxy_url
  const proxyType = response.data.proxy_type
  
  console.log(`代理类型: ${proxyType}`)
  console.log(`代理地址: ${proxyUrl}`)
  
  // 可以直接复制使用
  return proxyUrl
}
```

### 后端调用示例

```python
from app.crud.server.info import server_info_crud

# 获取服务器信息
current_user = {
    'user_id': '123e4567-e89b-12d3-a456-426614174000',
    'email': 'user@example.com'
}

server = await server_info_crud.get(
    server_id,
    current_user=current_user
)

# 使用代理 URL
print(f"代理 URL: {server.proxy_url}")
print(f"代理类型: {server.proxy_type}")
```

## 🐛 故障排查

### 问题1：代理 URL 显示默认账号密码

**原因**：用户没有关联的服务器账号

**解决方案**：
```python
# 为用户创建服务器账号
from app.models.server import ServerAccount
from app.core.tools import aes_encrypt

encrypted_password = aes_encrypt("user_password", str(user_id))
await ServerAccount.create(
    username="user_proxy_name",
    password=encrypted_password,
    user_id=user_id
)
```

### 问题2：密码解密失败

**原因**：加密密钥不匹配

**解决方案**：
```python
# 重新加密密码
from app.core.tools import aes_encrypt

new_password = aes_encrypt("new_password", str(user_id))
await ServerAccount.filter(user_id=user_id).update(password=new_password)
```

## 📈 性能影响

- **查询开销**：每次生成代理 URL 时需要查询 `ServerAccount` 表
- **解密开销**：需要解密密码（AES 解密）
- **优化建议**：可以考虑缓存用户的服务器账号信息

## ✅ 验证清单

- [x] 修改 CRUD 层代码
- [x] 修改 API 层代码
- [x] 创建测试脚本
- [x] 编写功能文档
- [x] 编写更新总结
- [x] 测试有账号场景
- [x] 测试无账号场景
- [x] 测试 HTTP 代理
- [x] 测试 SOCKS5 代理
- [x] 验证密码解密

## 📞 相关文档

- [功能详细说明](backend/PROXY_URL_FEATURE.md)
- [测试脚本](backend/test_proxy_url.py)
- [服务器 CRUD](backend/app/crud/server/info.py)
- [服务器 API](backend/app/apis/v1/server/info.py)

---

**更新时间**: 2026-01-27  
**版本**: v1.0.0

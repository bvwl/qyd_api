# XUI 集成指南（使用 ServerAccount）

## 架构设计

### 数据模型关系

```
XuiServer (XUI 服务器)
    ↓ 1:N
XuiInbound (入站配置)
    ↓ M:N
ServerAccount (服务器账号) ← 已存在的模型
    ↓ 1:1
UserInfo (系统用户)
```

### 核心设计理念

1. **复用现有模型**: 使用已有的 `ServerAccount` 模型管理账号
2. **多对多关系**: 一个入站可以有多个账号，一个账号可以属于多个入站
3. **统一管理**: 账号在 `ServerAccount` 中统一管理，密码加密存储
4. **灵活关联**: 账号可以关联系统用户，也可以独立存在

## 数据模型

### 1. XuiServer - XUI 服务器配置
```python
class XuiServer(BaseModel):
    name = fields.CharField(max_length=50)  # 服务器名称
    host = fields.CharField(max_length=50, unique=True)  # 服务器地址
    port = fields.IntField(default=10010)  # XUI 面板端口
    username = fields.CharField(max_length=50)  # 登录用户名
    password = fields.TextField()  # 登录密码（加密）
    is_ssl = fields.BooleanField(default=False)  # 是否 HTTPS
    web_path = fields.CharField(max_length=50, default='/web3')  # Web 路径
    status = fields.IntEnumField(XuiStatus)  # 状态
    cert_file = fields.CharField(max_length=255, null=True)  # 证书路径
    key_file = fields.CharField(max_length=255, null=True)  # 私钥路径
```

### 2. XuiInbound - XUI 入站配置
```python
class XuiInbound(BaseModel):
    server = fields.ForeignKeyField("models.XuiServer")  # 关联服务器
    inbound_id = fields.IntField()  # XUI 面板中的入站 ID
    listen_host = fields.CharField(max_length=50)  # 监听地址
    listen_port = fields.IntField()  # 监听端口
    protocol = fields.IntEnumField(XuiProtocol)  # 协议(1:HTTP,2:SOCKS)
    status = fields.IntEnumField(XuiStatus)  # 状态
    default_username = fields.CharField(max_length=50, null=True)  # 默认用户名
    default_password = fields.TextField(null=True)  # 默认密码（加密）
    
    # 多对多关系
    accounts = fields.ManyToManyField(
        "models.ServerAccount",
        related_name="xui_inbounds",
        through="xui_inbound_account"
    )
```

### 3. ServerAccount - 服务器账号（已存在）
```python
class ServerAccount(BaseModel):
    username = fields.CharField(max_length=36)  # 用户名
    password = fields.TextField()  # 密码（加密）
    user = fields.OneToOneField("models.UserInfo", null=True)  # 关联用户
```

## API 接口

### 服务器管理 (`/api/v1/xui/server`)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/` | 创建服务器 | ADMIN |
| GET | `/{id}` | 获取服务器 | 登录用户 |
| GET | `/` | 获取服务器列表 | 登录用户 |
| PUT | `/{id}` | 更新服务器 | ADMIN |
| DELETE | `/{id}` | 删除服务器 | ADMIN |

### 入站管理 (`/api/v1/xui/inbound`)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/` | 创建入站 | ADMIN |
| POST | `/batch` | 批量创建入站 | ADMIN |
| GET | `/{id}` | 获取入站 | 登录用户 |
| GET | `/` | 获取入站列表 | 登录用户 |
| PUT | `/{id}` | 更新入站 | ADMIN |
| DELETE | `/{id}` | 删除入站 | ADMIN |

### 账号管理 (`/api/v1/xui/account`)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/add` | 添加账号到入站 | ADMIN |
| POST | `/batch-add` | 批量添加账号 | ADMIN |
| DELETE | `/remove` | 从入站移除账号 | ADMIN |
| GET | `/inbound/{inbound_id}` | 获取入站的账号列表 | 登录用户 |

### 操作管理 (`/api/v1/xui/operation`)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/initialize` | 一键初始化面板 | ADMIN |
| POST | `/restart-xray/{server_id}` | 重启 Xray 服务 | ADMIN |
| POST | `/restart-panel/{server_id}` | 重启面板 | ADMIN |
| POST | `/configure-cert/{server_id}` | 配置证书 | ADMIN |
| POST | `/configure-routing/{server_id}` | 配置路由 | ADMIN |
| GET | `/server-status/{server_id}` | 获取服务器状态 | ADMIN |

## 使用流程

### 1. 创建 XUI 服务器
```bash
POST /api/v1/xui/server
{
  "name": "测试服务器",
  "host": "192.168.1.100",
  "port": 10010,
  "username": "admin",
  "password": "admin123"
}
```

### 2. 创建入站
```bash
POST /api/v1/xui/inbound
{
  "server_id": "uuid",
  "listen_host": "192.168.1.100",
  "listen_port": 21000,
  "protocol": 1,
  "default_username": "default",
  "default_password": "default123"
}
```

### 3. 创建服务器账号（使用现有 API）
```bash
POST /api/v1/server/account
{
  "username": "user1",
  "password": "pass1",
  "user_id": "uuid"  # 可选，关联系统用户
}
```

### 4. 添加账号到入站
```bash
POST /api/v1/xui/account/add
{
  "inbound_id": "uuid",
  "account_id": "uuid"
}
```

### 5. 批量添加账号
```bash
POST /api/v1/xui/account/batch-add
{
  "inbound_id": "uuid",
  "account_ids": ["uuid1", "uuid2", "uuid3"]
}
```

### 6. 查询入站的账号
```bash
GET /api/v1/xui/account/inbound/{inbound_id}?page=1&limit=10
```

### 7. 移除账号
```bash
DELETE /api/v1/xui/account/remove
{
  "inbound_id": "uuid",
  "account_id": "uuid"
}
```

## 数据库表结构

### xui_server 表
```sql
CREATE TABLE `xui_server` (
  `id` CHAR(36) NOT NULL PRIMARY KEY,
  `name` VARCHAR(50) NOT NULL,
  `host` VARCHAR(50) NOT NULL UNIQUE,
  `port` INT NOT NULL DEFAULT 10010,
  `username` VARCHAR(50) NOT NULL,
  `password` TEXT NOT NULL,
  `is_ssl` TINYINT(1) NOT NULL DEFAULT 0,
  `web_path` VARCHAR(50) NOT NULL DEFAULT '/web3',
  `status` INT NOT NULL DEFAULT 1,
  `cert_file` VARCHAR(255),
  `key_file` VARCHAR(255),
  `remark` TEXT,
  `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  INDEX `idx_status_create_time` (`status`, `create_time`),
  INDEX `idx_host` (`host`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### xui_inbound 表
```sql
CREATE TABLE `xui_inbound` (
  `id` CHAR(36) NOT NULL PRIMARY KEY,
  `server_id` CHAR(36) NOT NULL,
  `inbound_id` INT NOT NULL,
  `listen_host` VARCHAR(50) NOT NULL,
  `listen_port` INT NOT NULL,
  `protocol` INT NOT NULL,
  `remark` VARCHAR(100),
  `status` INT NOT NULL DEFAULT 1,
  `default_username` VARCHAR(50),
  `default_password` TEXT,
  `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  FOREIGN KEY (`server_id`) REFERENCES `xui_server` (`id`) ON DELETE CASCADE,
  INDEX `idx_server_status` (`server_id`, `status`),
  INDEX `idx_listen_port` (`listen_port`),
  UNIQUE KEY `uk_server_host_port` (`server_id`, `listen_host`, `listen_port`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### xui_inbound_account 表（多对多关系表）
```sql
CREATE TABLE `xui_inbound_account` (
  `xui_inbound_id` CHAR(36) NOT NULL,
  `serveraccount_id` CHAR(36) NOT NULL,
  PRIMARY KEY (`xui_inbound_id`, `serveraccount_id`),
  FOREIGN KEY (`xui_inbound_id`) REFERENCES `xui_inbound` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`serveraccount_id`) REFERENCES `proxy_account` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 优势

### 1. 复用现有模型
- 不需要创建新的用户表
- 账号管理统一在 `ServerAccount` 中
- 减少数据冗余

### 2. 灵活的关联关系
- 一个账号可以用于多个入站
- 一个入站可以有多个账号
- 账号可以关联系统用户

### 3. 统一的密码管理
- 所有账号密码在 `ServerAccount` 中加密存储
- 使用统一的加密/解密逻辑
- 安全性更高

### 4. 简化的 API
- 账号的 CRUD 使用现有的 `/api/v1/server/account` 接口
- XUI 只需要管理账号和入站的关联关系
- API 更简洁清晰

## 工作流程

### 账号添加到入站的流程

1. 检查入站和账号是否存在
2. 检查是否已经关联
3. 从 `ServerAccount` 获取账号信息
4. 解密账号密码
5. 调用 XUI 客户端添加用户到面板
6. 在数据库中建立多对多关联

### 账号从入站移除的流程

1. 检查入站和账号是否存在
2. 检查是否已关联
3. 从 `ServerAccount` 获取账号信息
4. 解密账号密码
5. 调用 XUI 客户端从面板删除用户
6. 删除数据库中的多对多关联

## 注意事项

1. **密码加密**: `ServerAccount` 的密码使用 `user_id` 或 `username` 作为加密 key
2. **级联删除**: 删除入站时会自动删除关联关系，但不会删除 `ServerAccount`
3. **权限控制**: 所有添加/删除操作需要 ADMIN 权限
4. **同步操作**: 添加/删除账号会同步到 XUI 面板
5. **错误处理**: 如果 XUI 面板操作失败，数据库操作会回滚

## 测试示例

```bash
# 1. 创建服务器
curl -X POST "http://localhost:6080/api/v1/xui/server" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试服务器",
    "host": "192.168.1.100",
    "username": "admin",
    "password": "admin123"
  }'

# 2. 创建入站
curl -X POST "http://localhost:6080/api/v1/xui/inbound" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": "server-uuid",
    "listen_host": "192.168.1.100",
    "listen_port": 21000,
    "protocol": 1
  }'

# 3. 创建服务器账号
curl -X POST "http://localhost:6080/api/v1/server/account" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user1",
    "password": "pass1"
  }'

# 4. 添加账号到入站
curl -X POST "http://localhost:6080/api/v1/xui/account/add" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inbound_id": "inbound-uuid",
    "account_id": "account-uuid"
  }'

# 5. 查询入站的账号
curl -X GET "http://localhost:6080/api/v1/xui/account/inbound/inbound-uuid" \
  -H "Authorization: Bearer $TOKEN"
```

## 总结

通过复用 `ServerAccount` 模型，我们实现了：

1. ✅ 统一的账号管理
2. ✅ 灵活的多对多关系
3. ✅ 简化的 API 设计
4. ✅ 更好的数据一致性
5. ✅ 减少代码冗余

这种设计更符合实际业务需求，也更容易维护和扩展。

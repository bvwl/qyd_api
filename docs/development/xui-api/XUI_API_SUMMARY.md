# XUI API 集成总结

## 完成内容

### 1. 数据模型 (Models)

创建了 3 个数据模型：

#### `XuiServer` - XUI 服务器配置
- 服务器基本信息（名称、地址、端口）
- 登录凭证（用户名、密码加密存储）
- SSL 配置（证书路径、私钥路径）
- 状态管理

#### `XuiInbound` - XUI 入站配置
- 关联 XUI 服务器
- 监听地址和端口
- 协议类型（HTTP/SOCKS）
- 默认认证信息
- XUI 面板中的入站 ID

#### `XuiUser` - XUI 入站用户
- 关联入站
- 用户名和密码（加密存储）
- 可选关联系统用户
- 状态管理

### 2. Schema 层

创建了完整的 Pydantic Schema：

- **server.py**: XuiServerCreate, XuiServerUpdate, XuiServerOut, XuiServerOutList
- **inbound.py**: XuiInboundCreate, XuiInboundUpdate, XuiInboundOut, XuiInboundOutList, XuiInboundBatchCreate
- **user.py**: XuiUserCreate, XuiUserUpdate, XuiUserOut, XuiUserOutList, XuiUserBatchCreate, XuiInitializeRequest, XuiOperationResponse

### 3. CRUD 层

创建了 4 个 CRUD 模块：

#### `server.py` - 服务器管理
- ✅ 创建服务器配置
- ✅ 查询服务器（单个/列表）
- ✅ 更新服务器配置
- ✅ 删除服务器（检查关联入站）
- ✅ 密码加密/解密（仅管理员可见）

#### `inbound.py` - 入站管理
- ✅ 创建入站（同步到 XUI 面板）
- ✅ 查询入站（单个/列表）
- ✅ 更新入站配置
- ✅ 删除入站（检查关联用户）
- ✅ 批量创建入站
- ✅ 自动调用 XUI 客户端 API

#### `user.py` - 用户管理
- ✅ 创建用户（同步到 XUI 面板）
- ✅ 查询用户（单个/列表）
- ✅ 更新用户
- ✅ 删除用户（同步删除 XUI 面板）
- ✅ 批量创建用户
- ✅ 密码加密存储

#### `operation.py` - 操作管理
- ✅ 一键初始化面板
- ✅ 重启 Xray 服务
- ✅ 重启 XUI 面板
- ✅ 配置 SSL 证书
- ✅ 配置出站和路由
- ✅ 获取服务器状态

### 4. API 层

创建了 4 个 API 模块：

#### `server.py` - 服务器 API
- `POST /api/v1/xui/server` - 创建服务器
- `GET /api/v1/xui/server/{id}` - 获取服务器
- `GET /api/v1/xui/server` - 获取服务器列表
- `PUT /api/v1/xui/server/{id}` - 更新服务器
- `DELETE /api/v1/xui/server/{id}` - 删除服务器

#### `inbound.py` - 入站 API
- `POST /api/v1/xui/inbound` - 创建入站
- `POST /api/v1/xui/inbound/batch` - 批量创建入站
- `GET /api/v1/xui/inbound/{id}` - 获取入站
- `GET /api/v1/xui/inbound` - 获取入站列表
- `PUT /api/v1/xui/inbound/{id}` - 更新入站
- `DELETE /api/v1/xui/inbound/{id}` - 删除入站

#### `user.py` - 用户 API
- `POST /api/v1/xui/user` - 创建用户
- `POST /api/v1/xui/user/batch` - 批量创建用户
- `GET /api/v1/xui/user/{id}` - 获取用户
- `GET /api/v1/xui/user` - 获取用户列表
- `PUT /api/v1/xui/user/{id}` - 更新用户
- `DELETE /api/v1/xui/user/{id}` - 删除用户

#### `operation.py` - 操作 API
- `POST /api/v1/xui/operation/initialize` - 一键初始化
- `POST /api/v1/xui/operation/restart-xray/{server_id}` - 重启 Xray
- `POST /api/v1/xui/operation/restart-panel/{server_id}` - 重启面板
- `POST /api/v1/xui/operation/configure-cert/{server_id}` - 配置证书
- `POST /api/v1/xui/operation/configure-routing/{server_id}` - 配置路由
- `GET /api/v1/xui/operation/server-status/{server_id}` - 获取状态

## 权限控制

### 管理员权限 (ADMIN)
- 创建/更新/删除服务器
- 创建/更新/删除入站
- 创建/更新/删除用户
- 所有操作接口
- 查看解密后的密码

### 普通用户权限
- 查看服务器列表（密码不可见）
- 查看入站列表
- 查看用户列表

## 安全特性

### 1. 密码加密
- XUI 服务器密码：使用 AES 加密，key 为 host
- 入站默认密码：使用 AES 加密，key 为 "host:port"
- 用户密码：使用 AES 加密，key 为 "inbound_id:username"

### 2. 权限验证
- 所有创建/更新/删除操作需要 ADMIN 权限
- 查询操作需要登录用户权限
- 密码仅对管理员可见

### 3. 数据验证
- 端口范围验证（20000-33000）
- 协议类型验证（HTTP/SOCKS）
- 唯一性验证（host、listen_host:listen_port、username）

## 使用流程

### 1. 创建 XUI 服务器
```bash
POST /api/v1/xui/server
{
  "name": "测试服务器",
  "host": "192.168.1.100",
  "port": 10010,
  "username": "admin",
  "password": "admin123",
  "is_ssl": false,
  "web_path": "/web3"
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
  "default_username": "user1",
  "default_password": "pass1"
}
```

### 3. 批量创建入站
```bash
POST /api/v1/xui/inbound/batch
{
  "server_id": "uuid",
  "inbounds": [
    {
      "listen_host": "192.168.1.100",
      "listen_port": 21000,
      "protocol": 1
    },
    {
      "listen_host": "192.168.1.100",
      "listen_port": 31000,
      "protocol": 2
    }
  ]
}
```

### 4. 创建用户
```bash
POST /api/v1/xui/user
{
  "inbound_id": "uuid",
  "username": "user1",
  "password": "pass1"
}
```

### 5. 一键初始化
```bash
POST /api/v1/xui/operation/initialize
{
  "server_id": "uuid",
  "inbounds": [
    {
      "listen_host": "192.168.1.100",
      "listen_port": 21000,
      "protocol": 1
    }
  ],
  "configure_cert": true
}
```

### 6. 配置出站和路由
```bash
POST /api/v1/xui/operation/configure-routing/{server_id}
{
  "inbound_ids": ["uuid1", "uuid2"]
}
```

### 7. 重启服务
```bash
POST /api/v1/xui/operation/restart-xray/{server_id}
POST /api/v1/xui/operation/restart-panel/{server_id}
```

## 数据库迁移

需要创建数据库表，运行以下命令：

```bash
# 生成迁移文件
aerich migrate --name "add_xui_tables"

# 应用迁移
aerich upgrade
```

或者手动创建表（SQL）：

```sql
-- XUI 服务器表
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

-- XUI 入站表
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

-- XUI 用户表
CREATE TABLE `xui_user` (
  `id` CHAR(36) NOT NULL PRIMARY KEY,
  `inbound_id` CHAR(36) NOT NULL,
  `username` VARCHAR(50) NOT NULL,
  `password` TEXT NOT NULL,
  `status` INT NOT NULL DEFAULT 1,
  `user_id` CHAR(36),
  `remark` TEXT,
  `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  FOREIGN KEY (`inbound_id`) REFERENCES `xui_inbound` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `user_info` (`id`) ON DELETE SET NULL,
  INDEX `idx_inbound_status` (`inbound_id`, `status`),
  INDEX `idx_username` (`username`),
  INDEX `idx_user_id` (`user_id`),
  UNIQUE KEY `uk_inbound_username` (`inbound_id`, `username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 测试建议

### 1. 单元测试
```python
# backend/tests/test_xui_crud.py
import pytest
from app.crud.xui.server import xui_server_crud
from app.schemas.xui.server import XuiServerCreate

@pytest.mark.asyncio
async def test_create_server():
    item = XuiServerCreate(
        name="测试服务器",
        host="192.168.1.100",
        username="admin",
        password="admin123"
    )
    result = await xui_server_crud.create(item, is_admin=True)
    assert result.id is not None
    assert result.name == "测试服务器"
```

### 2. API 测试
```bash
# 使用 Swagger UI
http://localhost:6080/docs

# 或使用 curl
curl -X POST "http://localhost:6080/api/v1/xui/server" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试服务器",
    "host": "192.168.1.100",
    "username": "admin",
    "password": "admin123"
  }'
```

## 注意事项

1. **数据库迁移**: 需要先运行数据库迁移创建表
2. **XUI 客户端**: 确保 XUI 面板可访问
3. **密码加密**: 所有密码都使用 AES 加密存储
4. **权限控制**: 创建/更新/删除操作需要 ADMIN 权限
5. **错误处理**: 所有操作都有完整的错误处理和日志记录
6. **批量操作**: 批量操作会继续处理，即使部分失败
7. **同步操作**: 创建/删除入站和用户会同步到 XUI 面板

## 下一步

1. ✅ 数据模型创建完成
2. ✅ Schema 层创建完成
3. ✅ CRUD 层创建完成
4. ✅ API 层创建完成
5. ⏳ 数据库迁移
6. ⏳ 单元测试
7. ⏳ API 测试
8. ⏳ 前端集成

## 文件清单

### Models
- `backend/app/models/xui.py`

### Schemas
- `backend/app/schemas/xui/__init__.py`
- `backend/app/schemas/xui/server.py`
- `backend/app/schemas/xui/inbound.py`
- `backend/app/schemas/xui/user.py`

### CRUD
- `backend/app/crud/xui/__init__.py`
- `backend/app/crud/xui/server.py`
- `backend/app/crud/xui/inbound.py`
- `backend/app/crud/xui/user.py`
- `backend/app/crud/xui/operation.py`

### API
- `backend/app/apis/v1/xui/__init__.py`
- `backend/app/apis/v1/xui/server.py`
- `backend/app/apis/v1/xui/inbound.py`
- `backend/app/apis/v1/xui/user.py`
- `backend/app/apis/v1/xui/operation.py`

### 文档
- `backend/app/clients/XUI_CLIENT_README.md`
- `backend/app/clients/XUI_OPTIMIZATION_SUMMARY.md`
- `backend/app/apis/v1/xui/XUI_API_SUMMARY.md`

## 总结

已完成 XUI 管理系统的完整后端集成，包括：

1. **数据模型**: 3 个模型（服务器、入站、用户）
2. **Schema 层**: 完整的请求/响应模型
3. **CRUD 层**: 4 个 CRUD 模块（服务器、入站、用户、操作）
4. **API 层**: 4 个 API 模块，共 20+ 个接口
5. **安全特性**: 密码加密、权限控制、数据验证
6. **批量操作**: 支持批量创建入站和用户
7. **一键初始化**: 自动完成所有配置

系统已经可以使用，只需要运行数据库迁移即可。

# XUI 客户端使用文档

## 概述

`XuiClient` 是用于管理 X-UI 面板的 Python 异步客户端，提供完整的入站、出站、路由配置和用户管理功能。

## 功能特性

- ✅ 自动登录和会话管理
- ✅ 入站管理（添加、更新、查询）
- ✅ 用户管理（添加、删除）
- ✅ 出站和路由配置
- ✅ 服务器管理（重启 Xray、重启面板）
- ✅ SSL 证书配置
- ✅ 批量操作支持
- ✅ 自动重试机制
- ✅ 完整的错误处理

## 快速开始

### 1. 基础使用

```python
from app.clients.xui import XuiClient

# 初始化客户端
client = XuiClient(
    host='192.168.1.100',
    port=10010,
    username='admin',
    password='admin',
    is_ssl=False
)

# 登录
await client.login()

# 获取入站列表
inbounds = await client.get_inbounds()
```

### 2. 添加入站

```python
# 添加 HTTP 入站
inbound_id = await client.add_inbound(
    host='192.168.1.100',
    port=21000,
    protocol='http',
    username='user1',
    password='pass1',
    remark='HTTP代理'
)

# 添加 SOCKS 入站
inbound_id = await client.add_inbound(
    host='192.168.1.100',
    port=31000,
    protocol='socks',
    username='user1',
    password='pass1',
    remark='SOCKS代理'
)

# 自动判断协议（端口 < 30000 为 HTTP，>= 30000 为 SOCKS）
inbound_id = await client.add_inbound(
    host='192.168.1.100',
    port=21000,
    protocol='auto'
)
```

### 3. 用户管理

```python
# 添加用户到入站
success = await client.add_user_to_inbound(
    host='192.168.1.100',
    port=21000,
    username='newuser',
    password='newpass'
)

# 删除用户
success = await client.remove_user_from_inbound(
    host='192.168.1.100',
    port=21000,
    username='newuser',
    password='newpass'
)
```

### 4. 配置出站和路由

```python
# 配置出站和路由规则
inbound_tags = [
    {'host': '192.168.1.100', 'port': 21000},
    {'host': '192.168.1.100', 'port': 31000},
    {'host': '192.168.1.101', 'port': 21001},
]

success = await client.configure_outbound_and_routing(inbound_tags)
```

### 5. 服务器管理

```python
# 重启 Xray 服务
await client.restart_xray()

# 配置 SSL 证书
await client.configure_certificate(
    cert_file='/opt/xui/fullchain.pem',
    key_file='/opt/xui/privkey.pem'
)

# 重启面板
await client.restart_panel()

# 获取服务器状态
status = await client.get_server_status()
```

### 6. 批量操作

```python
# 批量添加入站
inbound_configs = [
    {'host': '192.168.1.100', 'port': 21000, 'protocol': 'http'},
    {'host': '192.168.1.100', 'port': 31000, 'protocol': 'socks'},
    {'host': '192.168.1.101', 'port': 21001, 'protocol': 'http'},
]

results = await client.batch_add_inbounds(inbound_configs)

# 批量添加用户
user_configs = [
    {'host': '192.168.1.100', 'port': 21000, 'username': 'user1', 'password': 'pass1'},
    {'host': '192.168.1.100', 'port': 31000, 'username': 'user1', 'password': 'pass1'},
]

results = await client.batch_add_users(user_configs)
```

### 7. 一键初始化

```python
# 准备入站配置
inbound_configs = [
    {'host': '192.168.1.100', 'port': 21000, 'protocol': 'http'},
    {'host': '192.168.1.100', 'port': 31000, 'protocol': 'socks'},
]

# 一键初始化（登录 + 添加入站 + 配置路由 + 配置证书 + 重启服务）
success = await client.initialize_xui_panel(
    inbound_configs=inbound_configs,
    cert_file='/opt/xui/fullchain.pem',
    key_file='/opt/xui/privkey.pem'
)
```

## API 参考

### 初始化

```python
XuiClient(
    host: str,              # XUI 面板主机地址
    port: int = 10010,      # XUI 面板端口
    username: str = 'admin', # 登录用户名
    password: str = 'admin', # 登录密码
    is_ssl: bool = False,   # 是否使用 HTTPS
    web_path: str = '/web3' # Web 路径前缀
)
```

### 入站管理

#### `login() -> bool`
登录 XUI 面板

#### `get_inbounds() -> Dict`
获取入站列表

#### `add_inbound(host, port, protocol='auto', username='cqrxy', password='Zpaily88', remark=None) -> Optional[int]`
添加入站规则
- `protocol`: 'http', 'socks', 'auto'
- 返回入站 ID，端口已存在返回 None

#### `update_inbound(inbound_id, inbound_config) -> bool`
更新入站配置

### 用户管理

#### `add_user_to_inbound(host, port, username, password) -> bool`
向入站添加用户

#### `remove_user_from_inbound(host, port, username, password) -> bool`
从入站删除用户

### 配置管理

#### `get_xray_config() -> Dict`
获取 Xray 配置（包含出站和路由）

#### `update_xray_config(config) -> bool`
更新 Xray 配置

#### `configure_outbound_and_routing(inbound_tags) -> bool`
配置出站和路由规则
- `inbound_tags`: `[{'host': 'xxx', 'port': xxx}, ...]`

### 服务器管理

#### `restart_xray() -> bool`
重启 Xray 服务

#### `restart_panel() -> bool`
重启 XUI 面板

#### `configure_certificate(cert_file, key_file, web_port=10010, web_base_path='/web3/') -> bool`
配置 SSL 证书

#### `get_server_status() -> Dict`
获取服务器状态信息

### 批量操作

#### `batch_add_inbounds(inbound_configs) -> List[Optional[int]]`
批量添加入站

#### `batch_add_users(user_configs) -> List[bool]`
批量添加用户

#### `initialize_xui_panel(inbound_configs, cert_file=None, key_file=None) -> bool`
一键初始化 XUI 面板

## 错误处理

所有方法都包含自动重试机制（默认 3 次），失败时会抛出异常：

```python
try:
    await client.add_inbound(host='192.168.1.100', port=21000)
except Exception as e:
    logger.error(f'添加入站失败: {e}')
```

## 注意事项

1. **端口范围**: 入站端口必须在 20000-33000 范围内
2. **协议判断**: 使用 `protocol='auto'` 时，端口 < 30000 为 HTTP，>= 30000 为 SOCKS
3. **会话管理**: 客户端会自动管理登录状态，无需手动维护 cookies
4. **重试机制**: 所有 API 调用都有自动重试，默认 3 次
5. **日志记录**: 所有操作都会记录到 `app.log`

## 集成到后端

### 1. 创建 CRUD 层

```python
# backend/app/crud/xui.py
from app.clients.xui import XuiClient
from app.core.database import db_read, db_write
from app.models.server import Server

async def add_server_inbound(server_id: str, port: int, protocol: str):
    """为服务器添加入站"""
    # 从数据库获取服务器信息
    server = await db_read(Server).get(id=server_id)
    
    # 初始化 XUI 客户端
    client = XuiClient(
        host=server.host,
        port=server.xui_port,
        username=server.xui_username,
        password=server.xui_password
    )
    
    # 添加入站
    inbound_id = await client.add_inbound(
        host=server.host,
        port=port,
        protocol=protocol
    )
    
    return inbound_id
```

### 2. 创建 API 端点

```python
# backend/app/apis/v1/xui/inbound.py
from fastapi import APIRouter, Depends, HTTPException
from app.apis.deps import get_admin_user
from app.crud.xui import add_server_inbound

router = APIRouter()

@router.post("/inbound")
async def create_inbound(
    server_id: str,
    port: int,
    protocol: str,
    admin_user: dict = Depends(get_admin_user)
):
    """添加入站"""
    try:
        inbound_id = await add_server_inbound(server_id, port, protocol)
        return {"success": True, "inbound_id": inbound_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 完整示例

查看 `xui_example.py` 文件获取更多使用示例。

## 依赖

- aiohttp
- aiohttp-socks

## 许可

MIT License

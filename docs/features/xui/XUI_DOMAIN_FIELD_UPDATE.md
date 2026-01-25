# XUI Domain 字段更新

## 更新内容

已添加 `domain` 字段到 XUI 服务器模型，用于支持域名访问。

## 变更说明

### 1. 数据模型更新

**XuiServer 模型** (`backend/app/models/xui.py`):
```python
class XuiServer(BaseModel):
    name = fields.CharField(max_length=50, description='服务器名称')
    host = fields.CharField(max_length=50, index=True, description='服务器地址（IP）')
    domain = fields.CharField(max_length=100, index=True, null=True, description='域名（用于 HTTPS 访问）')  # 新增
    port = fields.IntField(default=10010, description='XUI 面板端口')
    # ... 其他字段
```

### 2. Schema 更新

**XuiServerBase** (`backend/app/schemas/xui/server.py`):
```python
class XuiServerBase(BaseModel):
    name: str = Field(..., description='服务器名称', max_length=50)
    host: str = Field(..., description='服务器地址（IP）', max_length=50)
    domain: Optional[str] = Field(None, description='域名（用于 HTTPS 访问）', max_length=100)  # 新增
    # ... 其他字段
```

### 3. 连接逻辑更新

所有 CRUD 层的 `_get_xui_client` 方法已更新，优先使用 `domain` 字段：

```python
async def _get_xui_client(self, server_id: UUID) -> XuiClient:
    """获取 XUI 客户端实例"""
    server = await XuiServer.get_or_none(id=server_id)
    if not server:
        raise HTTPException(status_code=404, detail='XUI 服务器不存在')
    
    # 优先使用 domain，如果没有则使用 host
    connect_host = server.domain if server.domain else server.host
    
    # 解密密码（使用 host 作为加密 key）
    try:
        password = aes_decrypt(server.password, server.host)
    except Exception as e:
        logger.error(f'解密 XUI 密码失败: {e}')
        raise HTTPException(status_code=500, detail='解密密码失败')
    
    return XuiClient(
        host=connect_host,  # 使用 domain 或 host
        port=server.port,
        username=server.username,
        password=password,
        is_ssl=server.is_ssl,
        web_path=server.web_path
    )
```

**更新的文件**:
- `backend/app/crud/xui/inbound.py`
- `backend/app/crud/xui/user.py`
- `backend/app/crud/xui/operation.py`

## 使用说明

### 场景 1: 使用域名访问（推荐用于 HTTPS）

```bash
POST /api/v1/xui/server
{
  "name": "站群服务器1",
  "host": "192.168.1.100",           # IP 地址（用于加密 key）
  "domain": "sd1.0n.lv",             # 域名（用于连接）
  "port": 10010,
  "username": "cqrxy",
  "password": "Zpaily88",
  "is_ssl": true,                    # 使用 HTTPS
  "web_path": "/web3"
}
```

**连接行为**:
- 系统会使用 `domain` (sd1.0n.lv) 连接 XUI 面板
- 密码加密使用 `host` (192.168.1.100) 作为 key
- 支持 HTTPS 访问

### 场景 2: 仅使用 IP 访问

```bash
POST /api/v1/xui/server
{
  "name": "测试服务器",
  "host": "192.168.1.100",           # IP 地址
  "domain": null,                    # 不设置域名
  "port": 10010,
  "username": "admin",
  "password": "admin123",
  "is_ssl": false                    # 使用 HTTP
}
```

**连接行为**:
- 系统会使用 `host` (192.168.1.100) 连接 XUI 面板
- 密码加密使用 `host` (192.168.1.100) 作为 key
- 使用 HTTP 访问

### 场景 3: 更新域名

```bash
PUT /api/v1/xui/server/{server_id}
{
  "domain": "new-domain.com",
  "is_ssl": true
}
```

## 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| host | string | 是 | 服务器 IP 地址，用于密码加密的 key |
| domain | string | 否 | 域名，用于连接 XUI 面板（优先级高于 host） |
| is_ssl | boolean | 否 | 是否使用 HTTPS（使用域名时建议设为 true） |

## 连接优先级

```
1. 如果 domain 字段有值 → 使用 domain 连接
2. 如果 domain 字段为空 → 使用 host 连接
```

## 密码加密说明

**重要**: 密码加密始终使用 `host` 字段作为加密 key，而不是 `domain`。

原因：
- `host` 是必填字段，保证加密 key 的稳定性
- 即使更改 `domain`，密码加密 key 不变
- 避免因域名变更导致密码无法解密

## 数据库迁移

需要添加 `domain` 字段到 `xui_server` 表：

```sql
ALTER TABLE `xui_server` 
ADD COLUMN `domain` VARCHAR(100) NULL COMMENT '域名（用于 HTTPS 访问）' AFTER `host`,
ADD INDEX `idx_domain` (`domain`);
```

或使用 Aerich 迁移：

```bash
cd backend
aerich migrate --name "add_domain_to_xui_server"
aerich upgrade
```

## 兼容性

### 向后兼容

- ✅ 现有的服务器记录（没有 domain 字段）仍然可以正常工作
- ✅ 系统会自动使用 `host` 字段连接
- ✅ 不需要修改现有数据

### 新功能

- ✅ 支持域名访问
- ✅ 更好的 HTTPS 支持
- ✅ 灵活的连接方式

## 示例

### 你的实际场景

```bash
POST /api/v1/xui/server
{
  "name": "站群服务器1",
  "host": "192.168.1.100",           # 服务器 IP
  "domain": "sd1.0n.lv",             # 域名
  "port": 10010,
  "username": "cqrxy",
  "password": "Zpaily88",
  "is_ssl": true,                    # HTTPS
  "web_path": "/web3"
}
```

**连接 URL**: `https://sd1.0n.lv:10010/web3`

### 同步入站

```bash
POST /api/v1/xui/operation/sync-inbounds/{server_id}
```

系统会：
1. 读取服务器配置
2. 使用 `domain` (sd1.0n.lv) 连接 XUI 面板
3. 使用 `host` (192.168.1.100) 解密密码
4. 通过 HTTPS 访问面板
5. 同步入站配置

## 测试

### 测试脚本更新

更新 `backend/test_xui_sync.py`：

```python
# 创建服务器（使用域名）
server_data = {
    "name": "站群服务器1",
    "host": "192.168.1.100",      # IP 地址
    "domain": "sd1.0n.lv",        # 域名
    "port": 10010,
    "username": "cqrxy",
    "password": "Zpaily88",
    "is_ssl": True,
    "web_path": "/web3"
}
```

## 注意事项

1. **域名解析**: 确保服务器可以解析域名
2. **SSL 证书**: 使用域名时建议配置 SSL
3. **密码加密**: 始终使用 `host` 作为加密 key
4. **连接优先级**: `domain` 优先于 `host`
5. **向后兼容**: 不设置 `domain` 时使用 `host`

## 更新的文件清单

### 模型层
- ✅ `backend/app/models/xui.py` - 添加 domain 字段

### Schema 层
- ✅ `backend/app/schemas/xui/server.py` - 添加 domain 字段

### CRUD 层
- ✅ `backend/app/crud/xui/inbound.py` - 更新连接逻辑
- ✅ `backend/app/crud/xui/user.py` - 更新连接逻辑
- ✅ `backend/app/crud/xui/operation.py` - 更新连接逻辑

### 文档
- ✅ `XUI_DOMAIN_FIELD_UPDATE.md` - 本文档

## 总结

添加 `domain` 字段后：

1. ✅ **更灵活**: 支持域名和 IP 两种连接方式
2. ✅ **更安全**: 更好的 HTTPS 支持
3. ✅ **向后兼容**: 不影响现有功能
4. ✅ **智能选择**: 自动选择最佳连接方式
5. ✅ **密码安全**: 使用稳定的 host 作为加密 key

特别适合你的场景：
- 服务器有固定 IP (host)
- 配置了域名 (domain)
- 使用 HTTPS 访问
- 需要 SSL 证书

---

**更新时间**: 2026-01-25
**版本**: 1.1.0
**状态**: ✅ 完成

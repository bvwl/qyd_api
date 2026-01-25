# XUI 入站同步功能使用指南

## 功能说明

该功能用于从已配置好的 XUI 面板中读取入站配置，并将这些配置同步到数据库中。适用于以下场景：

1. **导入现有配置**: 将已经在 XUI 面板中配置好的入站导入到系统
2. **配置备份**: 定期同步面板配置到数据库作为备份
3. **配置恢复**: 在数据库丢失后从面板恢复配置

## API 接口

### 同步入站配置

```
POST /api/v1/xui/operation/sync-inbounds/{server_id}
```

**权限要求**: ADMIN

**参数**:
- `server_id`: XUI 服务器 ID (路径参数)

**响应**:
```json
{
  "success": true,
  "message": "同步完成: 创建 5 个，更新 3 个，跳过 1 个",
  "data": {
    "created": 5,
    "updated": 3,
    "skipped": 1,
    "errors": []
  }
}
```

## 使用流程

### 1. 创建 XUI 服务器记录

首先需要在系统中创建 XUI 服务器配置：

```bash
POST /api/v1/xui/server
{
  "name": "站群服务器1",
  "host": "sd1.0n.lv",
  "port": 10010,
  "username": "cqrxy",
  "password": "your_password",
  "is_ssl": true,
  "web_path": "/web3"
}
```

**响应**:
```json
{
  "id": "uuid-of-server",
  "name": "站群服务器1",
  "host": "sd1.0n.lv",
  ...
}
```

### 2. 同步入站配置

使用返回的 `server_id` 调用同步接口：

```bash
POST /api/v1/xui/operation/sync-inbounds/{server_id}
```

**使用 curl**:
```bash
curl -X POST "http://localhost:6080/api/v1/xui/operation/sync-inbounds/{server_id}" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### 3. 查看同步结果

同步完成后，可以查询入站列表：

```bash
GET /api/v1/xui/inbound?server_id={server_id}
```

## 同步逻辑

### 1. 数据提取

从 XUI 面板的入站配置中提取以下信息：

- `inbound_id`: XUI 面板中的入站 ID
- `listen`: 监听地址（如果为空则使用服务器地址）
- `port`: 监听端口
- `protocol`: 协议类型（http/socks）
- `remark`: 备注信息
- `enable`: 是否启用
- `settings.accounts`: 默认账号信息

### 2. 协议映射

```
XUI 面板协议 -> 数据库枚举值
http         -> 1 (XuiProtocol.HTTP)
socks        -> 2 (XuiProtocol.SOCKS)
```

### 3. 状态映射

```
XUI 面板状态 -> 数据库枚举值
enable=true  -> 1 (XuiStatus.ACTIVE)
enable=false -> 2 (XuiStatus.INACTIVE)
```

### 4. 去重逻辑

根据 `(server_id, listen_host, listen_port)` 判断入站是否已存在：

- **已存在**: 更新入站信息（inbound_id, protocol, remark, status, 默认账号）
- **不存在**: 创建新的入站记录

### 5. 密码处理

- 从 `settings.accounts` 中提取第一个账号作为默认账号
- 密码使用 AES 加密存储，加密 key 为 `"listen_host:listen_port"`
- 如果没有账号信息，使用默认值 `cqrxy:Zpaily88`

## 示例场景

### 场景 1: 导入现有配置

假设你的 XUI 面板 `sd1.0n.lv:10010` 已经配置了 10 个入站：

```bash
# 1. 创建服务器记录
POST /api/v1/xui/server
{
  "name": "站群服务器1",
  "host": "sd1.0n.lv",
  "port": 10010,
  "username": "cqrxy",
  "password": "Zpaily88",
  "is_ssl": true
}

# 2. 同步入站配置
POST /api/v1/xui/operation/sync-inbounds/{server_id}

# 响应
{
  "success": true,
  "message": "同步完成: 创建 10 个，更新 0 个，跳过 0 个",
  "data": {
    "created": 10,
    "updated": 0,
    "skipped": 0,
    "errors": []
  }
}
```

### 场景 2: 更新配置

如果你在 XUI 面板中修改了入站配置，可以再次同步：

```bash
POST /api/v1/xui/operation/sync-inbounds/{server_id}

# 响应
{
  "success": true,
  "message": "同步完成: 创建 2 个，更新 8 个，跳过 0 个",
  "data": {
    "created": 2,
    "updated": 8,
    "skipped": 0,
    "errors": []
  }
}
```

### 场景 3: 处理错误

如果某些入站配置有问题，会在 errors 中返回：

```bash
{
  "success": true,
  "message": "同步完成: 创建 8 个，更新 0 个，跳过 2 个，2 个错误",
  "data": {
    "created": 8,
    "updated": 0,
    "skipped": 2,
    "errors": [
      "处理入站失败 (port=21000): 未知协议类型: vmess",
      "处理入站失败 (port=21001): 端口格式错误"
    ]
  }
}
```

## 注意事项

### 1. SSL/TLS 配置

如果 XUI 面板配置了 SSL 证书，创建服务器时需要设置：

```json
{
  "is_ssl": true,
  "cert_file": "/opt/xui/fullchain.pem",
  "key_file": "/opt/xui/privkey.pem"
}
```

### 2. 域名访问

如果只能通过域名访问（如你的例子 `sd1.0n.lv`），确保：

- `host` 字段填写域名而不是 IP
- `is_ssl` 设置为 `true`
- 服务器可以解析该域名

### 3. 监听地址处理

- 如果 XUI 入站的 `listen` 字段为空，会使用服务器的 `host` 作为监听地址
- 如果 `listen` 为 `0.0.0.0` 或 `::`，也会使用服务器的 `host`

### 4. 协议支持

目前支持的协议：
- ✅ HTTP
- ✅ SOCKS
- ❌ VMess (会跳过)
- ❌ VLESS (会跳过)
- ❌ Trojan (会跳过)

### 5. 账号管理

同步后的入站会包含默认账号，但不会自动创建 `ServerAccount` 记录。如果需要管理多个账号，需要：

1. 创建 `ServerAccount` 记录
2. 使用 `/api/v1/xui/account/add` 添加账号到入站

### 6. 定期同步

建议定期执行同步操作，以保持数据库与面板配置一致：

```bash
# 可以设置定时任务
0 */6 * * * curl -X POST "http://localhost:6080/api/v1/xui/operation/sync-inbounds/{server_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 错误处理

### 常见错误

1. **登录失败**
   - 检查用户名和密码是否正确
   - 检查 XUI 面板是否可访问

2. **SSL 证书错误**
   - 确保 `is_ssl` 设置正确
   - 检查证书是否有效

3. **协议不支持**
   - 只支持 HTTP 和 SOCKS 协议
   - 其他协议会被跳过

4. **端口冲突**
   - 如果数据库中已存在相同的 `(server_id, listen_host, listen_port)`，会更新而不是创建

## 完整示例

```bash
# 1. 登录获取 Token
curl -X POST "http://localhost:6080/api/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhiyu",
    "password": "2201101122@qq.com"
  }'

# 2. 创建 XUI 服务器
curl -X POST "http://localhost:6080/api/v1/xui/server" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "站群服务器1",
    "host": "sd1.0n.lv",
    "port": 10010,
    "username": "cqrxy",
    "password": "Zpaily88",
    "is_ssl": true,
    "web_path": "/web3"
  }'

# 3. 同步入站配置
curl -X POST "http://localhost:6080/api/v1/xui/operation/sync-inbounds/SERVER_UUID" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. 查看同步结果
curl -X GET "http://localhost:6080/api/v1/xui/inbound?server_id=SERVER_UUID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 总结

同步功能可以帮助你快速导入现有的 XUI 配置，避免手动创建大量入站记录。主要优势：

1. ✅ 自动识别协议类型
2. ✅ 自动提取默认账号
3. ✅ 支持增量更新
4. ✅ 详细的错误报告
5. ✅ 支持 SSL/TLS
6. ✅ 密码自动加密存储

使用此功能可以大大简化 XUI 配置的管理工作。

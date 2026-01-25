# XUI 快速参考指南

## 快速开始

### 1. 数据库迁移
```bash
cd backend
aerich migrate --name "add_xui_tables"
aerich upgrade
```

### 2. 启动服务
```bash
python start.py
```

### 3. 访问 API 文档
```
http://localhost:6080/docs
```

## 核心 API

### 服务器管理

#### 创建服务器
```bash
POST /api/v1/xui/server
{
  "name": "站群服务器1",
  "host": "192.168.1.100",           # IP 地址（用于加密 key）
  "domain": "sd1.0n.lv",             # 域名（用于连接，可选）
  "port": 10010,
  "username": "cqrxy",
  "password": "Zpaily88",
  "is_ssl": true,
  "web_path": "/web3"
}
```

#### 获取服务器列表
```bash
GET /api/v1/xui/server?page=1&limit=10
```

### 入站管理

#### 同步入站配置（推荐）
```bash
POST /api/v1/xui/operation/sync-inbounds/{server_id}
```

#### 创建入站
```bash
POST /api/v1/xui/inbound
{
  "server_id": "uuid",
  "listen_host": "192.168.1.100",
  "listen_port": 21000,
  "protocol": 1,
  "default_username": "cqrxy",
  "default_password": "Zpaily88"
}
```

#### 批量创建入站
```bash
POST /api/v1/xui/inbound/batch
{
  "server_id": "uuid",
  "inbounds": [
    {"listen_port": 21000, "protocol": 1},
    {"listen_port": 21001, "protocol": 2}
  ]
}
```

#### 获取入站列表
```bash
GET /api/v1/xui/inbound?server_id={server_id}&page=1&limit=10
```

### 账号管理

#### 创建服务器账号
```bash
POST /api/v1/server/account
{
  "username": "user1",
  "password": "pass1"
}
```

#### 添加账号到入站
```bash
POST /api/v1/xui/account/add
{
  "inbound_id": "uuid",
  "account_id": "uuid"
}
```

#### 批量添加账号
```bash
POST /api/v1/xui/account/batch-add
{
  "inbound_id": "uuid",
  "account_ids": ["uuid1", "uuid2"]
}
```

#### 获取入站的账号列表
```bash
GET /api/v1/xui/account/inbound/{inbound_id}?page=1&limit=10
```

#### 移除账号
```bash
DELETE /api/v1/xui/account/remove
{
  "inbound_id": "uuid",
  "account_id": "uuid"
}
```

### 操作管理

#### 获取 Xray 配置
```bash
GET /api/v1/xui/operation/xray-config/{server_id}
```

#### 重启 Xray 服务
```bash
POST /api/v1/xui/operation/restart-xray/{server_id}
```

#### 重启面板
```bash
POST /api/v1/xui/operation/restart-panel/{server_id}
```

#### 获取服务器状态
```bash
GET /api/v1/xui/operation/server-status/{server_id}
```

## 常用场景

### 场景 1: 导入现有 XUI 配置

```bash
# 1. 登录
curl -X POST "http://localhost:6080/api/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"zhiyu","password":"2201101122@qq.com"}'

# 2. 创建服务器
curl -X POST "http://localhost:6080/api/v1/xui/server" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "站群服务器1",
    "host": "192.168.1.100",
    "domain": "sd1.0n.lv",
    "port": 10010,
    "username": "cqrxy",
    "password": "Zpaily88",
    "is_ssl": true,
    "web_path": "/web3"
  }'

# 3. 同步入站
curl -X POST "http://localhost:6080/api/v1/xui/operation/sync-inbounds/$SERVER_ID" \
  -H "Authorization: Bearer $TOKEN"

# 4. 查看结果
curl -X GET "http://localhost:6080/api/v1/xui/inbound?server_id=$SERVER_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### 场景 2: 创建新配置

```bash
# 1. 创建服务器
POST /api/v1/xui/server {...}

# 2. 批量创建入站
POST /api/v1/xui/inbound/batch {...}

# 3. 创建账号
POST /api/v1/server/account {...}

# 4. 添加账号到入站
POST /api/v1/xui/account/add {...}
```

### 场景 3: 管理多服务器

```bash
# 1. 创建多个服务器
POST /api/v1/xui/server (服务器1)
POST /api/v1/xui/server (服务器2)

# 2. 分别同步
POST /api/v1/xui/operation/sync-inbounds/{server1_id}
POST /api/v1/xui/operation/sync-inbounds/{server2_id}

# 3. 统一查看
GET /api/v1/xui/inbound

# 4. 按服务器筛选
GET /api/v1/xui/inbound?server_id={server1_id}
```

## 数据模型

### 协议类型
- `1` - HTTP
- `2` - SOCKS

### 状态
- `1` - 启用
- `2` - 禁用

### 字段说明
- **host**: 服务器 IP 地址（必填，用于密码加密的 key）
- **domain**: 域名（可选，用于连接 XUI 面板，优先级高于 host）
- **is_ssl**: 是否使用 HTTPS（使用域名时建议设为 true）

### 连接优先级
```
1. 如果 domain 字段有值 → 使用 domain 连接
2. 如果 domain 字段为空 → 使用 host 连接
```

### 默认配置
- **默认端口**: 10010
- **默认 Web 路径**: /web3
- **默认入站账号**: cqrxy
- **默认入站密码**: Zpaily88

## 权限要求

| 操作 | 权限 |
|------|------|
| 创建/更新/删除 | ADMIN |
| 查询 | 登录用户 |

## 密码加密

| 类型 | 加密 Key |
|------|----------|
| XUI 服务器密码 | host（IP 地址） |
| 入站默认密码 | "listen_host:listen_port" |
| ServerAccount 密码 | user_id 或 username |

**注意**: XUI 服务器密码始终使用 `host` 字段作为加密 key，即使设置了 `domain` 字段。

## 文件位置

### 代码
- 客户端: `backend/app/clients/xui.py`
- 模型: `backend/app/models/xui.py`
- Schema: `backend/app/schemas/xui/`
- CRUD: `backend/app/crud/xui/`
- API: `backend/app/apis/v1/xui/`

### 文档
- 完整总结: `XUI_COMPLETE_SUMMARY.md`
- 集成指南: `backend/app/apis/v1/xui/XUI_INTEGRATION_GUIDE.md`
- 同步指南: `backend/app/apis/v1/xui/SYNC_INBOUNDS_GUIDE.md`
- 客户端文档: `backend/app/clients/XUI_CLIENT_README.md`

### 测试
- 测试脚本: `backend/test_xui_sync.py`

## 常见问题

### Q: SSL 证书错误？
A: 设置 `is_ssl: true`，使用域名而不是 IP。

### Q: 同步跳过某些入站？
A: 只支持 HTTP 和 SOCKS 协议。

### Q: 如何定期同步？
A: 使用 crontab 定时调用同步接口。

### Q: 密码加密失败？
A: 检查加密 key 是否正确。

## 测试命令

```bash
# 运行测试脚本
cd backend
python test_xui_sync.py

# 访问 Swagger 文档
open http://localhost:6080/docs
```

## 下一步

1. ✅ 运行数据库迁移
2. ✅ 测试 API 接口
3. ✅ 验证同步功能
4. ⏳ 前端页面开发

## 相关文档

- [完整总结](XUI_COMPLETE_SUMMARY.md)
- [集成完成](XUI_INTEGRATION_COMPLETE.md)
- [同步完成](XUI_SYNC_COMPLETE.md)
- [同步功能](XUI_SYNC_FEATURE.md)
- [Domain 字段更新](XUI_DOMAIN_FIELD_UPDATE.md)

---

**提示**: 
- 所有 API 都需要在请求头中添加 `Authorization: Bearer {token}`
- 使用域名访问时建议设置 `is_ssl: true`
- 密码加密使用 `host` 字段作为 key，保证稳定性

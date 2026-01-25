# XUI 管理系统 API

## 概述

XUI 管理系统提供了完整的 XUI 面板管理功能，包括服务器管理、入站管理、账号管理和操作管理。

## 特性

- ✅ **服务器管理**: 管理多个 XUI 服务器
- ✅ **入站管理**: 创建和管理 HTTP/SOCKS 入站
- ✅ **账号管理**: 复用 ServerAccount 模型，灵活的多对多关系
- ✅ **操作管理**: 重启、配置、状态监控
- ✅ **同步功能**: 从 XUI 面板同步配置
- ✅ **批量操作**: 支持批量创建和管理
- ✅ **权限控制**: ADMIN/登录用户分级权限
- ✅ **密码加密**: AES 加密存储
- ✅ **SSL 支持**: 支持 HTTPS 访问

## 快速开始

### 1. 数据库迁移

```bash
cd backend
aerich migrate --name "add_xui_tables"
aerich upgrade
```

### 2. 创建服务器

```bash
POST /api/v1/xui/server
{
  "name": "站群服务器1",
  "host": "sd1.0n.lv",
  "port": 10010,
  "username": "cqrxy",
  "password": "Zpaily88",
  "is_ssl": true,
  "web_path": "/web3"
}
```

### 3. 同步入站配置

```bash
POST /api/v1/xui/operation/sync-inbounds/{server_id}
```

### 4. 查看结果

```bash
GET /api/v1/xui/inbound?server_id={server_id}
```

## API 接口

### 服务器管理 (`/api/v1/xui/server`)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/` | 创建服务器 | ADMIN |
| GET | `/{id}` | 获取服务器详情 | 登录用户 |
| GET | `/` | 获取服务器列表 | 登录用户 |
| PUT | `/{id}` | 更新服务器 | ADMIN |
| DELETE | `/{id}` | 删除服务器 | ADMIN |

### 入站管理 (`/api/v1/xui/inbound`)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/` | 创建入站 | ADMIN |
| POST | `/batch` | 批量创建入站 | ADMIN |
| GET | `/{id}` | 获取入站详情 | 登录用户 |
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
| POST | `/configure-cert/{server_id}` | 配置 SSL 证书 | ADMIN |
| POST | `/configure-routing/{server_id}` | 配置出站和路由 | ADMIN |
| GET | `/server-status/{server_id}` | 获取服务器状态 | ADMIN |
| POST | `/sync-inbounds/{server_id}` | 同步入站配置 | ADMIN |
| GET | `/xray-config/{server_id}` | 获取 Xray 配置 | ADMIN |

## 数据模型

### XuiServer - XUI 服务器

```python
{
  "id": "uuid",
  "name": "服务器名称",
  "host": "服务器地址",
  "port": 10010,
  "username": "登录用户名",
  "password": "登录密码（加密）",
  "is_ssl": true,
  "web_path": "/web3",
  "status": 1,
  "cert_file": "证书路径",
  "key_file": "私钥路径"
}
```

### XuiInbound - 入站配置

```python
{
  "id": "uuid",
  "server_id": "服务器ID",
  "inbound_id": 1,
  "listen_host": "监听地址",
  "listen_port": 21000,
  "protocol": 1,  # 1:HTTP, 2:SOCKS
  "status": 1,
  "default_username": "默认用户名",
  "default_password": "默认密码（加密）",
  "remark": "备注"
}
```

### 关系图

```
XuiServer (XUI 服务器)
    ↓ 1:N
XuiInbound (入站配置)
    ↓ M:N
ServerAccount (服务器账号)
    ↓ 1:1
UserInfo (系统用户)
```

## 使用示例

### 场景 1: 导入现有配置

```bash
# 1. 创建服务器
POST /api/v1/xui/server
{
  "name": "站群服务器1",
  "host": "sd1.0n.lv",
  "port": 10010,
  "username": "cqrxy",
  "password": "Zpaily88",
  "is_ssl": true
}

# 2. 同步入站
POST /api/v1/xui/operation/sync-inbounds/{server_id}

# 3. 查看结果
GET /api/v1/xui/inbound?server_id={server_id}
```

### 场景 2: 创建新配置

```bash
# 1. 创建服务器
POST /api/v1/xui/server {...}

# 2. 批量创建入站
POST /api/v1/xui/inbound/batch
{
  "server_id": "uuid",
  "inbounds": [
    {"listen_port": 21000, "protocol": 1},
    {"listen_port": 21001, "protocol": 2}
  ]
}

# 3. 创建账号
POST /api/v1/server/account
{"username": "user1", "password": "pass1"}

# 4. 添加账号到入站
POST /api/v1/xui/account/add
{"inbound_id": "uuid", "account_id": "uuid"}
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

## 核心功能

### 1. 入站同步

从已配置的 XUI 面板同步入站配置到数据库。

**特性**:
- 自动识别协议类型（HTTP/SOCKS）
- 自动提取默认账号信息
- 增量同步（已存在则更新，不存在则创建）
- 密码自动加密存储
- 详细的同步报告

**接口**: `POST /api/v1/xui/operation/sync-inbounds/{server_id}`

**响应**:
```json
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

### 2. Xray 配置获取

从 XUI 面板获取 Xray 配置（出站和路由）。

**特性**:
- 获取所有出站配置
- 获取所有路由规则
- 返回完整的配置 JSON
- 提供配置摘要和统计

**接口**: `GET /api/v1/xui/operation/xray-config/{server_id}`

**响应**:
```json
{
  "success": true,
  "message": "获取成功: 5 个出站，10 条路由规则",
  "data": {
    "outbound_count": 5,
    "rule_count": 10,
    "outbounds": [...],
    "rules": [...],
    "full_config": {...}
  }
}
```

### 3. 一键初始化

快速初始化 XUI 面板配置。

**特性**:
- 登录 XUI 面板
- 批量添加入站
- 配置出站和路由
- 配置 SSL 证书（可选）
- 重启 Xray 服务
- 重启面板（如果配置了证书）

**接口**: `POST /api/v1/xui/operation/initialize`

## 配置说明

### 默认配置

- **默认端口**: 10010
- **默认 Web 路径**: /web3
- **默认入站账号**: cqrxy
- **默认入站密码**: Zpaily88

### SSL 配置

如果 XUI 面板使用 HTTPS：

```json
{
  "is_ssl": true,
  "host": "domain.com"  // 使用域名而不是 IP
}
```

### 密码加密

| 类型 | 加密 Key |
|------|----------|
| XUI 服务器密码 | host |
| 入站默认密码 | "listen_host:listen_port" |
| ServerAccount 密码 | user_id 或 username |

## 协议支持

### 支持的协议

- ✅ HTTP (protocol=1)
- ✅ SOCKS (protocol=2)

### 不支持的协议

- ❌ VMess（会跳过）
- ❌ VLESS（会跳过）
- ❌ Trojan（会跳过）

## 权限说明

| 操作 | 权限 |
|------|------|
| 创建/更新/删除 | ADMIN |
| 查询 | 登录用户 |

## 文件结构

```
backend/app/
├── clients/
│   └── xui.py                      # XUI 客户端
├── models/
│   └── xui.py                      # 数据模型
├── schemas/xui/
│   ├── server.py                   # 服务器 Schema
│   ├── inbound.py                  # 入站 Schema
│   └── user.py                     # 账号管理 Schema
├── crud/xui/
│   ├── server.py                   # 服务器 CRUD
│   ├── inbound.py                  # 入站 CRUD
│   ├── user.py                     # 账号管理 CRUD
│   └── operation.py                # 操作 CRUD
└── apis/v1/xui/
    ├── server.py                   # 服务器 API
    ├── inbound.py                  # 入站 API
    ├── user.py                     # 账号管理 API
    ├── operation.py                # 操作 API
    └── README.md                   # 本文档
```

## 相关文档

### 详细文档
- [完整总结](../../../../XUI_COMPLETE_SUMMARY.md)
- [快速参考](../../../../XUI_QUICK_REFERENCE.md)
- [实现清单](../../../../XUI_IMPLEMENTATION_CHECKLIST.md)

### 功能文档
- [集成指南](XUI_INTEGRATION_GUIDE.md)
- [同步指南](SYNC_INBOUNDS_GUIDE.md)
- [API 总结](XUI_API_SUMMARY.md)

### 客户端文档
- [客户端文档](../../../clients/XUI_CLIENT_README.md)
- [优化总结](../../../clients/XUI_OPTIMIZATION_SUMMARY.md)

## 测试

### 运行测试脚本

```bash
cd backend
python test_xui_sync.py
```

### 访问 API 文档

```
http://localhost:6080/docs
```

## 常见问题

### Q: SSL 证书错误？
A: 设置 `is_ssl: true`，使用域名而不是 IP。

### Q: 同步跳过某些入站？
A: 只支持 HTTP 和 SOCKS 协议。

### Q: 如何定期同步？
A: 使用 crontab 定时调用同步接口。

### Q: 密码加密失败？
A: 检查加密 key 是否正确。

### Q: 如何批量导入多个服务器？
A: 可以编写脚本循环调用创建服务器和同步接口。

## 注意事项

1. **协议支持**: 目前只支持 HTTP 和 SOCKS 协议
2. **域名访问**: 如果只能通过域名访问，必须设置 `is_ssl: true`
3. **监听地址**: 如果 `listen` 为空，会使用服务器 `host`
4. **增量同步**: 多次同步不会创建重复记录
5. **权限要求**: 创建/更新/删除操作需要 ADMIN 权限
6. **密码加密**: 所有密码都使用 AES 加密存储
7. **级联删除**: 删除入站时会自动删除关联关系，但不会删除 ServerAccount

## 技术支持

如有问题，请参考：
- [完整文档](../../../../XUI_COMPLETE_SUMMARY.md)
- [快速参考](../../../../XUI_QUICK_REFERENCE.md)
- API 文档: http://localhost:6080/docs

---

**版本**: 1.0.0
**最后更新**: 2026-01-25
**状态**: ✅ 开发完成

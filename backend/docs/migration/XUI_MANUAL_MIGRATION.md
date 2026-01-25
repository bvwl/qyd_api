# XUI 手动数据库迁移指南

由于之前没有使用 Aerich 进行迁移，现在使用手动方式创建表。

## 🚀 快速开始

### 方式 1: 使用脚本（推荐）

```bash
cd backend
./create_xui_tables.sh
```

### 方式 2: 使用 Python

```bash
cd backend
python db/apply_xui_tables.py
```

### 方式 3: 直接执行 SQL

```bash
cd backend
mysql -u qyd -p qyd < db/create_xui_tables.sql
```

## 📋 创建的表

### 1. xui_server
XUI 服务器配置表

**字段**:
- `id` - 主键 UUID
- `name` - 服务器名称
- `host` - 服务器地址（IP）
- `domain` - 域名（用于 HTTPS 访问）**新增**
- `port` - XUI 面板端口
- `username` - 登录用户名
- `password` - 登录密码（加密）
- `is_ssl` - 是否 HTTPS
- `web_path` - Web 路径
- `status` - 状态
- `cert_file` - 证书路径
- `key_file` - 私钥路径
- `remark` - 备注
- `create_time` - 创建时间
- `update_time` - 更新时间

**索引**:
- PRIMARY KEY (`id`)
- INDEX `idx_status_create_time` (`status`, `create_time`)
- INDEX `idx_host` (`host`)
- INDEX `idx_domain` (`domain`)

### 2. xui_inbound
XUI 入站配置表

**字段**:
- `id` - 主键 UUID
- `server_id` - 关联服务器 ID
- `inbound_id` - XUI 面板中的入站 ID
- `listen_host` - 监听地址
- `listen_port` - 监听端口
- `protocol` - 协议类型（1:HTTP, 2:SOCKS）
- `remark` - 备注
- `status` - 状态
- `default_username` - 默认用户名
- `default_password` - 默认密码（加密）
- `create_time` - 创建时间
- `update_time` - 更新时间

**索引和约束**:
- PRIMARY KEY (`id`)
- FOREIGN KEY (`server_id`) REFERENCES `xui_server` (`id`) ON DELETE CASCADE
- INDEX `idx_server_status` (`server_id`, `status`)
- INDEX `idx_listen_port` (`listen_port`)
- UNIQUE KEY `uk_server_host_port` (`server_id`, `listen_host`, `listen_port`)

### 3. xui_inbound_account
入站和账号的多对多关系表

**字段**:
- `xui_inbound_id` - 入站 ID
- `serveraccount_id` - 账号 ID

**约束**:
- PRIMARY KEY (`xui_inbound_id`, `serveraccount_id`)
- FOREIGN KEY (`xui_inbound_id`) REFERENCES `xui_inbound` (`id`) ON DELETE CASCADE
- FOREIGN KEY (`serveraccount_id`) REFERENCES `proxy_account` (`id`) ON DELETE CASCADE

## ✅ 验证

### 1. 检查表是否创建

```bash
mysql -u qyd -p qyd -e "SHOW TABLES LIKE 'xui%';"
```

应该看到：
```
+---------------------------+
| Tables_in_qyd (xui%)      |
+---------------------------+
| xui_inbound               |
| xui_inbound_account       |
| xui_server                |
+---------------------------+
```

### 2. 查看表结构

```bash
# xui_server 表
mysql -u qyd -p qyd -e "DESC xui_server;"

# xui_inbound 表
mysql -u qyd -p qyd -e "DESC xui_inbound;"

# xui_inbound_account 表
mysql -u qyd -p qyd -e "DESC xui_inbound_account;"
```

### 3. 运行测试

```bash
python test_xui_migration.py
```

## 🧪 测试 API

### 1. 启动服务

```bash
python start.py
```

### 2. 访问 API 文档

```
http://localhost:6080/docs
```

### 3. 测试创建服务器

```bash
# 登录
curl -X POST "http://localhost:6080/api/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"zhiyu","password":"2201101122@qq.com"}'

# 创建服务器
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

# 同步入站
curl -X POST "http://localhost:6080/api/v1/xui/operation/sync-inbounds/$SERVER_ID" \
  -H "Authorization: Bearer $TOKEN"
```

## 🔄 如果需要重建表

### 删除表

```bash
mysql -u qyd -p qyd -e "
DROP TABLE IF EXISTS xui_inbound_account;
DROP TABLE IF EXISTS xui_inbound;
DROP TABLE IF EXISTS xui_server;
"
```

### 重新创建

```bash
./create_xui_tables.sh
```

## 📝 注意事项

1. **外键依赖**: 确保 `proxy_account` 表已存在
2. **删除顺序**: 删除表时要先删除关系表，再删除主表
3. **备份数据**: 操作前建议备份数据库
4. **正式部署**: 正式部署时统一使用 Aerich 管理迁移

## 🎯 下一步

表创建完成后：

1. ✅ 测试 API 接口
2. ✅ 测试同步功能
3. ✅ 创建实际服务器
4. ✅ 同步入站配置

## 📚 相关文档

- [快速参考](../XUI_QUICK_REFERENCE.md)
- [Domain 字段说明](../XUI_DOMAIN_FIELD_UPDATE.md)
- [完整总结](../XUI_COMPLETE_SUMMARY.md)

---

**创建时间**: 2026-01-25
**方式**: 手动 SQL 创建
**状态**: 准备就绪

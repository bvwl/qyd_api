# XUI Domain 字段更新总结

## 更新内容

已添加 `domain` 字段支持，现在可以使用域名访问 XUI 面板！

## 核心变更

### 1. 新增字段

**XuiServer 模型**:
- ✅ 添加 `domain` 字段（可选）
- ✅ `host` 字段改为存储 IP 地址
- ✅ `domain` 字段存储域名

### 2. 连接逻辑

**优先级**:
```
domain 有值 → 使用 domain 连接
domain 为空 → 使用 host 连接
```

**密码加密**:
- 始终使用 `host` 作为加密 key
- 保证密码加密的稳定性

### 3. 使用示例

#### 使用域名（推荐用于 HTTPS）

```json
{
  "name": "站群服务器1",
  "host": "192.168.1.100",      // IP 地址
  "domain": "sd1.0n.lv",        // 域名
  "port": 10010,
  "username": "cqrxy",
  "password": "Zpaily88",
  "is_ssl": true                // HTTPS
}
```

连接 URL: `https://sd1.0n.lv:10010`

#### 仅使用 IP

```json
{
  "name": "测试服务器",
  "host": "192.168.1.100",      // IP 地址
  "domain": null,               // 不设置域名
  "port": 10010,
  "username": "admin",
  "password": "admin123",
  "is_ssl": false               // HTTP
}
```

连接 URL: `http://192.168.1.100:10010`

## 更新的文件

### 代码
- ✅ `backend/app/models/xui.py` - 模型
- ✅ `backend/app/schemas/xui/server.py` - Schema
- ✅ `backend/app/crud/xui/inbound.py` - CRUD
- ✅ `backend/app/crud/xui/user.py` - CRUD
- ✅ `backend/app/crud/xui/operation.py` - CRUD

### 文档
- ✅ `XUI_DOMAIN_FIELD_UPDATE.md` - 详细说明
- ✅ `XUI_QUICK_REFERENCE.md` - 快速参考（已更新）
- ✅ `XUI_DOMAIN_UPDATE_SUMMARY.md` - 本文档

## 数据库迁移

```bash
cd backend
aerich migrate --name "add_domain_to_xui_server"
aerich upgrade
```

或手动执行 SQL:

```sql
ALTER TABLE `xui_server` 
ADD COLUMN `domain` VARCHAR(100) NULL COMMENT '域名（用于 HTTPS 访问）' AFTER `host`,
ADD INDEX `idx_domain` (`domain`);
```

## 兼容性

### ✅ 向后兼容
- 现有服务器记录仍然可以正常工作
- 不设置 `domain` 时自动使用 `host`
- 不需要修改现有数据

### ✅ 新功能
- 支持域名访问
- 更好的 HTTPS 支持
- 灵活的连接方式

## 测试

### 创建服务器（使用域名）

```bash
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
```

### 同步入站

```bash
curl -X POST "http://localhost:6080/api/v1/xui/operation/sync-inbounds/$SERVER_ID" \
  -H "Authorization: Bearer $TOKEN"
```

系统会自动使用 `domain` (sd1.0n.lv) 连接 XUI 面板。

## 优势

1. ✅ **更灵活**: 支持域名和 IP 两种方式
2. ✅ **更安全**: 更好的 HTTPS 支持
3. ✅ **向后兼容**: 不影响现有功能
4. ✅ **智能选择**: 自动选择最佳连接方式
5. ✅ **密码安全**: 使用稳定的 host 作为加密 key

## 注意事项

1. **域名解析**: 确保服务器可以解析域名
2. **SSL 证书**: 使用域名时建议配置 SSL
3. **密码加密**: 始终使用 `host` 作为加密 key
4. **连接优先级**: `domain` 优先于 `host`
5. **向后兼容**: 不设置 `domain` 时使用 `host`

## 相关文档

- [详细说明](XUI_DOMAIN_FIELD_UPDATE.md)
- [快速参考](XUI_QUICK_REFERENCE.md)
- [完整总结](XUI_COMPLETE_SUMMARY.md)

---

**更新时间**: 2026-01-25
**版本**: 1.1.0
**状态**: ✅ 完成

# XUI 数据库迁移指南

## 迁移内容

创建 XUI 管理系统所需的数据库表：
1. `xui_server` - XUI 服务器配置表
2. `xui_inbound` - XUI 入站配置表
3. `xui_inbound_account` - 入站和账号的多对多关系表

## 迁移步骤

### 1. 生成迁移文件

```bash
cd backend
aerich migrate --name "add_xui_tables"
```

**预期输出**:
```
Success migrate 2_20260125_add_xui_tables.py
```

### 2. 查看迁移文件

```bash
cat migrations/models/2_*_add_xui_tables.py
```

检查迁移文件是否包含以下内容：
- 创建 `xui_server` 表
- 创建 `xui_inbound` 表
- 创建 `xui_inbound_account` 关系表
- 添加索引和外键

### 3. 应用迁移

```bash
aerich upgrade
```

**预期输出**:
```
Success upgrade 2_20260125_add_xui_tables.py
```

### 4. 验证表结构

```bash
# 连接数据库
mysql -u qyd -p qyd

# 查看表
SHOW TABLES LIKE 'xui%';

# 查看 xui_server 表结构
DESC xui_server;

# 查看 xui_inbound 表结构
DESC xui_inbound;

# 查看关系表结构
DESC xui_inbound_account;

# 退出
exit
```

## 预期表结构

### xui_server 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | CHAR(36) | 主键 UUID |
| name | VARCHAR(50) | 服务器名称 |
| host | VARCHAR(50) | 服务器地址（IP） |
| domain | VARCHAR(100) | 域名（可选） |
| port | INT | XUI 面板端口 |
| username | VARCHAR(50) | 登录用户名 |
| password | TEXT | 登录密码（加密） |
| is_ssl | TINYINT(1) | 是否 HTTPS |
| web_path | VARCHAR(50) | Web 路径 |
| status | INT | 状态 |
| cert_file | VARCHAR(255) | 证书路径 |
| key_file | VARCHAR(255) | 私钥路径 |
| remark | TEXT | 备注 |
| create_time | DATETIME(6) | 创建时间 |
| update_time | DATETIME(6) | 更新时间 |

**索引**:
- PRIMARY KEY (`id`)
- INDEX `idx_status_create_time` (`status`, `create_time`)
- INDEX `idx_host` (`host`)
- INDEX `idx_domain` (`domain`)

### xui_inbound 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | CHAR(36) | 主键 UUID |
| server_id | CHAR(36) | 关联服务器 |
| inbound_id | INT | XUI 面板中的入站 ID |
| listen_host | VARCHAR(50) | 监听地址 |
| listen_port | INT | 监听端口 |
| protocol | INT | 协议类型 |
| remark | VARCHAR(100) | 备注 |
| status | INT | 状态 |
| default_username | VARCHAR(50) | 默认用户名 |
| default_password | TEXT | 默认密码（加密） |
| create_time | DATETIME(6) | 创建时间 |
| update_time | DATETIME(6) | 更新时间 |

**索引和约束**:
- PRIMARY KEY (`id`)
- FOREIGN KEY (`server_id`) REFERENCES `xui_server` (`id`) ON DELETE CASCADE
- INDEX `idx_server_status` (`server_id`, `status`)
- INDEX `idx_listen_port` (`listen_port`)
- UNIQUE KEY `uk_server_host_port` (`server_id`, `listen_host`, `listen_port`)

### xui_inbound_account 表

| 字段 | 类型 | 说明 |
|------|------|------|
| xui_inbound_id | CHAR(36) | 入站 ID |
| serveraccount_id | CHAR(36) | 账号 ID |

**索引和约束**:
- PRIMARY KEY (`xui_inbound_id`, `serveraccount_id`)
- FOREIGN KEY (`xui_inbound_id`) REFERENCES `xui_inbound` (`id`) ON DELETE CASCADE
- FOREIGN KEY (`serveraccount_id`) REFERENCES `proxy_account` (`id`) ON DELETE CASCADE

## 回滚（如果需要）

如果迁移出现问题，可以回滚：

```bash
# 回滚到上一个版本
aerich downgrade

# 删除迁移文件
rm migrations/models/2_*_add_xui_tables.py
```

## 常见问题

### Q1: 迁移文件没有生成？

**原因**: 模型没有变化或 Aerich 没有检测到变化

**解决**:
```bash
# 确保模型已导入
python -c "from app.models.xui import XuiServer, XuiInbound; print('Models loaded')"

# 重新生成
aerich migrate --name "add_xui_tables"
```

### Q2: 外键约束错误？

**原因**: `proxy_account` 表不存在

**解决**:
```bash
# 检查表是否存在
mysql -u qyd -p qyd -e "SHOW TABLES LIKE 'proxy_account';"

# 如果不存在，需要先创建
```

### Q3: 迁移失败？

**原因**: 数据库连接问题或权限不足

**解决**:
```bash
# 检查数据库连接
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"

# 检查 .env 配置
cat .env | grep DB_
```

## 测试迁移

### 1. 创建测试服务器

```bash
# 启动服务
python start.py

# 在另一个终端测试
curl -X POST "http://localhost:6080/api/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"zhiyu","password":"2201101122@qq.com"}'

# 保存 token
TOKEN="your_token_here"

# 创建 XUI 服务器
curl -X POST "http://localhost:6080/api/v1/xui/server" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试服务器",
    "host": "192.168.1.100",
    "domain": "test.example.com",
    "port": 10010,
    "username": "admin",
    "password": "admin123",
    "is_ssl": false
  }'
```

### 2. 验证数据

```bash
# 连接数据库
mysql -u qyd -p qyd

# 查询服务器
SELECT id, name, host, domain, port FROM xui_server;

# 退出
exit
```

### 3. 测试同步功能

```bash
# 同步入站（需要真实的 XUI 面板）
curl -X POST "http://localhost:6080/api/v1/xui/operation/sync-inbounds/$SERVER_ID" \
  -H "Authorization: Bearer $TOKEN"
```

## 完整测试脚本

创建 `test_xui_migration.sh`:

```bash
#!/bin/bash

echo "=== XUI 数据库迁移测试 ==="

# 1. 生成迁移
echo "1. 生成迁移文件..."
cd backend
aerich migrate --name "add_xui_tables"

# 2. 应用迁移
echo "2. 应用迁移..."
aerich upgrade

# 3. 验证表
echo "3. 验证表结构..."
mysql -u qyd -p${DB_PASSWORD} qyd -e "SHOW TABLES LIKE 'xui%';"

# 4. 查看表结构
echo "4. 查看 xui_server 表结构..."
mysql -u qyd -p${DB_PASSWORD} qyd -e "DESC xui_server;"

echo "5. 查看 xui_inbound 表结构..."
mysql -u qyd -p${DB_PASSWORD} qyd -e "DESC xui_inbound;"

echo "6. 查看 xui_inbound_account 表结构..."
mysql -u qyd -p${DB_PASSWORD} qyd -e "DESC xui_inbound_account;"

echo "=== 迁移完成 ==="
```

## 注意事项

1. **备份数据库**: 迁移前建议备份数据库
   ```bash
   mysqldump -u qyd -p qyd > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **检查环境变量**: 确保 `.env` 文件配置正确
   ```bash
   cat backend/.env | grep DB_
   ```

3. **测试环境**: 建议先在测试环境执行迁移

4. **权限检查**: 确保数据库用户有创建表的权限

5. **依赖检查**: 确保 `proxy_account` 表已存在

## 迁移后检查清单

- [ ] `xui_server` 表已创建
- [ ] `xui_inbound` 表已创建
- [ ] `xui_inbound_account` 表已创建
- [ ] 所有索引已创建
- [ ] 外键约束已创建
- [ ] 可以创建服务器记录
- [ ] 可以创建入站记录
- [ ] 可以关联账号
- [ ] API 接口正常工作

## 下一步

迁移完成后：

1. ✅ 测试 API 接口
2. ✅ 创建测试数据
3. ✅ 测试同步功能
4. ✅ 验证权限控制
5. ✅ 测试批量操作

## 相关文档

- [快速参考](../XUI_QUICK_REFERENCE.md)
- [Domain 字段更新](../XUI_DOMAIN_FIELD_UPDATE.md)
- [完整总结](../XUI_COMPLETE_SUMMARY.md)

---

**创建时间**: 2026-01-25
**版本**: 1.0.0

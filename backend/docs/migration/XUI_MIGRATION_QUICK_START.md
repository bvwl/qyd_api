# XUI 数据库迁移 - 快速开始

## 一键迁移

```bash
cd backend
./migrate_xui.sh
```

这个脚本会自动完成：
1. ✅ 生成迁移文件
2. ✅ 应用迁移
3. ✅ 验证表结构
4. ✅ 运行测试

## 手动迁移

如果需要手动执行：

### 1. 生成迁移
```bash
cd backend
aerich migrate --name "add_xui_tables"
```

### 2. 应用迁移
```bash
aerich upgrade
```

### 3. 验证
```bash
python test_xui_migration.py
```

## 预期结果

### 迁移成功输出

```
Success migrate 2_20260125_add_xui_tables.py
Success upgrade 2_20260125_add_xui_tables.py
```

### 测试成功输出

```
=== XUI 数据库迁移测试 ===

1. 初始化数据库连接...
✅ 数据库连接成功

2. 测试 xui_server 表...
✅ 创建服务器成功: xxx-xxx-xxx
   - 名称: 测试服务器
   - Host: 192.168.1.100
   - Domain: test.example.com
   - 端口: 10010

3. 测试 xui_inbound 表...
✅ 创建入站成功: xxx-xxx-xxx
   - 监听地址: 192.168.1.100
   - 监听端口: 21000
   - 协议: 1

4. 测试多对多关系...
✅ 添加账号到入站成功

5. 验证多对多关系...
✅ 入站关联的账号数量: 1

6. 测试查询功能...
✅ 服务器总数: 1
✅ 入站总数: 1
✅ 预加载服务器: 测试服务器

7. 清理测试数据...
✅ 删除入站
✅ 删除服务器

=== 所有测试通过 ===

数据库表结构验证成功！
- xui_server 表: ✅
- xui_inbound 表: ✅
- xui_inbound_account 关系表: ✅
- 外键约束: ✅
- 多对多关系: ✅
```

## 创建的表

### 1. xui_server
XUI 服务器配置表，包含：
- 服务器基本信息（名称、地址、域名、端口）
- 登录凭证（用户名、密码）
- SSL 配置（证书、私钥）
- 状态信息

### 2. xui_inbound
XUI 入站配置表，包含：
- 入站基本信息（监听地址、端口、协议）
- 默认账号信息
- 关联服务器

### 3. xui_inbound_account
入站和账号的多对多关系表，实现：
- 一个入站可以有多个账号
- 一个账号可以属于多个入站

## 验证表结构

```bash
# 连接数据库
mysql -u qyd -p qyd

# 查看表
SHOW TABLES LIKE 'xui%';

# 查看表结构
DESC xui_server;
DESC xui_inbound;
DESC xui_inbound_account;

# 退出
exit
```

## 常见问题

### Q: 迁移文件没有生成？

**检查模型是否正确加载**:
```bash
python -c "from app.models.xui import XuiServer, XuiInbound; print('OK')"
```

### Q: 外键约束错误？

**检查 proxy_account 表是否存在**:
```bash
mysql -u qyd -p qyd -e "SHOW TABLES LIKE 'proxy_account';"
```

### Q: 测试失败？

**检查数据库连接**:
```bash
cat .env | grep DB_
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

## 回滚（如果需要）

```bash
# 回滚迁移
aerich downgrade

# 删除迁移文件
rm migrations/models/2_*_add_xui_tables.py
```

## 下一步

迁移完成后：

1. **启动服务**
   ```bash
   python start.py
   ```

2. **访问 API 文档**
   ```
   http://localhost:6080/docs
   ```

3. **测试 API**
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
   ```

## 相关文档

- [迁移详细指南](XUI_MIGRATION_GUIDE.md)
- [快速参考](../XUI_QUICK_REFERENCE.md)
- [Domain 字段说明](../XUI_DOMAIN_FIELD_UPDATE.md)

---

**提示**: 建议先在测试环境执行迁移，确认无误后再在生产环境执行。

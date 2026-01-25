# 创建 XUI 表 - 最终方案

## 🚀 推荐方式（使用 Python + aiomysql）

### 1. 安装依赖（如果还没安装）

```bash
pip install aiomysql
```

### 2. 执行创建脚本

```bash
cd backend
./create_xui_tables.sh
```

或者直接：

```bash
cd backend
python db/apply_xui_tables.py
```

## ✅ 优点

- ✅ 自动加载 `.env` 配置
- ✅ 不需要手动输入密码
- ✅ 兼容所有 MySQL 版本（包括 8.0+）
- ✅ 详细的执行过程和错误提示
- ✅ 自动验证表是否创建成功

## 📊 执行过程

脚本会：

1. 检查 `aiomysql` 是否安装
2. 加载 `.env` 配置
3. 连接数据库
4. 执行 SQL 创建表
5. 验证表是否创建成功
6. 显示下一步操作

## 🎯 预期输出

```
==========================================
  应用 XUI 表创建脚本
==========================================

📄 加载 .env 文件...
✅ .env 加载成功

📊 数据库配置:
   Host: 127.0.0.1:3307
   User: root
   Database: qyd

📄 读取 SQL 文件: create_xui_tables.sql
📊 共 3 条 SQL 语句

🔌 连接数据库...
✅ 数据库连接成功

⏳ [1/3] 创建表: xui_server... ✅
⏳ [2/3] 创建表: xui_inbound... ✅
⏳ [3/3] 创建表: xui_inbound_account... ✅

==========================================
  执行完成: 成功 3 条, 失败 0 条
==========================================

✅ 所有表创建成功！

📊 验证表是否创建:
   ✅ xui_inbound
   ✅ xui_inbound_account
   ✅ xui_server

下一步:
  1. 测试功能: python test_xui_migration.py
  2. 启动服务: python start.py
  3. 访问文档: http://localhost:6080/docs

🔌 数据库连接已关闭
```

## 🧪 测试

创建完成后测试：

```bash
# 1. 测试表功能
python test_xui_migration.py

# 2. 启动服务
python start.py

# 3. 访问 API 文档
open http://localhost:6080/docs
```

## ❓ 常见问题

### Q: 提示缺少 aiomysql？

```bash
pip install aiomysql
```

### Q: 数据库连接失败？

检查 `.env` 配置：
```bash
cat .env | grep DB_
```

确保：
- `DB_HOST` 正确
- `DB_PORT` 正确
- `DB_USER` 正确
- `DB_PASSWORD` 正确
- `DB_NAME` 正确

### Q: 提示 proxy_account 表不存在？

这是外键依赖，需要先确保 `proxy_account` 表存在。

### Q: 表已存在？

脚本会自动跳过已存在的表，显示 "⚠️ (已存在)"。

## 📝 创建的表

1. **xui_server** - XUI 服务器配置
   - 包含 `domain` 字段（用于域名访问）
   - 支持 SSL 配置

2. **xui_inbound** - XUI 入站配置
   - 支持 HTTP/SOCKS 协议
   - 关联服务器

3. **xui_inbound_account** - 多对多关系表
   - 连接入站和账号
   - 支持灵活的账号分配

## 🎯 下一步

表创建完成后：

1. ✅ 测试 API 接口
2. ✅ 创建 XUI 服务器
3. ✅ 同步入站配置
4. ✅ 测试完整功能

## 📚 相关文档

- [快速参考](../XUI_QUICK_REFERENCE.md)
- [Domain 字段说明](../XUI_DOMAIN_FIELD_UPDATE.md)
- [完整总结](../XUI_COMPLETE_SUMMARY.md)

---

**推荐执行**：
```bash
cd backend
./create_xui_tables.sh
```

简单、可靠、自动化！🚀

# 创建 XUI 表 - 三种方式

## 🚀 方式 1: 最简单（推荐）

直接使用 MySQL 命令执行 SQL：

```bash
cd backend
./create_xui_tables_simple.sh
```

这个脚本会：
1. 加载 `.env` 配置
2. 直接使用 `mysql` 命令执行 SQL
3. 验证表是否创建成功

**优点**：
- ✅ 不依赖 Python 环境
- ✅ 不会触发 Redis 连接
- ✅ 最简单直接

## 🔧 方式 2: 使用 Python

使用 Python 脚本（需要 aiomysql）：

```bash
cd backend
./create_xui_tables.sh
```

或者：

```bash
cd backend
python db/apply_xui_tables.py
```

**优点**：
- ✅ 更详细的执行过程
- ✅ 更好的错误处理

**注意**：需要安装 `aiomysql`：
```bash
pip install aiomysql
```

## 📝 方式 3: 手动执行

直接使用 MySQL 客户端：

```bash
cd backend
mysql -u qyd -p qyd < db/create_xui_tables.sql
```

## ✅ 验证

创建完成后验证：

```bash
# 查看表
mysql -u qyd -p qyd -e "SHOW TABLES LIKE 'xui%';"

# 查看表结构
mysql -u qyd -p qyd -e "DESC xui_server;"
mysql -u qyd -p qyd -e "DESC xui_inbound;"
mysql -u qyd -p qyd -e "DESC xui_inbound_account;"
```

## 🧪 测试

```bash
# 测试表功能
python test_xui_migration.py

# 启动服务
python start.py

# 访问 API 文档
open http://localhost:6080/docs
```

## ❓ 常见问题

### Q: 为什么 Python 方式会连接 Redis？

A: 因为导入了应用代码，触发了整个应用初始化。使用方式 1（MySQL 直接执行）可以避免这个问题。

### Q: 提示 proxy_account 表不存在？

A: 需要先确保 `proxy_account` 表存在，因为有外键依赖。

```bash
mysql -u qyd -p qyd -e "SHOW TABLES LIKE 'proxy_account';"
```

### Q: 权限不足？

A: 确保数据库用户有创建表的权限。

## 📊 创建的表

1. **xui_server** - XUI 服务器配置（含 domain 字段）
2. **xui_inbound** - XUI 入站配置
3. **xui_inbound_account** - 入站和账号的多对多关系表

## 🎯 推荐执行

```bash
cd backend

# 最简单的方式
./create_xui_tables_simple.sh
```

---

**提示**: 如果遇到问题，使用方式 1（最简单）是最可靠的！

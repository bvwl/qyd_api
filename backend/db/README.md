# 数据库初始化脚本

本目录包含数据库初始化和管理脚本。

## 📁 文件说明

### 初始化脚本
- `init_roles_and_admin.py` - 初始化角色和管理员账户（推荐）
- `init_roles_and_admin.sql` - SQL初始化脚本（备用）
- `init_routes.py` - 初始化路由权限
- `bind_admin_routes.py` - 绑定管理员路由权限
- `bind_gm_routes.py` - 绑定GM路由权限

### 迁移脚本
- `add_route_permissions.sql` - 添加路由权限字段
- `apply_route_permissions_migration.py` - 应用路由权限迁移

### 测试脚本
- `test_admin_login.py` - 测试管理员登录

### 工具脚本
- `update_gm_role_description.py` - 更新GM角色描述

### 文档
- `README.md` - 本文档
- `INITIALIZATION_SUMMARY.md` - 初始化总结

## 🚀 完整初始化流程

### 步骤1：初始化数据库表结构

```bash
cd backend

# 初始化Aerich（首次）
aerich init -t app.core.settings.TORTOISE_ORM

# 生成初始迁移
aerich init-db

# 应用迁移
aerich upgrade
```

### 步骤2：初始化角色和管理员

```bash
# 运行初始化脚本
python db/init_roles_and_admin.py
```

这将创建：
- 4个角色：ADMIN, GM, IT, MANUAL
- 1个管理员账户：zhiyu / 2201101122@qq.com

### 步骤3：初始化路由权限（可选）

```bash
# 初始化路由
python db/init_routes.py

# 绑定管理员路由
python db/bind_admin_routes.py

# 绑定GM路由
python db/bind_gm_routes.py
```

### 步骤4：验证初始化

```bash
# 测试管理员登录
python db/test_admin_login.py
```

## 📊 初始化内容

### 角色（4个）

| 角色代码 | 角色名称 | 描述 |
|---------|---------|------|
| ADMIN | 管理员 | 系统管理员，拥有所有权限 |
| GM | 项目管理员 | 项目管理员，负责项目运营和管理 |
| IT | 技术人员 | 技术人员，负责系统维护和技术支持 |
| MANUAL | 手动操作员 | 手动操作员，负责日常手动操作 |

### 管理员账户

| 字段 | 值 |
|-----|-----|
| 邮箱 | zhiyu |
| 密码 | 2201101122@qq.com |
| 昵称 | 至宇 |
| 角色 | ADMIN |
| 状态 | 正常 |

## 🔧 配置说明

脚本会自动读取 `backend/.env` 文件中的数据库配置：

```env
# 主库配置
DB_HOST=127.0.0.1
DB_PORT=3307
DB_USER=qyd
DB_PASSWORD=hWect7iWa4M67aSH
DB_NAME=qyd

# 从库配置（可选）
DB_SLAVE_HOSTS=127.0.0.1:3308,127.0.0.1:3309
```

**注意事项：**
- 初始化脚本只使用主库
- 确保主库配置正确
- 从库会自动同步数据

## 📝 运行示例

```bash
$ python db/init_roles_and_admin.py

============================================================
数据库初始化脚本
============================================================

============================================================
初始化数据库连接
============================================================
✓ 数据库连接成功
  主机: 149.88.87.93:3306
  数据库: qyd
  用户: qyd

============================================================
初始化角色
============================================================
✓ 创建角色: ADMIN - 管理员
✓ 创建角色: GM - 项目管理员
✓ 创建角色: IT - 技术人员
✓ 创建角色: MANUAL - 手动操作员

角色初始化完成:
  新建: 4 个
  更新: 0 个

============================================================
初始化管理员账户
============================================================
✓ 创建用户: zhiyu
✓ 分配角色: ADMIN

管理员账户创建成功:
  邮箱: zhiyu
  昵称: 至宇
  密码: 2201101122@qq.com
  角色: ADMIN

============================================================
验证初始化结果
============================================================
✓ 角色总数: 4
  - ADMIN: 管理员
  - GM: 项目管理员
  - IT: 技术人员
  - MANUAL: 手动操作员

✓ 管理员账户: zhiyu
  昵称: 至宇
  状态: 1
  角色: ADMIN
  密码验证: ✓ 通过

✓ 数据库连接已关闭
============================================================
✅ 初始化完成！
============================================================

📝 登录信息:
  邮箱: zhiyu
  密码: 2201101122@qq.com

🔐 安全提示:
  请在首次登录后立即修改密码！
```

## ⚠️ 注意事项

### 重复运行

脚本支持重复运行，会自动处理：
- 已存在的角色会被更新
- 已存在的用户会被更新（密码会重置）
- 角色关联会被重新建立

### 数据库迁移

如果数据库结构发生变化：

```bash
# 生成迁移文件
aerich migrate --name "description"

# 应用迁移
aerich upgrade

# 回滚迁移
aerich downgrade
```

### 主从同步

如果使用主从架构：
- 初始化脚本在主库执行
- 数据会自动同步到从库
- 检查同步状态：`python scripts/test/test_mysql_sync.sh`

### 安全建议

1. **立即修改密码**：首次登录后请立即修改管理员密码
2. **保护.env文件**：确保.env文件不被提交到版本控制
3. **限制访问权限**：限制数据库的访问IP和端口
4. **定期备份**：定期备份数据库
5. **使用强密码**：为数据库用户设置强密码

### 故障排查

**问题1：数据库连接失败**
```
✗ 数据库连接失败: Can't connect to MySQL server
```
解决方案：
- 检查.env中的数据库配置是否正确
- 确认数据库服务是否运行：`scripts/mysql/check_mysql_status.sh`
- 检查网络连接和防火墙设置
- 测试数据库连接：`python scripts/test_db_connection.py`

**问题2：密码加密失败**
```
✗ 初始化管理员账户失败: ...
```
解决方案：
- 确认已安装passlib和bcrypt
- 运行：`pip install passlib bcrypt==4.0.1`

**问题3：表不存在**
```
✗ Table 'qyd.users' doesn't exist
```
解决方案：
- 先运行数据库迁移：`aerich upgrade`
- 或运行：`bash scripts/init_db.sh`

**问题4：主从同步延迟**
```
从库数据不一致
```
解决方案：
- 检查主从同步状态：`bash scripts/mysql/test_mysql_sync.sh`
- 修复主从复制：`bash scripts/mysql/fix_replication.sh`
- 查看主库状态：`SHOW MASTER STATUS;`
- 查看从库状态：`SHOW SLAVE STATUS\G;`

## 🔍 验证初始化

### 方法1：使用脚本验证

脚本会自动验证初始化结果。

### 方法2：手动验证

```bash
# 连接数据库（主库）
mysql -h 127.0.0.1 -P 3307 -u qyd -p qyd

# 查看角色
SELECT * FROM user_roles;

# 查看管理员
SELECT u.*, GROUP_CONCAT(r.code) as roles
FROM users u
LEFT JOIN user_role_rel urr ON u.id = urr.userinfo_id
LEFT JOIN user_roles r ON urr.userrole_id = r.id
WHERE u.email = 'zhiyu'
GROUP BY u.id;

# 查看路由权限
SELECT * FROM user_routes;

# 查看角色路由关联
SELECT r.code, ur.path, ur.name
FROM user_roles r
LEFT JOIN user_role_route_rel rr ON r.id = rr.userrole_id
LEFT JOIN user_routes ur ON rr.userroute_id = ur.id
WHERE r.code = 'ADMIN';
```

### 方法3：API测试

```bash
# 测试登录
curl -X POST http://localhost:6080/api/v1/user/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhiyu",
    "password": "2201101122@qq.com"
  }'

# 使用返回的token测试API
curl -X POST http://localhost:6080/api/v1/user/list \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{"page": 1, "limit": 10}'
```

### 方法4：使用测试脚本

```bash
# 测试管理员登录
python db/test_admin_login.py

# 测试权限
bash scripts/test/test_crud_permission.sh
```

## 📚 相关文档

- `INITIALIZATION_SUMMARY.md` - 初始化总结
- `../docs/guides/RBAC_README.md` - RBAC使用指南
- `../docs/guides/PERMISSION_QUICK_START.md` - 权限快速开始
- `../docs/fixes/PASSWORD_ENCRYPTION_SUMMARY.md` - 密码加密说明
- `../docs/fixes/JWT_SUMMARY.md` - JWT认证说明
- `../app/models/user.py` - 用户模型定义

## 🛠️ 常用命令

```bash
# 初始化数据库
python db/init_roles_and_admin.py

# 初始化路由权限
python db/init_routes.py

# 绑定管理员路由
python db/bind_admin_routes.py

# 测试登录
python db/test_admin_login.py

# 数据库迁移
aerich migrate --name "description"
aerich upgrade

# 检查数据库状态
bash scripts/mysql/check_mysql_status.sh

# 测试主从同步
bash scripts/mysql/test_mysql_sync.sh
```

## 🆘 获取帮助

如果遇到问题：
1. 查看脚本输出的错误信息
2. 检查数据库连接配置
3. 确认依赖已正确安装
4. 查看相关文档

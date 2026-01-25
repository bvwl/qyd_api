# XUI 路由初始化指南

## 概述

将 XUI 管理相关的前端路由添加到数据库中，使其在前端菜单中可见。

## 路由结构

```
📁 XUI管理 (/xui) [sort=5]
  ├─ 服务器列表 (/xui/server)
  ├─ 入站列表 (/xui/inbound)
  └─ 账号管理 (/xui/account)
```

## 执行步骤

### 方法 1：使用 Shell 脚本（推荐）

```bash
cd backend
./add_xui_routes.sh
```

### 方法 2：直接运行 Python 脚本

```bash
cd backend
python db/add_xui_routes.py
```

## 脚本功能

### 1. 添加 XUI 路由

脚本会创建以下路由记录：

| 名称 | 路径 | 标题 | 组件 | 排序 |
|------|------|------|------|------|
| xui | /xui | XUI管理 | - | 5 |
| xui-server | /xui/server | 服务器列表 | XuiServerList | 1 |
| xui-inbound | /xui/inbound | 入站列表 | XuiInboundList | 2 |
| xui-account | /xui/account | 账号管理 | XuiAccountManage | 3 |

### 2. 调整其他路由排序

为了将 XUI 管理插入到合适的位置（sort=5），脚本会自动调整其他路由的排序：

- **原来的排序**:
  1. 仪表盘 (sort=1)
  2. 用户管理 (sort=2)
  3. 项目管理 (sort=3)
  4. 服务器管理 (sort=4)
  5. 邮箱管理 (sort=5)
  6. API文档 (sort=6)

- **调整后的排序**:
  1. 仪表盘 (sort=1)
  2. 用户管理 (sort=2)
  3. 项目管理 (sort=3)
  4. 服务器管理 (sort=4)
  5. **XUI管理 (sort=5)** ← 新增
  6. 邮箱管理 (sort=6) ← 从 5 调整到 6
  7. API文档 (sort=7) ← 从 6 调整到 7

### 3. 幂等性

脚本支持重复执行：
- 如果路由已存在，会更新现有路由
- 如果路由不存在，会创建新路由
- 排序调整只在首次创建时执行

## 执行结果

### 成功输出示例

```
✓ 已加载环境变量: /path/to/backend/.env

==========================================
添加 XUI 管理路由
==========================================

✓ 数据库连接成功

开始创建/更新 XUI 路由...
  ✓ 创建路由: XUI管理 (/xui)
  ✓ 创建路由: 服务器列表 (/xui/server)
  ✓ 创建路由: 入站列表 (/xui/inbound)
  ✓ 创建路由: 账号管理 (/xui/account)

==========================================
XUI 路由添加完成！
==========================================

XUI 路由结构:
------------------------------------------------------------
📁 XUI管理 (/xui)
  └─ 服务器列表 (/xui/server)
  └─ 入站列表 (/xui/inbound)
  └─ 账号管理 (/xui/account)

完整路由树结构:
------------------------------------------------------------
📁 仪表盘 (/dashboard) [sort=1]
📁 用户管理 (/user) [sort=2]
  └─ 用户列表 (/user/list)
  └─ 角色管理 (/user/role)
  └─ 路由管理 (/user/route)
  └─ 权限管理 (/user/permission)
  └─ Token管理 (/user/token)
  └─ 操作日志 (/user/log)
📁 项目管理 (/project) [sort=3]
  └─ 项目列表 (/project/list)
  └─ 项目账号 (/project/account)
  └─ 项目钱包 (/project/wallet)
📁 服务器管理 (/server) [sort=4]
  └─ 国家管理 (/server/country)
  └─ 分组管理 (/server/group)
  └─ 服务器列表 (/server/list)
  └─ 服务器账号 (/server/account)
📁 XUI管理 (/xui) [sort=5]
  └─ 服务器列表 (/xui/server)
  └─ 入站列表 (/xui/inbound)
  └─ 账号管理 (/xui/account)
📁 邮箱管理 (/mail) [sort=6]
  └─ 邮箱列表 (/mail/list)
  └─ 邮件查看 (/mail/viewer)
  └─ 发送邮件 (/mail/send)
📁 API文档 (/api-docs) [sort=7]
  └─ 用户列表 (/api-docs/user)
  └─ 创建用户 (/api-docs/user-create)
  └─ 角色列表 (/api-docs/role)
  └─ 项目列表 (/api-docs/project)
  └─ 项目账号 (/api-docs/project-account)
  └─ 服务器列表 (/api-docs/server)
  └─ 邮箱列表 (/api-docs/mail)

总路由数: 35
  - 一级菜单: 7
  - 二级菜单: 28
```

## 后续步骤

### 1. 重启后端服务

```bash
# 如果使用 start.py
python start.py

# 或者如果使用其他方式启动
# 重启你的后端服务
```

### 2. 刷新前端页面

在浏览器中刷新前端页面，新的菜单应该会出现。

### 3. 分配路由权限

在角色管理中为相应角色分配 XUI 路由权限：

1. 登录系统
2. 进入 **用户管理 > 角色管理**
3. 选择要授权的角色（如 ADMIN）
4. 点击 **编辑** 或 **权限管理**
5. 在路由树中勾选 **XUI管理** 及其子菜单
6. 保存

### 4. 验证菜单显示

1. 使用有权限的账号登录
2. 检查左侧菜单是否显示 **XUI管理**
3. 点击展开，应该看到三个子菜单：
   - 服务器列表
   - 入站列表
   - 账号管理

## 数据库表结构

路由数据存储在 `frontend_route` 表中：

```sql
CREATE TABLE `frontend_route` (
  `id` char(36) NOT NULL,
  `name` varchar(50) NOT NULL COMMENT '路由名称',
  `path` varchar(100) NOT NULL COMMENT '路由路径',
  `title` varchar(50) DEFAULT NULL COMMENT '菜单标题',
  `icon` varchar(50) DEFAULT NULL COMMENT '图标',
  `component` varchar(50) DEFAULT NULL COMMENT '组件名称',
  `sort` int DEFAULT '0' COMMENT '排序',
  `status` int NOT NULL DEFAULT '1' COMMENT '状态(1:正常,2:停用)',
  `parent_id` char(36) DEFAULT NULL COMMENT '父级ID',
  `create_time` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `update_time` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `parent_id` (`parent_id`),
  KEY `status` (`status`,`sort`)
);
```

## 查询路由

### 查询所有 XUI 路由

```sql
SELECT 
  r.id,
  r.name,
  r.path,
  r.title,
  r.sort,
  r.status,
  p.title as parent_title
FROM frontend_route r
LEFT JOIN frontend_route p ON r.parent_id = p.id
WHERE r.name LIKE 'xui%'
ORDER BY r.sort;
```

### 查询路由树

```sql
-- 一级菜单
SELECT id, name, path, title, sort, status
FROM frontend_route
WHERE parent_id IS NULL
ORDER BY sort;

-- XUI 子菜单
SELECT id, name, path, title, sort, status
FROM frontend_route
WHERE parent_id = (SELECT id FROM frontend_route WHERE name = 'xui')
ORDER BY sort;
```

## 删除 XUI 路由

如果需要删除 XUI 路由（用于测试或回滚）：

```sql
-- 删除子路由
DELETE FROM frontend_route WHERE parent_id = (SELECT id FROM frontend_route WHERE name = 'xui');

-- 删除父路由
DELETE FROM frontend_route WHERE name = 'xui';

-- 恢复其他路由的排序
UPDATE frontend_route SET sort = sort - 1 WHERE sort > 5 AND parent_id IS NULL;
```

## 故障排除

### 问题 1：路由已存在

**现象**：提示 "XUI 路由已存在"

**解决**：这是正常的，脚本会更新现有路由。如果需要重新创建，先删除现有路由。

### 问题 2：数据库连接失败

**现象**：提示 "数据库连接失败"

**解决**：
1. 检查 `.env` 文件中的数据库配置
2. 确保数据库服务正在运行
3. 检查数据库用户权限

### 问题 3：菜单不显示

**现象**：路由添加成功但前端菜单不显示

**解决**：
1. 检查用户角色是否有 XUI 路由权限
2. 清除浏览器缓存
3. 重新登录
4. 检查前端路由配置是否正确

### 问题 4：排序混乱

**现象**：菜单顺序不正确

**解决**：
1. 手动调整 `sort` 值
2. 或者删除所有路由，重新运行 `init_routes.py`

## 相关文件

- `backend/db/add_xui_routes.py` - Python 脚本
- `backend/add_xui_routes.sh` - Shell 脚本
- `backend/db/init_routes.py` - 初始化所有路由的脚本
- `frontend/src/router/index.tsx` - 前端路由配置
- `frontend/src/App.tsx` - 前端应用配置

## 完成状态

✅ Python 脚本已创建
✅ Shell 脚本已创建
✅ 脚本可执行权限已设置
✅ 支持幂等性（可重复执行）
✅ 自动调整其他路由排序
✅ 完整的错误处理
✅ 详细的输出信息
✅ 文档已完善

## 总结

XUI 路由初始化脚本已准备就绪，执行后将：

1. ✅ 在数据库中创建 XUI 管理菜单
2. ✅ 创建三个子菜单（服务器、入站、账号）
3. ✅ 自动调整其他菜单的排序
4. ✅ 显示完整的路由树结构

执行脚本后，需要在角色管理中为相应角色分配 XUI 路由权限，然后用户就可以在前端看到 XUI 管理菜单了。

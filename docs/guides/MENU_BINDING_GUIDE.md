# 菜单绑定指南

## 问题描述

前端页面看不到二级菜单和页面，这是因为：
1. 路由数据已经在数据库中
2. 但是角色没有绑定这些路由权限

## 解决方案

### 1. 初始化路由数据

运行路由初始化脚本，将前端菜单结构同步到数据库：

```bash
cd backend
python db/init_routes.py
```

**输出示例**：
```
✓ 已加载环境变量
✓ 数据库连接成功
✓ 更新路由: 仪表盘 (/dashboard)
✓ 更新路由: 项目管理 (/project)
  ✓ 更新路由: 项目列表 (/project/list)
  ✓ 更新路由: 项目账号 (/project/account)
  ✓ 更新路由: 项目钱包 (/project/wallet)
...
总路由数: 28
  - 一级菜单: 6
  - 二级菜单: 22
```

### 2. 为ADMIN角色绑定所有路由

```bash
cd backend
python db/bind_admin_routes.py
```

**输出示例**：
```
✓ 找到ADMIN角色: 管理员
  当前拥有 28 个路由权限
✓ ADMIN角色已拥有所有路由权限，无需添加
```

### 3. 为GM角色绑定路由（可选）

GM角色可以访问除了用户管理之外的所有功能：

```bash
cd backend
python db/bind_gm_routes.py
```

**输出示例**：
```
✓ 找到GM角色: 项目管理员
✓ GM角色应该拥有 21 个路由权限（排除用户管理）
✓ 已为GM角色绑定路由权限
```

### 4. 刷新前端页面

完成上述步骤后：
1. 退出登录
2. 重新登录
3. 现在应该可以看到所有菜单了

## 路由结构

### 完整路由树（28个路由）

```
📁 仪表盘 (/dashboard)

📁 用户管理 (/user)
  └─ 用户列表 (/user/list)
  └─ 角色管理 (/user/role)
  └─ 路由管理 (/user/route)
  └─ 权限管理 (/user/permission)
  └─ Token管理 (/user/token)
  └─ 操作日志 (/user/log)

📁 项目管理 (/project)
  └─ 项目列表 (/project/list)
  └─ 项目账号 (/project/account)
  └─ 项目钱包 (/project/wallet)

📁 服务器管理 (/server)
  └─ 国家管理 (/server/country)
  └─ 分组管理 (/server/group)
  └─ 服务器列表 (/server/list)
  └─ 服务器账号 (/server/account)

📁 邮箱管理 (/mail)
  └─ 邮箱列表 (/mail/list)
  └─ Outlook授权 (/mail/outlook)

📁 API文档 (/api-docs)
  └─ 用户列表 (/api-docs/user)
  └─ 创建用户 (/api-docs/user-create)
  └─ 角色列表 (/api-docs/role)
  └─ 项目列表 (/api-docs/project)
  └─ 项目账号 (/api-docs/project-account)
  └─ 服务器列表 (/api-docs/server)
  └─ 邮箱列表 (/api-docs/mail)
```

## 角色权限说明

### ADMIN（管理员）
- ✅ 拥有所有28个路由权限
- ✅ 可以访问所有功能模块
- ✅ 可以管理用户、角色、权限

### GM（项目管理员）
- ✅ 拥有21个路由权限（排除用户管理）
- ✅ 可以访问项目、服务器、邮箱、API文档
- ❌ 不能访问用户管理模块

### IT/MANUAL（其他角色）
- 需要手动分配路由权限
- 或者通过权限管理页面分配

## 工作原理

### 1. 动态菜单加载

前端Layout组件在加载时会调用API获取用户的路由权限：

```typescript
const loadUserRoutes = async () => {
  try {
    const routes = await getUserRoutes()
    const items = buildMenuItems(routes)
    setMenuItems(items)
  } catch (error) {
    console.error('加载菜单失败:', error)
  }
}
```

### 2. 后端路由过滤

后端API根据用户角色返回有权限的路由：

```python
@app.get("/user-routes")
async def get_user_routes(current_user: dict = Depends(get_current_user)):
    """获取当前用户的路由权限"""
    user_id = UUID(current_user["user_id"])
    user = await UserInfo.filter(id=user_id).prefetch_related("roles__routes").first()
    
    # 收集用户所有角色的路由
    all_routes = set()
    for role in user.roles:
        all_routes.update(role.routes)
    
    # 构建路由树
    return build_route_tree(all_routes)
```

### 3. 菜单渲染

前端根据返回的路由数据动态构建菜单：

```typescript
const buildMenuItems = (routes: any[]): MenuProps['items'] => {
  return routes
    .filter(route => !route.is_hidden && route.route_type === 1)
    .map(route => ({
      key: route.path,
      label: route.title,
      icon: route.icon ? iconMap[route.icon] : null,
      children: route.children ? buildMenuItems(route.children) : undefined,
    }))
}
```

## 常见问题

### Q1: 为什么看不到菜单？

**A**: 可能的原因：
1. 路由数据没有初始化 → 运行 `init_routes.py`
2. 角色没有绑定路由权限 → 运行 `bind_admin_routes.py`
3. 没有重新登录 → 退出后重新登录

### Q2: 如何添加新菜单？

**A**: 步骤：
1. 在 `backend/db/init_routes.py` 中添加路由数据
2. 运行 `python db/init_routes.py` 更新数据库
3. 运行 `python db/bind_admin_routes.py` 为ADMIN绑定权限
4. 在前端 `App.tsx` 中添加对应的路由配置
5. 重新登录查看

### Q3: 如何为其他角色分配菜单权限？

**A**: 两种方式：
1. **通过权限管理页面**：
   - 登录ADMIN账号
   - 进入"用户管理" → "权限管理"
   - 选择角色，勾选要分配的路由
   - 保存

2. **通过脚本**：
   - 参考 `bind_gm_routes.py` 创建新脚本
   - 运行脚本绑定权限

### Q4: GM角色为什么看不到用户管理？

**A**: 这是设计如此：
- GM是项目管理员，负责项目相关的管理
- 用户管理属于系统管理，只有ADMIN可以访问
- 如果需要修改，可以运行脚本重新绑定GM的路由权限

## 相关文件

### 后端文件
- `backend/db/init_routes.py` - 路由初始化脚本
- `backend/db/bind_admin_routes.py` - ADMIN角色路由绑定脚本
- `backend/db/bind_gm_routes.py` - GM角色路由绑定脚本
- `backend/app/apis/v1/user/route.py` - 路由API
- `backend/app/models/user.py` - 用户和路由模型

### 前端文件
- `frontend/src/components/Layout/index.tsx` - 布局和菜单组件
- `frontend/src/App.tsx` - 路由配置
- `frontend/src/api/user.ts` - 用户API

## 总结

菜单绑定的完整流程：
1. ✅ 初始化路由数据到数据库
2. ✅ 为角色绑定路由权限
3. ✅ 前端动态加载用户路由
4. ✅ 根据权限显示菜单

现在你应该可以看到完整的菜单结构了！

# RBAC 权限管理 - 快速开始

## 🚀 5分钟快速上手

### 1. 后端初始化（已完成✅）

数据库迁移和路由初始化已经完成，无需额外操作。

如需重新初始化，运行：
```bash
cd backend
python db/init_routes.py
```

### 2. 前端使用

#### 方式1：使用权限组件（推荐）

```typescript
import Permission from '@/components/Permission'

<Permission permission="user:create">
  <Button type="primary">创建用户</Button>
</Permission>
```

#### 方式2：使用权限Hook

```typescript
import { usePermission } from '@/hooks/usePermission'

function MyComponent() {
  const { hasPermission } = usePermission()
  
  return (
    <div>
      {hasPermission('user:delete') && (
        <Button danger>删除</Button>
      )}
    </div>
  )
}
```

### 3. 配置权限

#### 通过API配置（当前可用）

```bash
# 1. 获取角色ID
curl http://127.0.0.1:6080/v1/user/role

# 2. 获取路由ID
curl http://127.0.0.1:6080/v1/user/route/tree

# 3. 为角色分配路由权限
curl -X POST http://127.0.0.1:6080/v1/user/role/{role_id}/routes \
  -H "Content-Type: application/json" \
  -d '["route_id_1", "route_id_2"]'
```

#### 通过管理界面配置（待实现）

未来将提供可视化的权限配置界面。

## 📚 权限标识规范

```
格式：资源:操作

示例：
- user:view    - 查看用户
- user:create  - 创建用户
- user:edit    - 编辑用户
- user:delete  - 删除用户
```

## 🎯 常见场景

### 场景1：控制按钮显示

```typescript
<Space>
  <Permission permission="user:create">
    <Button type="primary">创建</Button>
  </Permission>
  
  <Permission permission="user:edit">
    <Button>编辑</Button>
  </Permission>
  
  <Permission permission="user:delete">
    <Button danger>删除</Button>
  </Permission>
</Space>
```

### 场景2：表格操作列

```typescript
{
  title: '操作',
  key: 'action',
  render: (_, record) => (
    <Space>
      <Permission permission="user:view">
        <Button type="link">查看</Button>
      </Permission>
      <Permission permission="user:edit">
        <Button type="link">编辑</Button>
      </Permission>
      <Permission permission="user:delete">
        <Button type="link" danger>删除</Button>
      </Permission>
    </Space>
  ),
}
```

### 场景3：复杂权限逻辑

```typescript
// 满足任意一个权限
<Permission anyPermissions={["user:edit", "user:delete"]}>
  <Button>操作</Button>
</Permission>

// 需要所有权限
<Permission allPermissions={["user:view", "user:edit"]}>
  <Button>查看并编辑</Button>
</Permission>

// 无权限时显示提示
<Permission 
  permission="admin:panel"
  fallback={<div>您没有访问权限</div>}
>
  <Button>管理面板</Button>
</Permission>
```

## 📖 完整文档

- [设计文档](./docs/RBAC_DESIGN.md) - 系统设计说明
- [快速入门](./docs/RBAC_QUICK_START.md) - 详细使用指南
- [实现总结](./backend/RBAC_IMPLEMENTATION_SUMMARY.md) - 技术实现
- [完成报告](./RBAC_COMPLETE.md) - 完整的实现报告
- [使用示例](./frontend/src/examples/PermissionExample.tsx) - 代码示例

## 🔧 测试

```bash
# 后端测试
cd backend
python test_rbac_apis.py

# 查看路由数据
curl http://127.0.0.1:6080/v1/user/route/tree
```

## ❓ 常见问题

### Q: 用户看不到某个按钮？
A: 检查：
1. 用户是否分配了角色
2. 角色是否有对应的路由权限
3. 权限标识是否正确

### Q: 如何添加新的权限？
A: 
1. 在 `backend/db/init_routes.py` 中添加路由
2. 运行 `python backend/db/init_routes.py`
3. 为角色分配新权限

### Q: 权限标识如何命名？
A: 使用 `资源:操作` 格式，如 `user:create`、`project:delete`

## 🎉 开始使用

现在你已经了解了基本用法，可以开始在项目中使用RBAC权限管理了！

如有问题，请查看完整文档或联系开发团队。

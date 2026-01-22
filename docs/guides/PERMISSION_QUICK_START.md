# 权限管理快速开始指南

## 1. 访问权限管理页面

### 登录系统
1. 打开浏览器访问：http://localhost:3000
2. 使用管理员账号登录：
   - 邮箱：`zhiyu`
   - 密码：`2201101122@qq.com`

### 进入权限管理
登录后，点击左侧菜单：**用户管理** → **权限管理**

或直接访问：http://localhost:3000/user/permission

## 2. 配置角色权限

### 步骤1：选择角色
在左侧"角色列表"中点击要配置的角色，例如：
- **管理员（ADMIN）**：系统管理员，拥有所有权限
- **项目管理员（GM）**：负责项目运营和管理
- **技术人员（IT）**：负责系统维护和技术支持
- **手动操作员（MANUAL）**：负责日常手动操作

### 步骤2：配置路由权限
在右侧路由树中勾选该角色可以访问的菜单：
- ☑ 仪表盘
- ☑ 用户管理
  - ☑ 用户列表
  - ☑ 角色管理
  - ☑ 路由管理
  - ☑ 权限管理
- ☑ 项目管理
  - ☑ 项目列表
  - ☑ 项目账号
  - ☑ 项目钱包
- ...

### 步骤3：保存配置
点击右上角的"保存"按钮，保存权限配置。

## 3. 测试权限

### 创建测试用户
1. 进入"用户管理" → "用户列表"
2. 点击"创建用户"
3. 填写用户信息并选择角色
4. 保存

### 测试权限效果
1. 退出当前账号
2. 使用新创建的用户登录
3. 查看左侧菜单，只显示该用户角色有权限的菜单项

## 4. API使用示例

### 获取路由树
```bash
curl -X GET "http://127.0.0.1:6080/v1/user/route/tree?status=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 获取角色列表
```bash
curl -X GET "http://127.0.0.1:6080/v1/user/role?page=1&limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 获取角色的路由权限
```bash
curl -X GET "http://127.0.0.1:6080/v1/user/role/{role_id}/routes" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 设置角色的路由权限
```bash
curl -X POST "http://127.0.0.1:6080/v1/user/role/{role_id}/routes" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '["route_id_1", "route_id_2", "route_id_3"]'
```

### 获取当前用户的路由权限
```bash
curl -X GET "http://127.0.0.1:6080/v1/user/route/user-routes" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 5. 前端开发示例

### 使用Permission组件控制按钮显示
```tsx
import Permission from '@/components/Permission'

function UserList() {
  return (
    <div>
      <h1>用户列表</h1>
      
      {/* 只有拥有 user:create 权限的用户才能看到此按钮 */}
      <Permission permission="user:create">
        <Button type="primary">创建用户</Button>
      </Permission>
      
      {/* 只有拥有 user:delete 权限的用户才能看到此按钮 */}
      <Permission permission="user:delete">
        <Button danger>删除用户</Button>
      </Permission>
    </div>
  )
}
```

### 使用usePermission Hook
```tsx
import { usePermission } from '@/hooks/usePermission'

function UserList() {
  const { hasPermission } = usePermission()
  
  return (
    <div>
      <h1>用户列表</h1>
      
      {hasPermission('user:create') && (
        <Button type="primary">创建用户</Button>
      )}
      
      {hasPermission('user:delete') && (
        <Button danger>删除用户</Button>
      )}
    </div>
  )
}
```

## 6. 常见问题

### Q1: 修改权限后需要重新登录吗？
A: 是的。权限信息存储在JWT token中，修改权限后需要重新登录才能生效。

### Q2: 如何添加新的路由？
A: 有两种方式：
1. 通过前端"路由管理"页面手动添加
2. 修改 `backend/db/init_routes.py` 脚本并重新运行

### Q3: 如何创建新的角色？
A: 进入"用户管理" → "角色管理"，点击"创建角色"按钮。

### Q4: 权限配置保存失败怎么办？
A: 检查：
1. 是否有管理员权限
2. 网络连接是否正常
3. 后端服务是否运行
4. 查看浏览器控制台的错误信息

### Q5: 如何查看某个角色的所有权限？
A: 在权限管理页面选择该角色，右侧会显示该角色已勾选的所有路由。

## 7. 权限设计建议

### 角色设计原则
1. **最小权限原则**：只授予完成工作所需的最小权限
2. **职责分离**：不同职责使用不同角色
3. **定期审查**：定期检查和更新角色权限

### 推荐的角色配置

#### ADMIN（管理员）
- 所有菜单和功能
- 用于系统管理员

#### GM（项目管理员）
- 仪表盘
- 项目管理（所有子菜单）
- 服务器管理（查看和基本操作）

#### IT（技术人员）
- 仪表盘
- 服务器管理（所有子菜单）
- 邮箱管理（所有子菜单）

#### MANUAL（手动操作员）
- 仪表盘
- 项目列表（只读）
- 服务器列表（只读）

## 8. 下一步

完成基础权限配置后，可以：

1. **实现动态菜单**：根据用户权限动态显示菜单
2. **添加按钮权限**：为页面内的操作按钮添加权限控制
3. **添加API权限**：为后端API添加权限验证
4. **权限审计**：记录权限变更历史

## 9. 相关文档

- [RBAC完整文档](./RBAC_COMPLETE.md)
- [RBAC修复总结](./RBAC_FIXED_SUMMARY.md)
- [权限管理指南](./PERMISSION_MANAGE_README.md)
- [API测试脚本](./test_permission_apis.sh)

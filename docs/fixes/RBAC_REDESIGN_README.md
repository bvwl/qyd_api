# 企业级 RBAC 权限管理系统 - 重新设计

## 📋 项目概述

按照标准的企业级 RBAC（Role-Based Access Control）模型，重新设计权限管理系统。

## 🎯 设计目标

1. **职责分离**：菜单和权限完全分离
2. **标准规范**：符合企业级 RBAC 标准
3. **灵活强大**：支持多种权限类型和数据权限
4. **易于维护**：清晰的代码结构和文档

## 📚 文档导航

### 快速开始
- **[docs/rbac/QUICK_START.md](./docs/rbac/QUICK_START.md)** ⭐ 5分钟快速上手

### 设计文档
- **[docs/rbac/ENTERPRISE_RBAC_DESIGN.md](./docs/rbac/ENTERPRISE_RBAC_DESIGN.md)** - 完整的设计文档

### 实施指南
- **[docs/rbac/IMPLEMENTATION_GUIDE.md](./docs/rbac/IMPLEMENTATION_GUIDE.md)** - 分步实施指南

## 🏗️ 核心架构

### 数据模型

```
┌─────────────┐
│    User     │ 用户
└──────┬──────┘
       │ N:M
       ▼
┌─────────────┐
│    Role     │ 角色
└──────┬──────┘
       │ N:M
       ├──────────────┬──────────────┐
       ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Permission  │ │    Menu     │ │ DataScope   │
│   权限      │ │    菜单     │ │  数据权限   │
└─────────────┘ └─────────────┘ └─────────────┘
```

### 核心表

1. **permissions** - 权限表（最细粒度）
2. **menus** - 菜单表（独立）
3. **roles** - 角色表（增强版）
4. **user_role_rel** - 用户-角色关联
5. **role_permission_rel** - 角色-权限关联
6. **role_menu_rel** - 角色-菜单关联
7. **custom_data_scopes** - 自定义数据权限

## 🔑 核心概念

### 权限（Permission）

```python
# 权限命名规范：{resource}:{action}
"user:create"    # 创建用户
"user:edit"      # 编辑用户
"user:delete"    # 删除用户
"project:view"   # 查看项目
```

### 菜单（Menu）

```python
# 菜单只负责前端显示
{
    "name": "UserList",
    "title": "用户列表",
    "path": "/user/list",
    "required_permission": "user:view"  # 可选：需要的权限
}
```

### 数据权限（Data Scope）

```python
class DataScope(IntEnum):
    ALL = 1              # 全部数据
    DEPT = 2             # 本部门数据
    DEPT_AND_CHILD = 3   # 本部门及下级部门
    SELF = 4             # 仅本人数据
    CUSTOM = 5           # 自定义范围
```

## 💻 代码示例

### 后端：权限检查

```python
from app.utils.rbac import require_permission

@app.post("/users")
@require_permission("user:create")
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_user)
):
    # 只有有 user:create 权限的用户才能访问
    pass
```

### 后端：数据权限

```python
from app.utils.rbac import filter_by_data_scope

@app.get("/projects")
async def get_projects(
    current_user: dict = Depends(get_current_user)
):
    query = Project.all()
    
    # 根据用户的数据权限过滤
    query = await filter_by_data_scope(
        query,
        current_user['user_id'],
        'project'
    )
    
    return await query.all()
```

### 前端：权限组件

```tsx
<Permission permission="user:create">
  <Button>创建用户</Button>
</Permission>
```

### 前端：权限指令

```vue
<button v-permission="'user:create'">创建用户</button>
```

## 📦 新增文件

### 后端

```
backend/
├── app/
│   ├── models/
│   │   └── rbac.py                    # RBAC 模型
│   ├── utils/
│   │   └── rbac.py                    # RBAC 工具函数
│   └── apis/v1/system/
│       ├── permission.py              # 权限管理 API
│       ├── menu.py                    # 菜单管理 API
│       └── role.py                    # 角色管理 API（增强）
└── db/
    └── migrate_to_rbac.py             # 数据迁移脚本
```

### 文档

```
docs/rbac/
├── ENTERPRISE_RBAC_DESIGN.md          # 设计文档
├── IMPLEMENTATION_GUIDE.md            # 实施指南
└── QUICK_START.md                     # 快速开始
```

## 🚀 实施步骤

### 第一阶段：准备（1天）
1. 备份数据库
2. 运行迁移脚本
3. 验证数据

### 第二阶段：后端（2-3天）
1. 实现新模型
2. 实现 RBAC 工具
3. 实现 API 接口
4. 更新现有 API

### 第三阶段：前端（2-3天）
1. 更新权限管理页面
2. 更新权限指令/组件
3. 更新菜单渲染逻辑

### 第四阶段：测试（1-2天）
1. 单元测试
2. 集成测试
3. 用户验收测试

### 第五阶段：上线（1天）
1. 灰度发布
2. 全量发布
3. 监控和优化

**预计总工期：7-10天**

## ✨ 核心优势

### 1. 职责清晰
- ✅ 菜单只负责显示
- ✅ 权限只负责控制
- ✅ 角色连接用户和权限

### 2. 灵活强大
- ✅ 支持 API 权限
- ✅ 支持按钮权限
- ✅ 支持数据权限
- ✅ 支持自定义权限

### 3. 标准规范
- ✅ 符合企业级 RBAC 标准
- ✅ 权限命名规范统一
- ✅ 代码结构清晰

### 4. 易于维护
- ✅ 文档完善
- ✅ 代码注释详细
- ✅ 测试覆盖完整

## 📊 对比：旧 vs 新

| 特性 | 旧系统 | 新系统 |
|------|--------|--------|
| 菜单和权限 | 混在一起 | 完全分离 ✅ |
| 权限粒度 | 粗粒度 | 细粒度 ✅ |
| 数据权限 | 不完善 | 完善 ✅ |
| 权限类型 | 单一 | 多种类型 ✅ |
| 扩展性 | 差 | 好 ✅ |
| 维护性 | 差 | 好 ✅ |

## 🧪 测试

### 运行迁移
```bash
cd backend
python db/migrate_to_rbac.py
```

### 运行测试
```bash
pytest app/tests/test_rbac.py
```

### 手动测试
1. 创建权限
2. 创建菜单
3. 分配权限给角色
4. 分配菜单给角色
5. 用户登录测试
6. 权限检查测试
7. 数据权限测试

## 📞 支持

### 问题排查

**问题1：权限检查失败**
```python
# 检查用户的权限
from app.utils.rbac import get_user_permissions
permissions = await get_user_permissions(user_id)
print([p.code for p in permissions])
```

**问题2：菜单不显示**
```python
# 检查用户的菜单
from app.utils.rbac import get_user_menus
menus = await get_user_menus(user_id)
print(menus)
```

**问题3：数据权限不生效**
```python
# 检查用户的数据范围
from app.utils.rbac import get_user_data_scope
data_scope = await get_user_data_scope(user_id)
print(f"数据范围: {data_scope}")
```

## 🎓 学习路径

### 新手（10分钟）
1. 阅读 [QUICK_START.md](./docs/rbac/QUICK_START.md)
2. 运行迁移脚本
3. 测试基本功能

### 开发者（30分钟）
1. 阅读 [ENTERPRISE_RBAC_DESIGN.md](./docs/rbac/ENTERPRISE_RBAC_DESIGN.md)
2. 理解核心概念
3. 查看代码示例

### 架构师（1小时）
1. 阅读完整设计文档
2. 阅读实施指南
3. 理解设计理念和权衡

## 🔄 迁移策略

### 兼容性
- ✅ 保留旧表作为备份
- ✅ 新旧 API 并行运行
- ✅ 逐步迁移到新系统

### 回滚方案
```bash
# 1. 停止服务
systemctl stop qyd-backend

# 2. 恢复数据库
mysql -u qyd -p qyd < backup_YYYYMMDD_HHMMSS.sql

# 3. 回滚代码
git checkout <previous-commit>

# 4. 重启服务
systemctl start qyd-backend
```

## 📝 更新日志

### 2026-01-23
- ✅ 完成企业级 RBAC 设计
- ✅ 实现核心模型和工具
- ✅ 编写完整文档
- ✅ 创建迁移脚本

## 🎉 总结

这是一个**生产级别**的企业级 RBAC 权限管理系统设计：

- ✅ **标准规范**：符合企业级 RBAC 标准
- ✅ **职责清晰**：菜单和权限完全分离
- ✅ **功能强大**：支持多种权限类型和数据权限
- ✅ **易于维护**：清晰的代码结构和完善的文档
- ✅ **可扩展性**：易于添加新的权限类型和功能

开始使用吧！🚀

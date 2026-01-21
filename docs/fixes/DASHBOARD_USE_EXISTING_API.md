# 仪表盘使用现有API - 更新说明

## 📋 变更概述

修改仪表盘实现，使用现有的API接口而不是创建新的dashboard API。

## 🔄 主要变更

### 1. 前端仪表盘 (`frontend/src/views/Dashboard/index.tsx`)

**变更前：**
- 调用 `/v1/user/dashboard/stats` 获取统计数据
- 调用 `/v1/user/dashboard/projects` 获取项目列表

**变更后：**
- 使用 `/v1/user/user` 获取用户数量
- 使用 `/v1/project/info` 获取项目列表
- 使用 `/v1/project/account` 获取账户数量
- 根据用户角色动态获取不同的数据

### 2. 数据获取逻辑

#### ADMIN（管理员）
```typescript
// 获取所有用户数量
getUserList({ page: 1, limit: 1, res_count: true })

// 获取所有项目
getProjectList({ page: 1, limit: 100, res_count: true })

// 获取所有账户数量
getProjectAccountList({ page: 1, limit: 1, res_count: true })
```

#### GM（项目管理员）
```typescript
// 获取所有项目
getProjectList({ page: 1, limit: 100, res_count: true })

// 获取所有账户数量
getProjectAccountList({ page: 1, limit: 1, res_count: true })
```

#### IT/MANUAL（技术人员/手动操作员）
```typescript
// 获取项目列表（暂时显示所有，后续可以按用户过滤）
getProjectList({ page: 1, limit: 100, res_count: true })

// 获取账户数量
getProjectAccountList({ page: 1, limit: 1, res_count: true })
```

### 3. 项目账户数量统计

为每个项目单独查询账户数量：

```typescript
const projectsWithAccounts = await Promise.all(
  projectList.map(async (project) => {
    const accountsRes = await getProjectAccountList({
      project_id: project.id,
      page: 1,
      limit: 1,
      res_count: true,
    })
    return {
      id: project.id,
      name: project.name,
      account_count: accountsRes.count || 0,
      status: project.status,
    }
  })
)
```

## 🗑️ 删除的文件

- `backend/app/apis/v1/user/dashboard.py` - 不再需要的dashboard API
- 从 `backend/app/apis/v1/user/__init__.py` 移除dashboard路由注册
- 从 `frontend/src/api/user.ts` 移除dashboard API函数

## 📝 使用的现有API

### 用户API
- `GET /v1/user/user?page=1&limit=1&res_count=true` - 获取用户总数

### 项目API
- `GET /v1/project/info?page=1&limit=100&res_count=true` - 获取项目列表和总数
- `GET /v1/project/account?page=1&limit=1&res_count=true` - 获取账户总数
- `GET /v1/project/account?project_id={id}&res_count=true` - 获取指定项目的账户数

## 🎯 角色权限控制

权限控制在前端实现，根据用户角色决定调用哪些API：

```typescript
const role_priority: Record<string, number> = { 
  ADMIN: 4, 
  GM: 3, 
  IT: 2, 
  MANUAL: 1 
}

const user_roles = userInfo.roles?.map(r => r.code) || []
const primary_role = user_roles.reduce((a, b) => 
  (role_priority[a] || 0) > (role_priority[b] || 0) ? a : b
)
```

## 🚀 使用方法

### 1. 重启前端服务

```bash
cd frontend
npm run dev
```

### 2. 访问仪表盘

登录后会自动跳转到仪表盘：`http://localhost:5173/dashboard`

### 3. 验证功能

- ✅ 管理员可以看到用户数量
- ✅ 所有角色可以看到项目和账户数量
- ✅ 项目列表显示每个项目的账户数量
- ✅ 项目状态正确显示

## ⚠️ 注意事项

1. **不需要重启后端服务**
   - 只修改了前端代码
   - 使用的都是现有API

2. **性能考虑**
   - 为每个项目单独查询账户数量可能较慢
   - 如果项目很多，建议后端添加批量查询接口

3. **IT/MANUAL用户过滤**
   - 目前显示所有项目
   - 后续可以在后端添加按用户过滤项目的功能

## 🎯 后续优化建议

### 1. 后端优化

添加批量查询项目账户数量的接口：

```python
@app.post("/batch-account-count")
async def get_batch_account_count(
    project_ids: List[UUID] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """批量获取项目账户数量"""
    result = {}
    for project_id in project_ids:
        count = await ProjectAccount.filter(project_id=project_id).count()
        result[str(project_id)] = count
    return result
```

### 2. 前端优化

使用批量接口减少请求次数：

```typescript
// 一次请求获取所有项目的账户数量
const accountCounts = await batchGetAccountCount(projectIds)
```

### 3. 缓存优化

添加数据缓存，减少重复请求：

```typescript
// 使用 React Query 或 SWR 缓存数据
const { data, isLoading } = useQuery('dashboard-stats', fetchDashboardData)
```

## ✨ 优点

- ✅ 使用现有API，无需修改后端
- ✅ 代码更简洁，易于维护
- ✅ 灵活性更高，可以根据需要调整数据获取逻辑
- ✅ 减少了API端点数量

## 📖 相关文档

- 项目API：`backend/app/apis/v1/project/info.py`
- 账户API：`backend/app/apis/v1/project/account.py`
- 用户API：`backend/app/apis/v1/user/user.py`

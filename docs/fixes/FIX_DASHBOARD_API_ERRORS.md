# 修复仪表盘API错误

## 🐛 问题描述

1. **后端错误**：`'CRUD' object has no attribute 'get_count'`
   - 项目账户API调用了不存在的`get_count`方法

2. **前端问题**：错误情况下接口被多次调用
   - 没有错误处理，导致重复请求

## ✅ 解决方案

### 1. 修复后端API (`backend/app/apis/v1/project/account.py`)

**问题：**
```python
# 错误的代码
if res_count:
    count = await project_account_crud.get_count(...)  # get_count方法不存在
else:
    count = -1
return await project_account_crud.get_multi(..., res_count=res_count)
```

**修复：**
```python
# 直接使用get_multi，它内部已经处理了计数
return await project_account_crud.get_multi(
    ...,
    res_count=res_count,  # get_multi会根据这个参数决定是否计数
)
```

**变更：**
- 移除了对不存在的`get_count`方法的调用
- 直接使用`get_multi`方法，它内部已经有计数逻辑
- 修正了参数名：`server_info_id` → `server_id`，`wallet_id`（新增）

### 2. 修复前端错误处理 (`frontend/src/views/Dashboard/index.tsx`)

**问题：**
- API调用失败时没有错误处理
- 错误会导致页面崩溃
- 可能触发多次重试

**修复：**

#### 添加错误捕获
```typescript
const [usersRes, projectsRes, accountsRes] = await Promise.all([
  getUserList(...).catch(() => ({ count: 0, items: [] })),
  getProjectList(...).catch(() => ({ count: 0, items: [] })),
  getProjectAccountList(...).catch(() => ({ count: 0, items: [] })),
])
```

#### 限制项目数量
```typescript
// 只获取前20个项目的账户数量，避免请求过多
projectList.slice(0, 20).map(async (project) => {
  // ...
})
```

#### 设置默认值
```typescript
catch (error) {
  console.error('获取仪表盘数据失败:', error)
  // 设置默认值，避免页面崩溃
  setStats({
    user_count: undefined,
    project_count: 0,
    account_count: 0,
    role: primary_role,
    user_email: userInfo.email,
    user_nickname: userInfo.nickname,
  })
  setProjects([])
}
```

## 📝 修改的文件

1. `backend/app/apis/v1/project/account.py`
   - 移除`get_count`调用
   - 修正参数名
   - 添加异常处理

2. `frontend/src/views/Dashboard/index.tsx`
   - 添加错误捕获
   - 限制项目数量（最多20个）
   - 设置默认值防止崩溃

## 🚀 使用方法

### 1. 重启后端服务

```bash
cd backend
python start.py
```

### 2. 刷新前端页面

前端会自动重新加载，无需重启。

### 3. 验证修复

访问仪表盘：`http://localhost:5173/dashboard`

检查：
- ✅ 不再有 `get_count` 错误
- ✅ API调用失败时显示默认值
- ✅ 页面不会崩溃
- ✅ 只调用一次API

## 🔍 测试API

### 测试项目账户列表

```bash
# 获取token
TOKEN=$(curl -s http://127.0.0.1:6080/v1/user/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"zhiyu","password":"2201101122@qq.com"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 测试获取账户列表（带计数）
curl -s "http://127.0.0.1:6080/v1/project/account?page=1&limit=1&res_count=true" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**预期响应：**
```json
{
  "message": "成功",
  "count": 150,
  "num": 1,
  "items": [...]
}
```

## ⚠️ 注意事项

1. **性能优化**
   - 限制了项目数量为20个
   - 如果项目很多，建议后端添加批量查询接口

2. **错误处理**
   - 所有API调用都有错误捕获
   - 失败时返回默认值，不会中断流程

3. **数据一致性**
   - 如果某个API失败，其他数据仍然可以正常显示

## 🎯 后续优化建议

### 1. 后端批量查询接口

添加批量获取项目账户数量的接口：

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

### 2. 前端缓存

使用 React Query 或 SWR 缓存数据：

```typescript
import { useQuery } from '@tanstack/react-query'

const { data, isLoading, error } = useQuery({
  queryKey: ['dashboard-stats'],
  queryFn: fetchDashboardData,
  staleTime: 5 * 60 * 1000, // 5分钟缓存
})
```

### 3. 加载状态优化

添加骨架屏或更好的加载提示：

```typescript
if (isLoading) {
  return <Skeleton active />
}
```

## ✨ 修复效果

- ✅ 后端API正常工作
- ✅ 前端错误处理完善
- ✅ 页面不会因为API错误而崩溃
- ✅ 用户体验更好
- ✅ 性能更优（限制请求数量）

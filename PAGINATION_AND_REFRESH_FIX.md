# 分页和数据刷新问题修复

## 问题描述

### 1. 邮箱列表翻页失效
- **现象**：点击翻页按钮没有反应
- **原因**：`pagination.onChange` 回调中的参数名与外层状态变量同名，导致作用域混淆

### 2. 项目列表新增后需要刷新
- **现象**：创建新项目后，列表不会自动显示新项目，需要手动刷新页面
- **原因**：
  1. `fetchData()` 调用没有使用 `await`，可能导致异步问题
  2. 多角色用户（IT + GM）的数据权限过滤逻辑复杂

## 修复方案

### 1. 邮箱列表 (MailList.tsx)

#### 修复分页参数名冲突
```typescript
// ❌ 错误：参数名与状态变量同名
onChange: (page, pageSize) => {
  setPage(page)
  setPageSize(pageSize)
}

// ✅ 正确：使用不同的参数名
onChange: (newPage, newPageSize) => {
  console.log('分页变化:', newPage, newPageSize)
  setPage(newPage)
  if (newPageSize !== pageSize) {
    setPageSize(newPageSize)
  }
}
```

#### 添加 ESLint 注释
```typescript
// 当分页、排序变化时重新加载数据
useEffect(() => {
  fetchData()
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, [page, pageSize, orderBy])
```

### 2. 项目列表 (ProjectList.tsx)

#### 修复数据刷新
```typescript
// ❌ 错误：没有等待数据加载完成
const handleSubmit = async () => {
  // ...
  setModalVisible(false)
  fetchData()  // 不等待
}

// ✅ 正确：等待数据加载完成
const handleSubmit = async () => {
  // ...
  setModalVisible(false)
  await fetchData()  // 等待完成
}
```

#### 修复分页参数名
```typescript
pagination={{
  current: page,
  pageSize: pageSize,
  total: total,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条`,
  onChange: (newPage, newPageSize) => {
    console.log('项目列表分页变化:', newPage, newPageSize)
    setPage(newPage)
    if (newPageSize !== pageSize) {
      setPageSize(newPageSize)
    }
  },
}}
```

#### 人员管理保存后刷新
```typescript
const handleSaveUsers = async () => {
  // ...
  message.success('人员关联更新成功')
  setUserModalVisible(false)
  await fetchData()  // 等待数据刷新
}
```

## 数据权限说明

### 后端权限逻辑 (backend/app/apis/v1/project/info.py)

```python
# 获取当前用户角色
user_roles = [role.code for role in user.roles]

# 判断是否有全局查看权限
has_global_access = any(role in ['ADMIN', 'GM'] for role in user_roles)

if has_global_access:
    # 管理员/GM：返回所有项目（可选择按用户筛选）
    if user_id:
        filter_user_id = user_id
else:
    # 非管理员：只能查看自己的项目
    await user.fetch_related('projects')
    user_project_ids = [str(project.id) for project in user.projects]
```

### 多角色用户
- 如果用户同时拥有 IT 和 GM 角色
- 系统会检测到 GM 角色，给予全局访问权限
- 可以看到所有项目，不需要手动关联

## 测试步骤

### 1. 测试邮箱列表翻页
1. 打开邮箱列表页面
2. 确保有超过10条数据
3. 点击翻页按钮（2、3、4等）
4. 验证：页面应该正常切换，显示对应页的数据

### 2. 测试项目列表新增
1. 以 GM 或 ADMIN 角色登录
2. 打开项目列表页面
3. 点击"新增项目"
4. 填写项目信息并保存
5. 验证：新项目应该立即出现在列表中，无需刷新页面

### 3. 测试多角色用户
1. 创建一个同时拥有 IT 和 GM 角色的用户
2. 以该用户登录
3. 创建新项目
4. 验证：新项目应该立即显示在列表中

### 4. 测试人员管理
1. 打开项目列表
2. 点击某个项目的"管理"按钮
3. 添加或移除关联人员
4. 保存
5. 验证：列表应该立即更新，显示最新的关联人员

## 调试技巧

### 1. 查看控制台日志
```typescript
// 分页变化日志
console.log('分页变化:', newPage, newPageSize)

// 权限检查日志
console.log('ProjectList 权限更新:', {
  userInfo,
  roles: userInfo?.roles?.map(r => r.code),
  canManageProject,
})
```

### 2. 检查网络请求
- 打开浏览器开发者工具 -> Network
- 筛选 XHR 请求
- 查看 `/v1/project/info` 请求
- 检查请求参数和响应数据

### 3. 检查用户角色
```typescript
// 在组件中添加
useEffect(() => {
  console.log('当前用户信息:', userInfo)
  console.log('用户角色:', userInfo?.roles?.map(r => r.code))
}, [userInfo])
```

## 相关文件

### 前端
- `frontend/src/views/Mail/MailList.tsx` - 邮箱列表
- `frontend/src/views/Project/ProjectList.tsx` - 项目列表
- `frontend/src/store/useUserStore.ts` - 用户状态管理

### 后端
- `backend/app/apis/v1/project/info.py` - 项目API
- `backend/app/crud/project/info.py` - 项目CRUD
- `backend/app/apis/deps.py` - 权限依赖

## 注意事项

1. **参数名冲突**：在回调函数中避免使用与外层状态变量同名的参数
2. **异步等待**：数据刷新操作应该使用 `await` 等待完成
3. **权限检查**：多角色用户会获得最高权限角色的访问级别
4. **数据预加载**：使用 `prefetch_related` 预加载关联数据，避免 N+1 查询

## 后续优化建议

1. **统一分页组件**：创建一个通用的分页组件，避免重复代码
2. **数据刷新策略**：考虑使用 React Query 或 SWR 进行数据缓存和自动刷新
3. **权限缓存**：前端缓存用户权限信息，减少重复请求
4. **乐观更新**：在创建/更新操作时，先更新本地状态，再同步到服务器

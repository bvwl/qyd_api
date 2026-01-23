# 项目列表用户筛选功能

## 📋 功能概述

在项目列表界面添加了根据用户筛选项目的功能，方便管理员和GM查看特定用户关联的项目。

## ✅ 实现内容

### 1. 后端API修改

**文件**: `backend/app/apis/v1/project/info.py`

添加了`user_id`查询参数：

```python
@app.get("", response_model=OutList, description="获取项目信息列表")
async def gets(
    ...
    user_id: UUID | None = Query(None, description="关联用户ID（筛选该用户的项目）"),
    ...
):
```

**权限逻辑**:
- **ADMIN/GM**: 可以使用`user_id`参数筛选任意用户的项目
- **IT/MANUAL**: 忽略`user_id`参数，只能查看自己的项目

### 2. 前端API修改

**文件**: `frontend/src/api/project.ts`

在`getProjectList`函数的参数类型中添加了`user_id`:

```typescript
export const getProjectList = (params?: PaginationParams & { 
  name?: string
  status?: number
  user_id?: string  // 新增
  ...
})
```

### 3. 前端界面修改

**文件**: `frontend/src/views/Project/ProjectList.tsx`

#### 3.1 新增状态

```typescript
const [searchUserId, setSearchUserId] = useState<string>()
const [filterUsers, setFilterUsers] = useState<User[]>([])
```

#### 3.2 加载用户列表

```typescript
const fetchFilterUsers = async () => {
  if (!isAdmin && !isGM) return // 只有管理员和GM可以按用户筛选
  
  try {
    const res = await getUserList({ page: 1, limit: 1000 })
    setFilterUsers(res.items || [])
  } catch (error) {
    setFilterUsers([])
  }
}
```

#### 3.3 添加用户筛选下拉框

在搜索栏中添加了用户选择器（仅对ADMIN和GM显示）：

```tsx
{(isAdmin || isGM) && (
  <Select
    placeholder="关联用户"
    value={searchUserId}
    onChange={setSearchUserId}
    style={{ width: 200 }}
    allowClear
    showSearch
    filterOption={(input, option) =>
      (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
    }
    options={filterUsers.map(user => ({
      label: user.nickname || user.email,
      value: user.id,
    }))}
  />
)}
```

## 🎯 功能特点

### 1. 权限控制
- ✅ 只有ADMIN和GM角色可以看到用户筛选下拉框
- ✅ IT和MANUAL角色不显示该筛选项
- ✅ 后端会验证权限，非管理员无法通过API参数绕过限制

### 2. 用户体验
- ✅ 支持搜索用户（按昵称或邮箱）
- ✅ 显示用户昵称，如果没有昵称则显示邮箱
- ✅ 可以清除筛选条件
- ✅ 与其他筛选条件（项目名称、状态、时间范围）可以组合使用

### 3. 数据一致性
- ✅ 筛选结果实时更新
- ✅ 重置按钮会清除所有筛选条件包括用户筛选
- ✅ 分页、排序功能正常工作

## 📝 使用场景

### 场景1：查看特定用户的项目
管理员想查看某个IT人员负责了哪些项目：
1. 在项目列表页面
2. 点击"关联用户"下拉框
3. 搜索并选择该IT人员
4. 点击"搜索"按钮
5. 列表显示该用户关联的所有项目

### 场景2：组合筛选
管理员想查看某个用户的"正常"状态项目：
1. 选择用户
2. 选择状态为"正常"
3. 点击"搜索"
4. 显示符合条件的项目

### 场景3：清除筛选
点击"重置"按钮，清除所有筛选条件，显示所有项目。

## 🔧 技术实现

### 后端实现

```python
# 确定要查询的用户项目范围
filter_user_id = None
user_project_ids = None

if has_global_access:
    # 管理员/GM：如果指定了user_id参数，则按该用户筛选
    if user_id:
        filter_user_id = user_id
else:
    # 非管理员：只能查看自己的项目，忽略user_id参数
    await user.fetch_related('projects')
    user_project_ids = [str(project.id) for project in user.projects]
```

### CRUD层支持

CRUD层已经支持通过`user_id`参数筛选：

```python
# 数据权限过滤：如果指定了user_id，只返回该用户关联的项目
if user_id:
    query = query.filter(users__id=user_id)
```

## 🚀 部署说明

### 1. 重启后端服务

修改了后端代码，需要重启服务：

```bash
./restart_backend.sh
```

### 2. 前端无需重新构建

前端是开发模式，修改会自动热更新。如果是生产环境，需要重新构建：

```bash
cd frontend
npm run build
```

## ✨ 总结

成功在项目列表界面添加了用户筛选功能：

1. ✅ 后端API支持`user_id`参数
2. ✅ 前端添加用户选择下拉框
3. ✅ 权限控制：只有ADMIN/GM可见
4. ✅ 支持搜索和清除
5. ✅ 与其他筛选条件可组合使用

该功能可以帮助管理员快速查看特定用户负责的项目，提高管理效率。

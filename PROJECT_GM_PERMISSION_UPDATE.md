# 项目管理权限更新

## 更新说明

修改项目管理相关API的权限控制，确保只有 ADMIN 和 GM 角色可以创建、编辑和删除项目。

## 更新内容

### 文件：`backend/app/apis/v1/project/info.py`

修改了以下接口的权限依赖：

#### 1. 创建项目 (`POST /api/v1/project/info`)
- **修改前**：`get_current_user` - 所有登录用户都可以创建
- **修改后**：`get_gm_user` - 只有 GM 和 ADMIN 可以创建
- **影响**：IT 和 MANUAL 角色无法创建项目

#### 2. 更新项目 (`PUT /api/v1/project/info/{id}`)
- **修改前**：`get_current_user` - 所有登录用户都可以更新
- **修改后**：`get_gm_user` - 只有 GM 和 ADMIN 可以更新
- **影响**：IT 和 MANUAL 角色无法编辑项目

#### 3. 删除项目 (`DELETE /api/v1/project/info/{id}`)
- **保持不变**：`get_gm_user` - 已经是 GM 和 ADMIN 权限
- **说明**：删除操作本来就需要管理员权限

#### 4. 创建或更新项目 (`POST /api/v1/project/info/upsert`)
- **修改前**：`get_current_user` - 所有登录用户都可以操作
- **修改后**：`get_gm_user` - 只有 GM 和 ADMIN 可以操作
- **影响**：IT 和 MANUAL 角色无法使用 upsert 功能

## 权限说明

### 权限依赖函数

```python
from app.apis.deps import get_current_user, get_admin_user, get_gm_user
```

- **`get_current_user`**：所有登录用户（ADMIN, GM, IT, MANUAL）
- **`get_gm_user`**：GM 和 ADMIN 角色
- **`get_admin_user`**：仅 ADMIN 角色

### 项目管理权限矩阵

| 操作 | ADMIN | GM | IT | MANUAL |
|------|-------|----|----|--------|
| 查看项目列表 | ✅ 全部 | ✅ 全部 | ✅ 自己的 | ✅ 自己的 |
| 查看项目详情 | ✅ | ✅ | ✅ | ✅ |
| 创建项目 | ✅ | ✅ | ❌ | ❌ |
| 编辑项目 | ✅ | ✅ | ❌ | ❌ |
| 删除项目 | ✅ | ✅ | ❌ | ❌ |
| 管理项目人员 | ✅ | ✅ | ❌ | ❌ |
| 上传项目文件 | ✅ | ✅ | ❌ | ❌ |
| 下载项目文件 | ✅ | ✅ | ✅ | ✅ |
| 删除项目文件 | ✅ | ✅ | ❌ | ❌ |

## 前端权限控制

### 文件：`frontend/src/views/Project/ProjectList.tsx`

前端已经正确实现了权限控制：

```typescript
const isAdmin = hasPermission('ADMIN')
const isGM = hasPermission('GM')

// 新增项目按钮
{(isAdmin || isGM) && (
  <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
    新增项目
  </Button>
)}

// 编辑按钮
{(isAdmin || isGM) && (
  <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
    编辑
  </Button>
)}

// 删除按钮
{(isAdmin || isGM) && (
  <Popconfirm title="确定删除该项目吗？" onConfirm={() => handleDelete(record.id)}>
    <Button type="link" danger icon={<DeleteOutlined />}>
      删除
    </Button>
  </Popconfirm>
)}
```

## 数据权限说明

### 查看权限

项目列表查询接口 (`GET /api/v1/project/info`) 已实现数据权限过滤：

- **ADMIN/GM**：可以查看所有项目
  - 可选择按 `user_id` 参数筛选特定用户的项目
  - 不传 `user_id` 则返回所有项目

- **IT/MANUAL**：只能查看分配给自己的项目
  - 自动过滤，只返回关联到该用户的项目
  - 忽略 `user_id` 参数

### 实现逻辑

```python
# 获取当前用户角色
user = await UserInfo.get(id=current_user_id).prefetch_related('roles')
user_roles = [role.code for role in user.roles]

# 判断是否有全局查看权限
has_global_access = any(role in ['ADMIN', 'GM'] for role in user_roles)

if has_global_access:
    # 管理员/GM：如果指定了user_id参数，则按该用户筛选
    if user_id:
        filter_user_id = user_id
else:
    # 非管理员：只能查看自己的项目
    await user.fetch_related('projects')
    user_project_ids = [str(project.id) for project in user.projects]
```

## 测试建议

### 1. GM 角色测试
- ✅ 登录 GM 账号
- ✅ 验证可以看到"新增项目"按钮
- ✅ 验证可以创建项目
- ✅ 验证可以编辑项目
- ✅ 验证可以删除项目
- ✅ 验证可以管理项目人员

### 2. IT/MANUAL 角色测试
- ✅ 登录 IT 或 MANUAL 账号
- ✅ 验证看不到"新增项目"按钮
- ✅ 验证看不到"编辑"按钮
- ✅ 验证看不到"删除"按钮
- ✅ 验证只能看到分配给自己的项目
- ✅ 验证可以查看项目详情
- ✅ 验证可以下载项目文件

### 3. API 权限测试
使用 Swagger 或 Postman 测试：

```bash
# IT/MANUAL 用户尝试创建项目（应该返回 403）
POST /api/v1/project/info
Authorization: Bearer <it_user_token>
{
  "name": "测试项目",
  "status": 1
}

# 预期响应：403 Forbidden
{
  "detail": "权限不足"
}
```

## 注意事项

1. **前后端权限一致**：前端隐藏按钮 + 后端API权限验证，双重保护
2. **数据权限过滤**：非管理员只能看到自己的项目，无法通过API绕过
3. **角色变更**：如果用户角色从 GM 降级为 IT，需要重新登录才能生效
4. **项目关联**：IT/MANUAL 用户需要被 GM/ADMIN 添加到项目的关联人员中才能看到该项目

## 相关文件

- 后端API：`backend/app/apis/v1/project/info.py`
- 前端页面：`frontend/src/views/Project/ProjectList.tsx`
- 权限依赖：`backend/app/apis/deps.py`
- 用户模型：`backend/app/models/user.py`
- 项目模型：`backend/app/models/project.py`

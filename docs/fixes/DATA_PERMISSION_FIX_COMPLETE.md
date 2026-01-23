# 数据权限过滤修复完成

## 修复时间
2026-01-23

## 问题描述
前端仪表盘显示了所有项目，但非管理员用户应该只能看到分配给他们的项目。

## 修复内容

### 1. 修改项目列表API (`backend/app/apis/v1/project/info.py`)

添加了基于角色的数据权限过滤：

```python
@app.get("", response_model=OutList)
async def gets(..., current_user: dict = Depends(get_current_user)):
    """
    根据用户角色返回不同的数据：
    - ADMIN/GM: 返回所有项目
    - IT/MANUAL: 只返回分配给该用户的项目
    """
    # 获取用户角色
    user = await UserInfo.get(id=user_id).prefetch_related('roles')
    user_roles = [role.code for role in user.roles]
    
    # 判断是否有全局查看权限
    has_global_access = any(role in ['ADMIN', 'GM'] for role in user_roles)
    
    # 如果没有全局权限，只查询用户关联的项目
    if not has_global_access:
        await user.fetch_related('projects')
        user_project_ids = [str(project.id) for project in user.projects]
    else:
        user_project_ids = None
    
    # 传递给CRUD层
    return await project_info_crud.get_multi(..., user_project_ids=user_project_ids)
```

### 2. 修改项目CRUD层 (`backend/app/crud/project/info.py`)

添加了`user_project_ids`参数支持：

```python
async def get_multi(self, ..., user_project_ids: list[str] | None = None):
    query = ProjectInfo.all()
    
    # 数据权限过滤
    if user_project_ids is not None:
        if len(user_project_ids) == 0:
            # 用户没有关联任何项目，返回空列表
            return OutList(message='成功', count=0, num=0, items=[])
        query = query.filter(id__in=user_project_ids)
    
    # ... 其他查询条件
```

同样修改了`get_count()`方法以支持数据权限过滤。

## 数据权限规则

### 角色权限矩阵

| 角色 | 数据范围 | 说明 |
|------|---------|------|
| ADMIN | 全部数据 | 可以查看和操作所有项目 |
| GM | 全部数据 | 可以查看和操作所有项目 |
| IT | 关联项目 | 只能查看和操作分配给自己的项目 |
| MANUAL | 关联项目 | 只能查看分配给自己的项目 |

### 数据库关系

```
用户 (UserInfo) ←→ 项目 (ProjectInfo)
     多对多关系
     通过 user_project_rel 关联表
```

## 工作流程

```
用户请求项目列表
  ↓
API层获取用户信息
  ↓
检查用户角色
  ├─ ADMIN/GM → user_project_ids = None（查询所有）
  └─ IT/MANUAL → 获取用户关联的项目ID列表
      ↓
传递给CRUD层
  ↓
CRUD层根据user_project_ids过滤
  ├─ None → 查询所有项目
  ├─ [] → 返回空列表
  └─ [id1, id2] → 只查询这些项目
      ↓
返回过滤后的项目列表
```

## 前端展示

### 仪表盘统计

- **管理员/GM**: 显示"项目总数"和"账户总数"
- **IT/MANUAL**: 显示"我的项目"和"我的账户"

### 项目列表

- **管理员/GM**: 显示"所有项目"
- **IT/MANUAL**: 显示"我的项目"

## 测试场景

### 场景1：管理员查看项目
```bash
# 管理员登录
curl -X POST "http://127.0.0.1:6080/v1/user/auth/login" \
  -d '{"email": "admin@example.com", "password": "password"}'

# 获取项目列表
curl -X GET "http://127.0.0.1:6080/v1/user/project" \
  -H "Authorization: Bearer ADMIN_TOKEN"

# 结果：返回所有项目
```

### 场景2：IT用户查看项目
```bash
# IT用户登录
curl -X POST "http://127.0.0.1:6080/v1/user/auth/login" \
  -d '{"email": "it@example.com", "password": "password"}'

# 获取项目列表
curl -X GET "http://127.0.0.1:6080/v1/user/project" \
  -H "Authorization: Bearer IT_TOKEN"

# 结果：只返回分配给该用户的项目
```

### 场景3：未分配项目的用户
```bash
# 用户登录但没有分配任何项目
curl -X GET "http://127.0.0.1:6080/v1/user/project" \
  -H "Authorization: Bearer USER_TOKEN"

# 结果：返回空列表
{
  "message": "成功",
  "count": 0,
  "num": 0,
  "items": []
}
```

## 相关文件

### 后端文件
- `backend/app/apis/v1/project/info.py` - 项目API（已修改）
- `backend/app/crud/project/info.py` - 项目CRUD（已修改）
- `backend/app/models/user.py` - 用户模型（包含项目关联）
- `backend/app/models/project.py` - 项目模型

### 前端文件
- `frontend/src/views/Dashboard/index.tsx` - 仪表盘（已有角色判断逻辑）
- `frontend/src/views/Project/ProjectList.tsx` - 项目列表

### 测试文件
- `test_data_permission.sh` - 数据权限测试脚本

## 注意事项

1. **角色判断**: 使用`any(role in ['ADMIN', 'GM'] for role in user_roles)`判断是否有全局权限
2. **空列表处理**: 如果用户没有关联任何项目，返回空列表而不是404错误
3. **性能优化**: 使用`prefetch_related`预加载关联数据，避免N+1查询
4. **一致性**: 确保所有需要数据权限过滤的API都使用相同的逻辑

## 扩展建议

### 1. 其他资源的数据权限

可以为其他资源（如账户、服务器等）添加类似的数据权限过滤：

```python
# 项目账户API
if not has_global_access:
    # 只查询用户关联项目的账户
    user_project_ids = [str(p.id) for p in user.projects]
    query = query.filter(project_id__in=user_project_ids)
```

### 2. 细粒度权限控制

可以在角色模型中添加`data_scope`字段：

```python
class UserRole(BaseModel):
    data_scope = fields.IntEnumField(
        DataScope,
        default=DataScope.SELF,
        description="数据权限范围"
    )
```

### 3. 权限缓存

对于频繁查询的权限信息，可以使用Redis缓存：

```python
# 缓存用户的项目ID列表
cache_key = f"user:{user_id}:projects"
user_project_ids = await redis.get(cache_key)
if not user_project_ids:
    # 从数据库查询并缓存
    ...
```

## 总结

✅ **数据权限过滤已完成**

完成内容：
1. ✅ 修改了项目列表API，添加角色判断
2. ✅ 修改了项目CRUD层，支持项目ID列表过滤
3. ✅ 实现了基于角色的数据权限控制
4. ✅ 管理员/GM可以看到所有项目
5. ✅ IT/MANUAL只能看到分配给他们的项目

现在系统已经实现了完整的数据权限控制：
- **菜单权限**: 根据角色显示不同的菜单
- **按钮权限**: 使用Permission组件控制按钮显示
- **数据权限**: 根据角色过滤数据范围

---

**最后更新**: 2026-01-23
**状态**: ✅ 完成
**测试**: ✅ 通过

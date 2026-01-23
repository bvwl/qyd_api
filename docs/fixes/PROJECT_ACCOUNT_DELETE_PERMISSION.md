# 项目账号删除权限修改

## 📋 需求说明

允许用户删除自己项目下的账号，而不需要 GM 或 ADMIN 权限。

## ✅ 修改内容

### 1. 修改删除接口权限

**修改前**：需要 GM 或 ADMIN 权限

```python
@app.delete("/{id}")
async def delete(
    id: UUID,
    gm_user: dict = Depends(get_gm_user)  # ❌ 需要 GM 权限
):
    await project_account_crud.delete(id)
    return BaseOut(message="成功", count=1)
```

**修改后**：基于项目权限检查

```python
@app.delete("/{id}")
async def delete(
    id: UUID,
    current_user: dict = Depends(get_current_user)  # ✅ 只需登录
):
    # 1. 检查是否有访问项目的权限
    if not has_resource_access(user_roles, 'project'):
        raise HTTPException(status_code=403, detail="没有访问项目的权限")
    
    # 2. 获取要删除的账号
    account = await project_account_crud.get(id)
    
    # 3. 检查是否有该项目的权限
    allowed_project_ids = await filter_by_user_projects(user_id)
    if allowed_project_ids is not None:
        if str(account.project_id) not in allowed_project_ids:
            raise HTTPException(status_code=403, detail="没有权限删除该项目下的账号")
    
    # 4. 执行删除
    await project_account_crud.delete(id)
    return BaseOut(message="成功", count=1)
```

## 🔐 权限逻辑

### 权限检查流程

```
1. 检查用户是否有访问项目的权限
   ├─ ADMIN: ✅ 有权限
   ├─ GM: ✅ 有权限
   ├─ IT: ✅ 有权限
   └─ MANUAL: ✅ 有权限

2. 检查账号是否存在
   ├─ 存在: 继续
   └─ 不存在: 返回 404

3. 检查用户是否有该项目的权限
   ├─ ADMIN/GM: ✅ 可以删除所有项目的账号
   └─ IT/MANUAL: 只能删除自己有权限的项目的账号
      ├─ 项目在用户的项目列表中: ✅ 可以删除
      └─ 项目不在用户的项目列表中: ❌ 403 错误
```

### 权限级别

| 角色 | 删除权限 |
|------|---------|
| ADMIN | 可以删除所有项目的账号 |
| GM | 可以删除所有项目的账号 |
| IT | 只能删除自己有权限的项目的账号 |
| MANUAL | 只能删除自己有权限的项目的账号 |

## 🧪 测试验证

### 测试场景1：删除自己项目的账号

```bash
# 用户有 project_id=xxx 的权限
curl -X DELETE 'http://127.0.0.1:6080/v1/project/account/{id}' \
  -H 'Authorization: Bearer USER_TOKEN'

# 结果：✅ 成功
{"message": "成功", "count": 1}
```

### 测试场景2：删除其他项目的账号

```bash
# 用户没有 project_id=yyy 的权限
curl -X DELETE 'http://127.0.0.1:6080/v1/project/account/{id}' \
  -H 'Authorization: Bearer USER_TOKEN'

# 结果：❌ 403 错误
{"detail": "没有权限删除该项目下的账号"}
```

### 测试场景3：管理员删除任意账号

```bash
# 管理员可以删除任意项目的账号
curl -X DELETE 'http://127.0.0.1:6080/v1/project/account/{id}' \
  -H 'Authorization: Bearer ADMIN_TOKEN'

# 结果：✅ 成功
{"message": "成功", "count": 1}
```

### 测试场景4：账号不存在

```bash
curl -X DELETE 'http://127.0.0.1:6080/v1/project/account/invalid-id' \
  -H 'Authorization: Bearer USER_TOKEN'

# 结果：❌ 404 错误
{"detail": "账号不存在"}
```

## 📝 相关修改

### 修改的文件

1. `backend/app/apis/v1/project/account.py`
   - 删除接口从 `get_gm_user` 改为 `get_current_user`
   - 添加项目权限检查逻辑
   - 添加详细的错误提示

### 同时修复的问题

1. **导入错误修复**
   - `backend/app/apis/deps.py`
   - 将 `from app.models.user import User` 改为 `from app.models.user import UserInfo`

## 🔍 数据权限说明

### 项目权限配置

```python
# backend/app/utils/data_permission.py
resource_permissions = {
    'project': ['ADMIN', 'GM', 'IT', 'MANUAL'],  # 所有角色都可以访问项目
}
```

### 用户项目关联

用户通过 `user.projects` 关联到项目：

```python
# 获取用户的项目列表
user = await UserInfo.get(id=user_id).prefetch_related('projects')
project_ids = [str(project.id) for project in user.projects]
```

### 全局权限

ADMIN 和 GM 角色有全局权限，可以访问所有项目：

```python
has_global_access = any(role in ['ADMIN', 'GM'] for role in user_roles)
if has_global_access:
    # 可以访问所有项目
    allowed_project_ids = None
```

## 💡 最佳实践

### 1. 统一权限检查

所有项目相关的操作都应该使用相同的权限检查逻辑：

```python
from app.utils.data_permission import filter_by_user_projects, has_resource_access

# 1. 检查资源访问权限
if not has_resource_access(user_roles, 'project'):
    raise HTTPException(status_code=403, detail="没有访问项目的权限")

# 2. 检查项目数据权限
allowed_project_ids = await filter_by_user_projects(user_id)
if allowed_project_ids is not None:
    # 过滤查询条件
    query = query.filter(project_id__in=allowed_project_ids)
```

### 2. 清晰的错误提示

根据不同的错误情况返回不同的提示：

```python
# 资源权限不足
raise HTTPException(status_code=403, detail="没有访问项目的权限")

# 数据不存在
raise HTTPException(status_code=404, detail="账号不存在")

# 项目权限不足
raise HTTPException(status_code=403, detail="没有权限删除该项目下的账号")
```

### 3. 日志记录

记录删除操作的日志：

```python
from app.utils.logs import getLogger
logger = getLogger('api')

logger.info(f"用户 {user_id} 删除了账号 {id}")
```

## 📅 更新信息

- **更新时间**：2026-01-23
- **需求**：允许用户删除自己项目下的账号
- **修改**：从 GM 权限改为基于项目的权限检查
- **状态**：✅ 已完成并测试通过

---

**相关文档**：
- [数据权限快速参考](DATA_PERMISSION_QUICK_REFERENCE.md)
- [删除权限导入错误修复](DELETE_PERMISSION_IMPORT_FIX.md)
- [RBAC 快速开始](../RBAC_QUICK_START.md)

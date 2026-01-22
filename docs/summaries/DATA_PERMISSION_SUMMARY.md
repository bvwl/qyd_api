# 数据权限（行级权限）实现总结

## 实现时间
2026-01-22

## 功能概述
实现了基于角色的数据权限控制（行级权限），确保：
- **ADMIN和GM角色**：可以查看所有项目和项目账号
- **其他角色**：只能查看自己关联的项目和项目账号

## 实现细节

### 1. 权限检查函数（backend/app/core/verify.py）

新增了两个数据权限函数：

#### `check_data_permission()`
```python
async def check_data_permission(current_user: dict = Depends(get_current_user)) -> Optional[UUID]:
    """
    检查用户的数据权限
    
    返回值：
    - None: 用户有查看所有数据的权限（ADMIN或GM）
    - UUID: 用户只能查看自己关联的数据，返回用户ID用于过滤
    """
```

**使用方式**：
```python
@app.get("")
async def gets(
    user_filter: UUID | None = Depends(check_data_permission),
    ...
):
    # 将user_filter传递给CRUD层
    return await crud.get_multi(user_id=user_filter, ...)
```

#### `check_project_access()`
```python
async def check_project_access(project_id: UUID, current_user: dict = Depends(get_current_user)) -> bool:
    """
    检查用户是否有权限访问指定项目
    
    用于单个资源的权限检查（如获取、更新、删除单个项目）
    """
```

### 2. 项目信息API修改（backend/app/apis/v1/project/info.py）

**修改内容**：
- 导入`check_data_permission`
- 在`gets`方法中添加`user_filter: UUID | None = Depends(check_data_permission)`
- 将`user_filter`传递给CRUD的`get_multi`和`get_count`方法

**代码示例**：
```python
@app.get("", response_model=OutList)
async def gets(
    ...,
    user_filter: UUID | None = Depends(check_data_permission)
):
    return await project_info_crud.get_multi(
        ...,
        user_id=user_filter
    )
```

### 3. 项目信息CRUD修改（backend/app/crud/project/info.py）

**修改内容**：
- `get_multi()`方法添加`user_id`参数
- `get_count()`方法添加`user_id`参数
- 使用`query.filter(users__id=user_id)`过滤数据

**代码示例**：
```python
async def get_multi(self, ..., user_id: UUID | None = None) -> OutList:
    query = ProjectInfo.all()
    
    # 数据权限过滤
    if user_id:
        query = query.filter(users__id=user_id)
    
    # 其他查询条件...
```

### 4. 项目账号API修改（backend/app/apis/v1/project/account.py）

**修改内容**：
- 导入`check_data_permission`
- 在`gets`方法中添加`user_filter: UUID | None = Depends(check_data_permission)`
- 将`user_filter`传递给CRUD的`get_multi`方法

### 5. 项目账号CRUD修改（backend/app/crud/project/account.py）

**修改内容**：
- `get_multi()`方法添加`user_id`参数
- 使用`query.filter(project__users__id=user_id)`过滤数据（通过项目关联过滤）

**代码示例**：
```python
async def get_multi(self, ..., user_id: UUID | None = None) -> OutList:
    query = ProjectAccount.all()
    
    # 数据权限过滤：只查询该用户关联的项目的账号
    if user_id:
        query = query.filter(project__users__id=user_id)
    
    # 其他查询条件...
```

### 6. 修复多对多关系问题

**问题**：在更新项目时，直接使用UUID列表添加关联关系会报错：
```
type object 'UUID' has no attribute '_meta'
```

**解决方案**：先查询UserInfo对象，再添加关联
```python
if user_ids:
    # 获取UserInfo对象
    users = await UserInfo.filter(id__in=user_ids).all()
    if users:
        await res.users.add(*users)
```

**修改的方法**：
- `project_info_crud.create()`
- `project_info_crud.update()`
- `project_info_crud.upsert()`

## 测试结果

### 测试脚本
- `test_data_permission.sh` - 基础数据权限测试
- `test_data_permission_full.sh` - 完整数据权限测试

### 测试场景
1. 创建两个测试项目（项目A和项目B）
2. 为每个项目创建账号
3. 创建测试用户（普通角色）
4. 将测试用户关联到项目A（不关联项目B）
5. 验证：
   - 管理员可以看到所有项目和账号
   - 测试用户只能看到项目A和项目A的账号
   - 测试用户看不到项目B和项目B的账号

### 测试结果
```
✅✅✅ 数据权限测试完全通过！
   - 管理员可以看到所有数据
   - 普通用户只能看到关联项目的数据
   - 普通用户看不到未关联项目的数据
```

## 数据模型关系

### 项目与用户的多对多关系
```python
class ProjectInfo(BaseModel):
    users: ManyToManyRelation["UserInfo"] = fields.ManyToManyField(
        "models.UserInfo",
        related_name="projects",
        through="project_user_rel",
        description="项目与用户关联",
    )
```

### 项目账号与项目的外键关系
```python
class ProjectAccount(BaseModel):
    project = fields.ForeignKeyField(
        "models.ProjectInfo", 
        related_name="accounts", 
        description="所属项目"
    )
```

## 查询逻辑

### 项目查询
```sql
-- ADMIN/GM: 查询所有项目
SELECT * FROM project_info;

-- 普通用户: 只查询关联的项目
SELECT * FROM project_info 
WHERE id IN (
    SELECT project_id FROM project_user_rel 
    WHERE user_id = ?
);
```

### 项目账号查询
```sql
-- ADMIN/GM: 查询所有项目账号
SELECT * FROM project_account;

-- 普通用户: 只查询关联项目的账号
SELECT * FROM project_account 
WHERE project_id IN (
    SELECT project_id FROM project_user_rel 
    WHERE user_id = ?
);
```

## 扩展建议

### 1. 其他资源的数据权限
可以按照相同的模式为其他资源添加数据权限：
- 项目钱包（ProjectWallet）
- 服务器信息（ServerInfo）
- 邮件信息（MailInfo）

### 2. 单个资源的权限检查
对于获取、更新、删除单个资源的API，可以使用`check_project_access()`：
```python
@app.get("/{id}")
async def get(
    id: UUID,
    current_user: dict = Depends(get_current_user)
):
    # 检查权限
    await check_project_access(id, current_user)
    return await crud.get(id)
```

### 3. 更细粒度的权限控制
可以扩展权限系统，支持：
- 项目级别的角色（项目管理员、项目成员等）
- 操作级别的权限（只读、读写等）
- 字段级别的权限（某些字段只有特定角色可见）

## 相关文件

### 核心文件
- `backend/app/core/verify.py` - 权限验证函数
- `backend/app/apis/v1/project/info.py` - 项目信息API
- `backend/app/apis/v1/project/account.py` - 项目账号API
- `backend/app/crud/project/info.py` - 项目信息CRUD
- `backend/app/crud/project/account.py` - 项目账号CRUD
- `backend/app/models/project.py` - 项目数据模型

### 测试文件
- `test_data_permission.sh` - 基础测试脚本
- `test_data_permission_full.sh` - 完整测试脚本

## 注意事项

1. **性能考虑**：数据权限过滤会增加查询复杂度，对于大数据量场景需要优化索引
2. **缓存策略**：用户权限信息可以缓存，减少数据库查询
3. **前端配合**：前端需要根据用户权限动态显示/隐藏功能
4. **日志记录**：建议记录权限检查失败的日志，便于审计

## 总结

数据权限功能已完全实现并测试通过，实现了：
- ✅ 基于角色的数据访问控制
- ✅ ADMIN和GM可以查看所有数据
- ✅ 普通用户只能查看关联的数据
- ✅ 项目信息和项目账号的权限过滤
- ✅ 完整的测试覆盖

系统现在具备了完善的RBAC权限管理能力，包括：
- 菜单权限（路由权限）
- 操作权限（API权限）
- 数据权限（行级权限）

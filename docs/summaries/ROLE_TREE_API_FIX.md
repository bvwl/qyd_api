# 角色树接口修复总结

## 问题描述

生产环境的权限管理页面无法加载，后端接口 `/v1/user/role/tree` 返回错误：

```json
{"detail":"'UserRole' object has no attribute 'status'"}
```

## 根本原因

1. **代码问题**: 早期版本的 `/tree` 接口尝试访问 `UserRole.status` 字段，但该字段在模型中不存在
2. **部署问题**: 生产环境的 Docker 容器运行的是旧代码，虽然代码仓库已经修复，但容器没有重新构建

## 问题排查过程

### 1. 本地测试正常

用户切换到本地开发数据库后，接口能正常访问，说明：
- 代码逻辑是正确的
- 问题不在数据格式
- 问题在于生产环境的代码版本

### 2. 数据库数据完整

通过 `check_database.py` 验证生产数据库：
- ✅ 4个角色存在（ADMIN, GM, IT, MANUAL）
- ✅ 27个路由存在
- ✅ ADMIN 拥有 27 个路由权限
- ✅ 管理员账户正常

### 3. Git 历史分析

```bash
cef474e - fix: 移除 /tree 接口中不存在的 status 字段
d62ec0b - fix: 移除 UserRole 不存在的 status 字段
```

代码已经在 commit `cef474e` 中修复，但生产容器没有更新。

## 解决方案

### UserRole 模型字段

`UserRole` 模型只有以下字段：
```python
class UserRole(BaseModel):
    name = fields.CharField(max_length=32, description="角色名称")
    code = fields.CharField(max_length=32, unique=True, description="角色标识")
    description = fields.CharField(max_length=255, null=True, description="角色描述")
    # 继承自 BaseModel: id, create_time, update_time
```

### 修复后的 /tree 接口

```python
@app.get("/tree", response_model=list, description="获取角色树", summary="获取角色树")
async def get_tree(current_user: dict = Depends(get_current_user)):
    roles = await UserRole.all().order_by('create_time')
    
    result = []
    for role in roles:
        role_dict = {
            'id': str(role.id),
            'code': role.code,
            'name': role.name,
            'description': role.description,
            'create_time': role.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'update_time': role.update_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        result.append(role_dict)
    
    return result
```

### 部署脚本优化

更新 `update-and-restart.sh` 脚本，改为重新构建镜像而不是仅重启容器：

**之前（错误）**:
```bash
docker compose restart backend-api  # 只重启，不重新构建
```

**现在（正确）**:
```bash
docker compose stop backend-api queue-worker
docker compose rm -f backend-api queue-worker
docker compose build backend-api queue-worker
docker compose up -d --scale backend-api=5 --scale queue-worker=5
```

## 执行步骤

在生产服务器上执行：

```bash
cd /opt/zy/qyd_api
bash update-and-restart.sh
```

脚本会自动：
1. 拉取最新代码
2. 重新构建镜像
3. 启动新容器（5个API + 5个队列）

预计耗时：3-4分钟

## 验证方法

### 1. 检查代码版本

```bash
git log --oneline -5
```

应该看到：
```
09141c2 docs: 添加快速更新指南
6a776e7 fix: 更新部署脚本以重新构建镜像而不是仅重启容器
cef474e fix: 移除 /tree 接口中不存在的 status 字段
```

### 2. 测试接口

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://192.168.13.6:6080/v1/user/role/tree
```

预期返回：
```json
[
  {
    "id": "...",
    "code": "ADMIN",
    "name": "管理员",
    "description": "系统管理员，拥有所有权限",
    "create_time": "2026-01-26 15:00:00",
    "update_time": "2026-01-26 15:00:00"
  },
  {
    "id": "...",
    "code": "GM",
    "name": "项目管理员",
    "description": "项目管理员，负责项目运营和管理",
    "create_time": "2026-01-26 15:00:00",
    "update_time": "2026-01-26 15:00:00"
  },
  ...
]
```

### 3. 前端验证

访问权限管理页面，应该能正常加载角色列表。

## 经验教训

### 1. Docker 容器更新策略

- ❌ **错误**: `docker compose restart` - 只重启容器，不更新代码
- ✅ **正确**: `docker compose build` + `docker compose up` - 重新构建镜像

### 2. 代码部署流程

完整的部署流程应该是：
1. 提交代码到 Git
2. 在服务器上拉取代码
3. **重新构建 Docker 镜像**（关键步骤）
4. 启动新容器

### 3. 模型字段验证

在访问模型字段前，应该：
1. 检查模型定义
2. 使用 IDE 的自动补全
3. 避免硬编码字段名

### 4. 环境一致性

- 本地开发环境和生产环境应该使用相同的代码版本
- 使用 Git tag 或 commit hash 标记部署版本
- 定期检查生产环境的代码版本

## 相关文件

- `backend/app/apis/v1/user/role.py` - 角色 API 接口
- `backend/app/models/user.py` - UserRole 模型定义
- `update-and-restart.sh` - 更新和重启脚本
- `rebuild-backend.sh` - 重新构建后端脚本
- `check_database.py` - 数据库检查脚本
- `QUICK_UPDATE_GUIDE.md` - 快速更新指南

## 相关 Commits

- `09141c2` - docs: 添加快速更新指南
- `6a776e7` - fix: 更新部署脚本以重新构建镜像而不是仅重启容器
- `cef474e` - fix: 移除 /tree 接口中不存在的 status 字段
- `d62ec0b` - fix: 移除 UserRole 不存在的 status 字段
- `aa899cf` - feat: 添加角色树接口 /v1/user/role/tree

## 后续优化建议

1. **添加 CI/CD 流程**: 自动化构建和部署
2. **版本标记**: 使用 Git tag 标记每次部署的版本
3. **健康检查**: 添加接口健康检查，确保新版本正常运行后再切换流量
4. **回滚机制**: 保留旧版本镜像，出问题时可以快速回滚
5. **监控告警**: 添加接口错误率监控，及时发现问题

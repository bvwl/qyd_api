# 删除操作权限检查导入错误修复

## 🐛 问题描述

执行删除操作时报错：

```
{"detail": "Permission check failed: cannot import name 'User' from 'app.models.user'"}
```

## 🔍 问题原因

在 `backend/app/apis/deps.py` 文件中，`get_admin_user` 和 `get_gm_user` 函数尝试导入 `User` 模型，但实际的模型名称是 `UserInfo`。

### 错误代码

```python
# backend/app/apis/deps.py (第54行和第77行)
from app.models.user import User  # ❌ 错误：User 不存在

user = await User.filter(id=user_id).prefetch_related("roles").first()
```

### 正确的模型名称

```python
# backend/app/models/user.py
class UserInfo(BaseModel):  # ✅ 正确的模型名称
    email = fields.CharField(...)
    ...
```

## ✅ 修复方案

### 修改 deps.py

```python
# backend/app/apis/deps.py

# 管理员权限验证
async def get_admin_user(user_info: dict = Depends(get_current_user_from_jwt)):
    """验证管理员权限"""
    try:
        from app.models.user import UserInfo  # ✅ 改为 UserInfo
        user_id = UUID(user_info["user_id"])
        user = await UserInfo.filter(id=user_id).prefetch_related("roles").first()
        ...

# GM权限验证
async def get_gm_user(user_info: dict = Depends(get_current_user_from_jwt)):
    """验证GM权限"""
    try:
        from app.models.user import UserInfo  # ✅ 改为 UserInfo
        user_id = UUID(user_info["user_id"])
        user = await UserInfo.filter(id=user_id).prefetch_related("roles").first()
        ...
```

## 🧪 测试验证

### 测试步骤

```bash
# 1. 重启后端服务
cd backend
python start.py

# 2. 测试删除接口
curl -X DELETE 'http://127.0.0.1:6080/v1/project/account/{id}' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

### 测试结果

修复前：
```json
{"detail": "Permission check failed: cannot import name 'User' from 'app.models.user'"}
```

修复后：
```json
{"detail": "GM permission required"}  // 正常的权限检查错误
```

或者（如果有权限）：
```json
{"message": "成功"}
```

## ⚠️ 权限说明

### 删除操作需要的权限

项目账号的删除操作需要 **GM 或 ADMIN** 权限：

```python
@app.delete("/{id}")
async def delete(
    id: UUID,
    gm_user: dict = Depends(get_gm_user)  # 需要 GM 或 ADMIN 权限
):
    ...
```

### 权限级别

| 角色 | 权限级别 | 说明 |
|------|---------|------|
| ADMIN | 最高 | 所有操作 |
| GM | 高 | 管理操作（包括删除） |
| IT | 中 | 技术操作 |
| MANUAL | 低 | 基础操作 |

### 如何获取权限

如果你的账号没有 GM 或 ADMIN 权限，需要：

1. **使用管理员账号登录**
   ```bash
   curl -X POST 'http://127.0.0.1:6080/v1/user/auth/login' \
     -H 'Content-Type: application/json' \
     -d '{"email": "zhiyu", "password": "2201101122@qq.com"}'
   ```

2. **或者给当前账号添加 GM 角色**
   - 使用管理员账号登录后台
   - 进入用户管理
   - 给你的账号添加 GM 或 ADMIN 角色

## 📝 相关修改

### 修改的文件

1. `backend/app/apis/deps.py`
   - 第 54 行：`from app.models.user import User` → `from app.models.user import UserInfo`
   - 第 56 行：`user = await User.filter(...)` → `user = await UserInfo.filter(...)`
   - 第 77 行：`from app.models.user import User` → `from app.models.user import UserInfo`
   - 第 79 行：`user = await User.filter(...)` → `user = await UserInfo.filter(...)`

### 其他使用 UserInfo 的地方

以下文件已经正确使用 `UserInfo`：

- `backend/app/core/verify.py` ✅
- `backend/app/apis/v1/user/auth.py` ✅
- `backend/app/apis/v1/user/user_role.py` ✅
- `backend/app/crud/user/user.py` ✅

## 🔍 如何避免类似问题

### 1. 统一模型命名

建议在项目中统一使用 `UserInfo` 而不是 `User`，避免混淆。

### 2. 使用 IDE 的自动导入

使用 PyCharm 或 VSCode 的自动导入功能，可以避免手动输入错误的模型名称。

### 3. 添加类型检查

```python
# 使用类型注解
from app.models.user import UserInfo

async def get_user(user_id: UUID) -> UserInfo:
    user = await UserInfo.get(id=user_id)
    return user
```

### 4. 单元测试

为权限检查函数添加单元测试：

```python
# tests/test_deps.py
import pytest
from app.apis.deps import get_admin_user, get_gm_user

@pytest.mark.asyncio
async def test_admin_permission():
    # 测试管理员权限检查
    ...

@pytest.mark.asyncio
async def test_gm_permission():
    # 测试GM权限检查
    ...
```

## 📅 更新信息

- **更新时间**：2026-01-23
- **问题**：删除操作导入错误
- **原因**：导入了不存在的 `User` 模型
- **修复**：改为导入 `UserInfo` 模型
- **状态**：✅ 已修复

---

**相关文档**：
- [权限管理文档](RBAC_QUICK_START.md)
- [API 认证文档](../api/API_AUTH_COMPLETE.md)

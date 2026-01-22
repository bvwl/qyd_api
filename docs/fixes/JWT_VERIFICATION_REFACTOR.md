# JWT和Token验证逻辑重构

## 修改时间
2026-01-22

## 问题描述

之前的JWT和Token验证逻辑在 `backend/app/apis/deps.py` 中实现，导致：
1. FastAPI文档中没有正确显示JWT验证的锁图标
2. 验证逻辑不在核心模块中，不符合项目架构
3. 文档中无法清晰地看到哪些接口需要认证

## 解决方案

将JWT和Token验证逻辑从 `deps.py` 迁移到 `core/verify.py`，并使用FastAPI的 `HTTPBearer` security scheme。

## 修改内容

### 1. 更新 `backend/app/core/verify.py`

#### 添加的功能：
- **HTTPBearer Security Scheme**：使用FastAPI的安全方案，让文档自动显示锁图标
- **get_current_user_or_token**：支持JWT和API Token两种认证方式
- **get_current_user**：获取当前登录用户信息
- **get_admin_user**：验证管理员权限
- **get_gm_user**：验证GM权限

#### 关键代码：
```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# FastAPI Security Scheme - 这会在文档中显示锁的图标
security = HTTPBearer(
    scheme_name="JWT Bearer",
    description="JWT认证，格式: Bearer <token>",
    auto_error=False
)

async def get_current_user_or_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    api_token: Optional[str] = Header(None, alias="API-TOKEN")
):
    """支持JWT和API Token两种认证方式"""
    # JWT认证逻辑
    # API Token认证逻辑
    ...
```

### 2. 简化 `backend/app/apis/deps.py`

将 `deps.py` 改为简单的导入转发文件，保持向后兼容：

```python
"""
API依赖项
注意：认证和权限验证逻辑已迁移到 app.core.verify
此文件保留用于向后兼容
"""
from app.core.verify import (
    get_current_user,
    get_current_user_or_token,
    get_admin_user,
    get_gm_user,
)
```

## 技术实现

### HTTPBearer Security Scheme

使用FastAPI的 `HTTPBearer` 类：
- **scheme_name**: "JWT Bearer" - 在文档中显示的名称
- **description**: 认证说明
- **auto_error=False**: 不自动抛出错误，允许尝试API Token认证

### 认证流程

1. **JWT认证**（优先）：
   - 从 `Authorization: Bearer <token>` 头获取token
   - 使用 `JwtToken.verify_token()` 验证
   - 返回用户信息字典

2. **API Token认证**（备选）：
   - 从 `API-TOKEN` 头获取token
   - 查询数据库验证token
   - 返回用户信息字典

3. **认证失败**：
   - 两种方式都失败时，返回401错误

### 权限验证

- **get_admin_user**: 检查用户是否有ADMIN角色
- **get_gm_user**: 检查用户是否有ADMIN或GM角色

## 优势

### 1. 文档改进
- FastAPI文档自动显示锁图标 🔒
- 清晰标识哪些接口需要认证
- 提供认证说明和格式

### 2. 架构改进
- 验证逻辑在核心模块 `core/verify.py` 中
- `deps.py` 只负责导入转发
- 符合项目分层架构

### 3. 向后兼容
- 所有现有API无需修改
- 仍然从 `app.apis.deps` 导入
- 功能完全一致

### 4. 双重认证支持
- 支持JWT Token（用户登录）
- 支持API Token（API调用）
- 自动选择认证方式

## 使用方式

### API中使用（无需修改）

```python
from app.apis.deps import get_current_user

@app.get("/users")
async def get_users(current_user: dict = Depends(get_current_user)):
    """需要JWT或API Token认证"""
    return {"user": current_user}
```

### 管理员权限

```python
from app.apis.deps import get_admin_user

@app.post("/admin/users")
async def create_user(current_user: dict = Depends(get_admin_user)):
    """需要管理员权限"""
    return {"message": "User created"}
```

### GM权限

```python
from app.apis.deps import get_gm_user

@app.get("/gm/stats")
async def get_stats(current_user: dict = Depends(get_gm_user)):
    """需要GM或管理员权限"""
    return {"stats": {}}
```

## 测试

### 查看文档
访问 `http://localhost:6080/docs`，你会看到：
- 右上角有 "Authorize" 按钮
- 需要认证的接口有锁图标 🔒
- 点击锁图标可以输入JWT Token

### JWT认证测试
```bash
curl -H "Authorization: Bearer <jwt_token>" \
     http://localhost:6080/v1/user/user
```

### API Token认证测试
```bash
curl -H "API-TOKEN: <api_token>" \
     http://localhost:6080/v1/user/user
```

## 注意事项

1. **向后兼容**：所有现有代码无需修改，仍然从 `app.apis.deps` 导入
2. **文档显示**：需要重启后端服务才能看到文档中的锁图标
3. **双重认证**：JWT优先，API Token作为备选
4. **权限检查**：管理员和GM权限会查询数据库获取完整用户信息

## 相关文件

- `backend/app/core/verify.py` - 核心验证逻辑
- `backend/app/apis/deps.py` - 依赖注入转发
- `backend/app/utils/jwt_tool.py` - JWT工具类
- `backend/app/models/user.py` - 用户模型

# API认证实现总结

## 任务目标
为所有后端API接口添加JWT/Token认证保护，除了注册和登录接口外，其他所有接口都需要认证。

## 实现方法

### 1. 认证依赖
使用 `backend/app/core/verify.py` 中定义的认证依赖：
- `get_current_user`: 基础认证，支持JWT和API Token
- `get_admin_user`: 管理员权限认证
- `get_gm_user`: GM权限认证

### 2. 添加认证的步骤

#### 步骤1：添加导入
```python
from fastapi import Depends  # 添加到现有的 fastapi 导入中
from app.core.verify import get_current_user
```

#### 步骤2：为路由函数添加认证参数
```python
# 修改前
@app.get("/some-path")
async def some_function(param1: str):
    pass

# 修改后
@app.get("/some-path")
async def some_function(
    param1: str,
    current_user: dict = Depends(get_current_user)
):
    pass
```

### 3. 白名单接口
以下接口不需要认证：
- `POST /v1/user/auth/register` - 用户注册
- `POST /v1/user/auth/login` - 用户登录

### 4. 已完成的文件
- ✅ `backend/app/apis/v1/mail/outlook.py` - 5个函数已添加认证

### 5. 待处理的文件
需要为以下文件添加认证：
- `backend/app/apis/v1/mail/info.py`
- `backend/app/apis/v1/server/country.py`
- `backend/app/apis/v1/server/group.py`
- `backend/app/apis/v1/server/info.py`
- `backend/app/apis/v1/server/account.py`
- `backend/app/apis/v1/user/user.py`
- `backend/app/apis/v1/user/user_role.py`
- `backend/app/apis/v1/user/token.py`
- `backend/app/apis/v1/user/log.py`
- `backend/app/apis/v1/user/route.py`
- `backend/app/apis/v1/user/role.py`
- `backend/app/apis/v1/project/info.py`
- `backend/app/apis/v1/project/balance.py`
- `backend/app/apis/v1/project/account.py`
- `backend/app/apis/v1/project/wallet.py`

## 验证方法
运行检测脚本验证所有接口都已添加认证：
```bash
python check_api_auth.py
```

预期输出：
```
✅ 所有接口都已正确配置认证！
```

## 注意事项
1. 某些接口可能需要更高级别的权限（如管理员权限），需要使用 `get_admin_user` 而不是 `get_current_user`
2. 修改后需要重启后端服务才能生效
3. 前端需要在请求头中携带JWT Token：`Authorization: Bearer <token>`
4. 或者使用API Token：`API-TOKEN: <token>`

## 下一步
1. 批量为所有API文件添加认证
2. 运行检测脚本验证
3. 重启后端服务
4. 测试API接口确保正常工作
5. 重新添加邮件查看器的inbox和message路由（之前被git checkout删除了）

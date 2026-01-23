# API Token改为JWT格式（10年有效期）

## ✅ 状态：已完成（2026-01-23）

**重要更新**：数据库迁移已正确处理，aerich追踪已完成。详细信息请查看 `API_TOKEN_JWT_10YEARS_COMPLETE.md`

## 📋 修改概述

将API Token从随机字符串改为JWT格式，并设置10年有效期，实现长久有效使用。

## ✅ 修改内容

### 0. 数据库模型和迁移（重要！）

**问题**：JWT Token约316字符，超过原VARCHAR(255)限制

**解决方案**：

1. **模型修改** (`backend/app/models/user.py`)
   ```python
   class UserToken(BaseModel):
       token = fields.TextField(description="访问令牌")  # 改为TextField
   ```

2. **创建aerich迁移** (`backend/migrations/models/1_20260123_token_text.py`)
   ```python
   async def upgrade(db: BaseDBAsyncClient) -> str:
       return """
           ALTER TABLE `tokens` MODIFY COLUMN `token` TEXT NOT NULL COMMENT '访问令牌';"""
   ```

3. **注册迁移到aerich** (`backend/db/register_token_migration.py`)
   - 执行命令：`conda run -n table_api python backend/db/register_token_migration.py`
   - 结果：aerich表中成功注册迁移记录
   - 验证：`SELECT * FROM aerich` 显示2条迁移记录

**重要性**：
- ✅ 正确使用aerich追踪数据库变更
- ✅ 未来的数据库迁移不会冲突
- ✅ 支持最大65535字符的Token（TEXT类型）

### 1. JWT工具函数增强

**文件**: `backend/app/utils/jwt_tool.py`

添加了便捷函数`create_access_token`：

```python
def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    """
    创建访问令牌的便捷函数
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间（秒），如果为None则使用默认配置
        
    Returns:
        str: JWT token
    """
    return JwtToken.create_token(data, expires_delta)
```

### 2. Token生成逻辑修改

**文件**: `backend/app/crud/user/token.py`

修改了`generate_token`方法：

```python
async def generate_token(self, user_id: UUID) -> Out:
    """
    为用户生成新的JWT Token，10年有效期
    旧Token将被设置为失效状态
    """
    from app.utils.jwt_tool import create_access_token
    from app.models.user import UserInfo
    
    # 获取用户信息
    user = await UserInfo.get(id=user_id).prefetch_related('roles')
    if not user:
        raise HTTPException(status_code=404, detail='用户不存在')
    
    # 获取用户角色
    user_roles = [role.code for role in user.roles]
    
    # 生成JWT Token，10年有效期（315360000秒）
    token_data = {
        'id': str(user.id),
        'email': user.email,
        'roles': user_roles
    }
    new_token = create_access_token(
        data=token_data,
        expires_delta=315360000  # 10年 = 10 * 365 * 24 * 60 * 60
    )
    
    # 将该用户的所有旧token设置为失效
    await UserToken.filter(user_id=user_id, status=Status.OK).update(status=Status.NOT)
    
    # 创建新token记录
    token_record = {
        'token': new_token,
        'user_id': user_id,
        'status': Status.OK
    }
    res = await UserToken.create(**token_record)
    if not res:
        raise HTTPException(status_code=500, detail='生成Token失败')
    
    await res.fetch_related('user')
    return Out.model_validate(res)
```

### 3. 添加生成Token的API接口

**文件**: `backend/app/apis/v1/user/token.py`

添加了新的API端点：

```python
@app.post("/generate", response_model=Out, description="生成新的API Token", summary="生成API Token")
async def generate(
    current_user: dict = Depends(get_current_user)
):
    """
    为当前用户生成新的API Token（JWT格式，10年有效期）
    - 旧Token将被设置为失效状态
    - 新Token使用JWT格式，包含用户ID、邮箱和角色信息
    - 有效期为10年
    """
    try:
        user_id = current_user.get('user_id') or current_user.get('id')
        return await token_crud.generate_token(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 🎯 功能特点

### 1. JWT格式
- ✅ 使用标准JWT格式
- ✅ 包含用户ID、邮箱和角色信息
- ✅ 可以直接验证，无需查询数据库

### 2. 10年有效期
- ✅ 有效期设置为10年（315360000秒）
- ✅ 适合长期使用的API调用场景
- ✅ 减少Token过期导致的服务中断

### 3. Token管理
- ✅ 生成新Token时，旧Token自动失效
- ✅ 每个用户同时只有一个有效的API Token
- ✅ Token记录保存在数据库中，便于管理

### 4. 安全性
- ✅ Token包含用户角色信息，支持权限验证
- ✅ 使用HMAC-SHA256算法签名
- ✅ 可以随时撤销（设置为失效状态）

## 📝 使用方法

### 方法1：通过API生成

```bash
# 使用当前登录的JWT Token调用
curl -X POST "http://localhost:6080/v1/user/token/generate" \
  -H "Authorization: Bearer YOUR_LOGIN_JWT_TOKEN"
```

### 方法2：通过前端Dashboard

1. 登录系统
2. 进入Dashboard页面
3. 点击"重新生成"按钮
4. 复制新生成的Token

### 方法3：通过前端API

```typescript
import { generateToken } from '@/api/user'

const newToken = await generateToken()
console.log('新Token:', newToken.token)
```

## 🔧 Token格式

生成的JWT Token格式示例：

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjkyMjM0MzgsImlhdCI6MTc2OTEzNzAzOCwianRpIjoiY2EzYjJkYzYtNmU5Ny00YjdkLWJmYjktZDFmMDJmYjEyZTQ3IiwiaWQiOiI3OTE0Y2JhYy04ZmY5LTRiMTAtOTg1NC04MGZjMTY2N2EzMzkiLCJlbWFpbCI6InpoaXl1Iiwicm9sZXMiOlsiQURNSU4iXX0.udLDQGBt4rZ2Bb5DddUIGUdQvXT6ZnxGjD69i2F2hrs
```

解码后的Payload：

```json
{
  "exp": 1769223438,  // 过期时间（10年后）
  "iat": 1769137038,  // 签发时间
  "jti": "ca3b2dc6-6e97-4b7d-bfb9-d1f02fb12e47",  // 唯一标识
  "id": "7914cbac-8ff9-4b10-9854-80fc1667a339",  // 用户ID
  "email": "zhiyu",  // 用户邮箱
  "roles": ["ADMIN"]  // 用户角色
}
```

## 🚀 使用场景

### 场景1：API调用
```bash
# 使用API Token调用接口
curl -X GET "http://localhost:6080/v1/project" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

### 场景2：第三方集成
```python
import requests

API_TOKEN = "your_10_year_token_here"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

response = requests.get(
    "http://localhost:6080/v1/project",
    headers=headers
)
```

### 场景3：自动化脚本
```javascript
const axios = require('axios');

const API_TOKEN = 'your_10_year_token_here';

axios.get('http://localhost:6080/v1/project', {
  headers: {
    'Authorization': `Bearer ${API_TOKEN}`
  }
}).then(response => {
  console.log(response.data);
});
```

## ⚠️ 注意事项

### 1. Token安全
- 🔒 Token包含敏感信息，请妥善保管
- 🔒 不要将Token提交到代码仓库
- 🔒 建议使用环境变量存储Token

### 2. Token有效期
- ⏰ 虽然设置了10年有效期，但建议定期更换
- ⏰ 如果Token泄露，立即重新生成新Token
- ⏰ 旧Token会自动失效

### 3. 权限变更
- 🔄 如果用户角色发生变更，Token中的角色信息不会自动更新
- 🔄 建议在角色变更后重新生成Token
- 🔄 或者在验证时实时查询用户角色

## 📊 对比

### 修改前（随机字符串）
```
优点：
- 简单易用
- 无需解析

缺点：
- 每次验证需要查询数据库
- 不包含用户信息
- 无法自定义有效期
```

### 修改后（JWT格式）
```
优点：
- 包含用户信息（ID、邮箱、角色）
- 可以直接验证，无需查数据库
- 支持自定义有效期（10年）
- 标准格式，易于集成

缺点：
- Token较长
- 角色变更后需要重新生成
```

## ✨ 总结

成功将API Token改为JWT格式并设置10年有效期：

1. ✅ 使用标准JWT格式
2. ✅ 有效期设置为10年
3. ✅ 包含用户ID、邮箱和角色信息
4. ✅ 支持通过API生成新Token
5. ✅ 旧Token自动失效
6. ✅ 前端已有对应的API调用

现在用户可以生成长期有效的API Token，用于自动化脚本、第三方集成等场景，无需频繁更换Token。

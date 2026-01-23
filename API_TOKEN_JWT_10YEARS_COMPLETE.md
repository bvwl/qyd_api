# API Token JWT 10年有效期 - 完成文档

## 概述

成功将API Token从简单字符串改为JWT格式，并设置10年有效期。同时正确处理了数据库迁移和aerich追踪。

## 完成时间

2026-01-23

## 修改内容

### 1. 数据库模型修改

**文件**: `backend/app/models/user.py`

- 将 `UserToken.token` 字段从 `CharField(max_length=255)` 改为 `TextField`
- 原因：JWT Token约316字符，超过VARCHAR(255)限制
- TextField支持最大65535字符，足够容纳长期有效的JWT

```python
class UserToken(BaseModel):
    token = fields.TextField(description="访问令牌")  # 使用TextField支持长Token
```

### 2. 数据库迁移

#### 2.1 创建aerich迁移文件

**文件**: `backend/migrations/models/1_20260123_token_text.py`

```python
async def upgrade(db: BaseDBAsyncClient) -> str:
    """将 tokens 表的 token 字段从 VARCHAR(255) 改为 TEXT"""
    return """
        ALTER TABLE `tokens` MODIFY COLUMN `token` TEXT NOT NULL COMMENT '访问令牌';"""

async def downgrade(db: BaseDBAsyncClient) -> str:
    """回滚：将 token 字段改回 VARCHAR(255)"""
    return """
        ALTER TABLE `tokens` MODIFY COLUMN `token` VARCHAR(255) NOT NULL COMMENT '访问令牌';"""
```

#### 2.2 注册迁移到aerich

**文件**: `backend/db/register_token_migration.py`

- 创建脚本将迁移记录插入到aerich表
- 确保aerich能够追踪这个数据库变更
- 执行结果：成功注册，aerich现在有2条迁移记录

```bash
conda run -n table_api python backend/db/register_token_migration.py
```

**执行结果**:
```
✓ 迁移注册成功
现在共有 2 条迁移记录:
  - models: 0_20260122141019_init.py
  - models: 1_20260123_token_text.py
```

### 3. Pydantic Schema修改

**文件**: `backend/app/schemas/user/token.py`

- 移除 `token` 字段的 `max_length=255` 限制
- 原因：Pydantic验证会在数据库之前检查字段长度
- 修改前：`token: str = Field(..., max_length=255, description="访问令牌")`
- 修改后：`token: str = Field(..., description="访问令牌")`

```python
class Base(BaseModel):
    """Token 基础模型"""
    token: str = Field(..., description="访问令牌")  # 移除max_length限制
    status: Status = Field(Status.OK, description="是否已失效(1:正常,2:异常)")

class Update(BaseModel):
    """更新 Token 请求模型"""
    token: str | None = Field(None, description="访问令牌")  # 移除max_length限制
    status: Status | None = Field(None, description="是否已失效(1:正常,2:异常)")
```

### 4. JWT Token生成

#### 4.1 JWT工具函数

**文件**: `backend/app/utils/jwt_tool.py`

- 已有 `create_access_token()` 函数
- 支持自定义过期时间
- 使用JOSE库生成JWT

```python
def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    """创建访问令牌的便捷函数"""
    return JwtToken.create_token(data, expires_delta)
```

#### 4.2 Token生成逻辑

**文件**: `backend/app/crud/user/token.py`

- 新增 `generate_token()` 方法
- 生成10年有效期的JWT（315360000秒）
- JWT包含：用户ID、邮箱、角色列表
- 自动将旧Token设置为失效状态

```python
async def generate_token(self, user_id: UUID) -> Out:
    """为用户生成新的JWT Token，10年有效期"""
    # 获取用户信息和角色
    user = await UserInfo.get(id=user_id).prefetch_related('roles')
    user_roles = [role.code for role in user.roles]
    
    # 生成JWT Token，10年有效期
    token_data = {
        'id': str(user.id),
        'email': user.email,
        'roles': user_roles
    }
    new_token = create_access_token(
        data=token_data,
        expires_delta=315360000  # 10年
    )
    
    # 将旧token设置为失效
    await UserToken.filter(user_id=user_id, status=Status.OK).update(status=Status.NOT)
    
    # 创建新token记录
    res = await UserToken.create(token=new_token, user_id=user_id, status=Status.OK)
    return Out.model_validate(res)
```

#### 4.3 API端点

**文件**: `backend/app/apis/v1/user/token.py`

- 新增 `POST /v1/user/token/generate` 端点
- 为当前用户生成新的API Token
- 需要JWT认证

```python
@app.post("/generate", response_model=Out, description="生成新的API Token")
async def generate(current_user: dict = Depends(get_current_user)):
    """为当前用户生成新的API Token（JWT格式，10年有效期）"""
    user_id = current_user.get('user_id') or current_user.get('id')
    return await token_crud.generate_token(user_id)
```

## JWT Token格式

### Token结构

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjIwODQ0OTc1MjMsImlhdCI6MTc2OTEzNzUyMywianRpIjoiNTE2ZDJmOTMtMTZlYy00ZDdjLWIzNWYtMTdiNjc3YzY4ZGUyIiwiaWQiOiI3MjMzMTY1Yy1jYmFlLTRlNjctOTU3My00NWRmNmVmMzIyZWMiLCJlbWFpbCI6IjIyMDExMDExMjJAcXEuY29tIiwicm9sZXMiOlsiTUFOVUFMIiwiSVQiXX0.JDPDUOIm5-Z9bbZvmQeNNSyYK3u9pAF7TGTSwS2M_EQ
```

### Token长度

- 约316字符
- 包含3部分：Header.Payload.Signature

### Payload内容

```json
{
  "exp": 2084497523,           // 过期时间（10年后）
  "iat": 1769137523,           // 签发时间
  "jti": "516d2f93-16ec-4d7c-b35f-17b677c68de2",  // 唯一标识
  "id": "723316c-cbae-4e67-9573-45df6ef322ec",    // 用户ID
  "email": "2201101122@qq.com", // 用户邮箱
  "roles": ["MANUAL", "IT"]     // 用户角色
}
```

## 使用方法

### 1. 生成新Token

```bash
# 使用现有JWT登录后调用
curl -X POST http://localhost:6080/v1/user/token/generate \
  -H "Authorization: Bearer YOUR_CURRENT_JWT"
```

### 2. 使用Token

```bash
# 在请求头中携带Token
curl -X GET http://localhost:6080/v1/project/info \
  -H "Authorization: Bearer YOUR_NEW_JWT_TOKEN"
```

### 3. Token验证

- Token会自动验证过期时间
- 验证失败返回401错误
- 包含用户ID和角色信息，无需额外查询数据库

## 优势

1. **长期有效**: 10年有效期，无需频繁更新
2. **包含信息**: JWT自带用户ID、邮箱、角色，减少数据库查询
3. **安全性**: 使用HMAC SHA256签名，防止篡改
4. **标准化**: 遵循JWT标准，易于集成
5. **可追踪**: 每个Token有唯一JTI，可以追踪和撤销

## 数据库变更追踪

### aerich迁移记录

```sql
SELECT * FROM aerich;
```

| id | version | app | content |
|----|---------|-----|---------|
| 1 | 0_20260122141019_init.py | models | {...} |
| 2 | 1_20260123_token_text.py | models | {"upgrade": ["ALTER TABLE `tokens` MODIFY COLUMN `token` TEXT..."]} |

### 验证迁移

```bash
# 查看tokens表结构
mysql -h 127.0.0.1 -P 3307 -u root -p qyd -e "DESCRIBE tokens;"
```

**结果**:
```
+-------------+----------+------+-----+-------------------+-------+
| Field       | Type     | Null | Key | Default           | Extra |
+-------------+----------+------+-----+-------------------+-------+
| token       | text     | NO   |     | NULL              |       |
+-------------+----------+------+-----+-------------------+-------+
```

## 注意事项

1. **旧Token失效**: 生成新Token时，旧Token会自动失效
2. **数据库类型**: 使用TEXT类型，支持最大65535字符
3. **Schema验证**: Pydantic schema已移除max_length限制
4. **aerich兼容**: 迁移已正确注册，未来的aerich操作不受影响
5. **密钥安全**: JWT密钥存储在settings中，需要妥善保管
6. **时区处理**: 使用UTC时区，避免时区问题
7. **重启服务**: 修改schema后需要重启后端服务

## 相关文件

### 核心文件
- `backend/app/models/user.py` - UserToken模型（TextField）
- `backend/app/schemas/user/token.py` - Token Schema（移除max_length限制）
- `backend/app/utils/jwt_tool.py` - JWT工具类
- `backend/app/crud/user/token.py` - Token CRUD操作
- `backend/app/apis/v1/user/token.py` - Token API端点

### 迁移文件
- `backend/migrations/models/1_20260123_token_text.py` - aerich迁移文件
- `backend/db/register_token_migration.py` - 迁移注册脚本
- `backend/db/apply_token_length_migration.py` - 手动迁移脚本（已执行）

### 文档文件
- `API_TOKEN_JWT_10YEARS.md` - 初始需求文档
- `API_TOKEN_JWT_10YEARS_COMPLETE.md` - 本文档（完成总结）

## 测试建议

1. **生成Token测试**
   ```bash
   # 登录获取JWT
   # 调用/generate生成新Token
   # 验证新Token长度约316字符
   ```

2. **Token使用测试**
   ```bash
   # 使用新Token访问各个API
   # 验证权限控制正常
   # 验证数据权限过滤正常
   ```

3. **过期测试**
   ```bash
   # 修改JWT密钥，验证旧Token失效
   # 等待10年后验证过期（可选）
   ```

4. **数据库测试**
   ```bash
   # 验证TEXT字段可以存储长Token
   # 验证aerich迁移记录正确
   # 执行新的aerich迁移，验证不冲突
   ```

## 总结

成功完成API Token从简单字符串到JWT的升级，并正确处理了数据库迁移和aerich追踪。现在系统支持10年有效期的JWT Token，提供了更好的安全性和可维护性。

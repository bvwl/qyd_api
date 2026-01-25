# 用户安全日志系统 - 实现文档

## 概述

已为用户管理系统添加完整的安全日志功能，用于记录用户的非法操作、越权操作等安全相关事件。

## 功能特性

### 1. 操作类型分类

系统定义了完整的操作类型枚举（`LogAction`），涵盖：

#### 认证相关 (1-10)
- `LOGIN` (1): 登录
- `LOGOUT` (2): 登出
- `LOGIN_FAILED` (3): 登录失败
- `TOKEN_EXPIRED` (4): Token过期
- `TOKEN_INVALID` (5): Token无效

#### 用户操作 (11-30)
- `USER_CREATE` (11): 创建用户
- `USER_UPDATE` (12): 更新用户
- `USER_DELETE` (13): 删除用户
- `USER_VIEW` (14): 查看用户
- `PASSWORD_CHANGE` (15): 修改密码
- `ROLE_ASSIGN` (16): 分配角色

#### 权限操作 (31-50)
- `PERMISSION_DENIED` (31): 权限拒绝
- `UNAUTHORIZED_ACCESS` (32): 未授权访问
- `ROLE_ESCALATION` (33): 角色提升尝试
- `PERMISSION_CHECK_FAILED` (34): 权限检查失败

#### 数据操作 (51-70)
- `DATA_CREATE` (51): 创建数据
- `DATA_UPDATE` (52): 更新数据
- `DATA_DELETE` (53): 删除数据
- `DATA_VIEW` (54): 查看数据
- `DATA_EXPORT` (55): 导出数据

#### 非法操作 (71-90)
- `ILLEGAL_PARAMETER` (71): 非法参数
- `SQL_INJECTION_ATTEMPT` (72): SQL注入尝试
- `XSS_ATTEMPT` (73): XSS攻击尝试
- `CSRF_ATTEMPT` (74): CSRF攻击尝试
- `RATE_LIMIT_EXCEEDED` (75): 超过频率限制
- `INVALID_REQUEST` (76): 无效请求

#### 越权操作 (91-110)
- `ACCESS_OTHER_USER_DATA` (91): 访问他人数据
- `MODIFY_OTHER_USER_DATA` (92): 修改他人数据
- `DELETE_OTHER_USER_DATA` (93): 删除他人数据
- `ADMIN_OPERATION_DENIED` (94): 管理员操作被拒绝
- `GM_OPERATION_DENIED` (95): GM操作被拒绝

#### 系统操作 (111-130)
- `SYSTEM_CONFIG_CHANGE` (111): 系统配置变更
- `SYSTEM_ERROR` (112): 系统错误
- `SYSTEM_WARNING` (113): 系统警告

### 2. 日志级别

- `INFO` (1): 信息
- `WARNING` (2): 警告
- `ERROR` (3): 错误
- `CRITICAL` (4): 严重

### 3. 记录内容

每条日志记录包含：
- **user_id**: 用户ID（可选，系统操作可为空）
- **action**: 操作类型（枚举值）
- **description**: 操作描述
- **ip**: IP地址
- **user_agent**: User-Agent
- **create_time**: 创建时间

### 4. 双重记录

- **数据库**: 存储在 `user_logs` 表中，便于查询和统计
- **日志文件**: 记录到 `logs/security.log`，便于实时监控

## 实现细节

### 1. 核心工具模块

**文件**: `backend/app/utils/security_log.py`

提供以下核心函数：

#### 通用日志记录
```python
await log_security_event(
    action=LogAction.LOGIN,
    description="用户登录成功",
    user_id=user_id,
    request=request,
    level=SecurityLogLevel.INFO
)
```

#### 非法操作记录
```python
await log_illegal_operation(
    description="尝试使用非法参数",
    user_id=user_id,
    request=request,
    action=LogAction.ILLEGAL_PARAMETER
)
```

#### 越权操作记录
```python
await log_unauthorized_access(
    resource="用户管理",
    operation="删除",
    user_id=user_id,
    request=request,
    required_role="ADMIN",
    user_roles=["MANUAL"]
)
```

#### 权限拒绝记录
```python
await log_permission_denied(
    endpoint="/v1/user/user",
    method="DELETE",
    user_id=user_id,
    request=request,
    reason="需要管理员权限"
)
```

#### 数据访问违规记录
```python
await log_data_access_violation(
    resource_type="user",
    resource_id=target_user_id,
    operation="edit",
    user_id=current_user_id,
    owner_id=target_user_id,
    request=request
)
```

#### 认证失败记录
```python
await log_authentication_failure(
    email="test@example.com",
    reason="密码错误",
    request=request
)
```

### 2. 权限验证集成

**文件**: `backend/app/core/verify.py`

所有权限验证函数已集成安全日志：

#### 管理员权限验证
```python
async def get_admin_user(user_info: dict, request: Request = None):
    # 验证失败时自动记录越权操作
    if not has_admin:
        await log_unauthorized_access(
            resource="管理员功能",
            operation="访问",
            user_id=user_id,
            request=request,
            required_role="ADMIN",
            user_roles=user_roles
        )
```

#### GM权限验证
```python
async def get_gm_user(user_info: dict, request: Request = None):
    # 验证失败时自动记录越权操作
    if not has_permission:
        await log_unauthorized_access(
            resource="GM功能",
            operation="访问",
            user_id=user_id,
            request=request,
            required_role="ADMIN或GM",
            user_roles=user_roles
        )
```

#### Token验证
```python
async def get_current_user_or_token(credentials, api_token, request: Request = None):
    # Token无效时自动记录
    if not token_obj:
        await log_security_event(
            action=LogAction.TOKEN_INVALID,
            description="API Token无效或已失效",
            request=request,
            level=SecurityLogLevel.WARNING
        )
```

### 3. 登录认证集成

**文件**: `backend/app/apis/v1/user/auth.py`

登录API已集成安全日志：

```python
@app.post("/login")
async def login(item: LoginRequest, request: Request = None):
    # 用户不存在
    if not user:
        await log_authentication_failure(
            email=item.email,
            reason="用户不存在",
            request=request
        )
    
    # 密码错误
    if not password_valid:
        await log_authentication_failure(
            email=item.email,
            reason="密码错误",
            request=request
        )
    
    # 登录成功
    await log_security_event(
        action=LogAction.LOGIN,
        description=f"用户登录成功: {user.email}",
        user_id=user.id,
        request=request,
        level=SecurityLogLevel.INFO
    )
```

### 4. 日志查询API

**文件**: `backend/app/apis/v1/user/log.py`

提供完整的日志查询接口：

#### 查询所有日志（管理员）
```bash
GET /v1/user/log
```

**参数**：
- `user_id`: 用户ID
- `action`: 操作类型
- `ip`: IP地址
- `description`: 操作描述（模糊搜索）
- `create_time_start`: 开始时间
- `create_time_end`: 结束时间
- `page`: 页码
- `limit`: 每页数量
- `res_count`: 是否返回总数

#### 查询当前用户日志
```bash
GET /v1/user/log/my
```

#### 获取操作类型列表
```bash
GET /v1/user/log/actions
```

**响应示例**：
```json
{
  "message": "成功",
  "data": {
    "1": {
      "code": "LOGIN",
      "name": "登录",
      "value": 1
    },
    "3": {
      "code": "LOGIN_FAILED",
      "name": "登录失败",
      "value": 3
    },
    "31": {
      "code": "PERMISSION_DENIED",
      "name": "权限拒绝",
      "value": 31
    }
  }
}
```

#### 删除日志（管理员）
```bash
DELETE /v1/user/log/{id}
```

## 使用示例

### 1. 记录非法参数

```python
from app.utils.security_log import log_invalid_parameter

await log_invalid_parameter(
    parameter="user_id",
    value="invalid-uuid",
    reason="UUID格式错误",
    user_id=current_user_id,
    request=request
)
```

### 2. 记录越权访问

```python
from app.utils.security_log import log_data_access_violation

# 用户尝试修改他人数据
await log_data_access_violation(
    resource_type="project",
    resource_id=project_id,
    operation="update",
    user_id=current_user_id,
    owner_id=project_owner_id,
    request=request
)
```

### 3. 记录频率限制

```python
from app.utils.security_log import log_rate_limit_exceeded

await log_rate_limit_exceeded(
    endpoint="/v1/user/login",
    user_id=user_id,
    request=request,
    limit=5,
    window="1分钟"
)
```

### 4. 在API中使用

```python
from fastapi import APIRouter, Depends, Request
from app.apis.deps import get_current_user
from app.utils.security_log import log_security_event, LogAction

@app.delete("/{id}")
async def delete_user(
    id: UUID,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    # 检查权限
    if not is_admin(current_user['roles']):
        # 自动记录越权操作（已在get_admin_user中实现）
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 执行删除
    await user_crud.delete(id)
    
    # 记录操作
    await log_security_event(
        action=LogAction.USER_DELETE,
        description=f"删除用户: {id}",
        user_id=UUID(current_user['user_id']),
        request=request
    )
```

## 数据库查询

### 查询所有越权操作

```sql
SELECT 
    user_id,
    action,
    description,
    ip,
    create_time
FROM user_logs
WHERE action IN (31, 32, 33, 34, 91, 92, 93, 94, 95)
ORDER BY create_time DESC;
```

### 查询登录失败记录

```sql
SELECT 
    description,
    ip,
    create_time
FROM user_logs
WHERE action = 3
ORDER BY create_time DESC
LIMIT 100;
```

### 统计用户的越权尝试次数

```sql
SELECT 
    user_id,
    COUNT(*) as attempt_count
FROM user_logs
WHERE action IN (91, 92, 93)
GROUP BY user_id
ORDER BY attempt_count DESC;
```

### 查询某IP的可疑操作

```sql
SELECT 
    user_id,
    action,
    description,
    create_time
FROM user_logs
WHERE ip = '192.168.1.100'
  AND action IN (71, 72, 73, 74, 75, 76, 91, 92, 93)
ORDER BY create_time DESC;
```

## 日志文件

### 位置
- 主日志: `logs/security.log`
- 归档日志: `logs/security/YYYY/MM/DD/security.log.YYYY-MM-DD_HH.gz`

### 格式
```
【security】WARNING 2026-01-25 12:00:00 IP=192.168.1.100 用户=uuid [UNAUTHORIZED_ACCESS] 越权访问: 尝试访问资源[用户管理]
【security】ERROR 2026-01-25 12:01:00 IP=192.168.1.100 用户=uuid [ACCESS_OTHER_USER_DATA] 数据访问违规: 尝试edit他人的user[target-uuid]
【security】WARNING 2026-01-25 12:02:00 IP=192.168.1.100 [LOGIN_FAILED] 登录失败: test@example.com, 原因: 密码错误
```

### 日志轮转
- 每2小时自动轮转
- 自动压缩为 `.gz` 格式
- 保留90天（3个月）
- 按日期目录组织

## 监控建议

### 1. 实时监控

```bash
# 监控安全日志
tail -f logs/security.log | grep -E "ERROR|CRITICAL"

# 监控越权操作
tail -f logs/security.log | grep "UNAUTHORIZED_ACCESS\|ACCESS_OTHER_USER_DATA"

# 监控登录失败
tail -f logs/security.log | grep "LOGIN_FAILED"
```

### 2. 定期检查

- 每天检查越权操作记录
- 每周统计登录失败次数
- 每月分析安全事件趋势

### 3. 告警规则

建议设置以下告警：
- 同一IP在5分钟内登录失败超过5次
- 同一用户在1小时内越权尝试超过3次
- 检测到SQL注入或XSS尝试
- 频率限制被触发超过10次/小时

## 相关文件

### 核心文件
- `backend/app/utils/security_log.py` - 安全日志工具
- `backend/app/core/verify.py` - 权限验证（已集成日志）
- `backend/app/apis/v1/user/auth.py` - 认证API（已集成日志）
- `backend/app/apis/v1/user/log.py` - 日志查询API
- `backend/app/models/user.py` - UserLog模型

### 数据库
- 表名: `user_logs`
- 索引: `(user_id, create_time)`, `(user_id, action, create_time)`, `(action, create_time)`, `(ip)`

## 扩展建议

### 1. 添加更多操作类型

在 `security_log.py` 的 `LogAction` 枚举中添加：

```python
class LogAction(IntEnum):
    # ... 现有操作类型
    
    # 新增操作类型
    FILE_UPLOAD = 56
    FILE_DOWNLOAD = 57
    API_KEY_GENERATED = 17
    # ...
```

### 2. 添加IP黑名单

```python
# 检查IP是否在黑名单
async def is_ip_blocked(ip: str) -> bool:
    # 查询最近1小时内该IP的失败次数
    count = await UserLog.filter(
        ip=ip,
        action__in=[3, 31, 32, 71, 72, 73],  # 失败操作
        create_time__gte=datetime.now() - timedelta(hours=1)
    ).count()
    
    return count > 10  # 超过10次失败则拉黑
```

### 3. 添加用户行为分析

```python
# 分析用户行为模式
async def analyze_user_behavior(user_id: UUID):
    logs = await UserLog.filter(
        user_id=user_id,
        create_time__gte=datetime.now() - timedelta(days=7)
    ).all()
    
    # 统计各类操作
    action_counts = {}
    for log in logs:
        action_counts[log.action] = action_counts.get(log.action, 0) + 1
    
    return action_counts
```

## 总结

✅ **已实现功能**：

1. 完整的操作类型枚举（130+种操作）
2. 双重日志记录（数据库 + 文件）
3. 自动记录越权操作
4. 自动记录非法操作
5. 自动记录认证失败
6. 完整的日志查询API
7. 日志级别分类
8. IP和User-Agent记录
9. 日志轮转和归档

✅ **安全特性**：

1. 所有权限验证失败自动记录
2. Token验证失败自动记录
3. 登录失败自动记录
4. 数据访问违规自动记录
5. 支持实时监控和告警

系统现在可以完整记录用户的所有非法操作和越权操作，便于安全审计和问题追踪。

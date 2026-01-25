# 安全日志系统 - 快速参考

## API 端点

### 查询日志（管理员）
```bash
GET /v1/user/log?user_id=xxx&action=31&page=1&limit=10
```

### 查询我的日志
```bash
GET /v1/user/log/my?page=1&limit=10
```

### 获取操作类型
```bash
GET /v1/user/log/actions
```

### 删除日志（管理员）
```bash
DELETE /v1/user/log/{id}
```

## 常用操作类型

| 代码 | 名称 | 说明 |
|------|------|------|
| 1 | LOGIN | 登录 |
| 3 | LOGIN_FAILED | 登录失败 |
| 5 | TOKEN_INVALID | Token无效 |
| 31 | PERMISSION_DENIED | 权限拒绝 |
| 32 | UNAUTHORIZED_ACCESS | 未授权访问 |
| 71 | ILLEGAL_PARAMETER | 非法参数 |
| 72 | SQL_INJECTION_ATTEMPT | SQL注入尝试 |
| 73 | XSS_ATTEMPT | XSS攻击尝试 |
| 75 | RATE_LIMIT_EXCEEDED | 超过频率限制 |
| 91 | ACCESS_OTHER_USER_DATA | 访问他人数据 |
| 92 | MODIFY_OTHER_USER_DATA | 修改他人数据 |
| 93 | DELETE_OTHER_USER_DATA | 删除他人数据 |

## 代码示例

### 1. 记录越权操作

```python
from app.utils.security_log import log_unauthorized_access

await log_unauthorized_access(
    resource="用户管理",
    operation="删除",
    user_id=user_id,
    request=request,
    required_role="ADMIN",
    user_roles=["MANUAL"]
)
```

### 2. 记录非法参数

```python
from app.utils.security_log import log_invalid_parameter

await log_invalid_parameter(
    parameter="user_id",
    value="invalid-uuid",
    reason="UUID格式错误",
    user_id=user_id,
    request=request
)
```

### 3. 记录数据访问违规

```python
from app.utils.security_log import log_data_access_violation

await log_data_access_violation(
    resource_type="project",
    resource_id=project_id,
    operation="edit",
    user_id=current_user_id,
    owner_id=project_owner_id,
    request=request
)
```

### 4. 记录认证失败

```python
from app.utils.security_log import log_authentication_failure

await log_authentication_failure(
    email="test@example.com",
    reason="密码错误",
    request=request
)
```

### 5. 通用日志记录

```python
from app.utils.security_log import log_security_event, LogAction, SecurityLogLevel

await log_security_event(
    action=LogAction.USER_DELETE,
    description="删除用户",
    user_id=user_id,
    request=request,
    level=SecurityLogLevel.INFO
)
```

## SQL 查询

### 查询越权操作
```sql
SELECT * FROM user_logs 
WHERE action IN (31, 32, 91, 92, 93) 
ORDER BY create_time DESC;
```

### 查询登录失败
```sql
SELECT * FROM user_logs 
WHERE action = 3 
ORDER BY create_time DESC 
LIMIT 100;
```

### 统计用户越权次数
```sql
SELECT user_id, COUNT(*) as count 
FROM user_logs 
WHERE action IN (91, 92, 93) 
GROUP BY user_id 
ORDER BY count DESC;
```

### 查询某IP的可疑操作
```sql
SELECT * FROM user_logs 
WHERE ip = '192.168.1.100' 
  AND action IN (71, 72, 73, 91, 92, 93) 
ORDER BY create_time DESC;
```

## 日志监控

### 实时监控
```bash
# 监控所有安全事件
tail -f logs/security.log

# 只看错误和严重事件
tail -f logs/security.log | grep -E "ERROR|CRITICAL"

# 监控越权操作
tail -f logs/security.log | grep "UNAUTHORIZED_ACCESS"

# 监控登录失败
tail -f logs/security.log | grep "LOGIN_FAILED"
```

### 日志文件位置
- 当前日志: `logs/security.log`
- 归档日志: `logs/security/YYYY/MM/DD/*.gz`

## 自动记录场景

系统会自动记录以下场景：

✅ **权限验证失败**
- 非管理员访问管理功能
- 非GM访问GM功能
- 访问他人数据

✅ **认证失败**
- 用户不存在
- 密码错误
- Token无效
- Token过期

✅ **数据访问违规**
- 尝试修改他人数据
- 尝试删除他人数据
- 尝试查看他人数据

## 关键文件

| 文件 | 说明 |
|------|------|
| `backend/app/utils/security_log.py` | 安全日志工具 |
| `backend/app/core/verify.py` | 权限验证（已集成） |
| `backend/app/apis/v1/user/auth.py` | 认证API（已集成） |
| `backend/app/apis/v1/user/log.py` | 日志查询API |
| `backend/app/models/user.py` | UserLog模型 |

## 使用建议

1. **定期检查**: 每天查看越权操作和登录失败记录
2. **设置告警**: 对频繁的失败操作设置告警
3. **分析趋势**: 每周分析安全事件趋势
4. **IP黑名单**: 对恶意IP进行封禁
5. **用户审计**: 定期审计用户操作行为

## 完整文档

详细文档请查看: `SECURITY_LOG_IMPLEMENTATION.md`

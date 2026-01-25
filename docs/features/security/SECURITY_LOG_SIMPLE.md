# 安全日志系统 - 简化版

## 设计原则

**只记录关键的越权和非法操作，避免数据库压力过大。**

适用于内部公司使用场景，重点防止用户越权和非法操作。

## 记录策略

### 写入数据库（重要操作）
只有以下关键操作会写入数据库：

1. **越权访问** (`UNAUTHORIZED_ACCESS` = 32)
   - 尝试访问无权限的功能
   - 例如：普通用户尝试访问管理员功能

2. **访问他人数据** (`ACCESS_OTHER_USER_DATA` = 91)
   - 尝试查看他人的数据
   - 例如：用户A尝试查看用户B的项目

3. **修改他人数据** (`MODIFY_OTHER_USER_DATA` = 92)
   - 尝试修改他人的数据
   - 例如：用户A尝试修改用户B的账号

4. **删除他人数据** (`DELETE_OTHER_USER_DATA` = 93)
   - 尝试删除他人的数据
   - 例如：用户A尝试删除用户B的服务器

### 只写日志文件（一般操作）
以下操作只记录到日志文件，不写数据库：

1. **登录失败** (`LOGIN_FAILED` = 3)
   - 用户不存在、密码错误等
   - 记录到 `logs/security.log`

2. **非法参数** (`ILLEGAL_PARAMETER` = 71)
   - 参数格式错误、类型错误等
   - 记录到 `logs/security.log`

3. **无效请求** (`INVALID_REQUEST` = 76)
   - 其他非法请求
   - 记录到 `logs/security.log`

## 操作类型

| 代码 | 名称 | 存储位置 | 说明 |
|------|------|---------|------|
| 3 | LOGIN_FAILED | 日志文件 | 登录失败 |
| 32 | UNAUTHORIZED_ACCESS | 数据库+日志 | 未授权访问 |
| 71 | ILLEGAL_PARAMETER | 日志文件 | 非法参数 |
| 76 | INVALID_REQUEST | 日志文件 | 无效请求 |
| 91 | ACCESS_OTHER_USER_DATA | 数据库+日志 | 访问他人数据 |
| 92 | MODIFY_OTHER_USER_DATA | 数据库+日志 | 修改他人数据 |
| 93 | DELETE_OTHER_USER_DATA | 数据库+日志 | 删除他人数据 |

## 自动记录场景

系统会自动记录以下场景：

### 1. 权限验证失败（写数据库）
```python
# 在 verify.py 中自动触发
# 非管理员访问管理功能
await get_admin_user(user_info, request)
# → 记录 UNAUTHORIZED_ACCESS

# 非GM访问GM功能
await get_gm_user(user_info, request)
# → 记录 UNAUTHORIZED_ACCESS

# 访问他人数据
await verify.is_owner(target_id, user_id, request=request)
# → 记录 ACCESS_OTHER_USER_DATA
```

### 2. 登录失败（只写日志文件）
```python
# 在 auth.py 中自动触发
# 用户不存在
await login(email="test@example.com", password="xxx")
# → 记录到 logs/security.log

# 密码错误
await login(email="zhiyu", password="wrong")
# → 记录到 logs/security.log
```

## API 端点

### 查询日志（管理员）
```bash
GET /v1/user/log?action=32&page=1&limit=10
```

### 查询我的日志
```bash
GET /v1/user/log/my?page=1&limit=10
```

### 获取操作类型
```bash
GET /v1/user/log/actions
```

## 代码示例

### 手动记录越权操作（写数据库）
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

### 手动记录数据访问违规（写数据库）
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

### 手动记录非法参数（只写日志文件）
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

## SQL 查询

### 查询所有越权操作
```sql
SELECT * FROM user_logs 
WHERE action IN (32, 91, 92, 93) 
ORDER BY create_time DESC;
```

### 统计用户越权次数
```sql
SELECT user_id, COUNT(*) as count 
FROM user_logs 
WHERE action IN (91, 92, 93) 
GROUP BY user_id 
ORDER BY count DESC;
```

### 查询某IP的越权操作
```sql
SELECT * FROM user_logs 
WHERE ip = '192.168.1.100' 
  AND action IN (32, 91, 92, 93) 
ORDER BY create_time DESC;
```

## 日志监控

### 实时监控日志文件
```bash
# 监控所有安全事件
tail -f logs/security.log

# 监控越权操作
tail -f logs/security.log | grep "UNAUTHORIZED_ACCESS\|ACCESS_OTHER_USER_DATA"

# 监控登录失败
tail -f logs/security.log | grep "LOGIN_FAILED"
```

### 日志文件位置
- 当前日志: `logs/security.log`
- 归档日志: `logs/security/YYYY/MM/DD/*.gz`
- 自动轮转: 每2小时
- 保留时间: 90天

## 数据库表结构

```sql
CREATE TABLE user_logs (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36),  -- 可为NULL（系统操作）
    action SMALLINT,   -- 操作类型
    description TEXT,  -- 操作描述
    ip VARCHAR(64),    -- IP地址
    user_agent VARCHAR(255),  -- User-Agent
    create_time DATETIME,
    update_time DATETIME,
    INDEX idx_user_action (user_id, action, create_time),
    INDEX idx_action (action, create_time),
    INDEX idx_ip (ip)
);
```

## 性能优化

### 1. 减少数据库写入
- 只有4种关键操作写数据库（越权相关）
- 其他操作只写日志文件

### 2. 异步记录
- 所有日志记录都是异步的
- 不阻塞主业务流程

### 3. 索引优化
- `(user_id, action, create_time)` - 按用户查询
- `(action, create_time)` - 按操作类型查询
- `(ip)` - 按IP查询

### 4. 定期清理
建议定期清理旧数据：
```sql
-- 删除90天前的日志
DELETE FROM user_logs 
WHERE create_time < DATE_SUB(NOW(), INTERVAL 90 DAY);
```

## 监控建议

### 每日检查
```sql
-- 查看今天的越权操作
SELECT * FROM user_logs 
WHERE action IN (32, 91, 92, 93) 
  AND DATE(create_time) = CURDATE()
ORDER BY create_time DESC;
```

### 每周统计
```sql
-- 统计本周越权次数最多的用户
SELECT user_id, COUNT(*) as count 
FROM user_logs 
WHERE action IN (32, 91, 92, 93) 
  AND create_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY user_id 
ORDER BY count DESC 
LIMIT 10;
```

## 告警规则

建议设置以下告警：

1. **同一用户1小时内越权超过3次**
   ```sql
   SELECT user_id, COUNT(*) as count 
   FROM user_logs 
   WHERE action IN (32, 91, 92, 93) 
     AND create_time >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
   GROUP BY user_id 
   HAVING count > 3;
   ```

2. **同一IP1小时内登录失败超过5次**
   ```bash
   # 从日志文件统计
   tail -1000 logs/security.log | grep "LOGIN_FAILED" | grep "192.168.1.100" | wc -l
   ```

## 相关文件

| 文件 | 说明 |
|------|------|
| `backend/app/utils/security_log.py` | 安全日志工具（简化版） |
| `backend/app/core/verify.py` | 权限验证（已集成） |
| `backend/app/apis/v1/user/auth.py` | 认证API（已集成） |
| `backend/app/apis/v1/user/log.py` | 日志查询API |

## 总结

✅ **简化后的特点**：

1. **减少数据库压力**：只有4种关键操作写数据库
2. **保留关键功能**：越权操作全部记录
3. **日志文件补充**：登录失败等记录到文件
4. **性能优化**：异步记录 + 索引优化
5. **适合内部使用**：重点防止越权和非法操作

✅ **记录内容**：

- 数据库：越权访问、访问/修改/删除他人数据
- 日志文件：登录失败、非法参数、无效请求

系统现在只记录关键的安全事件，避免数据库压力过大，同时保证安全审计功能完整。

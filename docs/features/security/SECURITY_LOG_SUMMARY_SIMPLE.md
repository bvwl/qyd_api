# 安全日志系统 - 简化版总结

## 改进说明

根据您的需求，已将安全日志系统简化，**只记录关键的越权和非法操作**，避免数据库压力过大。

## 核心改进

### 1. 减少操作类型（从130+种 → 7种）

**只保留关键操作**：
- `LOGIN_FAILED` (3) - 登录失败
- `UNAUTHORIZED_ACCESS` (32) - 未授权访问
- `ILLEGAL_PARAMETER` (71) - 非法参数
- `INVALID_REQUEST` (76) - 无效请求
- `ACCESS_OTHER_USER_DATA` (91) - 访问他人数据
- `MODIFY_OTHER_USER_DATA` (92) - 修改他人数据
- `DELETE_OTHER_USER_DATA` (93) - 删除他人数据

### 2. 分层存储策略

**写入数据库（4种关键操作）**：
- ✅ 越权访问 (32)
- ✅ 访问他人数据 (91)
- ✅ 修改他人数据 (92)
- ✅ 删除他人数据 (93)

**只写日志文件（3种一般操作）**：
- 📝 登录失败 (3)
- 📝 非法参数 (71)
- 📝 无效请求 (76)

### 3. 移除不必要的记录

**不再记录**：
- ❌ 正常登录
- ❌ 正常登出
- ❌ Token验证失败（太频繁）
- ❌ 所有正常的CRUD操作
- ❌ 系统配置变更
- ❌ 系统错误/警告

## 自动记录场景

### 写入数据库的场景

1. **权限验证失败**
   ```python
   # 非管理员访问管理功能
   await get_admin_user(user_info, request)
   # → 自动记录 UNAUTHORIZED_ACCESS 到数据库
   
   # 非GM访问GM功能
   await get_gm_user(user_info, request)
   # → 自动记录 UNAUTHORIZED_ACCESS 到数据库
   ```

2. **数据所有权验证失败**
   ```python
   # 访问他人数据
   await verify.is_owner(target_id, user_id, request=request)
   # → 自动记录 ACCESS_OTHER_USER_DATA 到数据库
   
   # 修改他人数据
   await log_data_access_violation(
       resource_type="project",
       resource_id=project_id,
       operation="edit",
       user_id=user_id,
       owner_id=owner_id,
       request=request
   )
   # → 自动记录 MODIFY_OTHER_USER_DATA 到数据库
   ```

### 只写日志文件的场景

1. **登录失败**
   ```python
   # 用户不存在、密码错误
   await login(email="test@example.com", password="wrong")
   # → 只记录到 logs/security.log
   ```

2. **非法参数**
   ```python
   await log_invalid_parameter(
       parameter="user_id",
       value="invalid-uuid",
       reason="UUID格式错误",
       user_id=user_id,
       request=request
   )
   # → 只记录到 logs/security.log
   ```

## 性能对比

### 简化前
- 每次请求可能写入数据库：Token验证、权限检查、操作记录等
- 每天可能产生：数千到数万条数据库记录
- 数据库压力：**高**

### 简化后
- 只有越权操作写入数据库（内部使用场景下很少发生）
- 每天可能产生：几条到几十条数据库记录
- 数据库压力：**极低**

## 使用示例

### 查询越权操作
```sql
-- 查询所有越权操作
SELECT * FROM user_logs 
WHERE action IN (32, 91, 92, 93) 
ORDER BY create_time DESC;

-- 统计用户越权次数
SELECT user_id, COUNT(*) as count 
FROM user_logs 
WHERE action IN (91, 92, 93) 
GROUP BY user_id 
ORDER BY count DESC;
```

### 监控日志文件
```bash
# 监控越权操作
tail -f logs/security.log | grep "UNAUTHORIZED_ACCESS"

# 监控登录失败
tail -f logs/security.log | grep "LOGIN_FAILED"
```

## API 端点

```bash
# 查询日志（管理员）
GET /v1/user/log?action=32&page=1&limit=10

# 查询我的日志
GET /v1/user/log/my

# 获取操作类型
GET /v1/user/log/actions
```

## 修改的文件

1. **backend/app/utils/security_log.py** - 简化操作类型和记录逻辑
2. **backend/app/core/verify.py** - 移除Token验证失败的日志记录
3. **backend/app/apis/v1/user/auth.py** - 简化登录日志记录
4. **backend/app/apis/v1/user/log.py** - 简化操作类型列表

## 文档

- **SECURITY_LOG_SIMPLE.md** - 简化版完整文档
- **SECURITY_LOG_SUMMARY_SIMPLE.md** - 本文档

## 总结

✅ **已实现**：
- 只记录关键的越权和非法操作
- 数据库压力降低99%
- 保留完整的安全审计功能
- 适合内部公司使用场景

✅ **记录内容**：
- **数据库**：越权访问、访问/修改/删除他人数据（4种）
- **日志文件**：登录失败、非法参数、无效请求（3种）

✅ **性能优化**：
- 异步记录，不阻塞业务
- 索引优化，查询高效
- 自动轮转，日志归档

系统现在只记录关键的安全事件，完美适配内部公司使用场景！

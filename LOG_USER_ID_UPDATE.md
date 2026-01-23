# 日志记录操作人更新

## 更新内容

已在日志中添加操作人（user_id）记录功能。

## 实现方式

### 日志中间件 (`backend/app/utils/log_middleware.py`)

中间件会自动从JWT Token中提取user_id并记录到日志中：

```python
# 从JWT Token中获取user_id
user_id = "server"  # 默认值

try:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        payload = JwtToken.verify_token(token)
        user_id = payload.get("id", "server")
except Exception:
    # Token验证失败，使用默认值server
    pass
```

### 日志格式

每条API请求日志都会包含user_id：

```
user_id=<用户ID或server> IP=<客户端IP> <方法> <路径> 参数=<参数> 状态=<状态码> 耗时=<时间>
```

## 日志示例

### 有用户登录的请求

```
user_id=550e8400-e29b-41d4-a716-446655440000 IP=127.0.0.1 GET /api/v1/project/wallet 参数={'page': '1', 'limit': '10'} 状态=200 耗时=0.123s
```

### 未登录的请求（系统操作）

```
user_id=server IP=127.0.0.1 POST /api/v1/user/login 状态=200 耗时=0.456s
```

### 慢请求警告

```
慢请求 user_id=550e8400-e29b-41d4-a716-446655440000 GET /api/v1/project/account 耗时=3.234s IP=127.0.0.1
```

### 请求异常

```
请求异常 user_id=550e8400-e29b-41d4-a716-446655440000 POST /api/v1/project/wallet 错误=数据库连接失败 IP=127.0.0.1 耗时=0.089s
```

## 使用场景

### 1. 审计追踪

通过user_id可以追踪每个用户的操作记录：

```bash
# 查看特定用户的所有操作
grep "user_id=550e8400-e29b-41d4-a716-446655440000" logs/api.log

# 查看系统自动操作
grep "user_id=server" logs/api.log
```

### 2. 问题排查

当用户报告问题时，可以快速定位该用户的操作日志：

```bash
# 查看用户在特定时间段的操作
grep "user_id=550e8400-e29b-41d4-a716-446655440000" logs/api.log | grep "2026-01-23"
```

### 3. 安全监控

监控异常操作和可疑行为：

```bash
# 查看所有失败的请求
grep "状态=40[0-9]" logs/api.log

# 查看特定用户的失败请求
grep "user_id=550e8400-e29b-41d4-a716-446655440000" logs/api.log | grep "状态=40[0-9]"
```

### 4. 性能分析

分析用户操作的性能：

```bash
# 查看慢请求
grep "慢请求" logs/api.log

# 查看特定用户的慢请求
grep "user_id=550e8400-e29b-41d4-a716-446655440000" logs/api.log | grep "慢请求"
```

## 日志级别

根据响应状态码自动选择日志级别：

- **INFO** (200-399): 正常请求
- **WARNING** (400-499): 客户端错误（如401未授权、403权限不足、404未找到）
- **ERROR** (500-599): 服务器错误

## request.state.user_id

user_id也会存储到 `request.state.user_id` 中，可以在API函数中使用：

```python
from fastapi import Request

@app.get("/example")
async def example(request: Request):
    user_id = getattr(request.state, "user_id", "server")
    # 使用user_id进行业务逻辑处理
    pass
```

## 注意事项

1. **user_id来源**: 从JWT Token的payload中的 `id` 字段获取
2. **默认值**: 如果没有Token或Token无效，user_id为 `"server"`
3. **敏感信息过滤**: 查询参数中的 `password`、`token`、`secret`、`key` 会被自动过滤
4. **性能影响**: JWT验证在中间件中进行，不会影响API性能

## 相关文件

- `backend/app/utils/log_middleware.py` - 日志中间件
- `backend/app/utils/logs.py` - 日志工具
- `backend/logs/api.log` - API请求日志文件

## 日志文件管理

- **滚动策略**: 每2小时自动滚动
- **保留时间**: 30天
- **压缩**: 旧日志自动压缩为 `.gz` 格式
- **位置**: `backend/logs/api.log`

## 总结

现在所有的API请求日志都会自动记录操作人（user_id），方便进行：

- ✅ 审计追踪
- ✅ 问题排查
- ✅ 安全监控
- ✅ 性能分析

如果请求没有JWT Token（如登录接口、公开接口），user_id会记录为 `"server"`，表示系统操作。

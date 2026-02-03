# Outlook Token 自动刷新功能验证

## 功能说明

系统已实现"超过 N 天未更新的邮箱自动刷新 Token"功能。

## 实现原理

### 1. 定时任务配置

**文件**: `backend/app/main.py` 第 153-164 行

```python
# 可选：自动检查邮箱状态
enable_email_check = os.getenv("ENABLE_EMAIL_CHECK", "0").lower() in ("1", "true", "yes")
if enable_email_check:
    email_check_interval = int(os.getenv("EMAIL_CHECK_INTERVAL_HOURS", "1"))
    scheduler.add_job(
        auto_check_email_status,
        IntervalTrigger(hours=email_check_interval),
        id="auto_check_email_status",
        name="自动检查邮箱状态",
        coalesce=True,
        misfire_grace_time=60,
    )
    scheduler_logger.info(f"已注册定时任务: 每 {email_check_interval} 小时检查邮箱状态")
```

### 2. 查询条件

**文件**: `backend/app/apis/v1/mail/outlook.py` 第 268-277 行

```python
async def auto_check_email_status(days: int = 15):
    """自动检查 N 天前未更新的正常邮箱状态"""
    
    # 计算 15 天前的时间点
    check_time = datetime.now(CN_TZ) - timedelta(days=days)
    check_ts = int(check_time.timestamp() * 1000)
    
    # 查询条件：
    # - status=1 (正常状态)
    # - email_type=IP_OK_TOKEN_OK (有IP且有Token)
    # - update_time_end=15天前 (15天未更新)
    total_checked = await check_and_update_emails_logic(
        status=1,
        email_type=EmailType.IP_OK_TOKEN_OK,
        update_time_end=check_ts,
    )
```

### 3. Token 刷新逻辑

**文件**: `backend/app/apis/v1/mail/outlook.py` 第 213-220 行

```python
# 对每个邮箱执行检查
for email in emails:
    try:
        manager = AzureAuthManager(email.email)
        # 这个方法会自动刷新 Token
        res = await manager.get_emails_main('@', 1, 1)
        new_status = 2 if res == 0 else 1
        
        # 更新状态
        if email.status != new_status:
            await EmailInfo.filter(id=email.id).update(status=new_status)
```

### 4. Token 刷新实现

**文件**: `backend/app/clients/outlook.py` 第 265-313 行

```python
async def refresh_token(self) -> int:
    """使用 refresh_token 刷新访问令牌"""
    
    # 调用微软 API 刷新 Token
    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    data = {
        "client_id": self.client_id,
        "scope": " ".join(self.SCOPES),
        "refresh_token": self.refresh_token_value,
        "grant_type": "refresh_token",
    }
    
    res = await self._req("POST", token_url, data=data, headers=headers, proxy_url=self.proxy)
    
    # 更新数据库
    email_info = await EmailInfo.get_or_none(email=self.email)
    if email_info:
        email_info.access_token = content.get("access_token")
        email_info.refresh_token = content.get("refresh_token")
        await email_info.save()  # ⭐ 这里会自动更新 update_time
    
    return 1
```

### 5. update_time 自动更新

**文件**: `backend/app/models/base.py` 第 13 行

```python
class BaseModel(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4, description='ID')
    create_time = fields.DatetimeField(auto_now_add=True, index=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now=True, description="更新时间")  # ⭐ auto_now=True
```

**关键点**: `auto_now=True` 表示每次调用 `save()` 时，`update_time` 会自动更新为当前时间。

## 完整流程

```
1. 定时任务启动（每1小时执行一次）
   ↓
2. 查询 15 天前未更新的邮箱
   SQL: SELECT * FROM email_info 
        WHERE status=1 
        AND server_id IS NOT NULL 
        AND access_token IS NOT NULL 
        AND update_time <= (NOW() - INTERVAL 15 DAY)
   ↓
3. 对每个邮箱执行检查
   ↓
4. 调用 get_emails_main('@', 1, 1)
   ↓
5. 内部调用 refresh_token()
   ↓
6. 请求微软 API 刷新 Token
   ↓
7. 更新数据库：
   - access_token (新的访问令牌)
   - refresh_token (新的刷新令牌)
   - update_time (自动更新为当前时间) ⭐
   ↓
8. 更新邮箱状态（如果检查失败）
   ↓
9. 下次定时任务不会再检查这个邮箱（因为 update_time 已更新）
```

## 环境变量配置

在 `.env` 文件中配置：

```bash
# 启用邮箱自动检查（默认关闭）
ENABLE_EMAIL_CHECK=1

# 检查间隔（小时）
EMAIL_CHECK_INTERVAL_HOURS=1
```

## 验证方法

### 1. 查看定时任务日志

```bash
tail -f backend/logs/scheduler.log
```

应该看到类似的日志：
```
INFO 2026-02-03 11:00:00 开始自动检查邮箱状态，检查 15 天前未更新的邮箱
INFO 2026-02-03 11:00:00 开始检查邮箱状态，条件: status=1, email_type=EmailType.IP_OK_TOKEN_OK, update_time: None ~ 1738483200000
DEBUG 2026-02-03 11:00:00 正在查询第 1 页，每页 10 条...
DEBUG 2026-02-03 11:00:01 第 1 页获取到 5 个邮箱，开始检查...
DEBUG 2026-02-03 11:00:01 检查邮箱 test@outlook.com: has_ip=True, has_token=True
INFO 2026-02-03 11:00:05 邮箱状态检查完成，共检查 5 个邮箱，耗时 5.23 秒
```

### 2. 查询数据库验证

```sql
-- 查看最近更新的邮箱
SELECT 
    email, 
    status, 
    update_time,
    TIMESTAMPDIFF(DAY, update_time, NOW()) as days_since_update
FROM email_info 
WHERE status = 1 
  AND server_id IS NOT NULL 
  AND access_token IS NOT NULL
ORDER BY update_time DESC 
LIMIT 10;
```

### 3. 手动触发测试

```python
import asyncio
from app.apis.v1.mail.outlook import auto_check_email_status

# 测试检查 15 天前未更新的邮箱
asyncio.run(auto_check_email_status(days=15))
```

### 4. 验证 Token 是否刷新

```sql
-- 查看某个邮箱的 Token 更新记录
SELECT 
    email,
    LEFT(access_token, 50) as token_preview,
    update_time
FROM email_info 
WHERE email = 'test@outlook.com';

-- 等待定时任务执行后再次查询，对比 update_time 和 token_preview
```

## 常见问题

### Q1: 为什么有些邮箱没有被检查？

**A**: 检查以下条件：
1. `status` 必须为 1（正常）
2. `server_id` 不能为空（必须有代理IP）
3. `access_token` 不能为空（必须有Token）
4. `update_time` 必须在 15 天前

### Q2: Token 刷新失败怎么办？

**A**: 系统会自动处理：
- 5xx 或 408 错误：自动重试 3 次
- 重试 3 次后仍失败：设置 `status=5`（需要人工处理）
- 其他错误：设置 `status=2`（异常）

### Q3: 如何修改检查间隔？

**A**: 修改环境变量：
```bash
# 每 2 小时检查一次
EMAIL_CHECK_INTERVAL_HOURS=2

# 检查 30 天前未更新的邮箱（需要修改代码）
# 在 main.py 中修改 auto_check_email_status(days=30)
```

### Q4: 如何查看哪些邮箱需要检查？

**A**: 执行 SQL 查询：
```sql
SELECT 
    email,
    status,
    update_time,
    TIMESTAMPDIFF(DAY, update_time, NOW()) as days_since_update
FROM email_info 
WHERE status = 1 
  AND server_id IS NOT NULL 
  AND access_token IS NOT NULL
  AND update_time <= DATE_SUB(NOW(), INTERVAL 15 DAY)
ORDER BY update_time ASC;
```

## 总结

✅ **功能已完整实现**

系统会自动：
1. 每 1 小时检查一次
2. 查找 15 天前未更新的邮箱
3. 自动刷新 Token
4. 自动更新 `update_time`
5. 更新邮箱状态

无需手动干预，系统会自动维护所有邮箱的 Token 有效性。

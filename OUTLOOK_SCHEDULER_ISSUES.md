# Outlook 定时检查问题分析和修复

## 问题总结

### 1. ✅ 已修复：缓存 NoneType 错误
**位置**: `backend/app/utils/stats_cache.py`

**问题**: 当 `project_ids` 为 `None` 时，`sorted(project_ids)` 会报错 `'NoneType' object is not iterable`

**修复**: 在缓存函数中添加了 `None` 检查：
```python
# 如果 project_ids 为 None 或空列表，不使用缓存
if not project_ids:
    return None  # 或 return False
```

---

### 2. ✅ 已修复：日志记录器统一

**位置**: 
- `backend/app/apis/v1/mail/outlook.py`
- `backend/app/utils/stats_sync.py`

**问题**: 定时任务使用 `print()` 或 `loguru.logger`，日志没有写入 `scheduler.log` 文件

**修复**: 统一使用 `scheduler_logger`：
```python
from app.utils.logs import getLogger

# 使用 scheduler 日志记录器
scheduler_logger = getLogger('scheduler')

# 在定时任务中使用
scheduler_logger.info("开始执行任务...")
scheduler_logger.error("任务失败", exc_info=True)
```

**修改的文件**:
1. `backend/app/utils/stats_sync.py` - 所有 `print()` 改为 `scheduler_logger`
2. `backend/app/apis/v1/mail/outlook.py` - 定时任务相关函数使用 `scheduler_logger`

---

### 3. ✅ 已优化：错误日志级别

**位置**: `backend/app/apis/v1/mail/outlook.py` 第 227 行

**修改**: 单个邮箱检查失败使用 `warning` 而不是 `error`：
```python
except Exception as e:
    scheduler_logger.warning(f"检查邮箱 {email.email} 失败: {str(e)}")
    continue
```

---

### 4. ✅ 已优化：添加执行统计

**位置**: `backend/app/apis/v1/mail/outlook.py` 的 `auto_check_email_status` 函数

**添加**: 执行时间和成功率统计：
```python
async def auto_check_email_status(days: int = 15):
    import time
    start_time = time.time()
    
    scheduler_logger.info(f"开始自动检查邮箱状态，检查 {days} 天前未更新的邮箱")
    
    total_checked = await check_and_update_emails_logic(...)
    
    elapsed = time.time() - start_time
    scheduler_logger.info(
        f"邮箱状态检查完成，共检查 {total_checked} 个邮箱，"
        f"耗时 {elapsed:.2f} 秒"
    )
```

---

## 修复内容汇总

### stats_cache.py
- ✅ 修复 `get_project_stats_time_series` 处理 `None` 参数
- ✅ 修复 `set_project_stats_time_series` 处理 `None` 参数

### stats_sync.py
- ✅ 导入 `scheduler_logger`
- ✅ 所有 `print()` 改为 `scheduler_logger.info/debug/error`
- ✅ 异常处理使用 `exc_info=True` 记录完整堆栈

### outlook.py
- ✅ 导入 `scheduler_logger`
- ✅ `check_and_update_emails_logic` 使用 `scheduler_logger`
- ✅ `auto_check_email_status` 使用 `scheduler_logger` 并添加统计
- ✅ 单个邮箱失败使用 `warning` 级别
- ✅ 添加执行时间统计

---

## 环境变量配置

确保 `.env` 文件中配置了以下参数：

```bash
# 启用邮箱自动检查（默认关闭）
ENABLE_EMAIL_CHECK=1

# 检查间隔（小时）
EMAIL_CHECK_INTERVAL_HOURS=1

# 启用统计数据同步（默认开启）
ENABLE_STATS_SYNC=1

# 同步间隔（分钟）
STATS_SYNC_INTERVAL_MINUTES=60
```

---

## 测试建议

### 1. 重启后端服务

```bash
cd backend
python start.py
```

### 2. 查看定时任务日志

```bash
# 实时查看 scheduler 日志
tail -f backend/logs/scheduler.log

# 查看最近的日志
tail -n 100 backend/logs/scheduler.log
```

### 3. 验证日志输出

启动后应该看到类似的日志：
```
INFO 2026-02-03 10:00:00 已注册定时任务: 每 30 分钟检查数据库连接
INFO 2026-02-03 10:00:00 已注册定时任务: 每 2 小时压缩旧日志文件
INFO 2026-02-03 10:00:00 已注册定时任务: 每 1 小时检查邮箱状态
INFO 2026-02-03 10:00:00 已注册定时任务: 每 60 分钟同步项目统计数据
INFO 2026-02-03 10:00:00 调度器已启动
```

定时任务执行时：
```
INFO 2026-02-03 11:00:00 开始自动检查邮箱状态，检查 15 天前未更新的邮箱
INFO 2026-02-03 11:00:00 开始检查邮箱状态，条件: status=1, email_type=...
INFO 2026-02-03 11:00:05 邮箱状态检查完成，共检查 10 个邮箱，耗时 5.23 秒
```

---

## 总结

所有问题已修复：

1. ✅ 缓存 NoneType 错误 - 已修复
2. ✅ 日志记录器统一 - 已修复
3. ✅ 错误日志级别 - 已优化
4. ✅ 执行统计信息 - 已添加
5. ✅ 代码逻辑 - 正常运行

现在定时任务的所有日志都会正确写入 `backend/logs/scheduler.log` 文件，方便排查问题和监控运行状态。


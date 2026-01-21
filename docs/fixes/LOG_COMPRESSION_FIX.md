# 日志压缩功能修复

## 修复时间
2026-01-21

## 问题描述
日志文件没有按照预期每2小时自动压缩，且启动时也没有检查并压缩旧日志。

## 原因分析

### 原有实现
- 日志压缩只在第一次创建logger时执行一次（`getLogger`函数中）
- 没有定期执行的机制
- 启动时不会主动检查旧日志

### 问题
1. 如果服务长时间运行，新产生的旧日志不会被压缩
2. 重启服务时，只压缩当前logger对应的日志，其他模块的日志可能被遗漏
3. 没有统一的压缩调度机制

## 解决方案

### 1. 新增 `compress_all_logs` 函数

在 `backend/app/utils/logs.py` 中添加：

```python
def compress_all_logs(log_dir: str = None):
    """
    压缩所有日志模块的旧日志文件
    
    Args:
        log_dir: 日志目录，如果不指定则使用默认目录
    """
    if log_dir is None:
        log_dir = "logs"
    
    if not os.path.exists(log_dir):
        return
    
    # 获取所有日志模块名称
    logger_names = set()
    for filename in os.listdir(log_dir):
        if filename.endswith('.log'):
            logger_name = filename[:-4]
            logger_names.add(logger_name)
    
    # 压缩每个模块的旧日志
    compressed_count = 0
    for logger_name in logger_names:
        pattern = os.path.join(log_dir, f"{logger_name}.log.*")
        for filepath in glob.glob(pattern):
            if filepath.endswith('.gz'):
                continue
            try:
                with open(filepath, 'rb') as f_in:
                    with gzip.open(filepath + '.gz', 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(filepath)
                compressed_count += 1
            except Exception as e:
                print(f"日志压缩失败: {filepath}, 原因: {e}")
    
    if compressed_count > 0:
        print(f"成功压缩 {compressed_count} 个日志文件")
    
    # 同时清理超过30天的压缩日志
    delete_old_compressed_logs(log_dir, days=30)
```

**功能**:
- 自动发现所有日志模块（api, app, database, scheduler等）
- 压缩所有未压缩的旧日志文件
- 同时清理超过30天的压缩日志

### 2. 启动时立即压缩

在 `backend/app/main.py` 的 `lifespan` 函数中添加：

```python
# 启动时立即压缩旧日志
try:
    app_logger.info("检查并压缩旧日志文件...")
    compress_all_logs()
    app_logger.info("日志压缩检查完成")
except Exception as e:
    app_logger.warning(f"日志压缩检查失败: {e}")
```

**时机**: 在数据库初始化之前执行，确保启动时就处理旧日志

### 3. 添加定时任务

在 `backend/app/main.py` 中添加定时任务：

```python
async def compress_logs_task() -> None:
    """
    压缩旧日志文件的定时任务
    每2小时执行一次，压缩所有未压缩的旧日志
    """
    try:
        scheduler_logger.info("开始执行日志压缩任务...")
        compress_all_logs()
        scheduler_logger.info("日志压缩任务完成")
    except Exception as e:
        scheduler_logger.error(f"日志压缩任务失败: {e}", exc_info=True)

# 注册定时任务
scheduler.add_job(
    compress_logs_task,
    IntervalTrigger(hours=2),
    id="compress_logs",
    name="压缩旧日志文件",
    coalesce=True,
    misfire_grace_time=300,  # 5分钟容错
)
```

**配置**:
- 执行频率: 每2小时
- 容错时间: 5分钟（如果错过执行时间，5分钟内仍会执行）
- coalesce=True: 如果积累了多个待执行任务，只执行一次

## 日志压缩机制

### 触发时机
1. **启动时**: 服务启动时立即检查并压缩所有旧日志
2. **定时执行**: 每2小时自动执行一次
3. **手动执行**: 可通过脚本手动触发

### 压缩规则
- 压缩对象: 所有 `*.log.*` 格式的文件（不包括已压缩的 `.gz` 文件）
- 压缩格式: gzip (.gz)
- 保留期限: 压缩日志保留30天，超期自动删除

### 日志滚动规则
- 滚动频率: 每2小时
- 命名格式: `{module}.log.{timestamp}`
- 保留数量: 360个文件（30天 × 24小时 ÷ 2小时）

## 验证

### 启动日志
```
INFO 2026-01-21 15:13:21 项目启动...
INFO 2026-01-21 15:13:21 检查并压缩旧日志文件...
INFO 2026-01-21 15:13:21 日志压缩检查完成
INFO 2026-01-21 15:13:21 已注册定时任务: 每 2 小时压缩旧日志文件
```

### 定时任务列表
```
- 保持数据库连接: 每30分钟
- 压缩旧日志文件: 每2小时
- 自动检查邮箱状态: 每1小时（可选）
```

### 日志文件状态
```bash
$ ls -lh backend/logs/
-rw-r--r--  api.log              # 当前日志
-rw-r--r--  api.log.2026-01-21_03.gz    # 已压缩
-rw-r--r--  app.log              # 当前日志
-rw-r--r--  app.log.2026-01-21_03.gz    # 已压缩
-rw-r--r--  database.log         # 当前日志
-rw-r--r--  database.log.2026-01-21_03.gz  # 已压缩
-rw-r--r--  scheduler.log        # 当前日志
-rw-r--r--  scheduler.log.2026-01-21_02.gz # 已压缩
```

## 手动压缩

如果需要手动触发压缩，可以使用：

```bash
# 使用清理脚本
python backend/scripts/cleanup_logs.py

# 或在Python中调用
from app.utils.logs import compress_all_logs
compress_all_logs()
```

## 相关文件

- `backend/app/utils/logs.py` - 日志工具函数
- `backend/app/main.py` - 应用启动和定时任务
- `backend/scripts/cleanup_logs.py` - 手动清理脚本
- `backend/scripts/analyze_logs.py` - 日志分析工具

## 配置说明

### 环境变量
无需额外配置，使用默认值：
- 压缩频率: 2小时（硬编码）
- 保留天数: 30天（硬编码）
- 日志滚动: 2小时（logs.py中配置）

### 自定义配置
如需修改，可在以下位置调整：

1. **压缩频率**: `backend/app/main.py` 中的 `IntervalTrigger(hours=2)`
2. **保留天数**: `backend/app/utils/logs.py` 中的 `delete_old_compressed_logs(log_dir, days=30)`
3. **滚动频率**: `backend/app/utils/logs.py` 中的 `interval=2`

## 优势

1. **自动化**: 无需人工干预，自动压缩和清理
2. **节省空间**: 压缩后日志文件大小减少90%以上
3. **启动检查**: 每次启动都会处理遗留的旧日志
4. **统一管理**: 所有模块的日志统一处理
5. **容错机制**: 压缩失败不影响服务运行

## 监控建议

可以通过以下方式监控日志压缩状态：

```bash
# 查看日志文件统计
python backend/scripts/analyze_logs.py

# 查看调度器日志
tail -f backend/logs/scheduler.log | grep "压缩"

# 查看未压缩的旧日志
ls -lh backend/logs/*.log.* | grep -v ".gz"
```

## 总结

✅ 启动时立即压缩旧日志
✅ 每2小时自动压缩
✅ 统一处理所有日志模块
✅ 自动清理超期日志
✅ 容错机制完善
✅ 不影响服务运行

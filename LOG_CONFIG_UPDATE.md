# 日志配置更新说明

## 更新时间
2026-02-22

## 更新内容

### 1. 日志分割策略变更

**之前**：按时间分割（每2小时一个文件）
**现在**：按文件大小分割（单个文件最大200MB）

### 2. 日志保留时间变更

**之前**：保留90天（3个月）
**现在**：保留7天

### 3. 技术实现

#### 日志处理器变更
- 从 `TimedRotatingFileHandler` 改为 `ConcurrentRotatingFileHandler`
- 支持多进程安全写入
- 单个日志文件最大：200MB
- 备份文件数量：50个（约10GB，足够7天使用）

#### 日志压缩和清理
- 旧日志自动压缩为 `.gz` 格式
- 按目录结构组织：`logs/模块名/年/月/日/`
- 定时任务每2小时执行一次压缩和清理
- 超过7天的日志自动删除

### 4. 修改的文件

1. **backend/app/utils/logs.py**
   - 修改 `getLogger()` 函数，使用 `ConcurrentRotatingFileHandler`
   - 更新 `_compress_and_organize_logs()` 函数，简化日期解析逻辑
   - 更新 `compress_all_logs()` 函数，改为7天保留期
   - 更新 `delete_old_compressed_logs()` 函数，默认保留7天

2. **backend/app/main.py**
   - 更新 `compress_logs_task()` 函数注释，说明新的日志策略
   - 更新定时任务日志输出，说明保留7天

3. **backend/scripts/cleanup_logs.py**
   - 更新默认保留天数从30天改为7天

4. **.kiro/steering/conventions.md**
   - 添加日志配置说明章节

## 优势

1. **更灵活的分割策略**
   - 不再受固定时间限制
   - 根据实际日志量动态分割
   - 避免单个文件过大

2. **节省存储空间**
   - 只保留7天日志，大幅减少磁盘占用
   - 自动压缩为 .gz 格式，压缩率约70-80%

3. **更好的性能**
   - 单个文件不会过大，读取更快
   - 多进程安全，避免写入冲突

4. **易于管理**
   - 按日期组织的目录结构，便于查找
   - 自动清理，无需手动维护

## 使用说明

### 查看日志
```bash
# 查看当前日志
tail -f logs/api.log

# 查看历史日志（已压缩）
zcat logs/api/2026/02/22/api.log.1.gz | less
```

### 手动清理日志
```bash
# 使用默认配置（保留7天）
python backend/scripts/cleanup_logs.py

# 自定义保留天数（例如保留3天）
python backend/scripts/cleanup_logs.py 3
```

### 环境变量配置
无需额外配置，日志系统会自动使用新的策略。

## 注意事项

1. **首次启动**：系统会自动压缩现有的旧日志文件
2. **磁盘空间**：确保有足够空间存储7天的日志（预计5-10GB）
3. **定时任务**：每2小时自动执行压缩和清理，无需手动干预
4. **日志查询**：超过7天的日志将被删除，如需长期保留请提前备份

## 回滚方案

如需回滚到之前的配置，修改以下内容：

1. 在 `backend/app/utils/logs.py` 中：
   - 将 `ConcurrentRotatingFileHandler` 改回 `TimedRotatingFileHandler`
   - 将保留天数从7改回90

2. 在 `backend/scripts/cleanup_logs.py` 中：
   - 将默认保留天数从7改回30

3. 在 `backend/app/main.py` 中：
   - 更新相关注释说明

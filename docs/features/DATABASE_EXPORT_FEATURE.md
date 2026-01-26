# 数据库导出功能

## 功能概述

管理员可以通过用户头像下拉菜单导出整个数据库，导出的数据会自动压缩为 ZIP 文件。

## 实现时间
2026-01-26

## 功能特性

### 1. 权限控制
- ✅ 只有 **ADMIN** 角色可以看到"导出数据"选项
- ✅ 其他角色（GM、IT、MANUAL）不显示此选项
- ✅ 后端 API 也有管理员权限验证

### 2. 导出功能
- ✅ 使用 `mysqldump` 导出完整数据库
- ✅ 自动压缩为 ZIP 文件
- ✅ 文件名包含时间戳：`database_backup_YYYYMMDD_HHMMSS.zip`
- ✅ 导出后自动清理临时文件
- ✅ 下载完成后自动删除服务器上的备份文件

### 3. 导出选项
- ✅ `--single-transaction`: 保证数据一致性
- ✅ `--quick`: 快速导出
- ✅ `--lock-tables=false`: 不锁表
- ✅ `--routines`: 导出存储过程和函数
- ✅ `--triggers`: 导出触发器
- ✅ `--events`: 导出事件

### 4. 安全特性
- ✅ 5分钟超时保护
- ✅ 异常时自动清理临时文件
- ✅ 下载后自动删除服务器文件
- ✅ 备份文件存储在独立目录 `backups/`

## 使用方法

### 前端操作

1. 以管理员身份登录系统
2. 点击右上角用户头像
3. 在下拉菜单中点击"导出数据"
4. 等待导出完成（显示加载提示）
5. 自动下载 ZIP 文件

### 文件结构

```
database_backup_20260126_143025.zip
└── database_backup_20260126_143025.sql  # 完整的 SQL 文件
```

## API 接口

### 导出数据库

**接口**: `GET /api/v1/system/export-database`

**权限**: 仅管理员（ADMIN）

**响应**: ZIP 文件流

**响应头**:
```
Content-Type: application/zip
Content-Disposition: attachment; filename="database_backup_20260126_143025.zip"
```

## 技术实现

### 前端实现

**文件**: `frontend/src/components/Layout/index.tsx`

**关键代码**:
```typescript
// 权限判断：只有管理员才显示
...(userInfo?.roles?.some((role: any) => role.code === 'ADMIN') ? [{
  key: 'export',
  icon: <DownloadOutlined />,
  label: '导出数据',
  onClick: async () => {
    // 调用导出 API
    const response = await fetch(`${API_URL}/api/v1/system/export-database`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })
    // 下载文件
    const blob = await response.blob()
    // ... 触发下载
  }
}] : [])
```

### 后端实现

**文件**: `backend/app/apis/v1/system/database.py`

**关键步骤**:
1. 验证管理员权限
2. 生成带时间戳的文件名
3. 使用 `mysqldump` 导出数据库到 SQL 文件
4. 使用 `zipfile` 压缩 SQL 文件
5. 返回 ZIP 文件流
6. 下载后自动清理临时文件

**关键代码**:
```python
@app.get("/export-database")
async def export_database(
    admin_user: dict = Depends(get_admin_user)
):
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sql_file = f"database_backup_{timestamp}.sql"
    zip_file = f"database_backup_{timestamp}.zip"
    
    # 导出数据库
    subprocess.run([
        "mysqldump",
        f"--host={DB_HOST}",
        f"--user={DB_USER}",
        f"--password={DB_PASSWORD}",
        "--single-transaction",
        DB_NAME,
    ], stdout=sql_file)
    
    # 压缩
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(sql_file)
    
    # 返回文件
    return FileResponse(zip_file)
```

## 环境要求

### 服务器要求

1. **MySQL 客户端工具**
   ```bash
   # 检查是否安装
   which mysqldump
   
   # Ubuntu/Debian 安装
   sudo apt-get install mysql-client
   
   # CentOS/RHEL 安装
   sudo yum install mysql
   
   # macOS 安装
   brew install mysql-client
   ```

2. **Python 依赖**
   - 已包含在标准库中，无需额外安装
   - `subprocess`: 执行系统命令
   - `zipfile`: ZIP 压缩

3. **磁盘空间**
   - 确保有足够空间存储临时文件
   - 临时文件会在下载后自动删除

## 错误处理

### 1. mysqldump 不存在
**错误**: `mysqldump 命令不存在`

**解决**: 安装 MySQL 客户端工具
```bash
sudo apt-get install mysql-client
```

### 2. 导出超时
**错误**: `数据库导出超时（超过5分钟）`

**原因**: 数据库太大或服务器性能不足

**解决**: 
- 增加超时时间（修改代码中的 `timeout=300`）
- 优化数据库（删除不必要的数据）
- 升级服务器配置

### 3. 权限不足
**错误**: `Access denied`

**原因**: 数据库用户权限不足

**解决**: 确保数据库用户有导出权限
```sql
GRANT SELECT, LOCK TABLES, SHOW VIEW ON database_name.* TO 'user'@'host';
FLUSH PRIVILEGES;
```

### 4. 磁盘空间不足
**错误**: `No space left on device`

**解决**: 清理磁盘空间或更换存储位置

## 安全建议

1. ✅ **定期备份**: 建议每天自动备份一次
2. ✅ **异地存储**: 将备份文件存储到其他服务器或云存储
3. ✅ **加密存储**: 对敏感数据进行加密
4. ✅ **访问控制**: 只有管理员可以导出
5. ✅ **审计日志**: 记录所有导出操作
6. ✅ **自动清理**: 定期清理旧的备份文件

## 性能优化

### 1. 大数据库优化
```python
# 分表导出
dump_command = [
    "mysqldump",
    "--single-transaction",
    "--quick",
    "--max_allowed_packet=512M",  # 增加包大小
    "--net_buffer_length=16384",  # 优化网络缓冲
    DB_NAME,
]
```

### 2. 压缩优化
```python
# 使用更高的压缩级别
with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
    zipf.write(sql_file)
```

### 3. 异步导出
```python
# 使用后台任务
from fastapi import BackgroundTasks

@app.get("/export-database")
async def export_database(
    background_tasks: BackgroundTasks,
    admin_user: dict = Depends(get_admin_user)
):
    # 添加后台任务
    background_tasks.add_task(do_export)
    return {"message": "导出任务已启动"}
```

## 未来改进

- [ ] 支持增量备份
- [ ] 支持定时自动备份
- [ ] 支持备份到云存储（S3、OSS等）
- [ ] 支持备份历史记录查看
- [ ] 支持备份文件管理（删除、下载历史备份）
- [ ] 支持备份加密
- [ ] 支持备份恢复功能
- [ ] 支持导出进度显示
- [ ] 支持选择性导出（指定表）

## 相关文档

- [系统管理 API](../../backend/app/apis/v1/system/database.py)
- [前端布局组件](../../frontend/src/components/Layout/index.tsx)
- [MySQL 备份最佳实践](https://dev.mysql.com/doc/refman/8.0/en/backup-and-recovery.html)

## 更新日志

### v1.0.0 (2026-01-26)
- ✅ 初始版本
- ✅ 支持完整数据库导出
- ✅ 自动压缩为 ZIP
- ✅ 管理员权限控制
- ✅ 自动清理临时文件

---

**状态**: ✅ 已完成  
**最后更新**: 2026-01-26  
**维护者**: Kiro AI Assistant

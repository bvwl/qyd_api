# 项目账号当天统计导出功能

## 更新时间
2026-01-25

## 功能说明

在项目账号页面新增"导出当天项目统计"按钮，可以导出当天更新过的所有项目账号统计数据。

## 功能特点

### 1. 与"导出所有项目统计"的区别

| 功能 | 导出所有项目统计 | 导出当天项目统计 |
|------|----------------|----------------|
| 数据范围 | 所有账号 | 仅当天更新的账号 |
| 项目筛选 | 包含所有项目 | 只包含当天有更新的项目 |
| 使用场景 | 全量数据分析 | 每日数据跟踪 |
| 文件大小 | 较大 | 较小 |

### 2. 统计维度

- 项目名称
- 项目状态
- 项目ID
- 所属用户
- **当天更新账号数**（只统计今天更新的账号）
- 余额统计（最高分、最低分、平均分、总分）
- 变动统计（最高分、最低分、平均分、总分）

### 3. 筛选逻辑

- 只统计 `update_time` 在今天的账号
- 如果某个项目今天没有账号更新，该项目不会出现在导出文件中
- 如果所有项目今天都没有更新，返回 404 错误

## 后端实现

### API 端点

```
GET /v1/project/account/export-today-stats
```

### 权限要求

- 仅 ADMIN 和 GM 角色可以访问

### 实现逻辑

```python
@app.get("/export-today-stats")
async def export_today_stats(current_user: dict = Depends(get_gm_user)):
    # 1. 获取今天的日期范围
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today + datetime.timedelta(days=1)
    
    # 2. 遍历所有项目
    for project in projects:
        # 3. 获取该项目当天更新的账号统计
        stats = await project_account_crud.get_stats(
            project_id=project.id,
            update_time_start=today,  # 今天开始
            update_time_end=today_end,  # 今天结束
        )
        
        # 4. 如果当天没有更新的账号，跳过该项目
        if stats.get("total_count", 0) == 0:
            continue
        
        # 5. 写入Excel
        # ...
```

### 文件命名

```
project_today_stats_YYYYMMDD_HHMMSS.xlsx
```

例如：`project_today_stats_20260125_143022.xlsx`

## 前端实现

### 按钮位置

在项目账号页面的搜索栏右侧，"导出所有项目统计"按钮旁边。

### 按钮代码

```typescript
{(isAdmin || isGM) && (
  <>
    <Button 
      type="default"
      icon={<DownloadOutlined />} 
      onClick={handleExportAllStats}
    >
      导出所有项目统计
    </Button>
    <Button 
      type="default"
      icon={<DownloadOutlined />} 
      onClick={handleExportTodayStats}
    >
      导出当天项目统计
    </Button>
  </>
)}
```

### 导出函数

```typescript
const handleExportTodayStats = async () => {
  try {
    setLoading(true)
    const blob = await exportTodayProjectStats()
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // 生成中文文件名
    const now = new Date()
    const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '')
    const timeStr = now.toTimeString().slice(0, 8).replace(/:/g, '')
    link.download = `当天项目统计_${dateStr}_${timeStr}.xlsx`
    
    // 触发下载
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    message.success('导出成功')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '导出失败')
  } finally {
    setLoading(false)
  }
}
```

## 使用方式

### 1. 访问页面

进入"项目管理" → "项目账号"页面

### 2. 点击导出

点击"导出当天项目统计"按钮

### 3. 下载文件

浏览器会自动下载 Excel 文件

### 4. 查看数据

打开 Excel 文件，查看当天更新的项目统计数据

## Excel 文件格式

### 表头

| 列名 | 说明 |
|------|------|
| 项目名称 | 项目的名称 |
| 项目状态 | 正常/未编写/编写中等 |
| 项目ID | 项目的UUID |
| 所属用户 | 项目关联的用户昵称 |
| 当天更新账号数 | 今天更新过的账号数量 |
| 余额最高分 | 账号余额的最大值 |
| 余额最低分 | 账号余额的最小值 |
| 余额平均分 | 账号余额的平均值 |
| 余额总分 | 账号余额的总和 |
| 变动最高分 | 账号变动的最大值 |
| 变动最低分 | 账号变动的最小值 |
| 变动平均分 | 账号变动的平均值 |
| 变动总分 | 账号变动的总和 |

### 样式

- 表头：蓝色背景，白色粗体文字，居中对齐
- 数据行：左对齐（前4列），居中对齐（其他列）
- 列宽：自动调整

## 错误处理

### 1. 当天没有数据

**错误信息：** "当天没有更新的账号数据"

**HTTP 状态码：** 404

**原因：** 所有项目今天都没有账号更新

**解决方案：** 等待有账号更新后再导出，或使用"导出所有项目统计"

### 2. 权限不足

**错误信息：** "没有权限"

**HTTP 状态码：** 403

**原因：** 当前用户不是 ADMIN 或 GM 角色

**解决方案：** 联系管理员分配权限

### 3. 导出失败

**错误信息：** "导出失败: xxx"

**HTTP 状态码：** 500

**原因：** 服务器内部错误

**解决方案：** 查看服务器日志，联系技术支持

## 使用场景

### 1. 每日数据跟踪

每天下班前导出当天的项目统计，跟踪项目进展。

### 2. 日报生成

将导出的数据作为日报的数据来源。

### 3. 异常监控

快速查看当天哪些项目有账号更新，哪些项目没有活动。

### 4. 性能优化

相比导出所有数据，只导出当天数据速度更快，文件更小。

## 修改的文件

### 后端（1个文件）

- `backend/app/apis/v1/project/account.py`
  - 新增 `export_today_stats` 端点

### 前端（2个文件）

- `frontend/src/api/project.ts`
  - 新增 `exportTodayProjectStats` 函数

- `frontend/src/views/Project/ProjectAccount.tsx`
  - 导入 `exportTodayProjectStats`
  - 新增 `handleExportTodayStats` 函数
  - 新增"导出当天项目统计"按钮

## 注意事项

### 1. 时区

使用服务器本地时区判断"今天"，确保服务器时区设置正确。

### 2. 更新时间

统计基于 `update_time` 字段，只要账号今天被更新过（无论是余额、状态还是其他字段），都会被统计。

### 3. 数据实时性

导出的是当前时刻的数据，如果导出后又有新的更新，需要重新导出。

### 4. 文件大小

如果项目数量很多且都有更新，文件可能较大，建议在非高峰期导出。

## 相关文档

- [项目账号管理](frontend/src/views/Project/ProjectAccount.tsx)
- [项目API](frontend/src/api/project.ts)
- [后端API](backend/app/apis/v1/project/account.py)

## 总结

"导出当天项目统计"功能提供了一个快速查看当天项目活动的方式，相比导出所有数据更加轻量和高效，特别适合日常数据跟踪和监控场景。

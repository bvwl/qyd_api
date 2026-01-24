# 导出功能更新 - 添加项目状态列和修复编码问题

## 更新日期
2026-01-25

## 更新内容

### 1. 添加项目状态列 ✅

在导出的 Excel 文件中新增"项目状态"列，显示项目的当前状态。

**位置**: 第2列（项目名称之后，项目ID之前）

**状态映射**:
| 状态值 | 显示文本 |
|--------|---------|
| NORMAL (1) | 正常 |
| NOT_WRITTEN (2) | 未编写 |
| WRITING (3) | 编写中 |
| ENDED (4) | 项目结束 |
| RUNAWAY (5) | 项目跑路 |
| MAINTENANCE (6) | 项目维护 |
| UNASSIGNED (7) | 未分配 |
| ACCOUNT_NOT_SUPPORT (8) | 账号不支持 |
| IP_NOT_SUPPORT (9) | IP不支持 |

### 2. 修复中文文件名编码错误 ✅

**问题**: 
```
'latin-1' codec can't encode characters in position 29-34: ordinal not in range(256)
```

**原因**: 
HTTP 响应头 `Content-Disposition` 使用 `filename*=UTF-8''` 格式时，某些浏览器或服务器配置可能不支持中文字符。

**解决方案**:
1. **后端**: 使用英文文件名 `project_stats_YYYYMMDD_HHMMSS.xlsx`
2. **前端**: 在下载时重命名为中文 `项目统计汇总_YYYYMMDD_HHMMSS.xlsx`

这样既避免了编码问题，又保证了用户看到的是中文文件名。

## 更新后的 Excel 表格结构

| 列序号 | 列名 | 宽度 | 对齐 | 说明 |
|--------|------|------|------|------|
| 1 | 项目名称 | 20 | 左 | 项目的名称 |
| **2** | **项目状态** | **12** | **左** | **项目的当前状态** |
| 3 | 项目ID | 38 | 左 | 项目的UUID |
| 4 | 所属用户 | 25 | 左 | 用户昵称（多个用逗号分隔） |
| 5 | 账号数量 | 12 | 中 | 该项目下的账号总数 |
| 6 | 余额最高分 | 12 | 中 | 当前余额的最大值 |
| 7 | 余额最低分 | 12 | 中 | 当前余额的最小值 |
| 8 | 余额平均分 | 12 | 中 | 当前余额的平均值 |
| 9 | 余额总分 | 12 | 中 | 当前余额的总和 |
| 10 | 变动最高分 | 12 | 中 | 变动余额的最大值 |
| 11 | 变动最低分 | 12 | 中 | 变动余额的最小值 |
| 12 | 变动平均分 | 12 | 中 | 变动余额的平均值 |
| 13 | 变动总分 | 12 | 中 | 变动余额的总和 |

## 技术实现

### 1. 项目状态映射

```python
from app.models.project import ProjectStatus

status_map = {
    ProjectStatus.NORMAL: "正常",
    ProjectStatus.NOT_WRITTEN: "未编写",
    ProjectStatus.WRITING: "编写中",
    ProjectStatus.ENDED: "项目结束",
    ProjectStatus.RUNAWAY: "项目跑路",
    ProjectStatus.MAINTENANCE: "项目维护",
    ProjectStatus.UNASSIGNED: "未分配",
    ProjectStatus.ACCOUNT_NOT_SUPPORT: "账号不支持",
    ProjectStatus.IP_NOT_SUPPORT: "IP不支持",
}

status_text = status_map.get(project.status, "未知")
```

### 2. 文件名编码修复

**后端**:
```python
# 使用英文文件名
filename = f"project_stats_{now}.xlsx"

# 简化响应头
headers={
    "Content-Disposition": f"attachment; filename={filename}",
    "Access-Control-Expose-Headers": "Content-Disposition"
}
```

**前端**:
```typescript
// 在前端重命名为中文
const now = new Date()
const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '')
const timeStr = now.toTimeString().slice(0, 8).replace(/:/g, '')
link.download = `项目统计汇总_${dateStr}_${timeStr}.xlsx`
```

### 3. 列宽和对齐调整

```python
# 列宽（添加项目状态列）
column_widths = [20, 12, 38, 25, 12, 12, 12, 12, 12, 12, 12, 12, 12]

# 对齐方式（前4列左对齐）
cell.alignment = Alignment(
    horizontal="left" if col_num <= 4 else "center", 
    vertical="center"
)
```

## 示例数据

### 示例1：正常项目
```
项目名称: 测试项目A
项目状态: 正常
项目ID: 2e6053b7-82d8-4632-a8d7-90479af9d67d
所属用户: 张三
账号数量: 50
...
```

### 示例2：编写中项目
```
项目名称: 测试项目B
项目状态: 编写中
项目ID: 3f7164c8-93e9-5743-b8e8-01580bg0e78e
所属用户: 张三, 李四
账号数量: 100
...
```

### 示例3：项目结束
```
项目名称: 测试项目C
项目状态: 项目结束
项目ID: 4g8275d9-a4fa-6854-c9f9-12691ch1f89f
所属用户: 未分配
账号数量: 0
...
```

## 文件命名

### 后端生成（英文）
```
project_stats_20260125_143025.xlsx
```

### 前端重命名（中文）
```
项目统计汇总_20260125_143025.xlsx
```

用户最终看到的文件名是中文的，但传输过程中使用英文，避免编码问题。

## 编码问题详解

### 问题原因

HTTP 响应头 `Content-Disposition` 有两种格式：

1. **简单格式**（仅支持 ASCII）:
   ```
   Content-Disposition: attachment; filename=file.xlsx
   ```

2. **RFC 2231 格式**（支持 UTF-8）:
   ```
   Content-Disposition: attachment; filename*=UTF-8''文件名.xlsx
   ```

问题在于：
- RFC 2231 格式需要对中文进行 URL 编码
- 某些服务器或浏览器可能不完全支持
- FastAPI 的 `StreamingResponse` 在处理时可能出现编码错误

### 解决方案对比

#### 方案1：URL 编码（复杂，可能失败）
```python
from urllib.parse import quote
filename = quote("项目统计汇总.xlsx")
headers = {
    "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
}
```
**问题**: 仍可能在某些环境下失败

#### 方案2：英文文件名 + 前端重命名（推荐）✅
```python
# 后端：英文文件名
filename = "project_stats_20260125.xlsx"
headers = {
    "Content-Disposition": f"attachment; filename={filename}"
}
```

```typescript
// 前端：重命名为中文
link.download = `项目统计汇总_${dateStr}.xlsx`
```
**优点**: 
- 完全避免编码问题
- 用户看到的是中文文件名
- 兼容性最好

## 测试步骤

### 1. 测试项目状态显示

1. 在数据库中创建不同状态的项目
2. 执行导出
3. 打开 Excel 文件
4. 检查"项目状态"列是否正确显示中文状态

### 2. 测试文件名

1. 执行导出
2. 检查下载的文件名是否为中文
3. 检查文件名格式是否正确（`项目统计汇总_YYYYMMDD_HHMMSS.xlsx`）

### 3. 测试编码问题

1. 在不同浏览器中测试（Chrome、Firefox、Safari、Edge）
2. 确认没有编码错误
3. 确认文件可以正常打开

## 更新的文件

### 后端
- `backend/app/apis/v1/project/account.py` - 添加项目状态列，修复编码问题

### 前端
- `frontend/src/views/Project/ProjectAccount.tsx` - 优化文件名生成

### 文档
- `EXPORT_STATUS_COLUMN_AND_FIX.md` - 本更新说明（新增）

## 完成状态

✅ 添加项目状态列
✅ 状态映射为中文
✅ 修复文件名编码错误
✅ 优化文件名生成
✅ 调整列宽和对齐
✅ 更新文档

## 测试清单

- [ ] 项目状态显示正确
- [ ] 所有状态都能正确映射
- [ ] 文件名为中文
- [ ] 文件名格式正确
- [ ] 没有编码错误
- [ ] Chrome 浏览器正常
- [ ] Firefox 浏览器正常
- [ ] Safari 浏览器正常
- [ ] Edge 浏览器正常
- [ ] Excel 文件可以正常打开

## 常见问题

### Q1: 为什么不直接在后端使用中文文件名？

**A**: 因为 HTTP 响应头对中文支持不完善，容易出现编码错误。在前端重命名是最可靠的方案。

### Q2: 如果项目状态是未知值怎么办？

**A**: 会显示"未知"。这种情况通常不会发生，因为数据库中的状态都是预定义的枚举值。

### Q3: 文件名中的时间格式可以修改吗？

**A**: 可以。在前端代码中修改 `dateStr` 和 `timeStr` 的格式即可。

### Q4: 为什么前4列左对齐？

**A**: 
- 项目名称、项目状态、项目ID、所属用户都是文本信息
- 文本信息左对齐更符合阅读习惯
- 数值信息（账号数量、分数等）居中对齐便于对比

## 扩展建议

1. **状态筛选导出**: 支持按项目状态筛选导出
2. **状态颜色标识**: 在 Excel 中为不同状态添加颜色
3. **状态统计**: 在文件末尾添加状态汇总统计
4. **自定义状态**: 支持用户自定义项目状态

## 相关文档

- [导出功能完整说明](./EXPORT_FEATURE_COMPLETE.md)
- [用户列更新说明](./EXPORT_USER_COLUMN_UPDATE.md)
- [快速参考](./QUICK_REFERENCE_EXPORT.md)

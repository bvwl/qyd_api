# 项目统计数据导出功能

## 功能概述

为 ADMIN 和 GM 角色添加一键导出所有项目统计数据为 Excel 文件的功能。

## 实现内容

### 1. 后端实现

#### 1.1 安装依赖

**文件**: `backend/requirements.txt`

添加 `openpyxl` 库用于生成 Excel 文件：
```
openpyxl
```

安装命令：
```bash
cd backend
pip install openpyxl
```

#### 1.2 导出接口

**文件**: `backend/app/apis/v1/project/account.py`

新增导出接口：
```
GET /v1/project/account/export-all-stats
```

**权限控制**:
- 仅 ADMIN/GM 可以访问（使用 `get_gm_user` 依赖）

**功能说明**:
1. 获取所有项目列表
2. 遍历每个项目，调用统计方法获取数据
3. 使用 openpyxl 创建 Excel 工作簿
4. 设置表头样式（蓝色背景、白色粗体文字、居中对齐）
5. 写入每个项目的统计数据
6. 返回 Excel 文件流供下载

**Excel 表格结构**:
| 列名 | 说明 |
|------|------|
| 项目名称 | 项目的名称 |
| 项目ID | 项目的UUID |
| 所属用户 | 项目关联的用户昵称（多个用户用逗号分隔，未分配显示"未分配"） |
| 账号数量 | 该项目下的账号总数 |
| 余额最高分 | 当前余额的最大值 |
| 余额最低分 | 当前余额的最小值 |
| 余额平均分 | 当前余额的平均值 |
| 余额总分 | 当前余额的总和 |
| 变动最高分 | 变动余额的最大值 |
| 变动最低分 | 变动余额的最小值 |
| 变动平均分 | 变动余额的平均值 |
| 变动总分 | 变动余额的总和 |

**文件命名**:
- 格式：`项目统计汇总_YYYYMMDD_HHMMSS.xlsx`
- 示例：`项目统计汇总_20260125_143025.xlsx`

**响应类型**:
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Content-Disposition: `attachment; filename*=UTF-8''项目统计汇总_20260125_143025.xlsx`

#### 1.3 Excel 样式设置

**表头样式**:
- 背景色：蓝色 (#4472C4)
- 字体：白色、粗体、11号
- 对齐：水平和垂直居中

**列宽设置**:
- 项目名称：20
- 项目ID：38
- 所属用户：25
- 其他列：12

**数据格式**:
- 数值保留2位小数
- 项目名称、项目ID、所属用户左对齐
- 其他数据居中对齐
- 多个用户用逗号和空格分隔（如："张三, 李四, 王五"）
- 未分配用户的项目显示"未分配"

### 2. 前端实现

#### 2.1 API 调用

**文件**: `frontend/src/api/project.ts`

新增导出 API：
```typescript
export const exportAllProjectStats = () => {
  return api.get('/v1/project/account/export-all-stats', {
    responseType: 'blob'
  })
}
```

**关键点**:
- 使用 `responseType: 'blob'` 接收二进制文件流

#### 2.2 页面功能

**文件**: `frontend/src/views/Project/ProjectAccount.tsx`

**新增功能**:
1. 导入 `DownloadOutlined` 图标
2. 导入 `exportAllProjectStats` API
3. 添加 `handleExportAllStats` 处理函数
4. 添加"导出所有项目统计"按钮

**导出按钮**:
- 位置：搜索栏右侧，"统计分析"按钮旁边
- 图标：下载图标 (DownloadOutlined)
- 文字：导出所有项目统计
- 权限：仅 ADMIN 和 GM 可见

**导出流程**:
1. 点击按钮，显示加载状态
2. 调用后端接口获取 Excel 文件流
3. 创建 Blob URL
4. 创建隐藏的 `<a>` 标签
5. 设置下载文件名（包含时间戳）
6. 触发点击下载
7. 清理临时 URL 和 DOM 元素
8. 显示成功提示

**文件命名**:
- 格式：`项目统计汇总_YYYYMMDDHHMMSS.xlsx`
- 示例：`项目统计汇总_20260125143025.xlsx`

#### 2.3 错误处理

- 网络错误：显示"导出失败"提示
- 权限错误：后端返回 403，前端显示错误详情
- 无数据：后端返回 404，前端显示"没有项目数据"

## 技术要点

### 1. 文件流下载

**后端**:
```python
from fastapi.responses import StreamingResponse
from io import BytesIO

excel_file = BytesIO()
wb.save(excel_file)
excel_file.seek(0)

return StreamingResponse(
    excel_file,
    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    headers={
        "Content-Disposition": f"attachment; filename*=UTF-8''{filename}",
        "Access-Control-Expose-Headers": "Content-Disposition"
    }
)
```

**前端**:
```typescript
const blob = await exportAllProjectStats()
const url = window.URL.createObjectURL(blob)
const link = document.createElement('a')
link.href = url
link.download = filename
document.body.appendChild(link)
link.click()
document.body.removeChild(link)
window.URL.revokeObjectURL(url)
```

### 2. Excel 样式设置

```python
from openpyxl.styles import Font, Alignment, PatternFill

# 表头样式
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
header_font = Font(color="FFFFFF", bold=True, size=11)
header_alignment = Alignment(horizontal="center", vertical="center")

cell.fill = header_fill
cell.font = header_font
cell.alignment = header_alignment
```

### 3. 权限控制

**后端**:
```python
async def export_all_stats(
    current_user: dict = Depends(get_gm_user)  # 仅 ADMIN/GM
):
```

**前端**:
```typescript
{(isAdmin || isGM) && (
  <Button onClick={handleExportAllStats}>
    导出所有项目统计
  </Button>
)}
```

### 4. 异常处理

**后端**:
- 如果某个项目统计失败，记录错误但继续处理其他项目
- 使用 try-except 包裹每个项目的统计逻辑
- 最终返回所有成功统计的项目数据

**前端**:
- 使用 try-catch 捕获错误
- 显示友好的错误提示
- 确保加载状态正确关闭

## 使用步骤

### 1. 安装依赖

```bash
cd backend
pip install openpyxl
```

### 2. 重启后端服务

```bash
cd backend
python start.py
```

### 3. 测试功能

1. 使用 ADMIN 或 GM 账号登录
2. 访问项目账号页面：`http://localhost:3000/project/account`
3. 点击"导出所有项目统计"按钮
4. 等待下载完成
5. 打开 Excel 文件查看数据

### 4. 验证权限

1. 使用 IT 或 MANUAL 账号登录
2. 访问项目账号页面
3. 确认"导出所有项目统计"按钮不可见

## 注意事项

1. **性能考虑**：
   - 如果项目数量很多（>100个），导出可能需要较长时间
   - 建议在后台异步处理或添加进度提示
   - 可以考虑添加缓存机制

2. **数据精度**：
   - 所有数值保留2位小数
   - 使用 Decimal 类型确保精度

3. **文件大小**：
   - Excel 文件大小取决于项目数量
   - 一般情况下，100个项目约 10-20KB

4. **浏览器兼容性**：
   - 使用标准的 Blob API
   - 支持所有现代浏览器
   - IE11 可能需要 polyfill

5. **错误恢复**：
   - 如果某个项目统计失败，不影响其他项目
   - 错误会在后端日志中记录
   - 前端只显示成功导出的提示

## 扩展功能建议

1. **筛选导出**：
   - 支持按项目状态筛选
   - 支持按时间范围筛选
   - 支持选择特定项目导出

2. **格式选项**：
   - 支持导出为 CSV 格式
   - 支持导出为 PDF 格式
   - 支持自定义列显示

3. **定时导出**：
   - 支持定时自动导出
   - 支持邮件发送导出文件
   - 支持保存历史导出记录

4. **数据可视化**：
   - 在 Excel 中添加图表
   - 添加数据透视表
   - 添加条件格式

## 相关文件

### 后端
- `backend/requirements.txt` - 添加 openpyxl 依赖
- `backend/app/apis/v1/project/account.py` - 导出接口实现

### 前端
- `frontend/src/api/project.ts` - API 调用
- `frontend/src/views/Project/ProjectAccount.tsx` - 页面功能

## 完成状态

✅ 后端依赖安装
✅ 后端导出接口
✅ Excel 样式设置
✅ 前端 API 调用
✅ 前端导出按钮
✅ 权限控制
✅ 错误处理
✅ 文件下载功能

## 测试清单

- [ ] ADMIN 用户可以看到导出按钮
- [ ] GM 用户可以看到导出按钮
- [ ] IT 用户看不到导出按钮
- [ ] MANUAL 用户看不到导出按钮
- [ ] 点击导出按钮可以下载 Excel 文件
- [ ] Excel 文件包含所有项目的统计数据
- [ ] Excel 表头样式正确
- [ ] 数据格式正确（2位小数）
- [ ] 文件名包含时间戳
- [ ] 导出失败时显示错误提示

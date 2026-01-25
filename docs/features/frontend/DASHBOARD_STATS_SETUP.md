# 仪表盘统计功能 - 前端设置指南

## 功能说明

在仪表盘中添加了项目账号更新趋势图表，支持：

- ✅ 显示最近N天的项目账号更新数量
- ✅ 支持7天、14天、30天、90天切换
- ✅ 使用ECharts绘制曲线图
- ✅ 权限控制：ADMIN/GM看所有项目，IT/MANUAL看自己的项目
- ✅ 管理员可清除缓存

## 安装依赖

### 1. 安装ECharts

```bash
cd frontend
npm install echarts
```

或使用yarn:

```bash
cd frontend
yarn add echarts
```

### 2. 安装ECharts类型定义（可选）

```bash
npm install --save-dev @types/echarts
```

## 文件说明

### 新增文件

1. **frontend/src/views/Dashboard/ProjectStatsChart.tsx**
   - 项目统计图表组件
   - 使用ECharts绘制曲线图
   - 支持时间范围切换
   - 支持缓存清除（管理员）

### 修改文件

2. **frontend/src/api/project.ts**
   - 添加了统计相关的API接口
   - `getProjectStatsForDashboard()` - 获取仪表盘统计数据
   - `getProjectTodayCount()` - 获取项目今天的更新数量
   - `clearStatsCache()` - 清除统计缓存
   - `syncStatsData()` - 手动同步统计数据

3. **frontend/src/views/Dashboard/index.tsx**
   - 导入 `ProjectStatsChart` 组件
   - 在统计卡片和项目列表之间添加图表

## 使用方法

### 1. 启动开发服务器

```bash
cd frontend
npm run dev
```

### 2. 访问仪表盘

打开浏览器访问 `http://localhost:3000/dashboard`（或你配置的端口）

### 3. 查看统计图表

- 图表会自动加载最近7天的数据
- 可以通过下拉菜单切换时间范围
- 点击"刷新"按钮重新加载数据
- 管理员可以点击"清除缓存"按钮清除Redis缓存

## API接口

### 1. 获取仪表盘统计数据

```typescript
import { getProjectStatsForDashboard } from '@/api/project'

const response = await getProjectStatsForDashboard({ days: 7 })

// 响应格式
{
  code: 1,
  message: "成功",
  data: [
    {
      project_id: "xxx",
      project_name: "项目A",
      dates: ["2026-01-19", "2026-01-20", ..., "2026-01-25"],
      counts: [10, 15, 20, 18, 25, 30, 28]
    }
  ]
}
```

### 2. 清除统计缓存（仅管理员）

```typescript
import { clearStatsCache } from '@/api/project'

// 清除所有缓存
await clearStatsCache()

// 清除指定项目的缓存
await clearStatsCache('project-id')
```

### 3. 手动同步统计数据（仅管理员）

```typescript
import { syncStatsData } from '@/api/project'

// 同步最近30天的数据
await syncStatsData(30)
```

## 组件使用

### ProjectStatsChart 组件

```typescript
import ProjectStatsChart from '@/views/Dashboard/ProjectStatsChart'

// 在Dashboard中使用
<ProjectStatsChart />
```

**Props**: 无（组件内部管理状态）

**Features**:
- 自动加载数据
- 响应式设计
- 支持时间范围切换
- 管理员可清除缓存
- 加载状态显示
- 错误处理

## 图表配置

### ECharts配置

```typescript
const option: echarts.EChartsOption = {
  title: {
    text: '项目账号更新趋势',
    left: 'center'
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross'
    }
  },
  legend: {
    data: statsData.map(item => item.project_name),
    top: 35,
    type: 'scroll'
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: dates
  },
  yAxis: {
    type: 'value',
    name: '更新数量'
  },
  series: statsData.map(item => ({
    name: item.project_name,
    type: 'line',
    data: item.counts,
    smooth: true
  }))
}
```

### 自定义配置

可以在 `ProjectStatsChart.tsx` 中修改图表配置：

- **颜色主题**: 修改 `series` 中的 `itemStyle.color`
- **线条样式**: 修改 `lineStyle.width` 和 `smooth`
- **图表高度**: 修改 `style.height`
- **时间范围选项**: 修改 `Select` 的 `options`

## 权限控制

### 数据权限

- **ADMIN/GM**: 可以看到所有项目的统计数据
- **IT/MANUAL**: 只能看到分配给自己的项目的统计数据

### 功能权限

- **清除缓存**: 仅 ADMIN 可见和使用
- **同步数据**: 仅 ADMIN 可见和使用（通过API）

### 实现方式

```typescript
// 检查是否是管理员
const isAdmin = userInfo?.roles?.some(role => role.code === 'ADMIN') || false

// 条件渲染
{isAdmin && (
  <Button
    icon={<ClearOutlined />}
    onClick={handleClearCache}
  >
    清除缓存
  </Button>
)}
```

## 样式定制

### 图表容器

```typescript
<div
  ref={chartRef}
  style={{
    width: '100%',
    height: 400,
    minHeight: 400
  }}
/>
```

### Card样式

```typescript
<Card
  title="项目账号更新趋势"
  extra={/* 操作按钮 */}
>
  {/* 图表内容 */}
</Card>
```

## 性能优化

### 1. 图表实例复用

```typescript
const chartInstance = useRef<ECharts | null>(null)

useEffect(() => {
  if (chartRef.current && !chartInstance.current) {
    chartInstance.current = echarts.init(chartRef.current)
  }
}, [])
```

### 2. 窗口大小监听

```typescript
const handleResize = () => {
  chartInstance.current?.resize()
}
window.addEventListener('resize', handleResize)
```

### 3. 组件卸载清理

```typescript
return () => {
  window.removeEventListener('resize', handleResize)
  chartInstance.current?.dispose()
  chartInstance.current = null
}
```

## 故障排查

### 问题1: 图表不显示

**检查**:
- ECharts是否已安装: `npm list echarts`
- 容器是否有高度: 检查 `style.height`
- 数据是否加载成功: 查看控制台

**解决**:
```bash
npm install echarts
```

### 问题2: 数据加载失败

**检查**:
- 后端服务是否启动
- API接口是否正确
- 网络请求是否成功

**解决**:
- 查看浏览器控制台的网络请求
- 检查后端日志

### 问题3: 权限错误

**检查**:
- 用户是否已登录
- Token是否有效
- 用户角色是否正确

**解决**:
- 重新登录
- 检查用户角色配置

## 扩展功能

### 1. 添加数据导出

```typescript
const handleExport = () => {
  // 导出图表为图片
  const url = chartInstance.current?.getDataURL({
    type: 'png',
    pixelRatio: 2,
    backgroundColor: '#fff'
  })
  
  // 下载图片
  const link = document.createElement('a')
  link.href = url
  link.download = 'project-stats.png'
  link.click()
}
```

### 2. 添加数据表格

```typescript
<Table
  dataSource={data}
  columns={[
    { title: '项目名称', dataIndex: 'project_name' },
    { title: '总更新数', render: (_, record) => record.counts.reduce((a, b) => a + b, 0) }
  ]}
/>
```

### 3. 添加实时更新

```typescript
useEffect(() => {
  const timer = setInterval(() => {
    loadData()
  }, 60000) // 每分钟刷新一次
  
  return () => clearInterval(timer)
}, [])
```

## 相关文档

- **后端文档**: `项目统计功能-完整实现总结.md`
- **API文档**: `PROJECT_STATS_DASHBOARD.md`
- **定时任务**: `项目统计定时任务配置.md`

## 完成日期

2026-01-25

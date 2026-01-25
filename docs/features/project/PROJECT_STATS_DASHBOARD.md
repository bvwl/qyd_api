# 项目统计仪表盘功能

## 功能概述

实现项目账号更新数量的统计和展示功能，支持：

1. **曲线图展示**：显示每个项目最近N天的账号更新数量
2. **权限控制**：
   - ADMIN/GM：可以看到所有项目的统计数据
   - IT/MANUAL：只能看到分配给自己的项目的统计数据
3. **Redis缓存**：使用Redis 10号数据库缓存统计结果，提升性能
4. **实时统计**：支持实时查询和缓存更新

## 技术方案

### 不需要额外创建模型

采用**实时查询 + Redis缓存**的方案，优点：

- ✅ 不增加数据冗余
- ✅ 数据始终准确（基于 `update_time` 字段）
- ✅ 灵活的查询条件（支持任意天数）
- ✅ Redis缓存提升性能（5分钟缓存）

### Redis数据库分配

- **Redis DB 0**：队列数据
- **Redis DB 10**：统计缓存（本功能使用）

这样可以避免不同功能的Redis数据冲突。

## 文件结构

```
backend/
├── app/
│   ├── schemas/
│   │   └── project/
│   │       └── stats.py              # 统计相关Schema
│   ├── crud/
│   │   └── project/
│   │       └── stats.py              # 统计CRUD
│   ├── apis/
│   │   └── v1/
│   │       └── project/
│   │           ├── stats.py          # 统计API
│   │           └── __init__.py       # 注册路由
│   └── utils/
│       └── stats_cache.py            # 统计缓存工具
├── test_project_stats.py             # 测试脚本
└── test_stats_api.sh                 # API测试脚本
```

## API接口

### 1. 获取仪表盘统计数据

**接口**: `GET /v1/project/stats/dashboard`

**参数**:
- `days`: 查询最近N天的数据（1-90天，默认7天）

**权限**:
- ADMIN/GM：返回所有项目的统计数据
- IT/MANUAL：只返回分配给自己的项目的统计数据

**响应示例**:
```json
{
  "code": 1,
  "message": "成功",
  "data": [
    {
      "project_id": "xxx-xxx-xxx",
      "project_name": "项目A",
      "dates": ["2026-01-19", "2026-01-20", "2026-01-21", "2026-01-22", "2026-01-23", "2026-01-24", "2026-01-25"],
      "counts": [10, 15, 20, 18, 25, 30, 28]
    },
    {
      "project_id": "yyy-yyy-yyy",
      "project_name": "项目B",
      "dates": ["2026-01-19", "2026-01-20", "2026-01-21", "2026-01-22", "2026-01-23", "2026-01-24", "2026-01-25"],
      "counts": [5, 8, 12, 10, 15, 18, 20]
    }
  ]
}
```

**前端使用示例（ECharts）**:
```typescript
import * as echarts from 'echarts';

// 获取统计数据
const response = await getProjectStats({ days: 7 });
const data = response.data;

// 配置ECharts
const option = {
  title: {
    text: '项目账号更新趋势'
  },
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: data.map(item => item.project_name)
  },
  xAxis: {
    type: 'category',
    data: data[0]?.dates || []
  },
  yAxis: {
    type: 'value',
    name: '更新数量'
  },
  series: data.map(item => ({
    name: item.project_name,
    type: 'line',
    data: item.counts,
    smooth: true
  }))
};

// 渲染图表
const chart = echarts.init(document.getElementById('chart'));
chart.setOption(option);
```

### 2. 获取项目今天的更新数量

**接口**: `GET /v1/project/stats/project/{project_id}/today`

**参数**:
- `project_id`: 项目ID（路径参数）

**权限**:
- ADMIN/GM：可以查看所有项目
- IT/MANUAL：只能查看分配给自己的项目

**响应示例**:
```json
{
  "code": 1,
  "message": "成功",
  "data": {
    "project_id": "xxx-xxx-xxx",
    "today_count": 28
  }
}
```

### 3. 清除统计缓存

**接口**: `POST /v1/project/stats/cache/clear`

**参数**:
- `project_id`: 项目ID（可选，不传则清除所有缓存）

**权限**:
- 仅 ADMIN 可以清除缓存

**响应示例**:
```json
{
  "code": 1,
  "message": "所有统计缓存已清除"
}
```

## 缓存策略

### 缓存键格式

```
stats:project:{project_id}:daily:{date}           # 单个项目每日统计
stats:time_series:{hash}:days:{days}              # 时间序列数据
```

### 缓存过期时间

- **每日统计**: 24小时（当天数据可能会更新）
- **时间序列**: 5分钟（仪表盘数据，需要较快更新）

### 缓存更新策略

1. **被动更新**: 缓存过期后，下次查询时重新生成
2. **主动清除**: 管理员可以手动清除缓存
3. **实时计数**: 支持使用 `increment_project_daily_count()` 实时增加计数

## 测试

### 1. 测试缓存和CRUD

```bash
python backend/test_project_stats.py
```

**测试内容**:
- Redis缓存读写
- 计数器增加
- 缓存清除
- 统计数据查询
- 缓存性能对比

### 2. 测试API接口

```bash
# 需要先启动后端服务
python backend/start.py

# 在另一个终端运行测试
bash backend/test_stats_api.sh
```

**测试内容**:
- 获取仪表盘统计数据（7天）
- 获取仪表盘统计数据（30天）
- 获取项目今天的更新数量
- 清除统计缓存
- 验证缓存清除效果

## 性能优化

### 1. Redis缓存

使用Redis缓存统计结果，避免频繁查询数据库：

- **首次查询**: 查询数据库 → 写入缓存 → 返回结果
- **后续查询**: 直接从缓存读取 → 返回结果
- **性能提升**: 约 10-50x（取决于数据量）

### 2. 数据库查询优化

```python
# 一次查询获取所有数据，避免N+1问题
accounts = await db_read(ProjectAccount).filter(
    update_time__gte=start_date,
    update_time__lte=end_date
).all()

# 在内存中统计，避免多次数据库查询
for account in accounts:
    # 统计逻辑
    ...
```

### 3. 批量查询

支持一次查询多个项目的统计数据，减少API调用次数。

## 前端集成

### 1. API定义

```typescript
// src/api/project.ts

export interface ProjectStatsTimeSeries {
  project_id: string;
  project_name: string;
  dates: string[];
  counts: number[];
}

export interface DashboardStatsResponse {
  code: number;
  message: string;
  data: ProjectStatsTimeSeries[];
}

// 获取仪表盘统计数据
export const getProjectStats = (params: { days: number }) => {
  return api.get<any, DashboardStatsResponse>('/v1/project/stats/dashboard', { params });
};

// 获取项目今天的更新数量
export const getProjectTodayCount = (projectId: string) => {
  return api.get(`/v1/project/stats/project/${projectId}/today`);
};
```

### 2. 仪表盘组件

```typescript
// src/views/Dashboard/ProjectStatsChart.tsx

import React, { useEffect, useState } from 'react';
import { Card, Select, Spin } from 'antd';
import * as echarts from 'echarts';
import { getProjectStats } from '@/api/project';

const ProjectStatsChart: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [days, setDays] = useState(7);
  const [chart, setChart] = useState<echarts.ECharts | null>(null);

  useEffect(() => {
    // 初始化图表
    const chartInstance = echarts.init(document.getElementById('stats-chart')!);
    setChart(chartInstance);

    return () => {
      chartInstance.dispose();
    };
  }, []);

  useEffect(() => {
    if (chart) {
      loadData();
    }
  }, [chart, days]);

  const loadData = async () => {
    setLoading(true);
    try {
      const response = await getProjectStats({ days });
      const data = response.data;

      // 配置图表
      const option = {
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
          data: data.map(item => item.project_name),
          top: 30,
          type: 'scroll'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: data[0]?.dates || []
        },
        yAxis: {
          type: 'value',
          name: '更新数量'
        },
        series: data.map(item => ({
          name: item.project_name,
          type: 'line',
          data: item.counts,
          smooth: true,
          emphasis: {
            focus: 'series'
          }
        }))
      };

      chart?.setOption(option);
    } catch (error) {
      console.error('加载统计数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card
      title="项目账号更新趋势"
      extra={
        <Select
          value={days}
          onChange={setDays}
          style={{ width: 120 }}
          options={[
            { label: '最近7天', value: 7 },
            { label: '最近14天', value: 14 },
            { label: '最近30天', value: 30 },
            { label: '最近90天', value: 90 }
          ]}
        />
      }
    >
      <Spin spinning={loading}>
        <div id="stats-chart" style={{ width: '100%', height: 400 }} />
      </Spin>
    </Card>
  );
};

export default ProjectStatsChart;
```

### 3. 添加到仪表盘

```typescript
// src/views/Dashboard/index.tsx

import ProjectStatsChart from './ProjectStatsChart';

const Dashboard: React.FC = () => {
  return (
    <div>
      {/* 其他仪表盘组件 */}
      
      {/* 项目统计图表 */}
      <ProjectStatsChart />
    </div>
  );
};
```

## 环境配置

确保 `.env` 文件中配置了Redis：

```env
# Redis配置
REDIS_ENABLED=1
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=your_password
REDIS_DB=0  # 队列使用0号数据库，统计自动使用10号数据库
```

## 常见问题

### 1. Redis连接失败

**问题**: 统计缓存Redis连接失败

**解决**:
- 检查Redis服务是否启动
- 检查 `.env` 中的Redis配置
- 确保Redis支持多数据库（默认支持16个数据库）

### 2. 缓存不生效

**问题**: 每次查询都很慢，缓存似乎不生效

**解决**:
- 检查Redis是否正常运行
- 查看日志，确认缓存是否写入成功
- 手动清除缓存后重试

### 3. 数据不准确

**问题**: 统计数据与实际不符

**解决**:
- 清除缓存：`POST /v1/project/stats/cache/clear`
- 检查 `update_time` 字段是否正确更新
- 确认时区设置正确（Asia/Shanghai）

## 扩展功能

### 1. 实时计数

在账号更新时，实时增加计数：

```python
from app.utils.stats_cache import stats_cache

# 在账号更新后
await stats_cache.increment_project_daily_count(project_id)
```

### 2. 更多统计维度

可以扩展统计其他维度：

- 按账号类型统计
- 按账号状态统计
- 按用户统计
- 按服务器统计

### 3. 导出功能

添加统计数据导出功能：

```python
@app.get("/export")
async def export_stats(days: int = 7):
    # 导出为Excel
    ...
```

## 总结

✅ **功能完整**
- 支持曲线图展示
- 权限控制完善
- Redis缓存优化性能

✅ **架构合理**
- 不需要额外模型
- 实时查询 + 缓存
- 使用独立的Redis数据库

✅ **易于集成**
- RESTful API
- 完整的前端示例
- 详细的文档

**实现日期**: 2026-01-25

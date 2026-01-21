# 时间范围查询功能指南

## 概述
后端API已全面支持创建时间和更新时间的范围查询，前端需要添加时间选择器组件。

## 后端API支持

所有列表API都支持以下时间范围参数：
- `create_time_start` - 创建时间开始（支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳）
- `create_time_end` - 创建时间结束
- `update_time_start` - 更新时间开始
- `update_time_end` - 更新时间结束

## 前端实现

### 1. 安装依赖
Ant Design的DatePicker组件已包含在antd中，无需额外安装。

### 2. 导入组件
```typescript
import { DatePicker } from 'antd'
import dayjs from 'dayjs'

const { RangePicker } = DatePicker
```

### 3. 添加状态
```typescript
const [createTimeRange, setCreateTimeRange] = useState<[dayjs.Dayjs | null, dayjs.Dayjs | null] | null>(null)
const [updateTimeRange, setUpdateTimeRange] = useState<[dayjs.Dayjs | null, dayjs.Dayjs | null] | null>(null)
```

### 4. 修改fetchData函数
```typescript
const fetchData = async () => {
  setLoading(true)
  try {
    const params: any = {
      page,
      limit: pageSize,
      res_count: true,
      // 其他搜索条件...
    }
    
    // 添加创建时间范围
    if (createTimeRange && createTimeRange[0] && createTimeRange[1]) {
      params.create_time_start = createTimeRange[0].format('YYYY-MM-DD HH:mm:ss')
      params.create_time_end = createTimeRange[1].format('YYYY-MM-DD HH:mm:ss')
    }
    
    // 添加更新时间范围
    if (updateTimeRange && updateTimeRange[0] && updateTimeRange[1]) {
      params.update_time_start = updateTimeRange[0].format('YYYY-MM-DD HH:mm:ss')
      params.update_time_end = updateTimeRange[1].format('YYYY-MM-DD HH:mm:ss')
    }
    
    const res = await getList(params)
    setData(res.items || [])
    setTotal(res.count || 0)
  } catch (error) {
    console.error('获取列表失败:', error)
    message.error('获取列表失败')
    setData([])
    setTotal(0)
  } finally {
    setLoading(false)
  }
}
```

### 5. 修改重置函数
```typescript
const handleReset = () => {
  // 清空其他搜索条件...
  setCreateTimeRange(null)
  setUpdateTimeRange(null)
  setPage(1)
  setTimeout(() => {
    fetchData()
  }, 0)
}
```

### 6. 添加UI组件
```tsx
<Space style={{ marginBottom: '16px' }} wrap>
  {/* 其他搜索字段... */}
  
  <RangePicker
    placeholder={['创建开始时间', '创建结束时间']}
    value={createTimeRange}
    onChange={setCreateTimeRange}
    showTime
    format="YYYY-MM-DD HH:mm:ss"
    style={{ width: 380 }}
  />
  
  <RangePicker
    placeholder={['更新开始时间', '更新结束时间']}
    value={updateTimeRange}
    onChange={setUpdateTimeRange}
    showTime
    format="YYYY-MM-DD HH:mm:ss"
    style={{ width: 380 }}
  />
  
  <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
    搜索
  </Button>
  <Button onClick={handleReset}>重置</Button>
</Space>
```

## 完整示例

```typescript
import { useState, useEffect } from 'react'
import { Table, Button, Input, Select, DatePicker, message, Space } from 'antd'
import { SearchOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import type { Role } from '@/types'
import { getRoleList } from '@/api/user'

const { RangePicker } = DatePicker

const RoleList = () => {
  const [data, setData] = useState<Role[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  
  // 搜索条件
  const [searchName, setSearchName] = useState('')
  const [searchCode, setSearchCode] = useState('')
  const [createTimeRange, setCreateTimeRange] = useState<[dayjs.Dayjs | null, dayjs.Dayjs | null] | null>(null)
  const [updateTimeRange, setUpdateTimeRange] = useState<[dayjs.Dayjs | null, dayjs.Dayjs | null] | null>(null)

  const fetchData = async () => {
    setLoading(true)
    try {
      const params: any = {
        page,
        limit: pageSize,
        res_count: true,
        name: searchName || undefined,
        code: searchCode || undefined,
      }
      
      // 添加时间范围
      if (createTimeRange && createTimeRange[0] && createTimeRange[1]) {
        params.create_time_start = createTimeRange[0].format('YYYY-MM-DD HH:mm:ss')
        params.create_time_end = createTimeRange[1].format('YYYY-MM-DD HH:mm:ss')
      }
      
      if (updateTimeRange && updateTimeRange[0] && updateTimeRange[1]) {
        params.update_time_start = updateTimeRange[0].format('YYYY-MM-DD HH:mm:ss')
        params.update_time_end = updateTimeRange[1].format('YYYY-MM-DD HH:mm:ss')
      }
      
      const res = await getRoleList(params)
      setData(res.items || [])
      setTotal(res.count || 0)
    } catch (error) {
      console.error('获取角色列表失败:', error)
      message.error('获取角色列表失败')
      setData([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [page, pageSize])

  const handleSearch = () => {
    setPage(1)
    fetchData()
  }

  const handleReset = () => {
    setSearchName('')
    setSearchCode('')
    setCreateTimeRange(null)
    setUpdateTimeRange(null)
    setPage(1)
    setTimeout(() => {
      fetchData()
    }, 0)
  }

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '16px' }}>
        <Space style={{ marginBottom: '16px' }} wrap>
          <Input
            placeholder="角色名称"
            value={searchName}
            onChange={(e) => setSearchName(e.target.value)}
            onPressEnter={handleSearch}
            style={{ width: 200 }}
          />
          <Input
            placeholder="角色标识"
            value={searchCode}
            onChange={(e) => setSearchCode(e.target.value)}
            onPressEnter={handleSearch}
            style={{ width: 200 }}
          />
          <RangePicker
            placeholder={['创建开始时间', '创建结束时间']}
            value={createTimeRange}
            onChange={setCreateTimeRange}
            showTime
            format="YYYY-MM-DD HH:mm:ss"
            style={{ width: 380 }}
          />
          <RangePicker
            placeholder={['更新开始时间', '更新结束时间']}
            value={updateTimeRange}
            onChange={setUpdateTimeRange}
            showTime
            format="YYYY-MM-DD HH:mm:ss"
            style={{ width: 380 }}
          />
          <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
            搜索
          </Button>
          <Button onClick={handleReset}>重置</Button>
        </Space>
        {/* 新增按钮 */}
      </div>
      <Table ... />
    </div>
  )
}

export default RoleList
```

## 时间格式说明

### 后端支持的格式
1. `YYYY-MM-DD` - 日期格式（如：2024-01-21）
2. `YYYY-MM-DD HH:mm:ss` - 日期时间格式（如：2024-01-21 10:30:00）
3. 13位时间戳 - Unix时间戳（如：1705809000000）

### 前端推荐格式
使用 `YYYY-MM-DD HH:mm:ss` 格式，因为：
- 可读性好
- 精确到秒
- 与后端完全兼容

## RangePicker配置选项

### 基础配置
```tsx
<RangePicker
  placeholder={['开始时间', '结束时间']}
  value={timeRange}
  onChange={setTimeRange}
  showTime                          // 显示时间选择
  format="YYYY-MM-DD HH:mm:ss"     // 显示格式
  style={{ width: 380 }}           // 宽度
/>
```

### 高级配置
```tsx
<RangePicker
  placeholder={['开始时间', '结束时间']}
  value={timeRange}
  onChange={setTimeRange}
  showTime={{
    defaultValue: [dayjs('00:00:00', 'HH:mm:ss'), dayjs('23:59:59', 'HH:mm:ss')]
  }}
  format="YYYY-MM-DD HH:mm:ss"
  disabledDate={(current) => {
    // 禁用未来日期
    return current && current > dayjs().endOf('day')
  }}
  presets={[
    { label: '今天', value: [dayjs().startOf('day'), dayjs().endOf('day')] },
    { label: '最近7天', value: [dayjs().subtract(7, 'day'), dayjs()] },
    { label: '最近30天', value: [dayjs().subtract(30, 'day'), dayjs()] },
    { label: '本月', value: [dayjs().startOf('month'), dayjs().endOf('month')] },
  ]}
  style={{ width: 380 }}
/>
```

## UI布局建议

### 1. 单行布局（字段较少）
```tsx
<Space style={{ marginBottom: '16px' }}>
  <Input ... />
  <Select ... />
  <RangePicker ... />
  <Button>搜索</Button>
  <Button>重置</Button>
</Space>
```

### 2. 多行布局（字段较多）
```tsx
<Space style={{ marginBottom: '16px' }} wrap>
  <Input ... />
  <Select ... />
  <RangePicker ... />
  <RangePicker ... />
  <Button>搜索</Button>
  <Button>重置</Button>
</Space>
```

### 3. 表单布局（字段很多）
```tsx
<Form layout="inline" style={{ marginBottom: '16px' }}>
  <Form.Item label="名称">
    <Input ... />
  </Form.Item>
  <Form.Item label="状态">
    <Select ... />
  </Form.Item>
  <Form.Item label="创建时间">
    <RangePicker ... />
  </Form.Item>
  <Form.Item label="更新时间">
    <RangePicker ... />
  </Form.Item>
  <Form.Item>
    <Button type="primary">搜索</Button>
    <Button style={{ marginLeft: 8 }}>重置</Button>
  </Form.Item>
</Form>
```

## 注意事项

1. **时区问题**
   - dayjs默认使用本地时区
   - 后端应该统一处理时区转换

2. **时间精度**
   - 使用 `showTime` 可以精确到秒
   - 不使用 `showTime` 只能精确到天

3. **性能优化**
   - 时间范围查询可能较慢
   - 建议在数据库中为时间字段建立索引

4. **用户体验**
   - 提供快捷选项（今天、最近7天等）
   - 时间范围不宜过大
   - 可以限制最大查询范围

5. **空值处理**
   - 只有两个时间都选择时才传递参数
   - 避免传递null或undefined

## 各页面时间查询优先级

### 高优先级（经常需要按时间查询）
1. 操作日志 - 查看特定时间段的操作
2. 项目余额 - 查看余额变化历史
3. Token管理 - 查看Token创建时间
4. 邮箱列表 - 查看邮箱添加时间

### 中优先级（偶尔需要按时间查询）
1. 用户列表 - 查看新注册用户
2. 项目列表 - 查看项目创建时间
3. 服务器列表 - 查看服务器添加时间

### 低优先级（很少按时间查询）
1. 角色管理 - 角色变化不频繁
2. 路由管理 - 路由变化不频繁
3. 国家管理 - 国家变化不频繁

## 实现建议

1. **分阶段实现**
   - 第一阶段：为高优先级页面添加时间查询
   - 第二阶段：为中优先级页面添加时间查询
   - 第三阶段：根据需求为低优先级页面添加

2. **统一组件**
   - 可以封装一个TimeRangeSearch组件
   - 统一样式和行为

3. **默认值**
   - 某些页面可以设置默认时间范围
   - 如操作日志默认显示最近7天

## 总结

后端API已全面支持时间范围查询，前端需要：
1. 添加RangePicker组件
2. 管理时间范围状态
3. 在API调用时传递时间参数
4. 提供友好的用户界面

建议优先为高频使用的页面添加时间查询功能，提升用户体验。

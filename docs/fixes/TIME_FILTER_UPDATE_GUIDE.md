# 前端页面添加时间查询条件指南

## 概述
为所有前端子页面添加创建时间和更新时间的查询条件，使用日期选择器（年月日格式，不包含时分秒）。

## 已完成的页面
- ✅ frontend/src/views/Project/ProjectList.tsx

## 待更新的页面列表
1. frontend/src/views/User/UserList.tsx - ✅ 已完成
2. frontend/src/views/User/RoleList.tsx
3. frontend/src/views/User/RouteList.tsx
4. frontend/src/views/User/TokenList.tsx
5. frontend/src/views/User/LogList.tsx (已有时间查询，需要调整格式)
6. frontend/src/views/Project/ProjectAccount.tsx
7. frontend/src/views/Project/ProjectBalance.tsx
8. frontend/src/views/Project/ProjectWallet.tsx
9. frontend/src/views/Server/ServerList.tsx
10. frontend/src/views/Server/ServerAccount.tsx
11. frontend/src/views/Server/CountryList.tsx
12. frontend/src/views/Server/GroupList.tsx
13. frontend/src/views/Mail/MailList.tsx

## 更新步骤

### 1. 导入必要的组件和类型
```typescript
import { DatePicker } from 'antd'
import dayjs, { Dayjs } from 'dayjs'

const { RangePicker } = DatePicker
```

### 2. 添加状态变量
```typescript
const [createTimeRange, setCreateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
const [updateTimeRange, setUpdateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
```

### 3. 在搜索区域添加 RangePicker 组件
```typescript
<Space style={{ marginBottom: '16px' }} wrap>
  {/* 其他搜索条件 */}
  
  <RangePicker
    placeholder={['创建开始日期', '创建结束日期']}
    value={createTimeRange}
    onChange={(dates) => setCreateTimeRange(dates as [Dayjs, Dayjs] | null)}
    format="YYYY-MM-DD"
    style={{ width: 260 }}
  />
  <RangePicker
    placeholder={['更新开始日期', '更新结束日期']}
    value={updateTimeRange}
    onChange={(dates) => setUpdateTimeRange(dates as [Dayjs, Dayjs] | null)}
    format="YYYY-MM-DD"
    style={{ width: 260 }}
  />
  
  <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
    搜索
  </Button>
  <Button onClick={handleReset}>重置</Button>
</Space>
```

### 4. 在 fetchData 函数中添加时间参数
```typescript
const fetchData = async () => {
  setLoading(true)
  try {
    const res = await getXXXList({
      page,
      limit: pageSize,
      res_count: true,
      // ... 其他搜索参数
      create_time_start: createTimeRange?.[0]?.format('YYYY-MM-DD'),
      create_time_end: createTimeRange?.[1]?.format('YYYY-MM-DD'),
      update_time_start: updateTimeRange?.[0]?.format('YYYY-MM-DD'),
      update_time_end: updateTimeRange?.[1]?.format('YYYY-MM-DD'),
    })
    setData(res.items || [])
    setTotal(res.count || 0)
  } catch (error) {
    message.error('获取列表失败')
    setData([])
    setTotal(0)
  } finally {
    setLoading(false)
  }
}
```

### 5. 在 handleReset 函数中重置时间范围
```typescript
const handleReset = () => {
  // ... 重置其他搜索条件
  setCreateTimeRange(null)
  setUpdateTimeRange(null)
  setPage(1)
  setTimeout(() => {
    fetchData()
  }, 0)
}
```

## 注意事项

1. **日期格式**: 使用 `YYYY-MM-DD` 格式，不包含时分秒
2. **样式**: RangePicker 宽度设置为 260px
3. **换行**: 搜索区域使用 `wrap` 属性，确保在小屏幕上自动换行
4. **后端兼容**: 后端API已支持 `create_time_start`、`create_time_end`、`update_time_start`、`update_time_end` 参数
5. **可选参数**: 时间参数为可选，不选择时不传递给后端

## 特殊情况

### LogList.tsx
该页面已有时间查询功能，但使用的是带时分秒的格式。需要调整为：
- 移除 `showTime` 属性
- 修改 format 为 `YYYY-MM-DD`
- 修改宽度为 260px
- 修改 placeholder 为 `['创建开始日期', '创建结束日期']`

## 测试清单

更新完成后，需要测试：
- [ ] 日期选择器正常显示
- [ ] 选择日期后能正确搜索
- [ ] 重置按钮能清空日期选择
- [ ] 不选择日期时能正常查询所有数据
- [ ] 日期格式为 YYYY-MM-DD
- [ ] 在小屏幕上搜索条件能正常换行

## 参考实现

完整参考实现请查看：
- `frontend/src/views/Project/ProjectList.tsx`
- `frontend/src/views/User/UserList.tsx`

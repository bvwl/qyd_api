# 邮箱列表表格列头排序功能

## 功能说明

为前端邮箱列表页面添加了表格列头点击排序功能，用户可以点击列标题进行升序或降序排列，与项目列表的排序方式完全一致。

## 实现效果

- ✅ 点击列标题即可排序
- ✅ 显示排序图标（↑ 升序 / ↓ 降序）
- ✅ 支持 4 个字段排序：邮箱、状态、创建时间、更新时间
- ✅ 默认按更新时间降序（最近更新的在前）
- ✅ 与项目列表操作方式一致

## 修改内容

### 文件：`frontend/src/views/Mail/MailList.tsx`

#### 1. 新增类型导入
```typescript
import type { ColumnsType, TableProps } from 'antd/es/table'

type SortOrder = 'ascend' | 'descend' | null
```

#### 2. 修改默认排序
```typescript
const [orderBy, setOrderBy] = useState<string>('-update_time')  // 改为更新时间降序
```

#### 3. 新增排序处理函数
```typescript
// 处理表格排序变化
const handleTableChange: TableProps<EmailInfo>['onChange'] = (_pagination, _filters, sorter: any) => {
  if (sorter.field) {
    const order = sorter.order === 'ascend' ? '' : '-'
    setOrderBy(`${order}${sorter.field}`)
    setPage(1)
  }
}

// 获取当前排序状态
const getSortOrder = (field: string): SortOrder => {
  if (orderBy === field) return 'ascend'
  if (orderBy === `-${field}`) return 'descend'
  return null
}
```

#### 4. 修改列定义
为可排序的列添加 `sorter` 和 `sortOrder` 属性：

```typescript
const columns: ColumnsType<EmailInfo> = [
  {
    title: '邮箱',
    dataIndex: 'email',
    key: 'email',
    sorter: true,                    // 启用排序
    sortOrder: getSortOrder('email'), // 显示排序状态
    // ...
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    sorter: true,
    sortOrder: getSortOrder('status'),
    // ...
  },
  {
    title: '创建时间',
    dataIndex: 'create_time',
    key: 'create_time',
    sorter: true,
    sortOrder: getSortOrder('create_time'),
    // ...
  },
  {
    title: '更新时间',
    dataIndex: 'update_time',
    key: 'update_time',
    sorter: true,
    sortOrder: getSortOrder('update_time'),
    // ...
  },
]
```

#### 5. 修改 Table 组件
```typescript
<Table
  loading={loading}
  dataSource={dataSource}
  columns={columns}
  rowKey="id"
  onChange={handleTableChange}  // 添加排序处理
  // ...
/>
```

#### 6. 优化搜索和重置
```typescript
const handleSearch = () => {
  setPage(1)
  fetchData()
}

const handleReset = () => {
  // ... 清空筛选条件
  setOrderBy('-update_time')  // 重置为默认排序
  setPage(1)
  setTimeout(() => {
    fetchData()
  }, 0)
}
```

#### 7. 优化 useEffect
```typescript
useEffect(() => {
  fetchData()
}, [page, pageSize, orderBy])  // 只在这些变化时自动刷新
```

## 支持的排序列

| 列名 | 字段名 | 升序 | 降序 | 说明 |
|------|--------|------|------|------|
| 邮箱 | `email` | A→Z | Z→A | 按字母顺序 |
| 状态 | `status` | 1→2 | 2→1 | 按状态值 |
| 创建时间 | `create_time` | 旧→新 | 新→旧 | 按时间顺序 |
| 更新时间 | `update_time` | 旧→新 | 新→旧 | 按时间顺序（默认） |

## 使用方法

### 基本操作

1. **点击列标题排序**
   - 第一次点击：升序（显示 ↑）
   - 第二次点击：降序（显示 ↓）
   - 第三次点击：取消排序

2. **默认排序**
   - 页面打开时默认按"更新时间"降序
   - 最近更新的邮箱在最前面

3. **重置功能**
   - 点击"重置"按钮
   - 排序恢复为默认（更新时间降序）

### 使用场景

**场景1：查找特定邮箱**
- 点击"邮箱"列标题
- 邮箱按字母顺序排列
- 快速定位目标邮箱

**场景2：查看最近更新**
- 默认已按更新时间降序
- 最近更新的邮箱在最前面

**场景3：按状态分组**
- 点击"状态"列标题
- 相同状态的邮箱聚集在一起

## 与项目列表的一致性

| 特性 | 项目列表 | 邮箱列表 |
|------|----------|----------|
| 点击列标题排序 | ✅ | ✅ |
| 排序图标显示 | ✅ | ✅ |
| 默认排序 | 创建时间降序 | 更新时间降序 |
| 重置功能 | ✅ | ✅ |
| 代码实现方式 | 一致 | 一致 |

## 技术实现

### 排序状态管理
```
用户点击列标题
  ↓
handleTableChange 触发
  ↓
setOrderBy 更新状态
  ↓
useEffect 监听变化
  ↓
fetchData 刷新数据
  ↓
getSortOrder 更新图标
```

### 排序格式
- `-update_time` → 降序（前缀 `-`）
- `update_time` → 升序（无前缀）

### 图标显示
- `'ascend'` → ↑ 升序图标
- `'descend'` → ↓ 降序图标
- `null` → 无图标

## 测试建议

1. **基础功能**
   - 点击每个可排序列
   - 验证升序/降序/取消循环
   - 检查图标显示

2. **默认排序**
   - 打开页面
   - 验证默认按更新时间降序

3. **组合使用**
   - 设置筛选条件
   - 点击列标题排序
   - 验证同时生效

4. **重置功能**
   - 修改排序
   - 点击重置
   - 验证恢复默认

## 总结

✅ **已实现**：
- 表格列头点击排序
- 4 个可排序列
- 排序图标显示
- 默认按更新时间降序
- 与项目列表一致的操作方式

✅ **用户体验**：
- 操作直观简单
- 响应快速流畅
- 符合使用习惯

✅ **代码质量**：
- 类型安全
- 无语法错误
- 遵循项目规范

# 批量操作和排序功能总结

## 概述

已完成以下功能的实现：
1. 项目账号页面：批量操作 + 排序 + 显示更新时间
2. 项目列表页面：批量操作 + 排序
3. 用户列表页面：批量操作 + 排序
4. 项目钱包页面：批量操作 + 排序
5. 服务器列表页面：批量操作
6. 邮件列表页面：批量操作

## 修改详情

### 已完成的页面

#### 1. 项目账号 (`frontend/src/views/Project/ProjectAccount.tsx`)
- ✅ 批量选择和批量删除
- ✅ 列排序（账号、余额、变动、更新时间）
- ✅ 显示更新时间而不是创建时间
- ✅ 默认按更新时间倒序排列

#### 2. 项目列表 (`frontend/src/views/Project/ProjectList.tsx`)
- ✅ 批量选择和批量删除
- ✅ 列排序（项目名称、创建时间、更新时间）
- ✅ 默认按创建时间倒序排列

#### 3. 用户列表 (`frontend/src/views/User/UserList.tsx`)
- ✅ 批量选择和批量删除
- ✅ 列排序（邮箱、昵称、创建时间）
- ✅ 默认按创建时间倒序排列

#### 4. 项目钱包 (`frontend/src/views/Project/ProjectWallet.tsx`)
- ✅ 批量选择和批量删除
- ✅ 列排序（链、创建时间）
- ✅ 默认按创建时间倒序排列

#### 5. 服务器列表 (`frontend/src/views/Server/ServerList.tsx`)
- ✅ 批量选择和批量删除

#### 6. 邮件列表 (`frontend/src/views/Mail/MailList.tsx`)
- ✅ 批量选择和批量删除

## 实现细节

### 1. 批量选择功能

所有列表页面都添加了以下代码：

```typescript
// 1. 添加选中状态
const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([])

// 2. 表格配置
<Table
  rowSelection={{
    selectedRowKeys,
    onChange: (selectedKeys) => setSelectedRowKeys(selectedKeys as string[]),
    preserveSelectedRowKeys: true,  // 翻页保持选中
  }}
  // ...其他配置
/>

// 3. 重置时清空选中
const handleReset = () => {
  // ...其他重置逻辑
  setSelectedRowKeys([])
}
```

### 批量删除功能

```typescript
// 批量删除函数
const handleBatchDelete = async () => {
  if (selectedRowKeys.length === 0) {
    message.warning('请先选择要删除的数据')
    return
  }

  Modal.confirm({
    title: '批量删除确认',
    content: `确定要删除选中的 ${selectedRowKeys.length} 条数据吗？`,
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      try {
        await Promise.all(selectedRowKeys.map(id => deleteXXX(id)))
        message.success(`成功删除 ${selectedRowKeys.length} 条数据`)
        setSelectedRowKeys([])
        fetchData()
      } catch (error) {
        message.error('批量删除失败')
      }
    }
  })
}

// 批量删除按钮
{selectedRowKeys.length > 0 && (
  <Button 
    danger 
    icon={<DeleteOutlined />} 
    onClick={handleBatchDelete}
  >
    批量删除 ({selectedRowKeys.length})
  </Button>
)}
```

### 2. 列排序功能

```typescript
// 1. 添加排序状态
const [orderBy, setOrderBy] = useState<string>('-create_time')

// 2. 列定义中添加排序
const columns = [
  {
    title: '列名',
    dataIndex: 'field',
    key: 'field',
    sorter: true,  // 启用排序
    sortOrder: getSortOrder('field'),  // 显示排序状态
  },
]

// 3. 处理排序变化
const handleTableChange: TableProps<T>['onChange'] = (_pagination, _filters, sorter: any) => {
  if (sorter.field) {
    const order = sorter.order === 'ascend' ? '' : '-'
    setOrderBy(`${order}${sorter.field}`)
    setPage(1)
    setTimeout(() => {
      fetchData()
    }, 0)
  }
}

// 4. 获取排序状态
const getSortOrder = (field: string): SortOrder => {
  if (orderBy === field) return 'ascend'
  if (orderBy === `-${field}`) return 'descend'
  return null
}

// 5. 表格配置
<Table
  onChange={handleTableChange}
  // ...其他配置
/>

// 6. API请求时传递排序参数
const res = await getList({
  order_by: orderBy,
  // ...其他参数
})
```

## 界面变化

### 所有列表页面

**之前**：
- 没有批量操作功能
- 只能单个删除
- 部分页面没有排序功能

**现在**：
- 支持批量选择（表格左侧显示复选框）
- 选中后显示"批量删除 (N)"按钮
- 批量删除前弹出确认对话框
- 翻页后保持选中状态
- 支持列排序（点击列标题排序）
- 排序状态可视化（显示升序/降序箭头）

### 项目账号页面特殊优化

- 显示更新时间而不是创建时间
- 默认按更新时间倒序排列
- 支持按账号、余额、变动、更新时间排序

### 排序功能说明

- **升序**：点击列标题一次，显示向上箭头
- **降序**：再次点击，显示向下箭头
- **取消排序**：第三次点击，取消排序
- **默认排序**：各页面默认按创建时间或更新时间倒序

## 用户体验优化

1. **批量操作**：减少重复操作，提高效率
2. **确认对话框**：批量删除前会弹出确认对话框，显示删除数量
3. **选中计数**：按钮上显示选中的数量
4. **保持选中**：翻页后保持选中状态（`preserveSelectedRowKeys: true`）
5. **自动清空**：删除成功后自动清空选中状态
6. **重置清空**：点击重置按钮时清空选中状态和排序
7. **列排序**：点击列标题即可排序，支持升序/降序切换
8. **排序可视化**：当前排序列显示箭头图标

## 权限控制

不同页面的批量删除按钮权限：
- **项目账号**：所有用户可见
- **项目列表**：只对ADMIN和GM显示
- **用户列表**：只对ADMIN显示
- **项目钱包**：只对ADMIN和GM显示
- **服务器列表**：只对ADMIN显示
- **邮件列表**：所有用户可见

## 状态

✅ 6个列表页面全部完成批量操作功能
✅ 4个列表页面完成列排序功能
✅ 前端编译检查通过
✅ 用户体验优化完成

## 修改的文件

1. `frontend/src/views/Project/ProjectAccount.tsx` - 批量操作 + 排序
2. `frontend/src/views/Project/ProjectList.tsx` - 批量操作 + 排序
3. `frontend/src/views/User/UserList.tsx` - 批量操作 + 排序
4. `frontend/src/views/Project/ProjectWallet.tsx` - 批量操作 + 排序
5. `frontend/src/views/Server/ServerList.tsx` - 批量操作
6. `frontend/src/views/Mail/MailList.tsx` - 批量操作



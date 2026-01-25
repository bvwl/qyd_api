# 服务器分组管理 - 批量删除功能

## 功能描述

为服务器管理下的分组管理页面添加多选框和批量删除功能，方便管理员批量操作分组。

## 新增功能

### 1. 多选框

- ✅ 表格左侧添加复选框列
- ✅ 支持单选和全选
- ✅ 保留选中状态（翻页后保持）

### 2. 批量删除按钮

- ✅ 选中分组后显示"批量删除"按钮
- ✅ 显示选中数量
- ✅ 确认对话框提示
- ✅ 批量删除成功后清空选中状态

## 实现细节

### 文件：`frontend/src/views/Server/GroupList.tsx`

#### 1. 添加状态管理

```typescript
const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([])
```

#### 2. 添加批量删除函数

```typescript
const handleBatchDelete = async () => {
  if (selectedRowKeys.length === 0) {
    message.warning('请先选择要删除的分组')
    return
  }

  Modal.confirm({
    title: '批量删除确认',
    content: `确定要删除选中的 ${selectedRowKeys.length} 个分组吗？`,
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      try {
        await Promise.all(selectedRowKeys.map(id => deleteGroup(id)))
        message.success(`成功删除 ${selectedRowKeys.length} 个分组`)
        setSelectedRowKeys([])
        fetchData()
      } catch (error) {
        message.error('批量删除失败')
      }
    }
  })
}
```

#### 3. 添加表格多选配置

```typescript
<Table
  columns={columns}
  dataSource={data}
  rowKey="id"
  loading={loading}
  rowSelection={{
    selectedRowKeys,
    onChange: (selectedKeys) => setSelectedRowKeys(selectedKeys as string[]),
    preserveSelectedRowKeys: true,  // 保留选中状态
  }}
  pagination={{...}}
/>
```

#### 4. 添加批量删除按钮

```typescript
<Space>
  {selectedRowKeys.length > 0 && isAdmin && (
    <Button 
      danger 
      icon={<DeleteOutlined />} 
      onClick={handleBatchDelete}
    >
      批量删除 ({selectedRowKeys.length})
    </Button>
  )}
  {isAdmin && (
    <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
      新增分组
    </Button>
  )}
</Space>
```

#### 5. 重置时清空选中状态

```typescript
const handleReset = () => {
  setSearchName('')
  setSearchCountryId(undefined)
  setSearchStatus(undefined)
  setCreateTimeRange(null)
  setUpdateTimeRange(null)
  setSelectedRowKeys([])  // 清空选中状态
  setPage(1)
  setTimeout(() => {
    fetchData()
  }, 0)
}
```

## 使用方法

### 1. 选择分组

- 点击表格左侧的复选框选择单个分组
- 点击表头的复选框全选当前页的所有分组

### 2. 批量删除

1. 选中一个或多个分组
2. 点击右上角的"批量删除 (N)"按钮
3. 在确认对话框中点击"确定"
4. 系统会批量删除选中的分组

### 3. 取消选择

- 点击"重置"按钮会清空所有选中状态
- 删除成功后会自动清空选中状态

## 权限控制

- ✅ 只有 ADMIN 用户可以看到多选框
- ✅ 只有 ADMIN 用户可以看到批量删除按钮
- ✅ 普通用户只能查看分组列表

## 界面效果

### 未选中状态

```
[搜索框] [筛选器] [搜索] [重置]     [新增分组]
```

### 选中状态

```
[搜索框] [筛选器] [搜索] [重置]     [批量删除 (3)] [新增分组]
```

### 表格显示

```
☑ 分组名称    国家      状态    创建时间    更新时间    操作
☑ 美国-洛杉矶  美国      正常    2024-01-01  2024-01-01  编辑 删除
☐ 日本-东京    日本      正常    2024-01-02  2024-01-02  编辑 删除
☑ 香港-HK     中国香港   正常    2024-01-03  2024-01-03  编辑 删除
```

## 确认对话框

```
┌─────────────────────────────┐
│ 批量删除确认                  │
├─────────────────────────────┤
│ 确定要删除选中的 3 个分组吗？  │
│                              │
│         [取消]    [确定]      │
└─────────────────────────────┘
```

## 成功提示

```
✅ 成功删除 3 个分组
```

## 注意事项

1. **级联删除**：
   - 删除分组前请确保没有服务器使用该分组
   - 如果有服务器关联该分组，删除可能失败

2. **批量操作**：
   - 批量删除使用 `Promise.all()` 并发执行
   - 如果部分删除失败，会显示"批量删除失败"

3. **选中状态**：
   - 翻页后选中状态会保留（`preserveSelectedRowKeys: true`）
   - 重置或删除成功后会清空选中状态

4. **权限限制**：
   - 非管理员用户看不到多选框和批量删除按钮
   - 只能查看分组列表

## 相关文件

- `frontend/src/views/Server/GroupList.tsx` - 服务器分组管理页面
- `frontend/src/api/server.ts` - 服务器相关 API
- `frontend/src/types/index.ts` - 类型定义

## 完成时间

2026-01-25 23:20

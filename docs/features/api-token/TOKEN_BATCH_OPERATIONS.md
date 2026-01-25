# Token 管理 - 批量操作功能

## 功能概述

为 Token 管理页面添加了多选和批量操作功能，允许管理员批量处理多个 Token。

## 新增功能

### 1. 多选功能
- ✅ 支持表格行多选
- ✅ 显示已选择数量
- ✅ 支持取消选择
- ✅ 仅管理员可以多选

### 2. 批量操作
- ✅ **批量删除**：一次删除多个 Token
- ✅ **批量设为正常**：将多个 Token 状态设置为正常
- ✅ **批量设为异常**：将多个 Token 状态设置为异常

### 3. 操作提示
- ✅ 显示已选择数量
- ✅ 操作前二次确认
- ✅ 显示操作结果（成功/失败数量）
- ✅ 操作完成后自动刷新列表

## 界面展示

### 未选择时
```
┌─────────────────────────────────────────────────────────┐
│ [选择用户▼] [状态▼] [创建日期] [更新日期] [搜索] [重置]  [新增Token] │
├─────────────────────────────────────────────────────────┤
│ □ Token                | 用户  | 状态 | 创建时间 | 操作   │
│ □ eyJhbGciOiJIUzI1...  | 张三  | 正常 | 2026-01  | 编辑 删除│
│ □ eyJhbGciOiJIUzI1...  | 李四  | 异常 | 2026-01  | 编辑 删除│
└─────────────────────────────────────────────────────────┘
```

### 选择后
```
┌─────────────────────────────────────────────────────────┐
│ [选择用户▼] [状态▼] [创建日期] [更新日期] [搜索] [重置]  [新增Token] │
├─────────────────────────────────────────────────────────┤
│ ℹ️ 已选择 2 项 [取消选择]                                  │
│    [批量设为正常] [批量设为异常] [批量删除]                │
├─────────────────────────────────────────────────────────┤
│ ☑ Token                | 用户  | 状态 | 创建时间 | 操作   │
│ ☑ eyJhbGciOiJIUzI1...  | 张三  | 正常 | 2026-01  | 编辑 删除│
│ □ eyJhbGciOiJIUzI1...  | 李四  | 异常 | 2026-01  | 编辑 删除│
└─────────────────────────────────────────────────────────┘
```

## 使用说明

### 批量删除

1. **选择 Token**：勾选要删除的 Token
2. **点击批量删除**：点击"批量删除"按钮
3. **确认操作**：在弹出的确认框中点击"确定"
4. **查看结果**：系统显示删除结果

**示例**：
```
选择 3 个 Token → 点击"批量删除" → 确认
结果：成功删除 3 个Token
```

### 批量更新状态

#### 批量设为正常

1. **选择 Token**：勾选要更新的 Token
2. **点击批量设为正常**：点击"批量设为正常"按钮
3. **确认操作**：在弹出的确认框中点击"确定"
4. **查看结果**：系统显示更新结果

**示例**：
```
选择 5 个异常 Token → 点击"批量设为正常" → 确认
结果：成功更新 5 个Token
```

#### 批量设为异常

1. **选择 Token**：勾选要更新的 Token
2. **点击批量设为异常**：点击"批量设为异常"按钮
3. **确认操作**：在弹出的确认框中点击"确定"
4. **查看结果**：系统显示更新结果

**示例**：
```
选择 2 个正常 Token → 点击"批量设为异常" → 确认
结果：成功更新 2 个Token
```

## 技术实现

### 1. 状态管理

```typescript
// 选中的行键
const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([])
```

### 2. 行选择配置

```typescript
const rowSelection = {
  selectedRowKeys,
  onChange: (selectedKeys: React.Key[]) => {
    setSelectedRowKeys(selectedKeys as string[])
  },
  getCheckboxProps: (record: UserToken) => ({
    disabled: !isAdmin, // 非管理员禁用选择
  }),
}
```

### 3. 批量删除实现

```typescript
const handleBatchDelete = async () => {
  if (selectedRowKeys.length === 0) {
    message.warning('请先选择要删除的Token')
    return
  }

  Modal.confirm({
    title: '批量删除确认',
    content: `确定要删除选中的 ${selectedRowKeys.length} 个Token吗？`,
    okText: '确定',
    cancelText: '取消',
    okButtonProps: { danger: true },
    onOk: async () => {
      try {
        let successCount = 0
        let failCount = 0

        for (const id of selectedRowKeys) {
          try {
            await deleteToken(id)
            successCount++
          } catch (error) {
            failCount++
          }
        }

        if (successCount > 0) {
          message.success(`成功删除 ${successCount} 个Token${failCount > 0 ? `，失败 ${failCount} 个` : ''}`)
          setSelectedRowKeys([])
          fetchData()
        } else {
          message.error('批量删除失败')
        }
      } catch (error) {
        message.error('批量删除失败')
      }
    },
  })
}
```

### 4. 批量更新状态实现

```typescript
const handleBatchUpdateStatus = async (status: number) => {
  if (selectedRowKeys.length === 0) {
    message.warning('请先选择要更新的Token')
    return
  }

  const statusText = status === 1 ? '正常' : '异常'
  Modal.confirm({
    title: '批量更新状态确认',
    content: `确定要将选中的 ${selectedRowKeys.length} 个Token状态设置为"${statusText}"吗？`,
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      try {
        let successCount = 0
        let failCount = 0

        for (const id of selectedRowKeys) {
          try {
            await updateToken(id, { status })
            successCount++
          } catch (error) {
            failCount++
          }
        }

        if (successCount > 0) {
          message.success(`成功更新 ${successCount} 个Token${failCount > 0 ? `，失败 ${failCount} 个` : ''}`)
          setSelectedRowKeys([])
          fetchData()
        } else {
          message.error('批量更新失败')
        }
      } catch (error) {
        message.error('批量更新失败')
      }
    },
  })
}
```

### 5. 批量操作提示栏

```typescript
{isAdmin && selectedRowKeys.length > 0 && (
  <Alert
    message={
      <Space>
        <span>已选择 {selectedRowKeys.length} 项</span>
        <Button
          type="link"
          size="small"
          onClick={() => setSelectedRowKeys([])}
        >
          取消选择
        </Button>
      </Space>
    }
    type="info"
    showIcon
    style={{ marginBottom: 16 }}
    action={
      <Space>
        <Button
          size="small"
          onClick={() => handleBatchUpdateStatus(1)}
        >
          批量设为正常
        </Button>
        <Button
          size="small"
          onClick={() => handleBatchUpdateStatus(2)}
        >
          批量设为异常
        </Button>
        <Button
          size="small"
          danger
          onClick={handleBatchDelete}
        >
          批量删除
        </Button>
      </Space>
    }
  />
)}
```

## 权限控制

### 管理员权限
- ✅ 可以多选 Token
- ✅ 可以批量删除
- ✅ 可以批量更新状态
- ✅ 可以单个编辑/删除

### 非管理员
- ❌ 不能多选 Token（复选框禁用）
- ❌ 不能批量操作
- ❌ 不能单个编辑/删除
- ✅ 可以查看 Token 列表
- ✅ 可以复制 Token

## 错误处理

### 1. 未选择提示
```typescript
if (selectedRowKeys.length === 0) {
  message.warning('请先选择要删除的Token')
  return
}
```

### 2. 操作确认
```typescript
Modal.confirm({
  title: '批量删除确认',
  content: `确定要删除选中的 ${selectedRowKeys.length} 个Token吗？`,
  okText: '确定',
  cancelText: '取消',
  okButtonProps: { danger: true },
  onOk: async () => {
    // 执行批量操作
  },
})
```

### 3. 部分失败处理
```typescript
let successCount = 0
let failCount = 0

for (const id of selectedRowKeys) {
  try {
    await deleteToken(id)
    successCount++
  } catch (error) {
    failCount++
  }
}

if (successCount > 0) {
  message.success(`成功删除 ${successCount} 个Token${failCount > 0 ? `，失败 ${failCount} 个` : ''}`)
  setSelectedRowKeys([])
  fetchData()
} else {
  message.error('批量删除失败')
}
```

## 用户体验优化

### 1. 选择状态显示
- 显示已选择数量
- 提供取消选择按钮
- 使用 Alert 组件突出显示

### 2. 操作反馈
- 操作前二次确认
- 显示详细的操作结果
- 区分成功和失败数量

### 3. 自动刷新
- 操作完成后自动刷新列表
- 清空选择状态

### 4. 视觉反馈
- 批量删除按钮使用危险色（红色）
- 使用图标增强可识别性
- Alert 提示使用信息色（蓝色）

## 使用场景

### 场景 1：清理过期 Token
```
1. 筛选异常状态的 Token
2. 全选所有异常 Token
3. 批量删除
4. 确认操作
```

### 场景 2：批量禁用 Token
```
1. 选择需要禁用的 Token
2. 点击"批量设为异常"
3. 确认操作
4. Token 状态更新为异常
```

### 场景 3：批量启用 Token
```
1. 筛选异常状态的 Token
2. 选择需要启用的 Token
3. 点击"批量设为正常"
4. 确认操作
5. Token 状态更新为正常
```

## 注意事项

1. **权限限制**：只有管理员可以使用批量操作功能
2. **操作不可逆**：批量删除操作不可恢复，请谨慎操作
3. **部分失败**：如果部分操作失败，系统会显示成功和失败的数量
4. **自动刷新**：操作完成后会自动刷新列表，选择状态会被清空
5. **二次确认**：所有批量操作都需要二次确认

## 相关文件

### 前端
- `frontend/src/views/User/TokenList.tsx` - Token 管理页面（已更新）

### 后端 API
- `GET /api/v1/user/token` - 获取 Token 列表
- `POST /api/v1/user/token` - 创建 Token
- `PUT /api/v1/user/token/{id}` - 更新 Token
- `DELETE /api/v1/user/token/{id}` - 删除 Token

## 更新日志

### 2026-01-25
- ✅ 添加多选功能
- ✅ 添加批量删除功能
- ✅ 添加批量更新状态功能
- ✅ 添加选择状态提示
- ✅ 添加操作确认对话框
- ✅ 添加详细的操作结果反馈
- ✅ 优化用户体验

## 测试建议

### 功能测试
1. 测试单选和多选
2. 测试批量删除（全部成功）
3. 测试批量更新状态（全部成功）
4. 测试取消选择
5. 测试取消操作确认

### 边界测试
1. 未选择时点击批量操作
2. 选择大量 Token（如 100 个）
3. 部分操作失败的情况
4. 非管理员用户访问

### 权限测试
1. 管理员可以多选和批量操作
2. 非管理员不能多选和批量操作
3. 非管理员复选框被禁用

## 总结

Token 管理页面现在支持多选和批量操作功能，大大提高了管理效率。管理员可以一次性处理多个 Token，包括批量删除和批量更新状态。所有操作都有二次确认和详细的结果反馈，确保操作的安全性和可追溯性。

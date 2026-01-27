# 批量选择功能添加状态

## 已完成的页面

### ✅ 已有多选框和批量删除
1. **ProjectWallet** (`frontend/src/views/Project/ProjectWallet.tsx`)
   - 项目钱包列表
   - 支持批量删除

2. **ProjectAccount** (`frontend/src/views/Project/ProjectAccount.tsx`)
   - 项目账号列表
   - 支持批量删除

3. **ServerList** (`frontend/src/views/Server/ServerList.tsx`)
   - 服务器信息列表
   - 支持批量删除

4. **ProjectList** (`frontend/src/views/Project/ProjectList.tsx`)
   - 项目列表
   - 支持批量删除

5. **XuiInboundList** (`frontend/src/views/Xui/XuiInboundList.tsx`)
   - XUI 入站配置列表
   - 支持批量删除
   - ✅ 刚添加 (2026-01-27)

6. **XuiServerList** (`frontend/src/views/Xui/XuiServerList.tsx`)
   - XUI 服务器列表
   - 支持批量删除
   - ✅ 刚添加 (2026-01-27)

## 需要添加的页面

### 🔄 服务器管理模块

7. **ServerAccount** (`frontend/src/views/Server/ServerAccount.tsx`)
   - 服务器账号列表
   - 有删除功能
   - ⏳ 待添加

8. **GroupList** (`frontend/src/views/Server/GroupList.tsx`)
   - 服务器分组列表
   - 有删除功能
   - ⏳ 待添加

9. **CountryList** (`frontend/src/views/Server/CountryList.tsx`)
   - 国家列表
   - 有删除功能
   - ⏳ 待添加

### 🔄 用户管理模块

10. **UserList** (`frontend/src/views/User/UserList.tsx`)
    - 用户列表
    - 有删除功能
    - ⏳ 待添加

11. **RoleList** (`frontend/src/views/User/RoleList.tsx`)
    - 角色列表
    - 有删除功能
    - ⏳ 待添加

12. **RouteList** (`frontend/src/views/User/RouteList.tsx`)
    - 路由列表
    - 有删除功能
    - ⏳ 待添加

13. **TokenList** (`frontend/src/views/User/TokenList.tsx`)
    - Token 列表
    - 有删除功能
    - ⏳ 待添加

### 🔄 邮件管理模块

14. **MailList** (`frontend/src/views/Mail/MailList.tsx`)
    - 邮件列表
    - 有删除功能
    - ⏳ 待添加

## 不需要添加的页面

### ❌ 只读或特殊页面

- **LogList** (`frontend/src/views/User/LogList.tsx`)
  - 操作日志列表
  - 只读，不支持删除

- **XuiOperationLog** (`frontend/src/views/Xui/XuiOperationLog.tsx`)
  - XUI 操作日志
  - 只读，不支持删除

- **XuiAccountManage** (`frontend/src/views/Xui/XuiAccountManage.tsx`)
  - XUI 账号管理（入站账号关联）
  - 特殊页面，不适合批量删除

- **XuiAccountList** (`frontend/src/views/Xui/XuiAccountList.tsx`)
  - XUI 账号列表
  - 特殊功能（批量添加到入站），不是删除

- **MailViewer** (`frontend/src/views/Mail/MailViewer.tsx`)
  - 邮件查看器
  - 特殊页面

- **WalletBatchCreate** (`frontend/src/views/Project/WalletBatchCreate.tsx`)
  - 批量创建钱包
  - 特殊页面

## 实现模板

### 1. 添加状态变量

```typescript
const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
```

### 2. 添加批量删除函数

```typescript
const handleBatchDelete = async () => {
  if (selectedRowKeys.length === 0) {
    message.warning('请先选择要删除的项')
    return
  }

  Modal.confirm({
    title: '批量删除确认',
    content: `确定要删除选中的 ${selectedRowKeys.length} 项吗？`,
    okText: '确定',
    cancelText: '取消',
    okButtonProps: { danger: true },
    onOk: async () => {
      let successCount = 0
      let failCount = 0
      const errors: string[] = []

      for (const id of selectedRowKeys) {
        try {
          await deleteXxx(id as string)  // 替换为实际的删除函数
          successCount++
        } catch (error: any) {
          failCount++
          const item = data.find(item => item.id === id)
          errors.push(`${item?.name} - ${error.response?.data?.detail || '删除失败'}`)
        }
      }

      if (failCount === 0) {
        message.success(`成功删除 ${successCount} 项`)
      } else {
        Modal.warning({
          title: '批量删除完成',
          content: (
            <div>
              <p>成功: {successCount} 个</p>
              <p>失败: {failCount} 个</p>
              {errors.length > 0 && (
                <>
                  <p style={{ marginTop: 8, fontWeight: 'bold' }}>失败详情:</p>
                  {errors.slice(0, 5).map((error, index) => (
                    <p key={index} style={{ fontSize: '12px', color: '#ff4d4f' }}>• {error}</p>
                  ))}
                  {errors.length > 5 && (
                    <p style={{ fontSize: '12px', color: '#ff4d4f' }}>... 还有 {errors.length - 5} 个错误</p>
                  )}
                </>
              )}
            </div>
          ),
          width: 500,
        })
      }

      setSelectedRowKeys([])
      fetchData()
    },
  })
}
```

### 3. 添加批量操作栏

```typescript
{isAdmin && selectedRowKeys.length > 0 && (
  <div style={{ marginBottom: 16, padding: '12px', background: '#f0f2f5', borderRadius: '4px' }}>
    <Space>
      <span>已选择 {selectedRowKeys.length} 项</span>
      <Button
        danger
        icon={<DeleteOutlined />}
        onClick={handleBatchDelete}
      >
        批量删除
      </Button>
      <Button onClick={() => setSelectedRowKeys([])}>
        取消选择
      </Button>
    </Space>
  </div>
)}
```

### 4. 添加 rowSelection 到 Table

```typescript
<Table
  // ... 其他属性
  rowSelection={isAdmin ? {
    selectedRowKeys,
    onChange: (selectedRowKeys) => setSelectedRowKeys(selectedRowKeys),
  } : undefined}
  // ... 其他属性
/>
```

## 优先级

### 高优先级（常用功能）
1. ✅ ServerList - 已完成
2. ✅ XuiServerList - 已完成
3. ✅ XuiInboundList - 已完成
4. ⏳ ServerAccount - 待添加
5. ⏳ UserList - 待添加

### 中优先级
6. ⏳ TokenList - 待添加
7. ⏳ MailList - 待添加
8. ⏳ GroupList - 待添加
9. ⏳ CountryList - 待添加

### 低优先级
10. ⏳ RoleList - 待添加
11. ⏳ RouteList - 待添加

## 下一步

继续为以下页面添加多选框功能：
1. ServerAccount (服务器账号)
2. UserList (用户列表)
3. TokenList (Token列表)
4. MailList (邮件列表)
5. GroupList (服务器分组)
6. CountryList (国家列表)
7. RoleList (角色列表)
8. RouteList (路由列表)

## 注意事项

1. **权限控制**：只有管理员（ADMIN）才能看到多选框和批量删除按钮
2. **错误处理**：批量删除时要显示详细的成功/失败统计
3. **用户体验**：删除前要二次确认，显示选中数量
4. **状态管理**：删除后要清空选中状态并刷新列表

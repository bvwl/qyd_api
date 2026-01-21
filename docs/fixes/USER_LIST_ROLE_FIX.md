# 用户列表角色显示修复

## 问题描述
在用户列表中编辑用户时，角色选择器只显示 "×" 符号，但不显示角色名称。

## 问题原因
可能的原因：
1. 角色列表数据在编辑弹窗打开时还未加载完成
2. Select 组件的 value 和 options 不匹配
3. 表单字段设置时使用了展开运算符可能导致额外字段干扰

## 修复方案

### 1. 优化 handleEdit 函数
```typescript
const handleEdit = (record: User) => {
  setEditingUser(record)
  // 确保角色列表已加载
  if (roles.length === 0) {
    fetchRoles()
  }
  // 明确设置表单值，避免使用展开运算符
  form.setFieldsValue({
    email: record.email,
    nickname: record.nickname,
    status: record.status,
    role_ids: record.roles?.map(r => r.id) || [],
  })
  setModalVisible(true)
}
```

### 2. 优化 handleAdd 函数
```typescript
const handleAdd = () => {
  setEditingUser(null)
  form.resetFields()
  // 确保角色列表已加载
  if (roles.length === 0) {
    fetchRoles()
  }
  setModalVisible(true)
}
```

### 3. 增强 Select 组件
```typescript
<Select 
  mode="multiple" 
  placeholder="请选择角色"
  optionFilterProp="children"
  showSearch
  filterOption={(input, option) =>
    (option?.children as string)?.toLowerCase().includes(input.toLowerCase())
  }
>
  {roles.map(role => (
    <Select.Option key={role.id} value={role.id}>
      {role.name}
    </Select.Option>
  ))}
</Select>
```

## 修改的文件
- `frontend/src/views/User/UserList.tsx`

## 测试步骤
1. 打开用户列表页面
2. 点击某个用户的"编辑"按钮
3. 检查角色选择器是否正确显示已选中的角色名称
4. 尝试添加或删除角色
5. 保存并验证角色是否正确更新

## 预期结果
- 编辑用户时，角色选择器应该显示完整的角色名称（如"管理员"、"技术人员"等）
- 可以正常添加和删除角色
- 保存后角色正确更新

## 额外优化
- 添加了搜索功能，可以在角色列表中搜索
- 添加了 optionFilterProp 确保搜索正常工作
- 在打开编辑/新增弹窗前检查角色列表是否已加载

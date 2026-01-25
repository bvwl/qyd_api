# 前端空字符串处理修复

## 问题描述

在编辑项目账号时，如果用户清空了某个字段（比如 password），前端会将空字符串 `""` 传给后端，而不是 `undefined` 或不传该字段。

这导致后端的 `exclude_unset=True` 无法正确工作，空字符串会被当作有效值处理，从而覆盖数据库中的原有值。

## 问题示例

### 场景
1. 用户编辑一个已有的项目账号
2. 用户清空了 password 字段（不想修改密码）
3. 点击保存

### 错误行为
```typescript
// 前端发送的数据
{
  "account": "test@example.com",
  "password": "",  // ❌ 空字符串
  "status": 1,
  "account_type": 1
}

// 后端处理
item.model_dump(exclude_unset=True)
// 结果：password="" 被包含，因为它被"设置"了（虽然是空字符串）
// 导致：数据库中的密码被清空或设置为空字符串的加密值
```

### 期望行为
```typescript
// 前端发送的数据
{
  "account": "test@example.com",
  // password 字段不传（undefined）
  "status": 1,
  "account_type": 1
}

// 后端处理
item.model_dump(exclude_unset=True)
// 结果：password 不在字典中
// 导致：数据库中的密码保持不变
```

## 解决方案

### 修改文件
`frontend/src/views/Project/ProjectAccount.tsx`

### 修改内容

在 `handleSubmit` 函数中，提交前过滤掉空字符串：

```typescript
const handleSubmit = async () => {
  try {
    const values = await form.validateFields()
    
    // 过滤掉空字符串，将其转换为 undefined
    // 这样后端的 exclude_unset=True 才能正确工作
    const filteredValues = Object.entries(values).reduce((acc, [key, value]) => {
      // 如果值是空字符串，不包含该字段（相当于 undefined）
      if (value === '') {
        return acc
      }
      // 其他值正常包含
      acc[key] = value
      return acc
    }, {} as any)
    
    if (editingAccount) {
      await updateProjectAccount(editingAccount.id, filteredValues)
      message.success('更新成功')
    } else {
      await createProjectAccount(filteredValues)
      message.success('创建成功')
    }
    setModalVisible(false)
    fetchData()
  } catch (error) {
    message.error('操作失败')
  }
}
```

## 工作原理

### 1. 过滤空字符串
```typescript
const filteredValues = Object.entries(values).reduce((acc, [key, value]) => {
  if (value === '') {
    return acc  // 不包含该字段
  }
  acc[key] = value
  return acc
}, {} as any)
```

### 2. 示例转换

**输入（表单值）：**
```typescript
{
  account: "test@example.com",
  password: "",  // 用户清空了
  status: 1,
  account_type: 1,
  balance: 100
}
```

**输出（过滤后）：**
```typescript
{
  account: "test@example.com",
  // password 字段被移除
  status: 1,
  account_type: 1,
  balance: 100
}
```

### 3. 后端处理

```python
# 后端 Update schema
class Update(BaseModel):
    password: str | None = Field(None, description="密码")
    # ... 其他字段

# CRUD update 方法
async def update(self, id: UUID, item: Update) -> Out:
    # exclude_unset=True 只包含前端传递的字段
    update_data = item.model_dump(exclude_unset=True, exclude={'balance', 'variable', 'balance_history'})
    
    # 如果前端没传 password，update_data 中就不会有 password
    # 数据库更新时不会修改 password 字段
    if 'password' in update_data and update_data['password']:
        update_data['password'] = encrypt_password(update_data['password'], account)
```

## 适用场景

这个修复适用于所有使用 PUT/PATCH 方法进行部分更新的场景：

1. **项目账号编辑** - 不想修改密码时清空 password 字段
2. **用户信息编辑** - 不想修改某些可选字段
3. **项目信息编辑** - 不想修改描述等可选字段
4. **任何部分更新场景** - 只更新用户填写的字段

## 注意事项

### 1. 空字符串 vs null vs undefined

- **空字符串 `""`**: 表示用户清空了字段，但前端仍然传递了该字段
- **`null`**: 表示明确设置为空值
- **`undefined`**: 表示不传递该字段（不修改）

### 2. 必填字段

对于必填字段（如 account），即使是空字符串也应该被验证拦截，不会到达这个过滤逻辑。

### 3. 数字类型

数字类型的字段（如 balance）不会是空字符串，所以不受影响：
- 用户清空数字输入框 → 表单值为 `undefined`
- 用户输入 0 → 表单值为 `0`（有效值）

### 4. 布尔类型

布尔类型的字段不会是空字符串，通常是 `true`/`false` 或 `undefined`。

## 其他需要修改的组件

建议在以下组件中也应用相同的修复：

1. **用户管理** (`frontend/src/views/User/UserList.tsx`)
2. **项目管理** (`frontend/src/views/Project/ProjectList.tsx`)
3. **服务器管理** (`frontend/src/views/Server/ServerList.tsx`)
4. **邮件管理** (`frontend/src/views/Mail/MailList.tsx`)
5. **所有其他编辑表单**

## 通用工具函数

可以创建一个通用的工具函数来处理这个逻辑：

```typescript
// frontend/src/utils/form.ts

/**
 * 过滤表单值中的空字符串
 * 将空字符串转换为 undefined（不传递该字段）
 * 
 * @param values 表单值对象
 * @returns 过滤后的对象
 */
export function filterEmptyStrings<T extends Record<string, any>>(values: T): Partial<T> {
  return Object.entries(values).reduce((acc, [key, value]) => {
    if (value === '') {
      return acc
    }
    acc[key] = value
    return acc
  }, {} as Partial<T>)
}

// 使用示例
const values = await form.validateFields()
const filteredValues = filterEmptyStrings(values)
await updateProjectAccount(editingAccount.id, filteredValues)
```

## 测试验证

### 测试步骤

1. 创建一个项目账号，填写所有字段包括 password
2. 编辑该账号，清空 password 字段
3. 保存
4. 查看数据库，password 字段应该保持原值（加密后的值）

### 预期结果

- ✅ password 字段在数据库中保持不变
- ✅ 其他修改的字段正常更新
- ✅ 没有错误提示

## 总结

这个修复确保了前端在进行部分更新时，只传递用户实际修改的字段，而不是将清空的字段作为空字符串传递给后端。

这样后端的 `exclude_unset=True` 才能正确工作，实现真正的部分更新（PATCH 语义）。

## 相关文档

- [项目账号加密更新](PROJECT_ACCOUNT_ENCRYPTION_UPDATE.md)
- [后端开发规范](docs/conventions.md)
- [前端开发规范](frontend/README.md)

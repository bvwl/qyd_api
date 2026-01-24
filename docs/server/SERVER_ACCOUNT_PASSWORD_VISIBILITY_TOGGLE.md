# 服务器账号密码显示/隐藏功能

## 更新日期
2026-01-24

## 功能说明

在服务器账号管理页面的表格中，添加了密码显示/隐藏切换功能，提升安全性和用户体验。

## 功能特性

### 1. 默认隐藏密码
- 表格中的密码列默认显示为 `••••••••••••`
- 保护密码不被他人偷看

### 2. 眼睛图标切换
- 每行密码旁边有一个眼睛图标按钮
- 点击眼睛图标可以切换显示/隐藏
- 👁 显示密码
- 👁‍🗨 隐藏密码

### 3. 独立控制
- 每行密码独立控制显示/隐藏
- 不影响其他行的显示状态

## 实现细节

### 前端修改

**文件**: `frontend/src/views/Server/ServerAccount.tsx`

#### 1. 添加状态管理

```typescript
const [visiblePasswords, setVisiblePasswords] = useState<Record<string, boolean>>({})
```

**说明**：
- 使用对象存储每个账号的密码显示状态
- Key: 账号ID
- Value: true（显示）/ false（隐藏）

#### 2. 导入图标

```typescript
import { EyeOutlined, EyeInvisibleOutlined } from '@ant-design/icons'
```

#### 3. 修改密码列渲染

```typescript
{
  title: '密码',
  dataIndex: 'password',
  key: 'password',
  render: (password: string, record: ServerAccount) => {
    const isVisible = visiblePasswords[record.id] || false
    return (
      <Space>
        <span style={{ fontFamily: 'monospace' }}>
          {isVisible ? password : '••••••••••••'}
        </span>
        <Button
          type="text"
          size="small"
          icon={isVisible ? <EyeInvisibleOutlined /> : <EyeOutlined />}
          onClick={() => {
            setVisiblePasswords(prev => ({
              ...prev,
              [record.id]: !prev[record.id]
            }))
          }}
        />
      </Space>
    )
  },
}
```

**逻辑说明**：
1. 从状态中获取当前行的显示状态
2. 根据状态显示明文或 `••••••••••••`
3. 根据状态显示不同的图标（眼睛/眼睛斜杠）
4. 点击按钮切换状态

## 用户体验

### 管理员使用

1. **查看所有账号**
   - 进入"服务器管理" → "服务器账号"
   - 表格显示所有账号
   - 密码列默认显示 `••••••••••••`

2. **查看密码**
   - 点击密码旁边的眼睛图标 👁
   - 密码显示为明文（如 `aB3dE7fGhJ9k`）
   - 图标变为眼睛斜杠 👁‍🗨

3. **隐藏密码**
   - 再次点击眼睛斜杠图标 👁‍🗨
   - 密码隐藏为 `••••••••••••`
   - 图标变回眼睛 👁

4. **独立控制**
   - 可以同时显示某些行的密码
   - 隐藏其他行的密码
   - 每行独立控制

### 普通用户使用

1. **查看自己的账号**
   - 进入"服务器管理" → "服务器账号"
   - 只显示自己的账号
   - 密码列显示加密密文（Base64）

2. **密码显示**
   - 普通用户看到的是加密密文
   - 眼睛图标切换显示/隐藏密文
   - 无法看到明文密码

## 界面效果

### 默认状态（密码隐藏）

```
┌──────────────┬────────────────┬──────────┬────────────┐
│ 用户名       │ 密码           │ 关联用户 │ 操作       │
├──────────────┼────────────────┼──────────┼────────────┤
│ user_7233165c│ •••••••••••• 👁│ 栀虞     │ 编辑 删除  │
│ user_7914cbac│ •••••••••••• 👁│ 至宇     │ 编辑 删除  │
└──────────────┴────────────────┴──────────┴────────────┘
```

### 显示密码状态

```
┌──────────────┬────────────────────┬──────────┬────────────┐
│ 用户名       │ 密码               │ 关联用户 │ 操作       │
├──────────────┼────────────────────┼──────────┼────────────┤
│ user_7233165c│ aB3dE7fGhJ9k 👁‍🗨  │ 栀虞     │ 编辑 删除  │
│ user_7914cbac│ •••••••••••• 👁    │ 至宇     │ 编辑 删除  │
└──────────────┴────────────────────┴──────────┴────────────┘
```

## 安全性

### 1. 默认隐藏
- 密码默认隐藏，防止被他人偷看
- 需要主动点击才能查看

### 2. 独立控制
- 每行独立控制，不会一次性显示所有密码
- 降低密码泄露风险

### 3. 权限控制
- 管理员：看到解密后的明文
- 普通用户：看到加密密文
- 权限控制在后端，前端只是显示

### 4. 临时显示
- 刷新页面后，所有密码恢复隐藏状态
- 不会持久化显示状态

## 代码优势

### 1. 简洁性
- 使用 React Hooks 管理状态
- 代码简洁易懂

### 2. 性能
- 只更新点击的那一行
- 不影响其他行的渲染

### 3. 可维护性
- 逻辑清晰，易于维护
- 易于扩展（如添加全部显示/隐藏按钮）

## 可能的扩展

### 1. 全部显示/隐藏按钮

可以在表格上方添加一个按钮，一键显示/隐藏所有密码：

```typescript
<Button
  onClick={() => {
    const allVisible = Object.values(visiblePasswords).every(v => v)
    const newState: Record<string, boolean> = {}
    data.forEach(item => {
      newState[item.id] = !allVisible
    })
    setVisiblePasswords(newState)
  }}
>
  {Object.values(visiblePasswords).every(v => v) ? '全部隐藏' : '全部显示'}
</Button>
```

### 2. 复制密码按钮

可以在密码旁边添加复制按钮：

```typescript
<Button
  type="text"
  size="small"
  icon={<CopyOutlined />}
  onClick={() => {
    navigator.clipboard.writeText(password)
    message.success('密码已复制')
  }}
/>
```

### 3. 自动隐藏

可以设置一段时间后自动隐藏密码：

```typescript
const handleTogglePassword = (id: string) => {
  setVisiblePasswords(prev => ({
    ...prev,
    [id]: !prev[id]
  }))
  
  // 10秒后自动隐藏
  if (!visiblePasswords[id]) {
    setTimeout(() => {
      setVisiblePasswords(prev => ({
        ...prev,
        [id]: false
      }))
    }, 10000)
  }
}
```

## 相关文档

- [SERVER_ACCOUNT_FINAL_SUMMARY.md](./SERVER_ACCOUNT_FINAL_SUMMARY.md) - 服务器账号功能总结
- [SERVER_ACCOUNT_PASSWORD_FIELD_UPDATE.md](./SERVER_ACCOUNT_PASSWORD_FIELD_UPDATE.md) - 密码字段更新

## 总结

### 完成的功能

- ✅ 密码默认隐藏
- ✅ 眼睛图标切换显示/隐藏
- ✅ 每行独立控制
- ✅ 提升安全性
- ✅ 改善用户体验

### 修改的文件

- `frontend/src/views/Server/ServerAccount.tsx` - 添加密码显示/隐藏功能

### 服务状态

- ✅ 前端会自动热更新
- ✅ 无需重启后端
- ✅ 功能立即生效

现在服务器账号管理页面的密码默认隐藏，点击眼睛图标可以切换显示/隐藏，更加安全和友好！

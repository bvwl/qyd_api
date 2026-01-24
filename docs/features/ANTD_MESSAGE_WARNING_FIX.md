# Ant Design Message 警告修复

## 问题描述

在控制台中出现警告：
```
Warning: [antd: message] Static function can not consume context like dynamic theme. Please use 'App' component instead.
```

这是因为 Ant Design 5 要求使用 `App.useApp()` hooks 来获取 `message` 实例，而不是直接导入静态的 `message` 方法。

## 修复方案

### 修改前
```typescript
import { message } from 'antd'

export default function MyComponent() {
  const handleClick = () => {
    message.success('操作成功')
  }
  // ...
}
```

### 修改后
```typescript
import { App } from 'antd'

export default function MyComponent() {
  const { message } = App.useApp()
  
  const handleClick = () => {
    message.success('操作成功')
  }
  // ...
}
```

## 修复的文件列表

已修复以下所有页面组件：

### 用户管理
- ✅ `frontend/src/views/User/UserList.tsx`
- ✅ `frontend/src/views/User/RoleList.tsx`
- ✅ `frontend/src/views/User/RouteList.tsx`
- ✅ `frontend/src/views/User/TokenList.tsx`
- ✅ `frontend/src/views/User/LogList.tsx`
- ✅ `frontend/src/views/User/PermissionManageWorking.tsx`

### 项目管理
- ✅ `frontend/src/views/Project/ProjectList.tsx`
- ✅ `frontend/src/views/Project/ProjectAccount.tsx`
- ✅ `frontend/src/views/Project/ProjectWallet.tsx`

### 服务器管理
- ✅ `frontend/src/views/Server/ServerList.tsx`
- ✅ `frontend/src/views/Server/ServerAccount.tsx`
- ✅ `frontend/src/views/Server/CountryList.tsx`
- ✅ `frontend/src/views/Server/GroupList.tsx`

### 邮箱管理
- ✅ `frontend/src/views/Mail/MailList.tsx`
- ✅ `frontend/src/views/Mail/MailViewer.tsx`
- ✅ `frontend/src/views/Mail/MailSend.tsx`

### 其他
- ✅ `frontend/src/views/Dashboard/index.tsx`
- ✅ `frontend/src/views/Login/index.tsx`

## 修改步骤

### 1. 修改 import 语句
```typescript
// 移除 message
- import { Button, message } from 'antd'
// 添加 App
+ import { Button, App } from 'antd'
```

### 2. 在组件函数开头添加 hook
```typescript
export default function MyComponent() {
  const { message } = App.useApp()
  // 其他代码...
}
```

或者对于箭头函数组件：
```typescript
const MyComponent = () => {
  const { message } = App.useApp()
  // 其他代码...
}
```

## 验证

修复后，刷新浏览器，控制台应该不再出现 message 相关的警告。

## 注意事项

1. **App 组件包裹**：确保应用的根组件已经用 `<App>` 包裹（在 `App.tsx` 中已配置）
2. **其他静态方法**：如果使用了其他 Ant Design 的静态方法（如 `Modal.confirm`、`notification` 等），也建议使用 hooks 方式
3. **兼容性**：这是 Ant Design 5 的推荐做法，可以正确消费动态主题等上下文

## 相关文档

- [Ant Design App 组件文档](https://ant.design/components/app-cn)
- [Ant Design 5 迁移指南](https://ant.design/docs/react/migration-v5-cn)

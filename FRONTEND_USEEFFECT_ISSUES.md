# 前端 useEffect 依赖问题汇总

## 问题说明

多个组件的 `useEffect` 存在依赖数组不完整的问题，可能导致：
1. ESLint 警告
2. 闭包陷阱（使用了过期的状态）
3. 潜在的无限循环
4. 首次加载时的渲染问题

## 修复原则

### 1. 使用 useCallback 包装函数
```tsx
// ❌ 错误
const fetchData = async () => { ... }
useEffect(() => {
  fetchData()
}, [page]) // fetchData 不在依赖中

// ✅ 正确
const fetchData = useCallback(async () => { ... }, [page])
useEffect(() => {
  fetchData()
}, [fetchData])
```

### 2. 或者将函数移到 useEffect 内部
```tsx
// ✅ 正确
useEffect(() => {
  const fetchData = async () => { ... }
  fetchData()
}, [page])
```

### 3. 避免在依赖中使用对象/数组
```tsx
// ❌ 可能导致无限循环
useEffect(() => {
  fetchData()
}, [userInfo]) // userInfo 是对象，每次渲染都是新引用

// ✅ 正确：只依赖需要的属性
useEffect(() => {
  fetchData()
}, [userInfo?.id])
```

## 需要修复的文件

### 高优先级（可能导致白屏或无限循环）

1. **frontend/src/views/Dashboard/index.tsx**
   - 问题：`useEffect` 依赖 `userInfo`，但调用的函数未包含在依赖中
   - 修复：使用 `useCallback` 或将函数移到 useEffect 内部
   ```tsx
   // 当前代码
   useEffect(() => {
     fetchData()
     if (userInfo?.id) {
       fetchUserToken()
       fetchServerAccount()
     }
   }, [userInfo])
   
   // 建议修复
   useEffect(() => {
     fetchData()
     if (userInfo?.id) {
       fetchUserToken()
       fetchServerAccount()
     }
   }, [userInfo?.id]) // 只依赖 id
   ```

2. **frontend/src/views/Project/ProjectAccount.tsx**
   - 问题：`fetchData` 未在依赖数组中
   - 修复：使用 `useCallback`

3. **frontend/src/views/Server/ServerAccount.tsx**
   - 问题：类似 ProjectAccount

4. **frontend/src/views/Project/ProjectWallet.tsx**
   - 问题：类似 ProjectAccount

### 中优先级（可能导致 ESLint 警告）

5. **frontend/src/views/User/UserList.tsx**
6. **frontend/src/views/User/TokenList.tsx**
7. **frontend/src/views/Server/ServerList.tsx**
8. **frontend/src/views/Server/GroupList.tsx**
9. **frontend/src/views/Xui/XuiAccountManage.tsx**
10. **frontend/src/views/Dashboard/ProjectStatsChart.tsx**

### 低优先级（依赖数组为空，通常没问题）

11. **frontend/src/views/User/RoleList.tsx**
12. **frontend/src/views/User/RouteList.tsx**
13. **frontend/src/views/Xui/XuiServerList.tsx**
14. **frontend/src/views/Xui/XuiInboundList.tsx**
15. **frontend/src/views/Xui/XuiAccountList.tsx**
16. **frontend/src/views/Xui/XuiOperationLog.tsx**

## 修复示例

### Dashboard.tsx 修复

```tsx
import { useState, useEffect, useCallback } from 'react'

export default function Dashboard() {
  const userInfo = useUserStore((state) => state.userInfo)
  
  // 使用 useCallback 包装函数
  const fetchData = useCallback(async () => {
    if (!userInfo) return
    // ... 原有逻辑
  }, [userInfo?.id]) // 只依赖需要的属性
  
  const fetchUserToken = useCallback(async () => {
    if (!userInfo?.id) return
    // ... 原有逻辑
  }, [userInfo?.id])
  
  const fetchServerAccount = useCallback(async () => {
    if (!userInfo?.id) return
    // ... 原有逻辑
  }, [userInfo?.id])
  
  useEffect(() => {
    fetchData()
    fetchUserToken()
    fetchServerAccount()
  }, [fetchData, fetchUserToken, fetchServerAccount])
  
  // ... 其他代码
}
```

### ProjectAccount.tsx 修复

```tsx
export default function ProjectAccount() {
  // 方案1：使用 useCallback
  const fetchData = useCallback(async () => {
    // ... 原有逻辑
  }, [page, pageSize, searchProjectId])
  
  useEffect(() => {
    if (searchProjectId) {
      fetchData()
    }
  }, [searchProjectId, fetchData])
  
  // 方案2：将函数移到 useEffect 内部
  useEffect(() => {
    if (!searchProjectId) return
    
    const fetchData = async () => {
      // ... 原有逻辑
    }
    
    fetchData()
  }, [page, pageSize, searchProjectId])
}
```

## 自动修复工具

可以使用 ESLint 的自动修复功能：

```bash
cd frontend
npm run lint -- --fix
```

但建议手动检查修复结果，因为自动修复可能会：
1. 添加不必要的依赖
2. 导致无限循环
3. 改变原有的业务逻辑

## 测试清单

修复后需要测试：
- [ ] 页面首次加载正常
- [ ] 刷新页面正常
- [ ] 切换路由正常
- [ ] 数据加载正常
- [ ] 没有无限循环（检查 Network 面板）
- [ ] 没有控制台错误

## 参考资料

- [React useEffect 完整指南](https://overreacted.io/a-complete-guide-to-useeffect/)
- [useCallback 使用指南](https://react.dev/reference/react/useCallback)
- [ESLint react-hooks/exhaustive-deps 规则](https://github.com/facebook/react/tree/main/packages/eslint-plugin-react-hooks)

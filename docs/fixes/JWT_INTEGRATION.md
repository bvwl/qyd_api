# 前端JWT集成说明

## ✅ 完成的工作

### 1. 登录页面优化
- ✅ 允许zhiyu账户通过非邮箱格式验证
- ✅ 自定义验证规则，支持邮箱和特殊账号
- ✅ 优化错误提示信息

### 2. JWT Token管理
- ✅ Token自动缓存到localStorage
- ✅ Token自动添加到请求头（Bearer Token）
- ✅ Token过期自动检测和处理
- ✅ Token解析和验证工具类

### 3. 用户状态管理
- ✅ 使用zustand持久化存储用户信息
- ✅ 自动同步token到localStorage
- ✅ 登出时清除所有认证信息
- ✅ 权限管理（支持角色和路由权限）

### 4. API拦截器
- ✅ 请求拦截：自动添加Bearer Token
- ✅ 响应拦截：处理401/403等认证错误
- ✅ Token过期自动跳转登录页
- ✅ 清除过期的认证信息

### 5. 路由保护
- ✅ ProtectedRoute组件验证登录状态
- ✅ 自动检测token有效性
- ✅ Token过期自动跳转登录

## 🔐 JWT工作流程

### 登录流程
```
1. 用户输入账号密码
   ↓
2. 前端发送登录请求
   ↓
3. 后端验证并返回JWT token
   ↓
4. 前端保存token到localStorage和store
   ↓
5. 提取用户信息和权限
   ↓
6. 跳转到首页
```

### 请求流程
```
1. 发起API请求
   ↓
2. 请求拦截器添加Bearer Token
   ↓
3. 后端验证token
   ↓
4. 返回数据或错误
   ↓
5. 响应拦截器处理结果
   ↓
6. 如果401错误，清除token并跳转登录
```

### 登出流程
```
1. 用户点击登出
   ↓
2. 清除localStorage中的token
   ↓
3. 清除store中的用户信息
   ↓
4. 跳转到登录页
```

## 📝 使用示例

### 1. 登录
```typescript
import { useUserStore } from '@/store/useUserStore'

const login = useUserStore((state) => state.login)

// 登录
await login('zhiyu', '2201101122@qq.com')
// 或
await login('user@example.com', 'password')
```

### 2. 获取用户信息
```typescript
import { useUserStore } from '@/store/useUserStore'

const userInfo = useUserStore((state) => state.userInfo)
const token = useUserStore((state) => state.token)
const isLoggedIn = useUserStore((state) => state.isLoggedIn)
```

### 3. 权限检查
```typescript
import { useUserStore } from '@/store/useUserStore'

const hasPermission = useUserStore((state) => state.hasPermission)

// 检查是否有某个权限
if (hasPermission('ADMIN')) {
  // 显示管理员功能
}

if (hasPermission('user:create')) {
  // 显示创建用户按钮
}
```

### 4. 登出
```typescript
import { useUserStore } from '@/store/useUserStore'

const logout = useUserStore((state) => state.logout)

// 登出
logout()
```

### 5. 使用Token工具类
```typescript
import { TokenManager } from '@/utils/token'

// 获取token
const token = TokenManager.getToken()

// 检查token是否过期
const isExpired = TokenManager.isTokenExpired()

// 获取token剩余时间（秒）
const remainingTime = TokenManager.getTokenRemainingTime()

// 从token中获取用户信息
const userInfo = TokenManager.getUserInfoFromToken()

// 清除所有认证信息
TokenManager.clearAuth()
```

## 🔧 配置说明

### API Base URL
在`.env`文件中配置：
```bash
VITE_API_BASE_URL=http://127.0.0.1:6080/api
```

### Token存储
- **localStorage key**: `access_token`
- **Store key**: `user-storage`

### Token格式
```
Authorization: Bearer <token>
```

## 🎯 特殊账户处理

### zhiyu账户
- ✅ 允许使用非邮箱格式登录
- ✅ 账号：`zhiyu`
- ✅ 密码：`2201101122@qq.com`
- ✅ 角色：ADMIN

### 验证规则
```typescript
// 允许zhiyu账户通过验证
if (value === 'zhiyu') {
  return Promise.resolve()
}

// 其他账户需要符合邮箱格式
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
if (!emailRegex.test(value)) {
  return Promise.reject(new Error('请输入有效的邮箱地址'))
}
```

## ⚠️ 注意事项

### Token过期处理
1. Token过期时间：24小时（后端配置）
2. 前端会自动检测token过期
3. 过期后自动清除认证信息并跳转登录页

### 安全建议
1. ✅ Token存储在localStorage（刷新页面不丢失）
2. ✅ 使用HTTPS传输（生产环境）
3. ✅ Token自动过期检测
4. ✅ 401错误自动处理
5. ⚠️ 不要在控制台打印token
6. ⚠️ 不要将token提交到版本控制

### 跨域配置
如果前后端分离部署，需要配置CORS：
```typescript
// 后端.env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 🧪 测试

### 测试登录
```bash
# 使用zhiyu账户
账号: zhiyu
密码: 2201101122@qq.com

# 使用邮箱账户
账号: user@example.com
密码: password
```

### 测试Token
1. 登录后查看localStorage中的`access_token`
2. 打开浏览器开发者工具 → Application → Local Storage
3. 查看`access_token`和`user-storage`

### 测试过期
1. 修改后端JWT_EXPIRE_TIME为60秒
2. 登录后等待60秒
3. 刷新页面或发起请求
4. 应该自动跳转到登录页

## 📚 相关文件

### 核心文件
- `src/api/index.ts` - API拦截器
- `src/store/useUserStore.ts` - 用户状态管理
- `src/utils/token.ts` - Token工具类
- `src/views/Login/index.tsx` - 登录页面
- `src/components/ProtectedRoute/index.tsx` - 路由保护

### 类型定义
- `src/types/index.ts` - TypeScript类型定义

## 🔄 更新日志

### v1.0.0 (2024-01-21)
- ✅ 集成JWT认证
- ✅ 实现token缓存
- ✅ 支持zhiyu特殊账户
- ✅ 完善权限管理
- ✅ 优化错误处理

## 🆘 常见问题

### Q1: 登录后刷新页面需要重新登录？
A: 检查localStorage中是否有`access_token`，确保zustand的persist配置正确。

### Q2: Token过期后没有自动跳转登录页？
A: 检查API拦截器的401错误处理，确保清除了token并跳转。

### Q3: zhiyu账户无法登录？
A: 确认后端已运行初始化脚本，检查数据库中是否有zhiyu用户。

### Q4: 请求没有携带token？
A: 检查请求拦截器，确保token正确添加到Authorization头。

### Q5: 如何查看token内容？
A: 使用TokenManager.parseToken()或访问 https://jwt.io 解析token。

## ✨ 总结

前端JWT集成已完成，主要功能包括：
- ✅ JWT token自动管理和缓存
- ✅ 登录状态持久化
- ✅ Token过期自动处理
- ✅ 支持zhiyu特殊账户
- ✅ 完善的权限管理
- ✅ 友好的错误处理

系统已可以正常使用JWT认证！🎉

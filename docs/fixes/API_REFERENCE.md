# API 参考文档

本文档列出所有已封装的 API 接口。

## 用户模块 (user.ts)

### 认证接口

#### login - 用户登录
```typescript
login(data: { email: string; password: string }): Promise<LoginResponse>
```

#### register - 用户注册
```typescript
register(data: { email: string; password: string; nickname: string }): Promise<LoginResponse>
```

### 用户管理

#### getUserList - 获取用户列表
```typescript
getUserList(params: {
  page?: number
  limit?: number
  res_count?: boolean
  email?: string
  nickname?: string
  status?: number
}): Promise<ApiResponse<User>>
```

#### getUserDetail - 获取用户详情
```typescript
getUserDetail(id: string): Promise<User>
```

#### createUser - 创建用户
```typescript
createUser(data: Partial<User> & { role_ids?: string[] }): Promise<User>
```

#### updateUser - 更新用户
```typescript
updateUser(id: string, data: Partial<User> & { role_ids?: string[] }): Promise<User>
```

#### deleteUser - 删除用户
```typescript
deleteUser(id: string): Promise<void>
```

### 角色管理

#### getRoleList - 获取角色列表
```typescript
getRoleList(params?: PaginationParams): Promise<ApiResponse<Role>>
```

#### getRoleDetail - 获取角色详情
```typescript
getRoleDetail(id: string): Promise<Role>
```

#### createRole - 创建角色
```typescript
createRole(data: Partial<Role> & { route_ids?: string[] }): Promise<Role>
```

#### updateRole - 更新角色
```typescript
updateRole(id: string, data: Partial<Role> & { route_ids?: string[] }): Promise<Role>
```

#### deleteRole - 删除角色
```typescript
deleteRole(id: string): Promise<void>
```

### 路由管理

#### getRouteList - 获取路由列表
```typescript
getRouteList(params?: PaginationParams): Promise<ApiResponse<Route>>
```

#### getRouteDetail - 获取路由详情
```typescript
getRouteDetail(id: string): Promise<Route>
```

#### createRoute - 创建路由
```typescript
createRoute(data: Partial<Route>): Promise<Route>
```

#### updateRoute - 更新路由
```typescript
updateRoute(id: string, data: Partial<Route>): Promise<Route>
```

#### deleteRoute - 删除路由
```typescript
deleteRoute(id: string): Promise<void>
```

### Token 管理

#### getTokenList - 获取 Token 列表
```typescript
getTokenList(params?: PaginationParams & { user_id?: string; status?: number }): Promise<ApiResponse<UserToken>>
```

#### getTokenDetail - 获取 Token 详情
```typescript
getTokenDetail(id: string): Promise<UserToken>
```

#### createToken - 创建 Token
```typescript
createToken(data: Partial<UserToken>): Promise<UserToken>
```

#### updateToken - 更新 Token
```typescript
updateToken(id: string, data: Partial<UserToken>): Promise<UserToken>
```

#### deleteToken - 删除 Token
```typescript
deleteToken(id: string): Promise<void>
```

### 日志管理

#### getLogList - 获取日志列表
```typescript
getLogList(params?: PaginationParams & { user_id?: string; action?: number }): Promise<ApiResponse<UserLog>>
```

#### getLogDetail - 获取日志详情
```typescript
getLogDetail(id: string): Promise<UserLog>
```

---

## 项目模块 (project.ts)

### 项目信息

#### getProjectList - 获取项目列表
```typescript
getProjectList(params?: PaginationParams & { name?: string; status?: number }): Promise<ApiResponse<Project>>
```

#### getProjectDetail - 获取项目详情
```typescript
getProjectDetail(id: string): Promise<Project>
```

#### createProject - 创建项目
```typescript
createProject(data: Partial<Project> & { user_ids?: string[] }): Promise<Project>
```

#### updateProject - 更新项目
```typescript
updateProject(id: string, data: Partial<Project> & { user_ids?: string[] }): Promise<Project>
```

#### deleteProject - 删除项目
```typescript
deleteProject(id: string): Promise<void>
```

### 项目账号

#### getProjectAccountList - 获取项目账号列表
```typescript
getProjectAccountList(params?: PaginationParams & {
  project_id?: string
  status?: number
  account_type?: number
}): Promise<ApiResponse<ProjectAccount>>
```

#### getProjectAccountDetail - 获取项目账号详情
```typescript
getProjectAccountDetail(id: string): Promise<ProjectAccount>
```

#### createProjectAccount - 创建项目账号
```typescript
createProjectAccount(data: Partial<ProjectAccount>): Promise<ProjectAccount>
```

#### updateProjectAccount - 更新项目账号
```typescript
updateProjectAccount(id: string, data: Partial<ProjectAccount>): Promise<ProjectAccount>
```

#### deleteProjectAccount - 删除项目账号
```typescript
deleteProjectAccount(id: string): Promise<void>
```

### 项目钱包

#### getProjectWalletList - 获取项目钱包列表
```typescript
getProjectWalletList(params?: PaginationParams & { chain?: string }): Promise<ApiResponse<ProjectWallet>>
```

#### getProjectWalletDetail - 获取项目钱包详情
```typescript
getProjectWalletDetail(id: string): Promise<ProjectWallet>
```

#### createProjectWallet - 创建项目钱包
```typescript
createProjectWallet(data: Partial<ProjectWallet>): Promise<ProjectWallet>
```

#### updateProjectWallet - 更新项目钱包
```typescript
updateProjectWallet(id: string, data: Partial<ProjectWallet>): Promise<ProjectWallet>
```

#### deleteProjectWallet - 删除项目钱包
```typescript
deleteProjectWallet(id: string): Promise<void>
```

### 项目余额

#### getProjectBalanceList - 获取项目余额列表
```typescript
getProjectBalanceList(params?: PaginationParams & { account_id?: string }): Promise<ApiResponse<ProjectBalance>>
```

#### getProjectBalanceDetail - 获取项目余额详情
```typescript
getProjectBalanceDetail(id: string): Promise<ProjectBalance>
```

#### createProjectBalance - 创建项目余额
```typescript
createProjectBalance(data: Partial<ProjectBalance>): Promise<ProjectBalance>
```

#### updateProjectBalance - 更新项目余额
```typescript
updateProjectBalance(id: string, data: Partial<ProjectBalance>): Promise<ProjectBalance>
```

#### deleteProjectBalance - 删除项目余额
```typescript
deleteProjectBalance(id: string): Promise<void>
```

---

## 服务器模块 (server.ts)

### 国家信息

#### getCountryList - 获取国家列表
```typescript
getCountryList(params?: PaginationParams & { status?: number }): Promise<ApiResponse<ServerCountry>>
```

#### getCountryDetail - 获取国家详情
```typescript
getCountryDetail(id: string): Promise<ServerCountry>
```

#### createCountry - 创建国家
```typescript
createCountry(data: Partial<ServerCountry>): Promise<ServerCountry>
```

#### updateCountry - 更新国家
```typescript
updateCountry(id: string, data: Partial<ServerCountry>): Promise<ServerCountry>
```

#### deleteCountry - 删除国家
```typescript
deleteCountry(id: string): Promise<void>
```

### 分组信息

#### getGroupList - 获取分组列表
```typescript
getGroupList(params?: PaginationParams & { country_id?: string; status?: number }): Promise<ApiResponse<ServerGroup>>
```

#### getGroupDetail - 获取分组详情
```typescript
getGroupDetail(id: string): Promise<ServerGroup>
```

#### createGroup - 创建分组
```typescript
createGroup(data: Partial<ServerGroup>): Promise<ServerGroup>
```

#### updateGroup - 更新分组
```typescript
updateGroup(id: string, data: Partial<ServerGroup>): Promise<ServerGroup>
```

#### deleteGroup - 删除分组
```typescript
deleteGroup(id: string): Promise<void>
```

### 服务器信息

#### getServerList - 获取服务器列表
```typescript
getServerList(params?: PaginationParams & {
  host?: string
  group_id?: string
  status?: number
  is_sale?: number
}): Promise<ApiResponse<ServerInfo>>
```

#### getServerDetail - 获取服务器详情
```typescript
getServerDetail(id: string): Promise<ServerInfo>
```

#### createServer - 创建服务器
```typescript
createServer(data: Partial<ServerInfo>): Promise<ServerInfo>
```

#### updateServer - 更新服务器
```typescript
updateServer(id: string, data: Partial<ServerInfo>): Promise<ServerInfo>
```

#### deleteServer - 删除服务器
```typescript
deleteServer(id: string): Promise<void>
```

### 服务器账号

#### getServerAccountList - 获取服务器账号列表
```typescript
getServerAccountList(params?: PaginationParams & { user_id?: string }): Promise<ApiResponse<ServerAccount>>
```

#### getServerAccountDetail - 获取服务器账号详情
```typescript
getServerAccountDetail(id: string): Promise<ServerAccount>
```

#### createServerAccount - 创建服务器账号
```typescript
createServerAccount(data: Partial<ServerAccount>): Promise<ServerAccount>
```

#### updateServerAccount - 更新服务器账号
```typescript
updateServerAccount(id: string, data: Partial<ServerAccount>): Promise<ServerAccount>
```

#### deleteServerAccount - 删除服务器账号
```typescript
deleteServerAccount(id: string): Promise<void>
```

---

## 邮箱模块 (mail.ts)

### 邮箱信息

#### getEmailList - 获取邮箱列表
```typescript
getEmailList(params?: PaginationParams & {
  email?: string
  status?: number
  email_type?: EmailType
  server_id?: string
}): Promise<ApiResponse<EmailInfo>>
```

#### getEmailDetail - 获取邮箱详情
```typescript
getEmailDetail(id: string): Promise<EmailInfo>
```

#### createEmail - 创建邮箱
```typescript
createEmail(data: Partial<EmailInfo>): Promise<EmailInfo>
```

#### updateEmail - 更新邮箱
```typescript
updateEmail(id: string, data: Partial<EmailInfo>): Promise<EmailInfo>
```

#### deleteEmail - 删除邮箱
```typescript
deleteEmail(id: string): Promise<void>
```

#### batchUpdateEmailStatus - 批量更新邮箱状态
```typescript
batchUpdateEmailStatus(data: { from_status: number; to_status: number }): Promise<ApiResponse>
```

### Outlook 操作

#### getOutlookAuthUrl - 获取 Outlook 授权 URL
```typescript
getOutlookAuthUrl(email: string): Promise<{ url: string; verifier: string }>
```

#### getOutlookToken - 获取 Outlook Token
```typescript
getOutlookToken(data: {
  email: string
  url: string
  verifier: string
}): Promise<ApiResponse>
```

#### sendOutlookEmail - 发送 Outlook 邮件
```typescript
sendOutlookEmail(data: {
  email: string
  to_email: string
  subject: string
  content: string
  content_type?: 'Text' | 'HTML'
}): Promise<ApiResponse>
```

#### getOutlookMessages - 获取 Outlook 邮件
```typescript
getOutlookMessages(data: {
  email: string
  from_email: string
  num?: number
  top?: number
}): Promise<{ code: number; message: string; data: any[] }>
```

#### checkEmailStatus - 检查邮箱状态
```typescript
checkEmailStatus(data: {
  update_time_start?: number
  update_time_end?: number
  status?: number
  email_type?: EmailType
}): Promise<ApiResponse>
```

---

## 通用类型

### PaginationParams
```typescript
interface PaginationParams {
  page?: number        // 页码，默认 1
  limit?: number       // 每页条数，默认 10
  res_count?: boolean  // 是否返回总数，默认 false
  order_by?: string    // 排序字段，如 '-create_time'
}
```

### ApiResponse
```typescript
interface ApiResponse<T = any> {
  message: string   // 响应消息
  count?: number    // 总数（res_count=true 时返回）
  num?: number      // 当前页条数
  items?: T[]       // 数据列表
  data?: T          // 单条数据
}
```

---

## 使用示例

### 基础查询
```typescript
const res = await getUserList({ page: 1, limit: 10 })
console.log(res.items) // 用户列表
console.log(res.count) // 总数
```

### 带筛选条件
```typescript
const res = await getUserList({
  page: 1,
  limit: 10,
  email: 'test@example.com',
  status: 1,
  res_count: true,
})
```

### 创建数据
```typescript
const user = await createUser({
  email: 'test@example.com',
  nickname: '测试用户',
  password: '123456',
  status: 1,
  role_ids: ['role-id-1', 'role-id-2'],
})
```

### 更新数据
```typescript
await updateUser('user-id', {
  nickname: '新昵称',
  status: 2,
})
```

### 删除数据
```typescript
await deleteUser('user-id')
```

---

## 错误处理

所有 API 调用的错误都已在 Axios 拦截器中统一处理：

- **401**：自动跳转登录页
- **404**：静默处理（表示无数据）
- **其他错误**：自动显示错误提示

因此在调用 API 时，通常不需要额外的错误处理：

```typescript
try {
  const res = await getUserList()
  // 处理数据
} catch (error) {
  // 错误已自动提示，这里可以做额外处理（可选）
}
```

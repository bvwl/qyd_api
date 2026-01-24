# 邮件查看器问题排查

## 问题描述

访问 `http://localhost:3000/mail/viewer` 时出现问题。

## 可能的情况

### 情况1：页面显示404或空白

**原因**：前端路由或组件加载问题

**排查步骤**：

1. 检查浏览器控制台是否有错误
2. 检查前端是否正常启动
3. 检查路由配置是否正确

**解决方案**：

```bash
# 重启前端开发服务器
cd frontend
npm run dev
```

### 情况2：页面显示但没有数据

**原因**：API 调用失败或数据格式问题

**排查步骤**：

1. 打开浏览器开发者工具（F12）
2. 切换到 Network 标签
3. 输入邮箱地址并点击"查看邮件"
4. 查看是否有 `/v1/mail/outlook/messages` 的请求
5. 查看请求的响应内容

**预期行为**：

- 请求地址：`http://127.0.0.1:6080/v1/mail/outlook/messages`
- 请求方法：POST
- 请求体：
  ```json
  {
    "email": "zhiyu918918@outlook.com",
    "from_email": "@",
    "num": 10,
    "top": 10
  }
  ```
- 响应状态：200
- 响应体：
  ```json
  {
    "code": 1,
    "message": "获取成功",
    "data": [...]
  }
  ```

### 情况3：CORS 错误

**症状**：浏览器控制台显示 CORS 相关错误

**原因**：后端 CORS 配置问题

**解决方案**：

检查后端 `.env` 文件中的 CORS 配置：

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

确保包含前端地址 `http://localhost:3000`。

### 情况4：后端未启动

**症状**：Network 标签显示请求失败，状态为 `net::ERR_CONNECTION_REFUSED`

**解决方案**：

```bash
# 启动后端服务
cd backend
python start.py
```

## 完整的测试流程

### 1. 确认后端正常运行

```bash
# 测试后端 API
curl -X POST "http://127.0.0.1:6080/v1/mail/outlook/messages" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhiyu918918@outlook.com",
    "from_email": "@",
    "num": 10,
    "top": 10
  }'
```

预期响应：
```json
{
  "code": 1,
  "message": "获取成功",
  "data": [...]
}
```

### 2. 确认前端正常运行

1. 访问 `http://localhost:3000`
2. 登录系统
3. 从菜单进入"邮件管理" -> "邮件查看器"
4. 或直接访问 `http://localhost:3000/mail/viewer`

### 3. 测试邮件查看功能

1. 在邮箱地址输入框输入：`zhiyu918918@outlook.com`
2. 点击"查看邮件"按钮
3. 打开浏览器开发者工具（F12）
4. 切换到 Network 标签
5. 查看是否有 API 请求
6. 查看请求和响应的内容

### 4. 检查常见问题

#### 问题：点击"查看邮件"没有反应

**可能原因**：
- JavaScript 错误
- 按钮事件未绑定

**排查**：
- 打开浏览器控制台（F12 -> Console）
- 查看是否有错误信息

#### 问题：显示"获取邮件失败"

**可能原因**：
- 后端返回错误
- 邮箱未授权
- Token 过期

**排查**：
- 查看 Network 标签中的响应内容
- 检查后端日志

#### 问题：显示"暂无邮件"

**可能原因**：
- 邮箱确实没有邮件
- 后端返回空数组

**排查**：
- 查看 Network 标签中的响应
- 确认 `data` 数组是否为空

## 前端路由说明

### 路由配置

```typescript
{
  path: 'mail/viewer',
  element: <MailViewer />,
}
```

### 访问方式

1. **通过菜单**：点击侧边栏的"邮件查看器"菜单项
2. **直接访问**：在浏览器地址栏输入 `http://localhost:3000/mail/viewer`

### 路由工作原理

1. 用户访问 `/mail/viewer`
2. React Router 匹配到路由配置
3. 渲染 `MailViewer` 组件
4. 组件加载后，用户输入邮箱地址
5. 点击"查看邮件"按钮
6. 组件调用 `getInboxMessages` API
7. API 发送 POST 请求到 `http://127.0.0.1:6080/v1/mail/outlook/messages`
8. 后端处理请求并返回数据
9. 前端接收数据并显示在表格中

## API 调用流程

```
前端组件 (MailViewer.tsx)
    ↓
    调用 fetchMessages()
    ↓
API 层 (mail.ts)
    ↓
    调用 getInboxMessages()
    ↓
Axios 实例 (index.ts)
    ↓
    发送 POST 请求
    ↓
后端 API (outlook.py)
    ↓
    /v1/mail/outlook/messages
    ↓
Outlook 客户端 (outlook.py)
    ↓
    get_emails_main()
    ↓
返回邮件数据
```

## 调试技巧

### 1. 使用浏览器开发者工具

- **Console**：查看 JavaScript 错误和日志
- **Network**：查看 API 请求和响应
- **Elements**：检查 DOM 结构
- **React DevTools**：查看组件状态和 props

### 2. 添加调试日志

在 `MailViewer.tsx` 的 `fetchMessages` 函数中添加：

```typescript
const fetchMessages = async (email: string, useCache: boolean = true) => {
  console.log('开始获取邮件，邮箱:', email)
  
  // ... 现有代码 ...
  
  try {
    const res = await getInboxMessages({ email, top: 10 })
    console.log('API 响应:', res)
    
    if (res.code === 1 && res.data && Array.isArray(res.data)) {
      console.log('成功获取邮件数量:', res.data.length)
      setMessages(res.data)
      // ...
    }
  } catch (error) {
    console.error('获取邮件失败:', error)
    // ...
  }
}
```

### 3. 检查后端日志

```bash
# 查看后端日志
tail -f backend/logs/api.log
```

## 常见错误及解决方案

### 错误1：404 Not Found

**错误信息**：`GET http://localhost:3000/mail/viewer 404 (Not Found)`

**原因**：前端路由配置错误或组件未正确导出

**解决**：
1. 检查 `frontend/src/router/index.tsx` 中的路由配置
2. 确认 `MailViewer` 组件正确导出
3. 重启前端开发服务器

### 错误2：Network Error

**错误信息**：`Network Error` 或 `ERR_CONNECTION_REFUSED`

**原因**：后端未启动或端口不正确

**解决**：
1. 启动后端服务：`python backend/start.py`
2. 确认后端端口为 6080
3. 检查防火墙设置

### 错误3：401 Unauthorized

**错误信息**：`401 Unauthorized`

**原因**：Token 过期或无效

**解决**：
1. 重新登录获取新 Token
2. 检查 Token 是否正确存储在 localStorage

### 错误4：500 Internal Server Error

**错误信息**：`500 Internal Server Error`

**原因**：后端代码错误

**解决**：
1. 查看后端日志：`tail -f backend/logs/api.log`
2. 检查后端代码是否有语法错误
3. 确认数据库连接正常

## 总结

如果你遇到问题，请按照以下步骤排查：

1. ✅ 确认后端正常运行（端口 6080）
2. ✅ 确认前端正常运行（端口 3000）
3. ✅ 打开浏览器开发者工具
4. ✅ 访问 `http://localhost:3000/mail/viewer`
5. ✅ 输入邮箱地址并点击"查看邮件"
6. ✅ 查看 Network 标签中的 API 请求
7. ✅ 查看 Console 标签中的错误信息

如果还有问题，请提供：
- 浏览器控制台的错误信息
- Network 标签中的请求和响应内容
- 后端日志中的错误信息

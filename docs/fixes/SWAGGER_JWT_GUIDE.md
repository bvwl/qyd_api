# Swagger文档中使用JWT认证指南

## 快速开始

### 1. 启动后端服务

```bash
cd backend
python start.py
```

### 2. 访问Swagger文档

打开浏览器访问：`http://localhost:6080/docs`

### 3. 获取JWT Token

有两种方式获取Token：

#### 方式A：使用Swagger的登录接口

1. 找到 `POST /api/v1/user/login` 接口
2. 点击 "Try it out"
3. 输入登录信息：
   ```json
   {
     "email": "zhiyu",
     "password": "2201101122@qq.com"
   }
   ```
4. 点击 "Execute"
5. 从响应中复制 `access_token` 的值

#### 方式B：使用curl命令

```bash
curl -X POST "http://localhost:6080/api/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhiyu",
    "password": "2201101122@qq.com"
  }'
```

### 4. 在Swagger中授权

1. 点击页面右上角的 **🔒 Authorize** 按钮
2. 在弹出的对话框中，粘贴你的JWT Token
   - **注意**：只需要粘贴token本身，不需要 "Bearer " 前缀
   - 系统会自动添加 "Bearer " 前缀
3. 点击 **Authorize** 按钮
4. 点击 **Close** 关闭对话框

### 5. 测试API

现在所有带🔒图标的API都会自动使用你的JWT Token：

1. 找到任意需要认证的API（例如 `GET /api/v1/project/wallet`）
2. 点击 "Try it out"
3. 输入参数（如果需要）
4. 点击 "Execute"
5. 查看响应结果

## 常见问题

### Q1: 为什么有些API没有🔒图标？

A: 只有需要认证的API才会显示🔒图标。例如：
- ✅ 需要认证：`GET /api/v1/project/wallet`（有🔒）
- ❌ 不需要认证：`POST /api/v1/user/login`（无🔒）

### Q2: Token过期了怎么办？

A: 重新登录获取新的Token，然后在Swagger中重新授权。

默认Token有效期：365天（可在 `.env` 中配置）

### Q3: 如何退出登录？

A: 在Swagger中：
1. 点击右上角的 **🔒 Authorize** 按钮
2. 点击 **Logout** 按钮
3. 点击 **Close**

### Q4: 为什么我授权后还是返回401？

可能的原因：
1. Token已过期 - 重新登录获取新Token
2. Token格式错误 - 确保只粘贴token本身，不要包含 "Bearer "
3. 用户被禁用 - 检查用户状态

### Q5: 如何查看当前使用的Token？

在Swagger中：
1. 点击右上角的 **🔒 Authorize** 按钮
2. 可以看到当前的Token（部分隐藏）
3. 点击 **Logout** 可以清除Token

## 权限说明

不同的API需要不同的权限级别：

### 🟢 基础权限（所有登录用户）
- 查看列表、详情
- 创建、更新自己的数据

### 🟡 GM权限（GM或ADMIN）
- 删除项目相关数据
- 管理项目账号

### 🔴 管理员权限（仅ADMIN）
- 删除用户
- 系统配置
- 角色管理

## 测试账号

### 管理员账号
- Email: `zhiyu`
- Password: `2201101122@qq.com`
- 角色: ADMIN
- 权限: 全部

## API响应示例

### 成功响应（200）
```json
{
  "message": "成功",
  "count": 10,
  "items": [...]
}
```

### 未授权（401）
```json
{
  "detail": "Authentication required"
}
```

### 权限不足（403）
```json
{
  "detail": "Admin permission required"
}
```

### 资源不存在（404）
```json
{
  "detail": "数据不存在"
}
```

## 前端集成

如果你在开发前端应用，参考以下代码：

```typescript
// src/api/index.ts
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:6080',
})

// 请求拦截器：自动添加JWT Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理401错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token过期或无效，跳转到登录页
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
```

## 相关文档

- [JWT认证完整文档](./JWT_AUTH_ONLY.md)
- [API文档](http://localhost:6080/docs)
- [ReDoc文档](http://localhost:6080/redoc)

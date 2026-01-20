# QYD API 前端应用（frontend）

本目录为 QYD API 的前端应用代码，基于 **React 18 + TypeScript + Ant Design** 实现，主要提供：

- 用户管理界面（用户、角色、权限、日志、Token）
- 项目管理界面（项目信息、账号、钱包、余额）
- 服务器管理界面（国家、分组、服务器信息、代理账号）
- 邮箱管理界面（邮箱信息、Outlook 授权/收发邮件）
- 基于角色的访问控制（RBAC）权限管理
- 响应式布局，支持移动端访问

运行环境：**Node.js 18+**（建议）  
包管理器：**npm** 或 **yarn**

**后端 API 地址：** `http://127.0.0.1:6080`  
**API 文档：** `http://127.0.0.1:6080/docs`

---

## 1. 快速启动

### 1.1 安装依赖

在 `frontend/` 目录下执行：

```bash
npm install
# 或
yarn install
```

### 1.2 启动开发服务器

```bash
npm run dev
# 或
yarn dev
```

服务启动后，访问：`http://localhost:3000`

默认登录账号（需要先在后端创建）：
- 邮箱：admin@example.com
- 密码：admin123

### 1.3 构建生产版本

```bash
npm run build
# 或
yarn build
```

构建产物在 `dist/` 目录下。

### 1.4 预览生产版本

```bash
npm run preview
# 或
yarn preview
```

---

## 2. 技术栈

### 核心框架
- **前端框架：** React 18.3.1 + TypeScript 5.6.2
- **构建工具：** Vite 6.0.1
- **状态管理：** Zustand 5.0.2（轻量级状态管理）
- **路由管理：** React Router 7.1.1

### UI 组件库
- **UI 框架：** Ant Design 5.22.5
- **图标库：** @ant-design/icons 5.5.2
- **样式方案：** CSS Modules + Less

### 网络请求
- **HTTP 客户端：** Axios 1.7.9
- **请求拦截：** 统一处理 Token、错误、加载状态

### 其他工具
- **日期处理：** dayjs 1.11.13
- **表单验证：** Ant Design Form 内置

---

## 3. 项目结构

```
frontend/
├── src/
│   ├── api/                    # API 接口封装
│   │   ├── index.ts           # Axios 实例配置
│   │   ├── user.ts            # 用户相关接口
│   │   ├── project.ts         # 项目相关接口
│   │   ├── server.ts          # 服务器相关接口
│   │   └── mail.ts            # 邮箱相关接口
│   ├── components/            # 公共组件
│   │   └── Layout/           # 布局组件
│   ├── views/                 # 页面视图
│   │   ├── Login/            # 登录页
│   │   ├── User/             # 用户管理
│   │   └── Mail/             # 邮箱管理
│   ├── router/                # 路由配置
│   │   └── index.tsx         # 路由定义
│   ├── store/                 # 状态管理
│   │   └── useUserStore.ts   # 用户状态
│   ├── types/                 # TypeScript 类型定义
│   │   └── index.ts          # 类型定义
│   ├── utils/                 # 工具函数
│   │   ├── constants.ts      # 常量定义
│   │   └── format.ts         # 格式化函数
│   ├── App.tsx               # 根组件
│   ├── main.tsx              # 入口文件
│   ├── index.css             # 全局样式
│   └── vite-env.d.ts         # Vite 类型定义
├── public/                    # 公共资源
├── index.html                # HTML 模板
├── .env.development          # 开发环境变量
├── .env.production           # 生产环境变量
├── vite.config.ts            # Vite 配置
├── tsconfig.json             # TypeScript 配置
├── package.json              # 依赖配置
└── README.md                 # 项目文档
```

---

## 4. 已实现功能

### 4.1 用户认证
- ✅ 登录页面（邮箱 + 密码）
- ✅ Token 管理（自动添加到请求头）
- ✅ 登录状态持久化
- ✅ 退出登录

### 4.2 用户管理
- ✅ 用户列表（分页、搜索、筛选）
- ✅ 新增用户
- ✅ 编辑用户
- ✅ 删除用户
- ✅ 角色分配

### 4.3 邮箱管理
- ✅ 邮箱列表（分页、搜索、筛选）
- ✅ 邮箱类型筛选（IP/Token 状态组合）
- ✅ 新增邮箱
- ✅ 编辑邮箱
- ✅ 删除邮箱
- ✅ 批量更新状态
- ✅ 密码脱敏显示

### 4.4 布局与导航
- ✅ 响应式侧边栏
- ✅ 顶部导航栏
- ✅ 用户信息展示
- ✅ 菜单导航

---

## 5. 待扩展功能

以下功能已完成 API 封装和类型定义，可快速开发：

### 5.1 角色权限模块
- 角色列表
- 角色编辑
- 路由管理
- 权限分配

### 5.2 项目管理模块
- 项目列表
- 项目详情
- 项目账号管理
- 项目钱包管理
- 项目余额管理

### 5.3 服务器管理模块
- 国家管理
- 分组管理
- 服务器列表
- 服务器账号管理

### 5.4 邮箱高级功能
- Outlook 授权流程
- 发送邮件
- 查看邮件
- 邮箱状态检查

---

## 6. 开发指南

### 6.1 添加新页面

1. 在 `src/views/` 下创建页面组件
2. 在 `src/router/index.tsx` 中添加路由
3. 在 `src/components/Layout/index.tsx` 中添加菜单项

示例：

```tsx
// 1. 创建页面组件 src/views/Project/ProjectList.tsx
export default function ProjectList() {
  return <div>项目列表</div>
}

// 2. 添加路由
{
  path: 'project/list',
  element: <ProjectList />,
}

// 3. 添加菜单项（已在 Layout 中定义）
```

### 6.2 调用 API

```tsx
import { getProjectList } from '@/api/project'

const fetchData = async () => {
  try {
    const res = await getProjectList({ page: 1, limit: 10 })
    console.log(res.items)
  } catch (error) {
    // 错误已在拦截器中处理
  }
}
```

### 6.3 使用状态管理

```tsx
import { useUserStore } from '@/store/useUserStore'

function MyComponent() {
  const { userInfo, logout } = useUserStore()
  
  return (
    <div>
      <p>当前用户：{userInfo?.nickname}</p>
      <button onClick={logout}>退出</button>
    </div>
  )
}
```

---

## 7. 代码规范

### 7.1 命名规范
- 组件名：PascalCase（如 `UserList.tsx`）
- 文件名：PascalCase（如 `UserList.tsx`）
- 变量名：camelCase（如 `userName`）
- 常量名：UPPER_SNAKE_CASE（如 `API_BASE_URL`）
- 类型名：PascalCase（如 `UserInfo`）

### 7.2 组件规范
- 使用函数式组件 + Hooks
- 使用 TypeScript 严格类型检查
- Props 使用 interface 定义类型
- 导出使用 `export default`

### 7.3 样式规范
- 使用 CSS Modules 或 Less
- 避免内联样式（除非必要）
- 使用 Ant Design 的 theme token

---

## 8. 环境变量

### 开发环境 (.env.development)
```env
VITE_API_BASE_URL=http://127.0.0.1:6080
VITE_APP_TITLE=QYD 项目管理系统（开发）
```

### 生产环境 (.env.production)
```env
VITE_API_BASE_URL=https://api.example.com
VITE_APP_TITLE=QYD 项目管理系统
```

---

## 9. 部署

### 9.1 Nginx 配置

```nginx
server {
    listen 80;
    server_name example.com;
    
    root /var/www/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /v1 {
        proxy_pass http://127.0.0.1:6080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 9.2 Docker 部署

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 10. 常见问题

### 10.1 API 请求 404

检查后端服务是否启动：
```bash
curl http://127.0.0.1:6080/docs
```

### 10.2 Token 过期

Token 过期会自动跳转到登录页，重新登录即可。

### 10.3 CORS 错误

确保后端 CORS 配置正确，或使用 Vite 代理（已配置）。

### 10.4 依赖安装失败

尝试清除缓存后重新安装：
```bash
rm -rf node_modules package-lock.json
npm install
```

---

## 11. 下一步开发建议

1. **完善其他页面**：参考 `UserList.tsx` 和 `MailList.tsx` 的实现，快速开发其他模块
2. **添加权限控制**：使用 `useUserStore` 中的 `hasPermission` 方法控制按钮显示
3. **优化用户体验**：添加 loading 状态、空状态、错误提示等
4. **添加单元测试**：使用 Vitest + React Testing Library
5. **性能优化**：使用 React.memo、useMemo、useCallback 等优化渲染

---

## 12. 联系方式

如有问题，请联系开发团队。

**后端 API 文档：** http://127.0.0.1:6080/docs

# QYD 前端应用

基于 React + TypeScript + Ant Design 的现代化管理系统前端。

## 技术栈

- **框架**: React 18
- **语言**: TypeScript 5
- **UI库**: Ant Design 5
- **路由**: React Router v6
- **状态管理**: Zustand
- **HTTP客户端**: Axios
- **构建工具**: Vite 5
- **日期处理**: dayjs
- **样式**: Less + CSS Modules

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API接口封装
│   │   ├── index.ts      # Axios配置和拦截器
│   │   ├── user.ts       # 用户相关API
│   │   ├── project.ts    # 项目相关API
│   │   ├── server.ts     # 服务器相关API
│   │   └── mail.ts       # 邮箱相关API
│   ├── components/       # 公共组件
│   │   ├── Layout/       # 布局组件
│   │   ├── ProtectedRoute/  # 路由守卫
│   │   ├── ApiTester/    # API测试工具
│   │   └── ...
│   ├── views/            # 页面组件
│   │   ├── Login/        # 登录页
│   │   ├── Dashboard/    # 仪表盘
│   │   ├── User/         # 用户管理
│   │   ├── Project/      # 项目管理
│   │   ├── Server/       # 服务器管理
│   │   ├── Mail/         # 邮箱管理
│   │   └── ApiDocs/      # API文档
│   ├── store/            # 状态管理
│   │   └── useUserStore.ts  # 用户状态
│   ├── utils/            # 工具函数
│   │   ├── token.ts      # Token管理
│   │   ├── format.ts     # 格式化工具
│   │   └── constants.ts  # 常量定义
│   ├── types/            # TypeScript类型定义
│   │   └── index.ts
│   ├── router/           # 路由配置
│   ├── App.tsx           # 应用入口
│   └── main.tsx          # 主入口
├── tests/                # 测试文件
├── public/               # 静态资源
├── .env.development      # 开发环境配置
├── .env.production       # 生产环境配置
├── vite.config.ts        # Vite配置
├── tsconfig.json         # TypeScript配置
├── package.json          # 依赖配置
└── README.md             # 本文档
```

## 安装

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

开发环境 (`.env.development`):

```env
VITE_API_BASE_URL=http://localhost:6080
VITE_APP_TITLE=QYD管理系统
```

生产环境 (`.env.production`):

```env
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_APP_TITLE=QYD管理系统
```

## 启动

### 开发模式

```bash
npm run dev
```

应用将在 `http://localhost:3000` 启动

### 生产构建

```bash
npm run build
```

构建产物在 `dist/` 目录

### 预览生产构建

```bash
npm run preview
```

## 核心功能

### 1. 认证系统

- JWT Token认证
- 自动Token刷新
- 路由守卫
- 权限控制 (RBAC)

### 2. 状态管理

使用Zustand管理全局状态：
- 用户信息
- 登录状态
- 权限信息

### 3. API封装

统一的API调用方式，自动添加Token：

```typescript
import { request } from '@/api'

// GET请求
const data = await request.get('/api/v1/users')

// POST请求
const result = await request.post('/api/v1/users', { email: 'test@example.com' })
```

### 4. 错误处理

- 全局错误拦截
- 友好的错误提示
- 401自动跳转登录
- 404静默处理

### 5. 组件库

基于Ant Design 5，包含：
- 表格组件 (支持分页、搜索、排序)
- 表单组件 (支持验证)
- 模态框组件
- 搜索组件 (支持时间范围)

### 6. 邮件查看器

集成Outlook邮件查看功能：

```typescript
import MailViewer from '@/views/Mail/MailViewer'

// 使用组件
<MailViewer mailId={mailId} />
```

特性：
- **HTML渲染**: 安全渲染HTML邮件内容 (使用DOMPurify)
- **本地缓存**: 10分钟本地缓存，减少API调用
- **搜索功能**: 支持文本搜索和正则表达式搜索
- **附件支持**: 显示附件列表和下载链接
- **响应式**: 适配不同屏幕尺寸

### 7. 数据加密显示

项目账号的敏感字段（`private_key`、`mnemonic`）会根据用户权限自动显示：

- **有权限用户**（ADMIN、项目所属人）：显示明文
- **无权限用户**：显示密文（加密数据）

前端无需特殊处理，后端API会根据用户权限自动返回相应的数据。

## 页面说明

### 仪表盘 (`/dashboard`)
- 数据统计卡片
- 最近用户列表
- 最近项目列表
- API Token管理

### 用户管理 (`/user/*`)
- **用户列表** (`/user/list`): 用户CRUD、角色分配
- **角色管理** (`/user/role`): 角色CRUD、权限配置
- **路由管理** (`/user/route`): 路由权限配置
- **操作日志** (`/user/log`): 用户操作记录

### 项目管理 (`/project/*`)
- **项目列表** (`/project/list`): 项目CRUD
- **项目账号** (`/project/account`): 账号管理、批量操作
- **项目钱包** (`/project/wallet`): 钱包管理

### 服务器管理 (`/server/*`)
- **服务器列表** (`/server/list`): 服务器CRUD
- **国家管理** (`/server/country`): 国家/地区管理
- **分组管理** (`/server/group`): 服务器分组
- **服务器账号** (`/server/account`): 账号管理

### 邮箱管理 (`/mail/*`)
- **邮箱列表** (`/mail/list`): 邮箱CRUD、状态监控
- **邮件查看** (`/mail/viewer/:id`): 查看邮件内容、搜索、附件
- **发送邮件** (`/mail/send`): 发送邮件功能

### API文档 (`/api-docs/*`)
- 内置API测试工具
- 支持所有API接口测试
- 自动添加认证Token

## 常用命令

```bash
npm run dev      # 开发模式
npm run build    # 生产构建
npm run preview  # 预览构建产物
npm run lint     # 代码检查
```

## 开发指南

### 添加新页面

1. 在 `src/views/` 创建页面组件
2. 在 `src/router/` 配置路由
3. 在 `src/api/` 添加API接口
4. 使用 `<ProtectedRoute>` 包裹需要认证的页面

示例：

```typescript
// src/views/Example/index.tsx
import { useEffect, useState } from 'react'
import { Table } from 'antd'
import { getExampleList } from '@/api/example'

export default function ExamplePage() {
  const [data, setData] = useState([])
  
  useEffect(() => {
    loadData()
  }, [])
  
  const loadData = async () => {
    const result = await getExampleList()
    setData(result.items)
  }
  
  return <Table dataSource={data} />
}
```

### 使用权限控制

```typescript
import { usePermission } from '@/hooks/usePermission'

function MyComponent() {
  const { hasPermission } = usePermission()
  
  return (
    <>
      {hasPermission('ADMIN') && <AdminButton />}
      {hasPermission(['ADMIN', 'GM']) && <ManagerButton />}
    </>
  )
}
```

### API调用规范

```typescript
// src/api/example.ts
import { request } from './index'

export interface ExampleItem {
  id: string
  name: string
}

export const getExampleList = (params?: any) => {
  return request.post<{ items: ExampleItem[] }>('/api/v1/example/list', params)
}

export const createExample = (data: Partial<ExampleItem>) => {
  return request.post('/api/v1/example/create', data)
}
```

## 相关链接

- [React文档](https://react.dev/)
- [Ant Design文档](https://ant.design/)
- [Vite文档](https://vitejs.dev/)

## 更新日志

查看 `../docs/fixes/` 目录了解详细的修复和更新记录。

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
- 权限控制

### 2. 状态管理

使用Zustand管理全局状态

### 3. API封装

统一的API调用方式，自动添加Token

### 4. 错误处理

- 全局错误拦截
- 友好的错误提示
- 401自动跳转登录

### 5. 组件库

基于Ant Design 5

## 页面说明

### 仪表盘
- 数据统计
- 最近用户/项目列表

### 用户管理
- 用户列表、角色管理、路由管理
- Token管理、操作日志

### 项目管理
- 项目列表、账号、钱包、余额

### 服务器管理
- 服务器列表、国家、分组、账号

### 邮箱管理
- 邮箱列表、Outlook集成

### API文档
- 内置API测试工具

## 常用命令

```bash
npm run dev      # 开发
npm run build    # 构建
npm run preview  # 预览
```

## 相关链接

- [React文档](https://react.dev/)
- [Ant Design文档](https://ant.design/)
- [Vite文档](https://vitejs.dev/)

## 更新日志

查看 `../docs/fixes/` 目录了解详细的修复和更新记录。

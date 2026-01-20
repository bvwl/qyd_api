# 快速开始指南

## 前置要求

- Node.js 18+ 
- npm 或 yarn
- 后端服务已启动（http://127.0.0.1:6080）

## 安装步骤

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问：http://localhost:3000

### 3. 登录系统

首次使用需要先在后端创建用户，或使用已有账号登录。

## 项目特点

✅ **完整的类型定义**：所有 API 和数据模型都有 TypeScript 类型  
✅ **统一的 API 封装**：所有接口已封装完成，开箱即用  
✅ **响应式布局**：支持桌面和移动端  
✅ **状态持久化**：登录状态自动保存  
✅ **错误处理**：统一的错误拦截和提示  

## 已实现的页面

- ✅ 登录页面
- ✅ 用户列表（完整 CRUD）
- ✅ 邮箱列表（完整 CRUD + 批量操作）

## 快速开发新页面

参考 `src/views/User/UserList.tsx` 或 `src/views/Mail/MailList.tsx`，只需：

1. 复制模板代码
2. 修改 API 调用
3. 调整表格列定义
4. 添加路由和菜单

所有 API 和类型定义都已准备好，开发效率极高！

## 技术亮点

- **Zustand**：比 Redux 更简单的状态管理
- **React Router 7**：最新的路由方案
- **Ant Design 5**：企业级 UI 组件
- **Vite 6**：极速的开发体验
- **TypeScript 严格模式**：类型安全

## 下一步

查看 [README.md](./README.md) 了解完整文档。

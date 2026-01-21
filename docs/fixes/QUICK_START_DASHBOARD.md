# 🚀 仪表盘功能 - 快速开始

## ⚡ 核心功能

基于角色的仪表盘系统，不同角色看到不同的数据：

- **ADMIN**：所有用户、项目、账户数量 + 所有项目列表
- **GM**：所有项目、账户数量 + 所有项目列表
- **IT/MANUAL**：自己的项目、账户数量 + 自己的项目列表

## 🔧 新增文件

### 后端
- `backend/app/apis/v1/user/dashboard.py` - 仪表盘API

### 前端
- `frontend/src/views/Dashboard/index.tsx` - 仪表盘页面

## 📝 修改文件

- `backend/app/apis/v1/user/__init__.py` - 注册仪表盘路由
- `frontend/src/api/user.ts` - 添加仪表盘API函数
- `frontend/src/router/index.tsx` - 添加仪表盘路由，设为首页

## 🧪 快速测试

### 1. 重启服务

```bash
# 后端（如果正在运行，先停止）
cd backend
python start.py

# 前端
cd frontend
npm run dev
```

### 2. 测试API

```bash
python backend/test_dashboard.py
```

### 3. 访问页面

登录后会自动跳转到仪表盘：`http://localhost:5173/dashboard`

## 📊 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/v1/user/dashboard/stats` | GET | 获取统计数据 |
| `/v1/user/dashboard/projects` | GET | 获取项目列表 |

## ⚠️ 重要提示

1. **需要重启后端服务**才能使用新API
2. IT/MANUAL 用户需要先关联项目才能看到数据
3. 登录后默认跳转到仪表盘页面

## 📖 详细文档

查看完整文档：`DASHBOARD_IMPLEMENTATION.md`

## 🎯 角色数据对比

| 数据项 | ADMIN | GM | IT/MANUAL |
|--------|-------|----|----|
| 用户数量 | ✅ | ❌ | ❌ |
| 项目数量 | 全部 | 全部 | 自己的 |
| 账户数量 | 全部 | 全部 | 自己的 |
| 项目列表 | 全部 | 全部 | 自己的 |

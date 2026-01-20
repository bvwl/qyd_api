# QYD 项目管理系统

企业级全栈项目管理系统，基于 FastAPI + React + TypeScript 构建。

## 快速开始

### 后端启动

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 配置数据库连接
bash scripts/init_db.sh
python start.py
```

访问：http://127.0.0.1:6080/docs

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:3000

## 技术栈

### 后端
- FastAPI + Tortoise ORM
- Python 3.11+
- MySQL 8.0 + Redis 8.4
- APScheduler

### 前端
- React 18 + TypeScript 5
- Ant Design 5
- Zustand + React Router 7
- Vite 6

## 核心功能

- ✅ 用户管理（用户、角色、权限、日志）
- ✅ 项目管理（项目、账号、钱包、余额）
- ✅ 服务器管理（国家、分组、服务器、账号）
- ✅ 邮箱管理（邮箱、Outlook 授权、收发邮件）
- ✅ RBAC 权限控制
- ✅ 定时任务

## 文档

- [项目总览](PROJECT_OVERVIEW.md)
- [后端文档](backend/README.md)
- [前端文档](frontend/README.md)
- [需求文档](需求文档.md)

## 项目结构

```
qyd_api/
├── backend/          # 后端服务（FastAPI）
├── frontend/         # 前端应用（React）
├── 需求文档.md       # 项目需求
└── README.md         # 本文件
```

## 开发进度

- 后端：95% ✅
- 前端：40% 🚧（API 封装 100%，页面开发中）

## License

MIT

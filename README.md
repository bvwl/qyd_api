# QYD 项目管理系统

一个基于 FastAPI + React + TypeScript 的全栈项目管理系统，提供用户管理、项目管理、服务器管理、邮箱管理等功能。

## 项目结构

```
qyd_api2/
├── backend/          # 后端服务 (FastAPI + Python)
├── frontend/         # 前端应用 (React + TypeScript + Ant Design)
├── docs/            # 项目文档
│   └── fixes/       # 修复记录文档
└── README.md        # 项目说明文档
```

## 技术栈

### 后端
- **框架**: FastAPI 
- **数据库**: MySQL + Tortoise ORM
- **认证**: JWT (JSON Web Token)
- **密码加密**: bcrypt
- **任务调度**: APScheduler
- **日志**: 自定义日志系统

### 前端
- **框架**: React 18 + TypeScript
- **UI库**: Ant Design 5
- **路由**: React Router v6
- **状态管理**: Zustand
- **HTTP客户端**: Axios
- **构建工具**: Vite
- **日期处理**: dayjs

## 快速开始

### 后端启动

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库等信息

# 初始化数据库
python db/init_roles_and_admin.py

# 启动服务
python start.py
```

后端服务将在 `http://localhost:6080` 启动

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 `http://localhost:3000` 启动

## 默认账号

- **邮箱**: zhiyu
- **密码**: 2201101122@qq.com
- **角色**: ADMIN (管理员)

## 主要功能

### 用户管理
- ✅ 用户注册/登录 (JWT认证)
- ✅ 用户列表管理 (CRUD)
- ✅ 角色管理 (ADMIN, GM, IT, MANUAL)
- ✅ 用户角色分配
- ✅ 路由权限管理
- ✅ API Token管理
- ✅ 操作日志记录

### 项目管理
- ✅ 项目信息管理
- ✅ 项目账号管理
- ✅ 项目钱包管理
- ✅ 项目余额管理
- ✅ 多状态支持 (正常、维护、结束等)

### 服务器管理
- ✅ 服务器信息管理
- ✅ 国家/地区管理
- ✅ 服务器分组管理
- ✅ 服务器账号管理

### 邮箱管理
- ✅ 邮箱信息管理
- ✅ Outlook集成
- ✅ 邮箱状态监控
- ✅ 8种邮箱类型支持

### 其他功能
- ✅ 仪表盘数据统计
- ✅ 高级搜索 (支持时间范围过滤)
- ✅ 分页查询
- ✅ API接口测试工具
- ✅ 响应式布局

## API文档

启动后端服务后，访问以下地址查看API文档：

- Swagger UI: `http://localhost:6080/docs`
- ReDoc: `http://localhost:6080/redoc`

或在前端应用中使用内置的API测试工具（菜单：API文档）

## 开发指南

### 后端开发

详见 [backend/README.md](backend/README.md)

### 前端开发

详见 [frontend/README.md](frontend/README.md)

## 项目文档

所有修复记录和开发文档位于 `docs/fixes/` 目录：

- JWT认证实现
- 密码加密方案
- 角色权限系统
- 时间过滤功能
- API错误处理
- 前端组件开发
- 等等...

## 测试

### 后端测试

```bash
cd backend
pytest
```

测试文件位于 `backend/tests/`

### 前端测试

```bash
cd frontend
npm run test
```

测试文件位于 `frontend/tests/`

## 环境要求

### 后端
- Python 3.11+
- MySQL 5.7+ / 8.0+
- Redis (可选，用于缓存)

### 前端
- Node.js 18+
- npm 9+

## 部署

### 后端部署

使用 Docker:

```bash
cd backend
docker-compose up -d
```

### 前端部署

```bash
cd frontend
npm run build
# 将 dist/ 目录部署到静态服务器
```

## 许可证

[MIT License](LICENSE)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请联系项目维护者。

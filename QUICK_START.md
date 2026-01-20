# 快速启动指南

## 前置要求

### 后端
- Python 3.11+
- MySQL 8.0+
- Redis 8.4+（可选）

### 前端
- Node.js 18+
- npm 或 yarn

## 启动步骤

### 1. 启动后端

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接信息

# 初始化数据库
bash scripts/init_db.sh

# 启动服务
python start.py
```

后端服务启动后，访问：
- API 文档：http://127.0.0.1:6080/docs
- ReDoc：http://127.0.0.1:6080/redoc

### 2. 启动前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用启动后，访问：http://localhost:3000

### 3. 登录系统

首次使用需要先创建用户：

#### 方法 1：使用 API 文档创建
1. 访问 http://127.0.0.1:6080/docs
2. 找到 `POST /v1/user/user` 接口
3. 点击 "Try it out"
4. 输入用户信息：
   ```json
   {
     "email": "admin@example.com",
     "nickname": "管理员",
     "password": "admin123",
     "status": 1
   }
   ```
5. 点击 "Execute"

#### 方法 2：使用 Python 脚本创建
```python
import requests

url = "http://127.0.0.1:6080/v1/user/user"
data = {
    "email": "admin@example.com",
    "nickname": "管理员",
    "password": "admin123",
    "status": 1
}
response = requests.post(url, json=data)
print(response.json())
```

#### 登录
1. 访问 http://localhost:3000
2. 输入邮箱：admin@example.com
3. 输入密码：admin123
4. 点击登录

## 验证安装

### 后端验证

```bash
# 检查后端服务
curl http://127.0.0.1:6080/docs

# 检查数据库连接
cd backend
python scripts/test_db_connection.py

# 检查数据库表
python scripts/check_db_tables.py

# 验证项目配置
python scripts/verify_setup.py
```

### 前端验证

```bash
# 检查前端服务
curl http://localhost:3000

# 检查 API 代理
curl http://localhost:3000/v1/user/user
```

## 常见问题

### Q1: 后端启动失败

**问题：** `ModuleNotFoundError: No module named 'xxx'`

**解决：**
```bash
pip install -r requirements.txt
```

### Q2: 数据库连接失败

**问题：** `Can't connect to MySQL server`

**解决：**
1. 检查 MySQL 是否启动
2. 检查 `.env` 文件中的数据库配置
3. 确保数据库已创建（默认名称：qyd）

### Q3: 前端启动失败

**问题：** `Cannot find module 'xxx'`

**解决：**
```bash
rm -rf node_modules package-lock.json
npm install
```

### Q4: 前端无法访问后端 API

**问题：** `Network Error` 或 `CORS Error`

**解决：**
1. 检查后端服务是否启动
2. 检查 Vite 代理配置（vite.config.ts）
3. 检查后端 CORS 配置（.env 中的 CORS_ORIGINS）

### Q5: 登录后 Token 过期

**问题：** 登录后立即跳转到登录页

**解决：**
1. 检查浏览器控制台错误
2. 清除浏览器缓存和 localStorage
3. 重新登录

## 开发模式

### 后端开发

```bash
cd backend

# 启动开发服务器（热重载）
APP_DEBUG=1 python start.py

# 查看日志
tail -f logs/api.log

# 运行测试
pytest app/tests/ -v
```

### 前端开发

```bash
cd frontend

# 启动开发服务器（热重载）
npm run dev

# 代码检查
npm run lint

# 类型检查
npm run type-check
```

## 生产部署

### 后端部署

```bash
cd backend

# 设置生产环境变量
export APP_DEBUG=0
export ENABLE_DOCS=0

# 启动服务
python start.py

# 或使用 Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:6080
```

### 前端部署

```bash
cd frontend

# 构建生产版本
npm run build

# 产物在 dist/ 目录
ls -lh dist/

# 使用 Nginx 部署
# 参考 frontend/README.md 中的 Nginx 配置
```

## 下一步

1. 查看 [项目总览](PROJECT_OVERVIEW.md) 了解整体架构
2. 查看 [后端文档](backend/README.md) 了解后端详情
3. 查看 [前端文档](frontend/README.md) 了解前端详情
4. 查看 [开发指南](frontend/DEVELOPMENT_GUIDE.md) 开始开发

## 技术支持

- 后端 API 文档：http://127.0.0.1:6080/docs
- 前端应用：http://localhost:3000
- 项目文档：查看各目录下的 README.md

## 快速命令参考

```bash
# 后端
cd backend && python start.py                    # 启动后端
cd backend && python scripts/verify_setup.py     # 验证配置
cd backend && pytest app/tests/ -v               # 运行测试

# 前端
cd frontend && npm run dev                       # 启动前端
cd frontend && npm run build                     # 构建生产版本
cd frontend && npm run lint                      # 代码检查

# 数据库
cd backend && bash scripts/init_db.sh            # 初始化数据库
cd backend && bash scripts/update_db.sh          # 更新数据库
cd backend && python scripts/check_db_tables.py  # 检查数据库表
```

## 开发效率提示

### 后端
- 使用 `/docs` 测试 API
- 使用 `scripts/verify_setup.py` 验证配置
- 使用日志系统调试问题

### 前端
- 复制 `UserList.tsx` 或 `MailList.tsx` 快速开发新页面
- 所有 API 已封装，直接调用即可
- 使用浏览器开发者工具调试

## 祝你开发愉快！🎉

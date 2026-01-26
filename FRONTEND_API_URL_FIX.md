# 前端 API 地址修复指南

## 问题描述

前端在浏览器中访问后端 API 时，使用了错误的地址（`http://127.0.0.1:6080` 或 `http://localhost:6080`），而不是正确的生产地址（`http://192.168.13.6:6080`），导致连接被拒绝（ERR_CONNECTION_REFUSED）。

## 根本原因

**Vite 在构建时会将环境变量硬编码到 JavaScript 文件中**，而不是在运行时读取。

### 问题流程

1. 前端使用 Vite 构建
2. Vite 读取 `.env.production` 或构建参数中的 `VITE_API_BASE_URL`
3. 将这个值硬编码到打包后的 JS 文件中
4. 运行时无法更改这个值

### 之前的错误配置

**docker-compose.yml（错误）**:
```yaml
frontend:
  build:
    context: ./frontend
  environment:
    - VITE_API_BASE_URL=${VITE_API_BASE_URL:-http://localhost:6080}  # ❌ 运行时环境变量无效
```

**Dockerfile（错误）**:
```dockerfile
# 没有接收构建参数
COPY . .
RUN npx vite build  # ❌ 使用 .env.production 中的默认值
```

## 解决方案

### 1. 修改 Dockerfile 接收构建参数

**frontend/Dockerfile**:
```dockerfile
# 接收构建参数
ARG VITE_API_BASE_URL=http://192.168.13.6:6080
ARG VITE_APP_TITLE=QYD项目管理系统

# 设置环境变量（Vite 会在构建时读取）
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_APP_TITLE=${VITE_APP_TITLE}

# 显示构建配置
RUN echo "Building with API URL: ${VITE_API_BASE_URL}"

# 构建应用
RUN npx vite build
```

### 2. 修改 docker-compose.yml 传递构建参数

**docker-compose.yml**:
```yaml
frontend:
  build:
    context: ./frontend
    args:
      - VITE_API_BASE_URL=${VITE_API_BASE_URL:-http://192.168.13.6:6080}
      - VITE_APP_TITLE=${VITE_APP_TITLE:-QYD项目管理系统}
```

### 3. 确保 .env.high_concurrency 中配置正确

**.env.high_concurrency**:
```bash
VITE_API_BASE_URL=http://192.168.13.6:6080
```

## 执行步骤

在生产服务器上执行：

```bash
cd /opt/zy/qyd_api

# 拉取最新代码
git pull

# 重新构建前端（会自动使用正确的 API 地址）
bash rebuild_frontend.sh
```

## 验证方法

### 1. 检查构建日志

重建时应该看到：
```
Building with API URL: http://192.168.13.6:6080
```

### 2. 浏览器开发者工具

1. 打开浏览器开发者工具（F12）
2. 切换到 Network 标签
3. 刷新页面（Ctrl+Shift+R 强制刷新）
4. 查看 API 请求的地址

**正确的请求**：
```
Request URL: http://192.168.13.6:6080/v1/user/role/tree
```

**错误的请求**：
```
Request URL: http://127.0.0.1:6080/v1/user/role/tree  ❌
Request URL: http://localhost:6080/v1/user/role/tree  ❌
```

### 3. 检查前端源码

在浏览器中查看打包后的 JS 文件，搜索 `192.168.13.6`，应该能找到这个地址。

## 构建参数 vs 运行时环境变量

### 构建参数（Build Args）

- **时机**: Docker 构建镜像时
- **用途**: 传递给 Dockerfile 中的 `ARG` 指令
- **生效**: 构建时硬编码到文件中
- **适用**: Vite、React、Vue 等前端框架

```yaml
build:
  args:
    - VITE_API_BASE_URL=http://192.168.13.6:6080  # ✅ 正确
```

### 运行时环境变量（Environment Variables）

- **时机**: Docker 容器运行时
- **用途**: 传递给容器内的进程
- **生效**: 运行时动态读取
- **适用**: 后端服务（FastAPI、Node.js 等）

```yaml
environment:
  - DB_HOST=192.168.13.6  # ✅ 后端可以运行时读取
  - VITE_API_BASE_URL=...  # ❌ 前端无法运行时读取（已构建）
```

## 为什么前端不能用运行时环境变量？

前端代码在构建时会被编译、压缩、打包成静态文件（HTML、CSS、JS）：

1. **构建时**: Vite 读取环境变量，替换代码中的 `import.meta.env.VITE_API_BASE_URL`
2. **打包后**: 生成的 JS 文件中直接包含 `"http://192.168.13.6:6080"` 字符串
3. **运行时**: Nginx 只是提供静态文件，无法修改 JS 中的字符串

## 其他解决方案（不推荐）

### 方案1: 使用相对路径

```typescript
// 前端代码
const api = axios.create({
  baseURL: '/api'  // 相对路径
})
```

```nginx
# Nginx 配置
location /api/ {
  proxy_pass http://backend-api:6080/;
}
```

**缺点**: 需要修改所有 API 路径，增加 Nginx 配置复杂度

### 方案2: 运行时注入配置

在 Nginx 中使用 `sub_filter` 替换 JS 文件中的字符串：

```nginx
location / {
  sub_filter 'API_BASE_URL_PLACEHOLDER' 'http://192.168.13.6:6080';
  sub_filter_once off;
}
```

**缺点**: 性能差，维护困难，不推荐

## 最佳实践

1. **前端**: 使用构建参数（Build Args）传递配置
2. **后端**: 使用运行时环境变量（Environment Variables）
3. **配置文件**: 使用 `.env` 文件统一管理
4. **文档**: 清楚说明哪些配置是构建时，哪些是运行时

## 相关文件

- `frontend/Dockerfile` - 前端 Dockerfile（接收构建参数）
- `docker-compose.yml` - Docker Compose 配置（传递构建参数）
- `frontend/.env.production` - 前端生产环境配置（默认值）
- `.env.high_concurrency` - 生产环境配置（覆盖默认值）
- `rebuild_frontend.sh` - 重新构建前端脚本

## 相关 Commits

- `65157b9` - fix: 修复前端构建时 API 地址配置，使用构建参数而不是运行时环境变量
- `b360adb` - fix: 修复 Nginx 配置使用 Docker Compose 服务名而不是容器名

## 故障排查

### 问题1: 重建后还是错误的地址

**检查**:
```bash
# 查看构建日志
docker compose build frontend 2>&1 | grep "Building with API URL"
```

**解决**: 确保 `.env.high_concurrency` 中的 `VITE_API_BASE_URL` 正确

### 问题2: 浏览器缓存

**解决**: 
- 强制刷新：Ctrl+Shift+R（Windows/Linux）或 Cmd+Shift+R（Mac）
- 清除缓存：浏览器设置 → 清除浏览器数据 → 缓存的图片和文件

### 问题3: 构建参数没有传递

**检查**:
```bash
# 查看 docker-compose.yml 中的 build.args
grep -A 5 "frontend:" docker-compose.yml
```

**解决**: 确保 `build.args` 正确配置

## 总结

- ✅ 前端使用**构建参数**（在构建时硬编码）
- ✅ 后端使用**运行时环境变量**（在运行时读取）
- ✅ 使用 `.env` 文件统一管理配置
- ✅ 重建前端容器才能更新 API 地址

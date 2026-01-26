# 前端部署指南

本文档详细说明前端应用的部署方式，重点介绍 Docker 多阶段构建方案。

## 📋 目录

- [部署方式对比](#部署方式对比)
- [Docker 部署（推荐）](#docker-部署推荐)
- [传统部署](#传统部署)
- [性能优化](#性能优化)
- [故障排查](#故障排查)

## 🔄 部署方式对比

### 方式一：Docker 多阶段构建（推荐）

**优势**：
- ✅ 镜像体积小（~30MB）
- ✅ 性能优异（Nginx 优化）
- ✅ 安全性高（不暴露源码）
- ✅ 部署简单（一键启动）
- ✅ 环境一致（开发/生产）

**劣势**：
- ❌ 需要 Docker 环境
- ❌ 构建时间稍长

### 方式二：传统部署

**优势**：
- ✅ 不需要 Docker
- ✅ 灵活性高

**劣势**：
- ❌ 需要手动配置 Nginx
- ❌ 环境差异可能导致问题
- ❌ 部署步骤多

## 🐳 Docker 部署（推荐）

### 什么是多阶段构建？

多阶段构建（Multi-stage Build）是 Docker 的一个特性，允许在一个 Dockerfile 中使用多个 `FROM` 指令，每个 `FROM` 指令开始一个新的构建阶段。

**核心思想**：
1. **构建阶段**：使用完整的开发环境（Node.js）编译代码
2. **生产阶段**：只复制编译产物到轻量级镜像（Nginx）

### Dockerfile 详解

```dockerfile
# ============================================
# 第一阶段：构建（Builder Stage）
# ============================================
FROM node:18-alpine as builder

# 设置工作目录
WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖（只安装生产依赖）
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用（生成 dist 目录）
RUN npm run build

# ============================================
# 第二阶段：生产（Production Stage）
# ============================================
FROM nginx:alpine

# 复制自定义 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制构建产物
# 注意：只复制 dist 目录，不复制源码和 node_modules
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
```

### 构建过程详解

#### 第一阶段：构建

```bash
# 1. 使用 Node.js 18 Alpine 镜像
FROM node:18-alpine as builder

# 为什么选择 Alpine？
# - 体积小（~5MB vs ~900MB）
# - 安全性高（最小化攻击面）
# - 启动快

# 2. 安装依赖
RUN npm ci --only=production

# 为什么用 npm ci 而不是 npm install？
# - 更快（跳过某些检查）
# - 更可靠（严格按照 package-lock.json）
# - 适合 CI/CD 环境

# 3. 构建应用
RUN npm run build

# 执行 Vite 构建：
# - 编译 TypeScript → JavaScript
# - 打包所有模块
# - 压缩代码
# - 优化资源
# - 生成 dist/ 目录
```

#### 第二阶段：生产

```bash
# 1. 使用 Nginx Alpine 镜像
FROM nginx:alpine

# 为什么选择 Nginx？
# - 专门优化静态文件服务
# - 性能优异（高并发）
# - 配置灵活
# - 体积小（~25MB）

# 2. 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 关键点：
# - 只复制 dist 目录
# - 不包含 node_modules（~200MB）
# - 不包含源码（安全）
# - 不包含 Node.js（不需要）
```

### 镜像大小对比

| 构建方式 | 镜像大小 | 包含内容 |
|---------|---------|---------|
| **单阶段构建** | ~800MB | Node.js + 源码 + node_modules + dist |
| **多阶段构建** | ~30MB | Nginx + dist |
| **节省** | ~770MB | 96% 体积减少 |

### Nginx 配置

```nginx
server {
    listen 80;
    server_name localhost;
    
    # 静态文件根目录
    root /usr/share/nginx/html;
    index index.html;
    
    # ==========================================
    # 前端路由配置（SPA）
    # ==========================================
    location / {
        # 尝试按顺序查找：
        # 1. 文件本身（如 /logo.png）
        # 2. 目录（如 /assets/）
        # 3. 回退到 index.html（React Router）
        try_files $uri $uri/ /index.html;
    }
    
    # ==========================================
    # API 反向代理
    # ==========================================
    location /v1/ {
        # 代理到后端容器
        proxy_pass http://backend-api:6080;
        
        # 传递原始请求头
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # ==========================================
    # 静态资源缓存优化
    # ==========================================
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        # 缓存 1 年
        expires 1y;
        
        # 添加缓存控制头
        add_header Cache-Control "public, immutable";
        
        # 允许跨域（如果需要）
        # add_header Access-Control-Allow-Origin *;
    }
    
    # ==========================================
    # Gzip 压缩
    # ==========================================
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/rss+xml
        font/truetype
        font/opentype
        application/vnd.ms-fontobject
        image/svg+xml;
}
```

### 部署步骤

#### 1. 构建镜像

```bash
# 进入项目根目录
cd /path/to/qyd_api2

# 构建前端镜像
docker-compose build frontend

# 构建过程：
# [1/2] Building builder stage...
#   - 安装 Node.js 依赖
#   - 执行 npm run build
#   - 生成 dist 目录
# [2/2] Building production stage...
#   - 复制 Nginx 配置
#   - 复制 dist 目录
#   - 配置健康检查
```

#### 2. 启动容器

```bash
# 启动前端容器
docker-compose up -d frontend

# 查看状态
docker-compose ps frontend

# 查看日志
docker-compose logs -f frontend
```

#### 3. 验证部署

```bash
# 访问前端
curl http://localhost

# 检查健康状态
docker inspect qyd-frontend | grep -A 10 Health

# 查看 Nginx 配置
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
```

### 环境变量配置

前端支持通过环境变量配置 API 地址：

```env
# .env.production
VITE_API_BASE_URL=http://localhost:6080
VITE_APP_TITLE=QYD管理系统
```

**注意**：
- 环境变量在**构建时**注入
- 修改环境变量需要**重新构建**镜像
- 生产环境建议使用 Nginx 代理，不依赖环境变量

### 更新部署

```bash
# 1. 修改代码后重新构建
docker-compose build frontend

# 2. 重启容器
docker-compose up -d frontend

# 3. 查看新容器状态
docker-compose ps frontend
```

## 🔧 传统部署

### 手动打包部署

#### 1. 构建生产版本

```bash
cd frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 生成的文件在 dist/ 目录
ls -lh dist/
```

#### 2. 部署到 Nginx

```bash
# 复制文件到 Nginx 目录
sudo cp -r dist/* /var/www/html/

# 或创建软链接
sudo ln -s /path/to/frontend/dist /var/www/html/qyd
```

#### 3. 配置 Nginx

```bash
# 编辑 Nginx 配置
sudo vim /etc/nginx/sites-available/qyd

# 添加配置（参考上面的 Nginx 配置）

# 启用站点
sudo ln -s /etc/nginx/sites-available/qyd /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 使用 PM2 部署（开发环境）

```bash
# 安装 PM2
npm install -g pm2

# 启动开发服务器
pm2 start npm --name "qyd-frontend" -- run dev

# 查看状态
pm2 status

# 查看日志
pm2 logs qyd-frontend
```

## ⚡ 性能优化

### 1. 构建优化

```javascript
// vite.config.ts
export default defineConfig({
  build: {
    // 代码分割
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'antd-vendor': ['antd', '@ant-design/icons'],
        },
      },
    },
    
    // 压缩
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,  // 移除 console
        drop_debugger: true, // 移除 debugger
      },
    },
    
    // 关闭 source map（生产环境）
    sourcemap: false,
  },
})
```

### 2. Nginx 优化

```nginx
# 启用 HTTP/2
listen 443 ssl http2;

# 启用 Brotli 压缩（比 gzip 更好）
brotli on;
brotli_comp_level 6;
brotli_types text/plain text/css application/json application/javascript;

# 增加缓存
location ~* \.(js|css)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# 预加载
location = /index.html {
    add_header Link "</assets/main.js>; rel=preload; as=script";
}
```

### 3. Docker 优化

```dockerfile
# 使用 BuildKit 加速构建
# export DOCKER_BUILDKIT=1

# 利用缓存层
COPY package*.json ./
RUN npm ci --only=production
COPY . .

# 多阶段并行构建
FROM node:18-alpine as deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine as builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build
```

## 🐛 故障排查

### 1. 构建失败

**问题**：`npm run build` 失败

**排查**：

```bash
# 查看构建日志
docker-compose build frontend 2>&1 | tee build.log

# 进入构建阶段调试
docker run -it --rm node:18-alpine sh
cd /app
npm install
npm run build
```

**常见原因**：
- TypeScript 类型错误
- 依赖版本冲突
- 内存不足

### 2. 容器无法启动

**问题**：容器启动后立即退出

**排查**：

```bash
# 查看容器日志
docker-compose logs frontend

# 查看 Nginx 错误日志
docker-compose exec frontend cat /var/log/nginx/error.log

# 测试 Nginx 配置
docker-compose exec frontend nginx -t
```

### 3. 页面无法访问

**问题**：访问 http://localhost 无响应

**排查**：

```bash
# 检查容器状态
docker-compose ps frontend

# 检查端口映射
docker port qyd-frontend

# 检查防火墙
sudo ufw status
sudo ufw allow 80

# 测试容器内部
docker-compose exec frontend wget -O- http://localhost
```

### 4. API 请求失败

**问题**：前端无法访问后端 API

**排查**：

```bash
# 检查 Nginx 代理配置
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf

# 测试后端连接
docker-compose exec frontend wget -O- http://backend-api:6080/docs

# 查看 Nginx 访问日志
docker-compose exec frontend tail -f /var/log/nginx/access.log
```

### 5. 静态资源 404

**问题**：JS/CSS 文件无法加载

**排查**：

```bash
# 检查文件是否存在
docker-compose exec frontend ls -la /usr/share/nginx/html/assets/

# 检查文件权限
docker-compose exec frontend ls -la /usr/share/nginx/html/

# 查看 index.html 中的资源路径
docker-compose exec frontend cat /usr/share/nginx/html/index.html
```

## 📊 监控和维护

### 查看容器状态

```bash
# 查看运行状态
docker-compose ps frontend

# 查看资源使用
docker stats qyd-frontend

# 查看健康状态
docker inspect qyd-frontend | grep -A 10 Health
```

### 查看日志

```bash
# 实时查看日志
docker-compose logs -f frontend

# 查看 Nginx 访问日志
docker-compose exec frontend tail -f /var/log/nginx/access.log

# 查看 Nginx 错误日志
docker-compose exec frontend tail -f /var/log/nginx/error.log
```

### 性能监控

```bash
# 查看响应时间
curl -w "@curl-format.txt" -o /dev/null -s http://localhost

# curl-format.txt 内容：
# time_namelookup:  %{time_namelookup}\n
# time_connect:  %{time_connect}\n
# time_starttransfer:  %{time_starttransfer}\n
# time_total:  %{time_total}\n
```

## 🔒 安全建议

1. ✅ 使用 HTTPS（配置 SSL 证书）
2. ✅ 设置安全响应头
3. ✅ 限制请求大小
4. ✅ 防止目录遍历
5. ✅ 隐藏 Nginx 版本
6. ✅ 配置 CSP（内容安全策略）
7. ✅ 定期更新基础镜像
8. ✅ 扫描镜像漏洞

### Nginx 安全配置

```nginx
# 隐藏版本号
server_tokens off;

# 安全响应头
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;

# CSP
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;

# 限制请求大小
client_max_body_size 10M;

# 防止目录遍历
location ~ /\. {
    deny all;
}
```

## 📚 相关文档

- [Docker 完整部署指南](DOCKER_DEPLOYMENT.md)
- [部署架构说明](DEPLOYMENT_ARCHITECTURE.md)
- [后端部署指南](../../backend/README.md)
- [项目结构说明](../../.kiro/steering/structure.md)

---

**最后更新**: 2026-01-26  
**版本**: v1.2.0

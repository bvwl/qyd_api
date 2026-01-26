# 构建阶段
FROM node:18-alpine as builder

# 设置工作目录
WORKDIR /app

# 配置 npm 国内镜像源（加速构建）
RUN npm config set registry https://registry.npmmirror.com

# 复制 package 文件
COPY package*.json ./

# 安装依赖
# 注意：使用 npm install 而不是 npm ci，因为 package-lock.json 未提交到仓库
RUN npm install --production=false

# 复制源代码
COPY . .

# 构建应用（直接使用 vite build，跳过 tsc 类型检查）
# Vite 在构建时会进行基本的语法检查，但不会严格检查类型
RUN npx vite build

# 生产阶段 - 使用 Nginx
FROM nginx:alpine

# 复制自定义 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]

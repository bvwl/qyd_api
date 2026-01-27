# Docker 代码更新指南

## 问题原因

Docker 容器中的代码是在构建镜像时复制进去的，不会自动更新。当你修改了代码后，需要重新构建镜像才能生效。

## 快速解决方案

### 方式 1: 使用脚本（推荐）

```bash
# 在项目根目录运行
./restart-backend-docker.sh
```

### 方式 2: 手动执行

```bash
# 1. 停止服务
docker compose -f docker-compose.backend.yml stop backend-api

# 2. 重新构建镜像（包含最新代码）
docker compose -f docker-compose.backend.yml build backend-api

# 3. 启动服务
docker compose -f docker-compose.backend.yml up -d backend-api

# 4. 查看日志
docker compose -f docker-compose.backend.yml logs -f backend-api
```

### 方式 3: 一键重启（不重新构建）

```bash
# 仅当代码没有变化，只需要重启时使用
docker compose -f docker-compose.backend.yml restart backend-api
```

## 为什么需要重新构建？

### Dockerfile 构建过程

```dockerfile
# 1. 复制代码到镜像
COPY . .

# 2. 代码被打包到镜像中
# 3. 容器运行时使用镜像中的代码
```

### 代码更新流程

```
本地修改代码 → Git 提交 → 重新构建镜像 → 重启容器 → 代码生效
```

## 验证代码已更新

### 1. 检查容器内的代码

```bash
# 进入容器
docker compose -f docker-compose.backend.yml exec backend-api bash

# 查看代码
cat /app/app/apis/v1/xui/operation.py | grep -A 3 "return XuiOperationResponse"

# 应该看到:
#     return XuiOperationResponse(
#         success=True,
#         message="同步入站配置任务已提交，正在后台执行",
#         data={"server_id": str(server_id), "task": "sync_inbounds"}

# 退出容器
exit
```

### 2. 测试 API

```bash
# 调用同步入站 API
curl -X POST "http://192.168.13.6:6080/v1/xui/operation/sync-inbounds/YOUR_SERVER_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# 正确的响应:
{
  "success": true,
  "message": "同步入站配置任务已提交，正在后台执行",
  "data": {
    "server_id": "...",
    "task": "sync_inbounds"
  }
}

# 错误的响应（旧代码）:
{
  "detail": [
    {
      "type": "missing",
      "loc": ["response", "success"],
      "msg": "Field required"
    }
  ]
}
```

### 3. 查看日志

```bash
# 查看容器日志
docker compose -f docker-compose.backend.yml logs --tail=50 backend-api

# 应该看到:
# INFO 2026-01-27 XX:XX:XX 项目启动...
# INFO 2026-01-27 XX:XX:XX 数据库初始化完成
# 没有 ValidationError 错误
```

## 开发模式 vs 生产模式

### 开发模式（代码自动更新）

如果想要代码自动更新，可以使用卷挂载：

```yaml
# docker-compose.backend.yml
services:
  backend-api:
    volumes:
      - ./backend:/app  # 挂载本地代码
    environment:
      - APP_DEBUG=1     # 开启调试模式
```

**优点**: 代码修改后自动生效（需要重启容器）
**缺点**: 性能较差，不适合生产环境

### 生产模式（当前配置）

代码打包到镜像中，需要重新构建才能更新。

**优点**: 性能好，适合生产环境
**缺点**: 每次代码更新需要重新构建

## 常见问题

### 1. 构建很慢

```bash
# 使用缓存加速构建
docker compose -f docker-compose.backend.yml build --parallel backend-api

# 清理旧镜像释放空间
docker image prune -f
```

### 2. 端口冲突

```bash
# 检查端口占用
docker ps | grep 6080

# 停止占用端口的容器
docker stop <container_id>
```

### 3. 镜像构建失败

```bash
# 清理构建缓存
docker builder prune -f

# 重新构建（不使用缓存）
docker compose -f docker-compose.backend.yml build --no-cache backend-api
```

### 4. 容器无法启动

```bash
# 查看详细日志
docker compose -f docker-compose.backend.yml logs backend-api

# 检查容器状态
docker compose -f docker-compose.backend.yml ps

# 查看容器详细信息
docker inspect <container_id>
```

## 自动化部署脚本

### 完整的更新流程

```bash
#!/bin/bash
# update-and-deploy.sh

echo "=== 更新并部署后端服务 ==="

# 1. 拉取最新代码
git pull origin main

# 2. 停止服务
docker compose -f docker-compose.backend.yml stop backend-api

# 3. 重新构建
docker compose -f docker-compose.backend.yml build backend-api

# 4. 启动服务
docker compose -f docker-compose.backend.yml up -d backend-api

# 5. 查看日志
docker compose -f docker-compose.backend.yml logs --tail=20 -f backend-api
```

## 多容器扩展

如果使用多容器部署，需要更新所有容器：

```bash
# 停止所有后端容器
docker compose -f docker-compose.backend.yml stop backend-api

# 重新构建
docker compose -f docker-compose.backend.yml build backend-api

# 启动多个容器
docker compose -f docker-compose.backend.yml up -d --scale backend-api=3

# 查看所有容器
docker compose -f docker-compose.backend.yml ps
```

## 零停机更新

使用滚动更新避免服务中断：

```bash
# 1. 构建新镜像
docker compose -f docker-compose.backend.yml build backend-api

# 2. 启动新容器（不停止旧容器）
docker compose -f docker-compose.backend.yml up -d --scale backend-api=2 --no-recreate

# 3. 等待新容器就绪
sleep 10

# 4. 停止旧容器
docker compose -f docker-compose.backend.yml stop backend-api

# 5. 清理旧容器
docker compose -f docker-compose.backend.yml rm -f backend-api
```

## 相关文档

- [后端重启指南](./RESTART_BACKEND_GUIDE.md)
- [XUI 后台任务更新](./XUI_BACKGROUND_TASK_UPDATE.md)
- [Docker 部署指南](./DEPLOYMENT_README.md)

## 总结

**记住**: Docker 容器中的代码不会自动更新，每次修改代码后都需要：

1. ✅ 提交代码到 Git
2. ✅ 重新构建镜像
3. ✅ 重启容器
4. ✅ 验证更新生效

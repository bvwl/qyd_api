# 后端服务重启指南

## 问题说明

代码已经更新并提交到 Git，但服务器上运行的还是旧代码，需要重启后端服务来加载新代码。

## 检查当前运行方式

### 方式 1: Docker 部署

```bash
# 检查是否有 Docker 容器在运行
docker ps | grep backend

# 如果有输出，说明是 Docker 部署
```

### 方式 2: 原生部署

```bash
# 检查是否有 Python 进程在运行
ps aux | grep "python.*start.py" | grep -v grep

# 如果有输出，说明是原生部署
```

## 重启方法

### Docker 部署重启

```bash
# 方式 1: 重启容器（推荐）
docker compose -f docker-compose.backend.yml restart backend-api

# 方式 2: 重新构建并启动（如果修改了依赖）
docker compose -f docker-compose.backend.yml up -d --build backend-api

# 方式 3: 停止并重新启动
docker compose -f docker-compose.backend.yml stop backend-api
docker compose -f docker-compose.backend.yml start backend-api

# 查看日志确认启动成功
docker compose -f docker-compose.backend.yml logs -f backend-api
```

### 原生部署重启

```bash
# 1. 找到进程 ID
ps aux | grep "python.*start.py" | grep -v grep

# 2. 停止进程（使用上面找到的 PID）
kill <PID>

# 或者使用 pkill
pkill -f "python.*start.py"

# 3. 确认进程已停止
ps aux | grep "python.*start.py" | grep -v grep

# 4. 重新启动
cd backend
python start.py

# 或者使用 nohup 后台运行
nohup python start.py > ../logs/backend.log 2>&1 &

# 5. 查看日志确认启动成功
tail -f ../logs/app.log
```

## 验证代码已更新

### 1. 检查 Git 提交

```bash
# 查看最近的提交
git log --oneline -1

# 应该看到:
# 5e47f75 fix(xui): 修复同步入站响应格式并支持WORKERS环境变量
```

### 2. 检查代码内容

```bash
# 检查 API 文件
grep -A 3 "return XuiOperationResponse" backend/app/apis/v1/xui/operation.py | tail -4

# 应该看到:
#     return XuiOperationResponse(
#         success=True,
#         message="同步入站配置任务已提交，正在后台执行",
#         data={"server_id": str(server_id), "task": "sync_inbounds"}
```

### 3. 测试 API

```bash
# 调用同步入站 API
curl -X POST "http://192.168.13.6:6080/v1/xui/operation/sync-inbounds/YOUR_SERVER_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# 应该返回:
# {
#   "success": true,
#   "message": "同步入站配置任务已提交，正在后台执行",
#   "data": {
#     "server_id": "...",
#     "task": "sync_inbounds"
#   }
# }
```

## 常见问题

### 1. 端口被占用

```bash
# 检查端口占用
lsof -i :6080

# 或者
netstat -tlnp | grep 6080

# 停止占用端口的进程
kill -9 <PID>
```

### 2. 权限问题

```bash
# 确保有执行权限
chmod +x backend/start.py

# 确保日志目录可写
chmod -R 755 logs/
```

### 3. 依赖问题

```bash
# 重新安装依赖
cd backend
pip install -r requirements.txt
```

### 4. 环境变量问题

```bash
# 检查 .env 文件
cat backend/.env | grep WORKERS

# 应该看到:
# WORKERS=1  # 或其他数字
```

## 启动后检查清单

- [ ] 进程正在运行
- [ ] 日志没有错误
- [ ] API 可以访问 (http://192.168.13.6:6080/docs)
- [ ] 同步入站功能正常
- [ ] 响应格式正确（包含 success, message, data 字段）

## 多 Worker 启动

如果需要启动多个 Worker：

```bash
# 修改 .env 文件
echo "WORKERS=4" >> backend/.env

# 重启服务
# Docker: docker compose restart backend-api
# 原生: 停止并重新启动 Python 进程

# 验证 Worker 数量
ps aux | grep "python.*start.py" | wc -l
# 应该看到 4 个进程（如果设置 WORKERS=4）
```

## 相关文档

- [XUI 后台任务更新](./XUI_BACKGROUND_TASK_UPDATE.md)
- [部署指南](./DEPLOYMENT_README.md)
- [Docker 部署](./docker-compose.backend.yml)

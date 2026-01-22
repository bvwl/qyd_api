# 端口占用问题解决方案

## 错误信息

```
ERROR: [Errno 48] error while attempting to bind on address ('0.0.0.0', 6080): address already in use
```

## 问题原因

端口 6080 已经被另一个进程占用（通常是之前启动的后端服务实例还在运行）。

## 解决方案

### 方法1: 使用重启脚本（推荐）

我们创建了一个自动重启脚本，它会：
1. 检查端口是否被占用
2. 如果被占用，自动停止旧进程
3. 启动新的后端服务

```bash
cd backend
./scripts/restart_server.sh
```

### 方法2: 手动查找并停止进程

#### 步骤1: 查找占用端口的进程

```bash
# macOS/Linux
lsof -ti:6080

# 或者使用
ps aux | grep "python start.py" | grep -v grep
```

#### 步骤2: 停止进程

```bash
# 使用进程ID停止
kill -9 <PID>

# 或者停止所有相关进程
pkill -9 -f "python start.py"
```

#### 步骤3: 启动新服务

```bash
cd backend
python start.py
```

### 方法3: 使用不同的端口

如果不想停止旧进程，可以修改端口：

```bash
# 编辑 backend/.env 文件
APP_PORT=6081  # 改为其他端口

# 然后启动服务
python start.py
```

## 常见场景

### 场景1: 修改代码后需要重启

```bash
# 快速重启
cd backend
./scripts/restart_server.sh
```

### 场景2: 多次启动导致端口冲突

```bash
# 停止所有后端进程
pkill -9 -f "python start.py"

# 等待1秒
sleep 1

# 重新启动
python start.py
```

### 场景3: 开发时使用热重载

在 `backend/.env` 中设置：

```env
APP_DEBUG=1  # 启用热重载
```

这样修改代码后会自动重启，无需手动重启。

## 预防措施

### 1. 使用进程管理工具

**使用 supervisor**:

```ini
[program:qyd_api]
command=python start.py
directory=/path/to/backend
autostart=true
autorestart=true
```

**使用 systemd**:

```ini
[Unit]
Description=QYD API Service

[Service]
Type=simple
WorkingDirectory=/path/to/backend
ExecStart=/usr/bin/python start.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. 使用 Docker

```bash
cd backend
docker-compose up -d
```

Docker 会自动管理端口和进程。

### 3. 开发时使用热重载

在 `.env` 中设置 `APP_DEBUG=1`，代码修改后自动重启。

## 检查服务状态

### 检查端口是否被占用

```bash
lsof -ti:6080
# 如果有输出，说明端口被占用
```

### 检查服务是否正常运行

```bash
curl http://127.0.0.1:6080/docs
# 如果返回HTML，说明服务正常
```

### 查看服务日志

```bash
# 如果后台运行
tail -f backend/logs/app.log

# 如果前台运行
# 直接查看终端输出
```

## 重启脚本说明

**文件**: `backend/scripts/restart_server.sh`

**功能**:
1. ✅ 自动检查端口占用
2. ✅ 自动停止旧进程
3. ✅ 启动新服务
4. ✅ 验证服务是否启动成功

**使用方法**:

```bash
cd backend
./scripts/restart_server.sh
```

**输出示例**:

```
正在检查端口 6080...
发现进程 31562 正在使用端口 6080
正在停止进程...
✅ 进程已停止

正在启动后端服务...
✅ 后端服务启动成功！
📝 API文档: http://127.0.0.1:6080/docs
```

## 故障排查

### 问题1: kill 命令无效

```bash
# 使用强制停止
kill -9 <PID>

# 或者
sudo kill -9 <PID>
```

### 问题2: 找不到进程

```bash
# 使用更详细的查找
ps aux | grep python | grep start.py

# 或者查看所有监听6080端口的进程
lsof -i:6080
```

### 问题3: 权限不足

```bash
# 使用 sudo
sudo lsof -ti:6080
sudo kill -9 <PID>
```

### 问题4: 端口仍然被占用

```bash
# 等待几秒后再试
sleep 3
lsof -ti:6080

# 或者重启系统（最后手段）
```

## 最佳实践

1. **开发环境**: 使用热重载（`APP_DEBUG=1`）
2. **生产环境**: 使用进程管理工具（supervisor/systemd）
3. **Docker环境**: 使用 docker-compose
4. **修改代码后**: 使用重启脚本 `./scripts/restart_server.sh`
5. **遇到端口冲突**: 先停止旧进程，再启动新服务

## 相关文件

- ✅ `backend/scripts/restart_server.sh` - 重启脚本
- ✅ `backend/.env` - 配置文件（包含端口设置）
- ✅ `backend/start.py` - 启动脚本
- ✅ `docs/fixes/PORT_ALREADY_IN_USE_FIX.md` - 本文档

## 总结

✅ 端口占用是常见问题，通常是旧进程还在运行
✅ 使用 `lsof -ti:6080` 查找占用端口的进程
✅ 使用 `kill -9 <PID>` 停止进程
✅ 使用重启脚本 `./scripts/restart_server.sh` 自动处理
✅ 开发时启用热重载避免频繁手动重启

现在你可以使用重启脚本轻松解决端口占用问题了！

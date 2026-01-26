# 更新部署指南

本次更新包含代理类型功能和后台任务优化，以下是部署步骤。

## 📋 更新内容

### 1. 代理类型功能
- ✅ 根据端口自动判断代理类型（HTTP/SOCKS5）
- ✅ 支持按代理类型筛选账号
- ✅ 前端显示彩色标签区分类型

### 2. 后台任务优化
- ✅ 添加账号到所有入站改为后台任务
- ✅ 从所有入站删除账号改为后台任务
- ✅ 不再阻塞用户界面，立即返回响应

### 3. 文档完善
- ✅ 新增多个指南文档
- ✅ 优化项目结构说明

---

## 🚀 部署步骤

### 方式一：Docker 部署（推荐）

```bash
# 1. 进入项目目录
cd /opt/zy/qyd_api

# 2. 拉取最新代码
git pull origin main

# 3. 重新构建并启动
docker compose down
docker compose build
docker compose up -d

# 4. 查看日志
docker compose logs -f
```

### 方式二：本地部署

```bash
# 1. 进入项目目录
cd /opt/zy/qyd_api

# 2. 拉取最新代码
git pull origin main

# 3. 更新后端
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 4. 更新前端
cd ../frontend
npm install
npm run build

# 5. 重启服务
sudo systemctl restart qyd-backend qyd-queue-worker
sudo systemctl restart nginx
```

### 方式三：快速更新脚本

```bash
# 使用项目提供的更新脚本
bash update-and-restart.sh
```

---

## ✅ 验证部署

### 1. 检查服务状态

**Docker 部署**:
```bash
docker compose ps
```

**本地部署**:
```bash
sudo systemctl status qyd-backend qyd-queue-worker
```

### 2. 测试新功能

#### 代理类型功能
1. 访问 "服务器管理" → "服务器账号"
2. 查看是否显示 "代理类型" 列
3. 测试代理类型筛选功能

#### 后台任务功能
1. 访问 "XUI管理" → "账号管理"
2. 点击 "添加到所有入站" 按钮
3. 应该立即收到提示："已提交后台任务..."
4. 等待3秒后自动刷新，查看状态变化

### 3. 查看日志

**Docker 部署**:
```bash
# 查看后端日志
docker compose logs -f backend-api

# 查看队列 Worker 日志
docker compose logs -f queue-worker
```

**本地部署**:
```bash
# 查看应用日志
tail -f backend/logs/app.log

# 查看 Systemd 日志
sudo journalctl -u qyd-backend -f
```

---

## 🔍 常见问题

### 1. 代理类型显示为空

**原因**: 账号未关联到任何 XUI 入站

**解决**: 
- 先添加账号到入站
- 刷新页面查看

### 2. 后台任务没有执行

**检查**:
```bash
# 查看日志中是否有任务执行记录
tail -f backend/logs/app.log | grep "后台任务"
```

**可能原因**:
- 服务未正确重启
- 日志级别设置过高

### 3. 前端显示异常

**解决**:
```bash
# 清除浏览器缓存
# 或强制刷新（Ctrl + F5）

# 重新构建前端
cd frontend
npm run build
```

---

## 📊 性能提升

### 之前
- 添加账号到所有入站：30-60秒（阻塞）
- 用户需要等待操作完成

### 现在
- 添加账号到所有入站：< 100ms（立即返回）
- 后台异步执行，不阻塞界面
- 用户可以继续其他操作

---

## 📝 注意事项

1. **后台任务执行时间**
   - 取决于入站数量和网络状况
   - 通常在几秒到几十秒之间
   - 可通过日志查看执行进度

2. **账号状态更新**
   - 任务完成后，`is_all_inbound_added` 字段会自动更新
   - 前端会在3秒后自动刷新一次
   - 也可以手动刷新页面查看最新状态

3. **错误处理**
   - 如果任务失败，会在日志中记录详细错误
   - 账号状态不会更新
   - 可以重新执行操作

---

## 🔗 相关文档

- [STARTUP_GUIDE.md](STARTUP_GUIDE.md) - 启动指南
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 快速参考
- [NAVIGATION_GUIDE.md](NAVIGATION_GUIDE.md) - 导航指南
- [README.md](README.md) - 项目说明

---

**更新日期**: 2026-01-26  
**版本**: v1.3.0  
**提交**: f114b24

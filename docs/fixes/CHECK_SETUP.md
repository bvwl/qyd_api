# 前端启动检查清单

## 快速诊断

### 1. 访问测试页面

在浏览器访问：`http://localhost:3000`

**应该看到什么：**
- 如果看到登录页面（紫色渐变背景） ✅ 一切正常
- 如果看到空白页面 ❌ 需要排查

### 2. 打开浏览器控制台

按 `F12` 或 `Ctrl+Shift+I`（Mac: `Cmd+Option+I`）

查看 **Console** 标签：
- 如果没有红色错误 ✅ 正常
- 如果有错误 ❌ 记录错误信息

### 3. 检查当前 URL

查看浏览器地址栏：
- `http://localhost:3000` → 应该自动跳转到 `/login`
- `http://localhost:3000/login` → 应该看到登录页面

### 4. 手动测试路由

依次访问以下 URL：

1. `http://localhost:3000/login` - 应该看到登录页面
2. `http://localhost:3000/` - 应该自动跳转到 `/login`

## 如果看不到页面

### 方法 1：使用测试页面

临时修改 `src/App.tsx`：

```tsx
import Test from './Test'

function App() {
  return <Test />
}

export default App
```

保存后，浏览器应该自动刷新，如果能看到"✅ React 正常工作"，说明基础环境正常。

然后恢复 `src/App.tsx` 的原始内容。

### 方法 2：清除缓存

```bash
# 停止开发服务器（Ctrl+C）
# 然后执行：

rm -rf node_modules/.vite
npm run dev
```

### 方法 3：重新安装依赖

```bash
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## 登录页面说明

### 登录页面应该是什么样子

```
┌─────────────────────────────────────┐
│                                     │
│     (紫色渐变背景)                   │
│                                     │
│    ┌─────────────────────┐         │
│    │ QYD 项目管理系统     │         │
│    ├─────────────────────┤         │
│    │                     │         │
│    │  📧 邮箱            │         │
│    │  [输入框]           │         │
│    │                     │         │
│    │  🔒 密码            │         │
│    │  [输入框]           │         │
│    │                     │         │
│    │  [  登录按钮  ]     │         │
│    │                     │         │
│    └─────────────────────┘         │
│                                     │
└─────────────────────────────────────┘
```

### 登录页面特征

- **背景**：紫色到粉色的渐变
- **卡片**：白色，居中，带阴影
- **标题**：QYD 项目管理系统
- **输入框**：两个（邮箱和密码）
- **按钮**：蓝色，全宽

## 测试登录功能

### 前提条件

1. 后端服务已启动（`http://127.0.0.1:6080`）
2. 数据库中已有用户

### 创建测试用户

使用后端 API 创建用户：

```bash
curl -X POST "http://127.0.0.1:6080/v1/user/user" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "nickname": "管理员",
    "password": "admin123",
    "status": 1
  }'
```

### 测试登录

1. 访问 `http://localhost:3000/login`
2. 输入邮箱：`admin@example.com`
3. 输入密码：`admin123`
4. 点击登录

**预期结果：**
- 显示"登录成功"提示
- 自动跳转到用户列表页面
- 看到侧边栏和顶部导航栏

## 常见问题

### Q1: 页面完全空白

**可能原因：**
- JavaScript 加载失败
- React 渲染错误
- CSS 未加载

**解决方法：**
1. 打开浏览器控制台查看错误
2. 检查 Network 标签，确认所有资源都加载成功
3. 尝试清除浏览器缓存（Ctrl+Shift+Delete）

### Q2: 看到 "Cannot GET /"

**可能原因：**
- Vite 开发服务器未启动
- 端口错误

**解决方法：**
1. 确认终端显示 "ready in xxx ms"
2. 使用终端显示的实际端口
3. 重新启动开发服务器

### Q3: 登录页面样式错乱

**可能原因：**
- antd 样式未加载
- Less 编译失败

**解决方法：**
1. 确认 `antd` 版本为 5.x
2. 确认 `less` 已安装
3. 重新安装依赖

### Q4: 点击登录无反应

**可能原因：**
- 后端服务未启动
- API 地址配置错误
- CORS 问题

**解决方法：**
1. 确认后端服务已启动（访问 `http://127.0.0.1:6080/docs`）
2. 检查 `.env.development` 中的 `VITE_API_BASE_URL`
3. 查看浏览器控制台的 Network 标签

## 完整的启动流程

```bash
# 1. 启动后端（在 backend 目录）
cd backend
python start.py

# 2. 启动前端（在 frontend 目录）
cd frontend
npm install  # 首次启动或更新后
npm run dev

# 3. 访问前端
# 打开浏览器访问 http://localhost:3000
# 应该自动跳转到 /login

# 4. 登录
# 使用创建的测试用户登录
```

## 验证清单

- [ ] 后端服务已启动（http://127.0.0.1:6080/docs 可访问）
- [ ] 前端服务已启动（终端显示 "ready in xxx ms"）
- [ ] 浏览器访问 http://localhost:3000
- [ ] 自动跳转到 /login
- [ ] 看到登录页面（紫色渐变背景）
- [ ] 可以输入邮箱和密码
- [ ] 点击登录按钮有反应
- [ ] 登录成功后跳转到用户列表

## 需要帮助？

如果以上方法都无法解决问题，请提供：

1. **浏览器控制台截图**（F12 -> Console）
2. **Network 标签截图**（F12 -> Network，刷新页面）
3. **终端输出**（npm run dev 的完整输出）
4. **浏览器和版本**（如：Chrome 120）
5. **操作系统**（如：Windows 11）

查看详细排查指南：[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

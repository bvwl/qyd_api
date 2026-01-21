# 🚀 从这里开始

## 第一次启动？

### 1. 运行诊断工具

**Mac/Linux:**
```bash
chmod +x diagnose.sh
./diagnose.sh
```

**Windows:**
```bash
diagnose.bat
```

### 2. 安装依赖

```bash
npm install
```

### 3. 启动开发服务器

```bash
npm run dev
```

### 4. 访问应用

打开浏览器访问：`http://localhost:3000`

应该自动跳转到登录页面。

## 看不到页面？

### 快速检查

1. **打开浏览器控制台**（F12）
2. **查看 Console 标签**，是否有错误？
3. **查看 Network 标签**，刷新页面，是否所有资源都加载成功？

### 使用测试页面

临时修改 `src/App.tsx`：

```tsx
import Test from './Test'

function App() {
  return <Test />
}

export default App
```

如果能看到测试页面，说明基础环境正常。

然后恢复原始内容继续排查。

## 详细文档

- [CHECK_SETUP.md](./CHECK_SETUP.md) - 启动检查清单
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 详细的问题排查指南
- [README.md](./README.md) - 完整的项目文档

## 登录页面预览

访问 `http://localhost:3000/login` 应该看到：

```
┌─────────────────────────────────────┐
│                                     │
│     (紫色渐变背景)                   │
│                                     │
│    ┌─────────────────────┐         │
│    │ QYD 项目管理系统     │         │
│    ├─────────────────────┤         │
│    │  📧 邮箱            │         │
│    │  [输入框]           │         │
│    │  🔒 密码            │         │
│    │  [输入框]           │         │
│    │  [  登录按钮  ]     │         │
│    └─────────────────────┘         │
└─────────────────────────────────────┘
```

## 测试登录

### 创建测试用户

使用后端 API：

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

### 登录

- 邮箱：`admin@example.com`
- 密码：`admin123`

## 常见问题

### Q: 页面空白

**A:** 
1. 打开浏览器控制台查看错误
2. 运行诊断工具
3. 查看 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

### Q: 登录失败

**A:**
1. 确认后端服务已启动
2. 确认用户已创建
3. 检查邮箱和密码是否正确

### Q: 样式错乱

**A:**
1. 清除浏览器缓存
2. 重新启动开发服务器
3. 检查 antd 版本是否为 5.x

## 需要帮助？

查看完整的排查指南：[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

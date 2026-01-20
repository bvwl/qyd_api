# 前端问题排查指南

## 问题：启动后看不到页面内容

### 1. 检查浏览器控制台

打开浏览器（Chrome/Firefox），按 F12 打开开发者工具，查看：

#### Console 标签
查看是否有 JavaScript 错误，常见错误：
- `Cannot find module` - 模块未找到
- `Unexpected token` - 语法错误
- `Failed to fetch` - API 请求失败

#### Network 标签
查看是否有资源加载失败：
- 红色的请求表示失败
- 检查 `main.tsx`、`index.css` 等是否加载成功

### 2. 检查页面是否正确跳转

访问 `http://localhost:3000` 时，应该：
1. 如果没有登录（没有 token），自动跳转到 `/login`
2. 如果已登录（有 token），跳转到 `/user/list`

在浏览器地址栏查看当前 URL：
- 如果是 `/login` - 应该看到登录页面
- 如果是 `/` - 应该自动跳转到 `/login` 或 `/user/list`

### 3. 手动访问登录页

直接在浏览器访问：`http://localhost:3000/login`

应该看到：
- 一个紫色渐变背景
- 中间有一个白色卡片
- 标题：QYD 项目管理系统
- 两个输入框：邮箱和密码
- 一个蓝色的登录按钮

### 4. 检查是否安装了所有依赖

```bash
cd frontend
npm install
```

确保安装了以下关键依赖：
- react
- react-dom
- react-router-dom
- antd
- axios
- zustand

### 5. 清除缓存重新启动

```bash
# 停止开发服务器（Ctrl+C）

# 清除缓存
rm -rf node_modules/.vite

# 重新启动
npm run dev
```

### 6. 检查端口是否被占用

如果 3000 端口被占用，Vite 会自动使用其他端口（如 3001）。

查看终端输出：
```
➜  Local:   http://localhost:3000/
```

使用终端显示的实际端口访问。

### 7. 检查 TypeScript 编译错误

```bash
cd frontend
npm run build
```

如果有 TypeScript 错误，会在这里显示。

### 8. 常见问题解决

#### 问题：页面空白，控制台无错误

**原因：** 可能是 CSS 没有加载

**解决：**
1. 检查 `src/index.css` 是否存在
2. 检查 `src/main.tsx` 是否导入了 `./index.css`
3. 清除浏览器缓存（Ctrl+Shift+Delete）

#### 问题：Cannot find module '@/xxx'

**原因：** 路径别名配置问题

**解决：**
1. 检查 `vite.config.ts` 中的 `resolve.alias` 配置
2. 检查 `tsconfig.json` 中的 `paths` 配置
3. 重启开发服务器

#### 问题：antd 样式不生效

**原因：** antd 样式未导入

**解决：**
antd 5.x 使用 CSS-in-JS，不需要手动导入样式。如果样式不生效：
1. 检查 `antd` 版本是否为 5.x
2. 检查 `ConfigProvider` 是否正确包裹
3. 清除缓存重新启动

#### 问题：路由不工作

**原因：** React Router 配置问题

**解决：**
1. 检查 `src/router/index.tsx` 是否正确导出
2. 检查 `src/App.tsx` 是否正确使用 `RouterProvider`
3. 检查浏览器地址栏 URL 是否正确

### 9. 完整的启动流程

```bash
# 1. 确保在 frontend 目录
cd frontend

# 2. 安装依赖（首次或更新后）
npm install

# 3. 启动开发服务器
npm run dev

# 4. 在浏览器访问
# 打开 http://localhost:3000
# 或终端显示的实际地址

# 5. 应该自动跳转到登录页
# URL: http://localhost:3000/login
```

### 10. 验证步骤

#### 步骤 1：访问首页
访问：`http://localhost:3000`

**预期结果：** 自动跳转到 `/login`

#### 步骤 2：查看登录页
访问：`http://localhost:3000/login`

**预期结果：** 看到登录表单

#### 步骤 3：打开控制台
按 F12，查看 Console 标签

**预期结果：** 无错误信息

#### 步骤 4：查看 Network
在 Network 标签中，刷新页面

**预期结果：** 
- `index.html` - 200 OK
- `main.tsx` - 200 OK
- `index.css` - 200 OK
- 其他资源 - 200 OK

### 11. 如果还是看不到页面

请提供以下信息：

1. **浏览器控制台截图**（F12 -> Console 标签）
2. **Network 标签截图**（F12 -> Network 标签，刷新页面）
3. **终端输出**（npm run dev 的完整输出）
4. **浏览器地址栏 URL**
5. **Node.js 版本**（`node -v`）
6. **npm 版本**（`npm -v`）

### 12. 快速测试命令

```bash
# 测试 1：检查文件是否存在
ls -la src/main.tsx src/App.tsx src/index.css

# 测试 2：检查依赖是否安装
npm list react react-dom react-router-dom antd

# 测试 3：检查 TypeScript 配置
cat tsconfig.json | grep baseUrl

# 测试 4：检查 Vite 配置
cat vite.config.ts | grep alias

# 测试 5：清除所有缓存
rm -rf node_modules/.vite dist
npm run dev
```

### 13. 临时解决方案：创建简单测试页面

如果还是有问题，可以先创建一个简单的测试页面：

```tsx
// src/Test.tsx
export default function Test() {
  return (
    <div style={{ padding: 50 }}>
      <h1>测试页面</h1>
      <p>如果你能看到这个页面，说明 React 正常工作</p>
    </div>
  )
}
```

然后修改 `src/App.tsx`：

```tsx
import Test from './Test'

function App() {
  return <Test />
}

export default App
```

如果能看到测试页面，说明基础环境正常，问题在于路由或其他配置。

## 联系支持

如果以上方法都无法解决问题，请提供：
1. 完整的错误信息
2. 浏览器控制台截图
3. 终端输出
4. 操作系统和浏览器版本

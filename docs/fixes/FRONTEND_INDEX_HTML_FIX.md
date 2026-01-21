# 前端启动问题修复 - index.html 丢失

## 问题时间
2026-01-21

## 问题描述
前端项目突然无法启动，浏览器显示"找不到 localhost 的网页"。

## 问题现象
- Vite开发服务器正常启动（显示 `VITE v6.4.1 ready in 99 ms`）
- 端口3000正在监听
- 浏览器访问 http://localhost:3000 显示404错误
- curl测试返回 `HTTP/1.1 404 Not Found`

## 问题原因
**根本原因**: `frontend/index.html` 文件丢失

Vite项目需要根目录下的 `index.html` 作为入口文件。如果该文件不存在，Vite服务器会启动但无法提供任何页面内容。

## 诊断过程

### 1. 检查进程
```bash
ps aux | grep vite
# 发现Vite进程正在运行
```

### 2. 检查端口
```bash
lsof -i :3000
# 端口3000正在监听
```

### 3. 测试访问
```bash
curl -v http://localhost:3000
# 返回 HTTP/1.1 404 Not Found
```

### 4. 检查文件
```bash
ls frontend/index.html
# 文件不存在！
```

## 解决方案

### 创建 index.html 文件

在 `frontend/` 目录下创建 `index.html`:

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>QYD 项目管理系统</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

### 关键要素

1. **DOCTYPE声明**: `<!doctype html>`
2. **字符编码**: `<meta charset="UTF-8" />`
3. **视口设置**: `<meta name="viewport" content="width=device-width, initial-scale=1.0" />`
4. **根元素**: `<div id="root"></div>` - React挂载点
5. **入口脚本**: `<script type="module" src="/src/main.tsx"></script>` - Vite入口

## 验证

### 访问测试
```bash
curl -s http://localhost:3000 | head -10
```

预期结果：
```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <script type="module">import { injectIntoGlobalHook } from "/@react-refresh";
    ...
```

### 浏览器测试
1. 打开浏览器
2. 访问 http://localhost:3000
3. 应该能看到登录页面

## 为什么会丢失？

可能的原因：
1. **误删除**: 在清理文件时不小心删除
2. **Git操作**: 可能在某次git操作中被移除
3. **文件移动**: 在整理文档时误操作

## 预防措施

### 1. 添加到 .gitignore 排除列表
确保 `index.html` **不在** `.gitignore` 中：

```bash
# 检查
cat frontend/.gitignore | grep index.html
# 应该没有输出
```

### 2. 版本控制
确保 `index.html` 已提交到Git：

```bash
git add frontend/index.html
git commit -m "fix: 恢复丢失的 index.html 入口文件"
```

### 3. 项目模板
保留一份项目模板或文档，记录必需文件列表。

## Vite 项目必需文件

以下文件是Vite + React + TypeScript项目的核心文件，不能删除：

### 根目录
- ✅ `index.html` - **入口HTML文件**
- ✅ `package.json` - 依赖配置
- ✅ `tsconfig.json` - TypeScript配置
- ✅ `vite.config.ts` - Vite配置

### src 目录
- ✅ `src/main.tsx` - 应用入口
- ✅ `src/App.tsx` - 根组件
- ✅ `src/index.css` - 全局样式

### public 目录
- `public/vite.svg` - 图标（可选）

## 相关文件

- `frontend/index.html` - 入口文件（已恢复）
- `frontend/vite.config.ts` - Vite配置
- `frontend/src/main.tsx` - React入口
- `frontend/package.json` - 项目配置

## 总结

✅ 问题已解决：创建了丢失的 `index.html` 文件
✅ 前端服务正常运行
✅ 页面可以正常访问
✅ 已添加预防措施

**教训**: 在清理或移动文件时，要特别注意项目的核心入口文件，避免误删。

@echo off
chcp 65001 >nul
echo 🔍 QYD 前端诊断工具
echo ====================
echo.

echo 📦 Node.js 版本:
node -v
echo.

echo 📦 npm 版本:
npm -v
echo.

echo 📁 检查关键文件:
if exist "src\main.tsx" (echo   ✅ src\main.tsx) else (echo   ❌ src\main.tsx)
if exist "src\App.tsx" (echo   ✅ src\App.tsx) else (echo   ❌ src\App.tsx)
if exist "src\index.css" (echo   ✅ src\index.css) else (echo   ❌ src\index.css)
if exist "src\router\index.tsx" (echo   ✅ src\router\index.tsx) else (echo   ❌ src\router\index.tsx)
if exist "src\views\Login\index.tsx" (echo   ✅ src\views\Login\index.tsx) else (echo   ❌ src\views\Login\index.tsx)
echo.

echo 📦 检查 node_modules:
if exist "node_modules" (echo   ✅ node_modules 目录存在) else (echo   ❌ node_modules 目录不存在，请运行: npm install)
echo.

echo ⚙️  检查配置文件:
if exist "tsconfig.json" (echo   ✅ tsconfig.json) else (echo   ❌ tsconfig.json)
if exist "vite.config.ts" (echo   ✅ vite.config.ts) else (echo   ❌ vite.config.ts)
if exist "package.json" (echo   ✅ package.json) else (echo   ❌ package.json)
echo.

echo ====================
echo 诊断完成！
echo.
echo 💡 下一步:
echo   1. 如果所有检查都通过，运行: npm run dev
echo   2. 访问: http://localhost:3000
echo   3. 应该自动跳转到登录页面
echo.
echo 📚 查看详细文档:
echo   - CHECK_SETUP.md - 启动检查清单
echo   - TROUBLESHOOTING.md - 问题排查指南
echo.
pause

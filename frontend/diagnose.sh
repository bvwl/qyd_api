#!/bin/bash

echo "🔍 QYD 前端诊断工具"
echo "===================="
echo ""

# 检查 Node.js 版本
echo "📦 Node.js 版本:"
node -v
echo ""

# 检查 npm 版本
echo "📦 npm 版本:"
npm -v
echo ""

# 检查关键文件是否存在
echo "📁 检查关键文件:"
files=(
  "src/main.tsx"
  "src/App.tsx"
  "src/index.css"
  "src/router/index.tsx"
  "src/views/Login/index.tsx"
  "src/components/Layout/index.tsx"
  "src/store/useUserStore.ts"
  "src/api/index.ts"
  "src/types/index.ts"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "  ✅ $file"
  else
    echo "  ❌ $file (缺失)"
  fi
done
echo ""

# 检查依赖是否安装
echo "📦 检查关键依赖:"
deps=(
  "react"
  "react-dom"
  "react-router-dom"
  "antd"
  "axios"
  "zustand"
)

for dep in "${deps[@]}"; do
  if npm list "$dep" > /dev/null 2>&1; then
    version=$(npm list "$dep" --depth=0 2>/dev/null | grep "$dep@" | sed 's/.*@//')
    echo "  ✅ $dep@$version"
  else
    echo "  ❌ $dep (未安装)"
  fi
done
echo ""

# 检查 node_modules 是否存在
if [ -d "node_modules" ]; then
  echo "✅ node_modules 目录存在"
else
  echo "❌ node_modules 目录不存在，请运行: npm install"
fi
echo ""

# 检查 TypeScript 配置
echo "⚙️  TypeScript 配置:"
if [ -f "tsconfig.json" ]; then
  echo "  ✅ tsconfig.json 存在"
else
  echo "  ❌ tsconfig.json 缺失"
fi
echo ""

# 检查 Vite 配置
echo "⚙️  Vite 配置:"
if [ -f "vite.config.ts" ]; then
  echo "  ✅ vite.config.ts 存在"
else
  echo "  ❌ vite.config.ts 缺失"
fi
echo ""

# 检查后端服务
echo "🔌 检查后端服务:"
if curl -s http://127.0.0.1:6080/docs > /dev/null 2>&1; then
  echo "  ✅ 后端服务正常 (http://127.0.0.1:6080)"
else
  echo "  ❌ 后端服务未启动或无法访问"
  echo "     请先启动后端: cd backend && python start.py"
fi
echo ""

echo "===================="
echo "诊断完成！"
echo ""
echo "💡 下一步:"
echo "  1. 如果所有检查都通过，运行: npm run dev"
echo "  2. 访问: http://localhost:3000"
echo "  3. 应该自动跳转到登录页面"
echo ""
echo "📚 查看详细文档:"
echo "  - CHECK_SETUP.md - 启动检查清单"
echo "  - TROUBLESHOOTING.md - 问题排查指南"
echo ""

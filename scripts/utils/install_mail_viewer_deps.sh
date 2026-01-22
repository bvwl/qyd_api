#!/bin/bash

echo "正在安装邮件查看器所需的依赖..."

cd frontend

echo "安装 dompurify 和相关类型定义..."
npm install dompurify@^3.0.8 isomorphic-dompurify@^2.9.0
npm install --save-dev @types/dompurify@^3.0.5

echo "依赖安装完成！"
echo ""
echo "现在可以访问邮件查看器了："
echo "  URL: http://localhost:3000/mail/viewer"
echo ""
echo "如果前端正在运行，请重启前端服务："
echo "  cd frontend"
echo "  npm run dev"

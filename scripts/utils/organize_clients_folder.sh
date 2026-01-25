#!/bin/bash

echo "整理 backend/app/clients 文件夹..."

# 创建目标文件夹
mkdir -p docs/development/clients
mkdir -p backend/examples

# 移动文档文件到 docs
echo "移动文档文件..."
mv backend/app/clients/XUI_CLIENT_README.md docs/development/clients/ 2>/dev/null
mv backend/app/clients/XUI_OPTIMIZATION_SUMMARY.md docs/development/clients/ 2>/dev/null

# 移动示例文件到 examples
echo "移动示例文件..."
mv backend/app/clients/xui_example.py backend/examples/ 2>/dev/null

echo "整理完成！"
echo ""
echo "clients 文件夹现在只包含实际的客户端代码："
ls -la backend/app/clients/

echo ""
echo "文档已移动到: docs/development/clients/"
ls -la docs/development/clients/

echo ""
echo "示例已移动到: backend/examples/"
ls -la backend/examples/

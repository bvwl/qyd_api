#!/bin/bash

echo "整理 backend 目录下的文档文件..."

# 创建目标文件夹
mkdir -p docs/development/xui-api
mkdir -p docs/development/testing
mkdir -p docs/development/logging

# 移动 XUI API 文档
echo "移动 XUI API 文档..."
mv backend/app/apis/v1/xui/XUI_INTEGRATION_GUIDE.md docs/development/xui-api/ 2>/dev/null
mv backend/app/apis/v1/xui/XUI_API_SUMMARY.md docs/development/xui-api/ 2>/dev/null
mv backend/app/apis/v1/xui/README.md docs/development/xui-api/XUI_API_README.md 2>/dev/null
mv backend/app/apis/v1/xui/SYNC_INBOUNDS_GUIDE.md docs/development/xui-api/ 2>/dev/null
mv backend/app/apis/v1/xui/DEFAULT_CREDENTIALS.md docs/development/xui-api/ 2>/dev/null
mv backend/app/apis/v1/xui/QUICK_START.md docs/development/xui-api/XUI_API_QUICK_START.md 2>/dev/null

# 移动测试文档
echo "移动测试文档..."
mv backend/app/tests/README.md docs/development/testing/TESTING_README.md 2>/dev/null

# 移动日志文档
echo "移动日志文档..."
mv backend/app/logs/USAGE.md docs/development/logging/LOGGING_USAGE.md 2>/dev/null
mv backend/app/logs/README.md docs/development/logging/LOGGING_README.md 2>/dev/null

echo "整理完成！"
echo ""
echo "文档已移动到:"
echo "- docs/development/xui-api/     (XUI API 文档)"
echo "- docs/development/testing/     (测试文档)"
echo "- docs/development/logging/     (日志文档)"
echo ""
echo "查看移动的文件:"
ls -la docs/development/xui-api/
ls -la docs/development/testing/
ls -la docs/development/logging/

#!/bin/bash

echo "=== 检查 XUI 同步入站代码 ==="
echo ""

echo "1. 检查 API 文件中的响应格式:"
grep -A 3 "return XuiOperationResponse" backend/app/apis/v1/xui/operation.py | tail -4
echo ""

echo "2. 检查 Schema 定义:"
grep -A 3 "class XuiOperationResponse" backend/app/schemas/xui/user.py
echo ""

echo "3. 检查 Git 状态:"
git status --short
echo ""

echo "4. 检查最近的提交:"
git log --oneline -1
echo ""

echo "=== 部署建议 ==="
echo "如果代码已更新但服务器还在报错，需要："
echo "1. 重启后端服务"
echo "2. 如果是 Docker 部署: docker compose restart backend-api"
echo "3. 如果是原生部署: 重启 Python 进程"

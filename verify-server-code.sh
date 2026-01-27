#!/bin/bash

echo "=== 验证服务器代码版本 ==="
echo ""

echo "1. 检查 Git 提交:"
git log --oneline -3
echo ""

echo "2. 检查本地代码（应该有 success=True）:"
grep -A 2 "return XuiOperationResponse" backend/app/apis/v1/xui/operation.py | tail -3
echo ""

echo "3. 检查容器内代码:"
docker compose -f docker-compose.backend.yml exec backend-api grep -A 2 "return XuiOperationResponse" /app/app/apis/v1/xui/operation.py | tail -3
echo ""

echo "=== 解决方案 ==="
echo "如果容器内代码不同，需要强制重新构建（不使用缓存）："
echo "docker compose -f docker-compose.backend.yml build --no-cache backend-api"
echo "docker compose -f docker-compose.backend.yml up -d backend-api"

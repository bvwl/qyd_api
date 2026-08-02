#!/bin/bash

echo "=== 检查 WORKERS 配置 ==="
echo ""

echo "1. 检查 .env 文件中的 WORKERS 配置:"
grep "^WORKERS=" .env || echo "  未找到 WORKERS 配置"

echo ""
echo "2. 检查容器中的 WORKERS 环境变量:"
docker compose -f docker-compose.backend.yml exec backend-api printenv | grep WORKERS || echo "  未找到 WORKERS 环境变量"

echo ""
echo "3. 检查容器中运行的进程数:"
docker compose -f docker-compose.backend.yml exec backend-api ps aux | grep "uvicorn" | grep -v grep

echo ""
echo "4. 检查 uvicorn 进程树:"
docker compose -f docker-compose.backend.yml exec backend-api pgrep -a uvicorn

echo ""
echo "=== 完成 ==="

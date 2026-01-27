#!/bin/bash

# 检查用户 zhiyu 的服务器账号

echo "=========================================="
echo "检查用户 zhiyu 的服务器账号"
echo "=========================================="

docker compose -f docker-compose.backend.yml exec backend-api python check_server_account.py zhiyu

echo ""
echo "=========================================="
echo "如果显示'未找到服务器账号'，请运行以下命令创建："
echo "bash create_account_for_zhiyu.sh"
echo "=========================================="

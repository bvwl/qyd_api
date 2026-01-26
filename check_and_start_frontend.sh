#!/bin/bash

echo "=========================================="
echo "检查和启动前端服务"
echo "=========================================="
echo ""

# 1. 查看所有容器状态
echo "1. 所有容器状态："
docker compose ps
echo ""

# 2. 尝试启动前端
echo "2. 启动前端容器..."
docker compose up -d frontend
echo ""

# 3. 等待启动
echo "3. 等待 5 秒..."
sleep 5
echo ""

# 4. 再次检查状态
echo "4. 前端容器状态："
docker compose ps frontend
echo ""

# 5. 查看前端日志
echo "5. 前端日志："
docker compose logs frontend --tail=30
echo ""

# 6. 测试访问
echo "6. 测试访问："
curl -I http://192.168.13.6:80
echo ""

echo "=========================================="
echo "如果前端仍未启动，请查看上面的日志"
echo "=========================================="

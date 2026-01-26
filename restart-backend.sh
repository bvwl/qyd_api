#!/bin/bash

# ==========================================
# 快速重启后端服务脚本
# ==========================================

echo "==========================================
重启后端服务
=========================================="

# 使用 .env.high_concurrency 配置
export $(grep -v '^#' .env.high_concurrency | xargs)

echo "重启后端 API 容器..."
docker compose restart backend-api

echo ""
echo "等待服务启动..."
sleep 5

echo ""
echo "检查服务状态..."
docker compose ps backend-api

echo ""
echo "✅ 后端服务已重启"
echo ""
echo "测试 API 访问："
echo "  curl -I http://192.168.13.6:6080/docs"

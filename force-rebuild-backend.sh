#!/bin/bash

echo "=== 强制重新构建后端服务（不使用缓存） ==="
echo ""

# 检查是否在正确的目录
if [ ! -f "docker-compose.backend.yml" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

echo "⚠️  警告: 此操作将清除构建缓存并重新构建镜像"
echo "⚠️  这可能需要几分钟时间"
echo ""
read -p "是否继续？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 1
fi

echo ""
echo "1. 停止后端服务..."
docker compose -f docker-compose.backend.yml stop backend-api

echo ""
echo "2. 删除旧镜像..."
docker rmi qyd_api-backend-api:latest 2>/dev/null || echo "  (镜像不存在，跳过)"

echo ""
echo "3. 强制重新构建镜像（不使用缓存）..."
docker compose -f docker-compose.backend.yml build --no-cache backend-api

echo ""
echo "4. 启动后端服务..."
docker compose -f docker-compose.backend.yml up -d backend-api

echo ""
echo "5. 等待服务启动..."
sleep 5

echo ""
echo "6. 验证代码已更新..."
echo "容器内代码:"
docker compose -f docker-compose.backend.yml exec backend-api grep -A 2 "return XuiOperationResponse" /app/app/apis/v1/xui/operation.py | tail -3

echo ""
echo "7. 查看服务状态..."
docker compose -f docker-compose.backend.yml ps backend-api

echo ""
echo "8. 查看最近的日志..."
docker compose -f docker-compose.backend.yml logs --tail=30 backend-api

echo ""
echo "=== 完成 ==="
echo "查看实时日志: docker compose -f docker-compose.backend.yml logs -f backend-api"
echo "访问 API 文档: http://192.168.13.6:6080/docs"
echo ""
echo "测试同步入站 API:"
echo "curl -X POST 'http://192.168.13.6:6080/v1/xui/operation/sync-inbounds/YOUR_SERVER_ID' \\"
echo "  -H 'Authorization: Bearer YOUR_TOKEN'"

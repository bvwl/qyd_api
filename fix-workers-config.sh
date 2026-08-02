#!/bin/bash

echo "=== 修复 WORKERS 配置（避免定时任务重复执行） ==="
echo ""

# 检查是否在正确的目录
if [ ! -f ".env" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

echo "1. 检查当前 WORKERS 配置..."
current_workers=$(grep "^WORKERS=" .env | cut -d'=' -f2)
if [ -z "$current_workers" ]; then
    echo "  ⚠️  未找到 WORKERS 配置"
else
    echo "  当前值: WORKERS=$current_workers"
fi

echo ""
echo "2. 检查容器中的实际配置..."
if docker compose -f docker-compose.backend.yml ps | grep -q "backend-api"; then
    container_workers=$(docker compose -f docker-compose.backend.yml exec -T backend-api printenv WORKERS 2>/dev/null || echo "未运行")
    echo "  容器中的值: WORKERS=$container_workers"
    
    echo ""
    echo "3. 检查实际运行的进程数..."
    process_count=$(docker compose -f docker-compose.backend.yml exec -T backend-api ps aux 2>/dev/null | grep -c "uvicorn" || echo "0")
    echo "  uvicorn 进程数: $process_count"
else
    echo "  ⚠️  backend-api 容器未运行"
fi

echo ""
echo "4. 修复 WORKERS 配置..."

# 备份 .env 文件
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
echo "  ✅ 已备份 .env 文件"

# 更新 WORKERS 配置
if grep -q "^WORKERS=" .env; then
    # 替换现有配置
    sed -i.bak 's/^WORKERS=.*/WORKERS=1/' .env
    echo "  ✅ 已更新 WORKERS=1"
else
    # 添加新配置
    echo "" >> .env
    echo "# Worker 配置（生产环境推荐使用 1）" >> .env
    echo "WORKERS=1" >> .env
    echo "  ✅ 已添加 WORKERS=1"
fi

echo ""
echo "5. 重新启动服务..."
echo "  停止服务..."
docker compose -f docker-compose.backend.yml stop backend-api queue-worker

echo "  启动服务..."
docker compose -f docker-compose.backend.yml up -d backend-api queue-worker

echo ""
echo "6. 等待服务启动..."
sleep 5

echo ""
echo "7. 验证修复..."
new_workers=$(docker compose -f docker-compose.backend.yml exec -T backend-api printenv WORKERS 2>/dev/null || echo "未运行")
echo "  容器中的 WORKERS: $new_workers"

new_process_count=$(docker compose -f docker-compose.backend.yml exec -T backend-api ps aux 2>/dev/null | grep -c "uvicorn" || echo "0")
echo "  uvicorn 进程数: $new_process_count"

echo ""
if [ "$new_workers" = "1" ] && [ "$new_process_count" -le "2" ]; then
    echo "✅ 修复成功！"
    echo ""
    echo "现在定时任务只会执行一次，不会重复。"
else
    echo "⚠️  可能需要手动检查"
    echo ""
    echo "请运行以下命令查看日志："
    echo "  docker compose -f docker-compose.backend.yml logs -f backend-api"
fi

echo ""
echo "=== 完成 ==="
echo ""
echo "查看实时日志（检查定时任务是否只执行一次）："
echo "  docker compose -f docker-compose.backend.yml logs -f backend-api | grep '开始执行'"
echo ""
echo "如需高并发，使用容器扩展而不是多 worker："
echo "  docker compose -f docker-compose.backend.yml up -d --scale backend-api=3"
echo ""
echo "详细说明请参考: WORKERS_DUPLICATE_TASKS.md"

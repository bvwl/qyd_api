#!/bin/bash

# ==========================================
# 修复 Nginx 配置中的容器名称
# ==========================================

set -e

echo "=========================================="
echo "修复 Nginx 配置"
echo "=========================================="

# 1. 检查当前容器名称
echo ""
echo "[1/4] 检查当前容器名称..."
echo ""
docker compose ps --format "table {{.Name}}\t{{.Service}}\t{{.Status}}"

# 2. 获取项目名称（从容器名推断）
echo ""
echo "[2/4] 获取项目名称..."
PROJECT_NAME=$(docker compose ps --format "{{.Name}}" | grep backend-api | head -1 | sed 's/-backend-api-.*//')
echo "  项目名称: $PROJECT_NAME"

# 3. 生成新的 Nginx 配置
echo ""
echo "[3/4] 生成新的 Nginx 配置..."

cat > nginx-lb.conf << EOF
# ==========================================
# Nginx 负载均衡配置（生产环境）
# 自动生成 - $(date)
# ==========================================

# 后端 API 负载均衡池
upstream backend_api {
    # 负载均衡策略：least_conn（最少连接）
    least_conn;
    
    # 5 个后端容器（通过容器名访问）
    server ${PROJECT_NAME}-backend-api-1:6080 max_fails=3 fail_timeout=30s;
    server ${PROJECT_NAME}-backend-api-2:6080 max_fails=3 fail_timeout=30s;
    server ${PROJECT_NAME}-backend-api-3:6080 max_fails=3 fail_timeout=30s;
    server ${PROJECT_NAME}-backend-api-4:6080 max_fails=3 fail_timeout=30s;
    server ${PROJECT_NAME}-backend-api-5:6080 max_fails=3 fail_timeout=30s;
    
    # 保持连接
    keepalive 100;
}

# HTTP 服务器
server {
    listen 80;
    server_name _;
    
    # 访问日志
    access_log /var/log/nginx/qyd_access.log;
    error_log /var/log/nginx/qyd_error.log;
    
    # 客户端最大请求体大小
    client_max_body_size 100M;
    
    # 前端静态文件
    location / {
        # 使用变量强制 DNS 重新解析
        set \$frontend_upstream ${PROJECT_NAME}-frontend-1;
        proxy_pass http://\$frontend_upstream:80;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

# 后端 API 服务器
server {
    listen 6080;
    server_name _;
    
    # 访问日志
    access_log /var/log/nginx/qyd_api_access.log;
    error_log /var/log/nginx/qyd_api_error.log;
    
    # 客户端最大请求体大小
    client_max_body_size 100M;
    
    # 后端 API（负载均衡）
    location / {
        proxy_pass http://backend_api;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲配置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
        
        # WebSocket 支持
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

echo "  ✓ 已生成新配置"
echo ""
echo "  后端容器名称："
echo "    - ${PROJECT_NAME}-backend-api-1:6080"
echo "    - ${PROJECT_NAME}-backend-api-2:6080"
echo "    - ${PROJECT_NAME}-backend-api-3:6080"
echo "    - ${PROJECT_NAME}-backend-api-4:6080"
echo "    - ${PROJECT_NAME}-backend-api-5:6080"
echo ""
echo "  前端容器名称："
echo "    - ${PROJECT_NAME}-frontend-1:80"

# 4. 重启 Nginx
echo ""
echo "[4/4] 重启 Nginx..."
docker compose restart nginx-lb

# 等待 Nginx 启动
sleep 5

# 5. 测试配置
echo ""
echo "=========================================="
echo "测试配置"
echo "=========================================="

echo ""
echo "测试前端（80端口）："
curl -I http://192.168.13.6/ 2>&1 | head -1

echo ""
echo "测试后端 API（6080端口）："
curl -I http://192.168.13.6:6080/docs 2>&1 | head -1

echo ""
echo "测试后端 API 接口："
curl -s http://192.168.13.6:6080/v1/user/role/tree 2>&1 | head -c 100

echo ""
echo ""
echo "=========================================="
echo "✅ 修复完成！"
echo "=========================================="
echo ""
echo "如果还有问题，请检查 Nginx 日志："
echo "  docker compose logs nginx-lb"

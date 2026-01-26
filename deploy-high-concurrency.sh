#!/bin/bash

# ==========================================
# QYD 高并发部署脚本
# ==========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "=========================================="
echo -e "${BLUE}QYD 高并发部署脚本${NC}"
echo "=========================================="
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ==========================================
# 配置参数（可根据服务器资源调整）
# ==========================================
BACKEND_INSTANCES=5      # 后端 API 容器数量
QUEUE_INSTANCES=5        # 队列 Worker 容器数量
REDIS_MEMORY="8gb"       # Redis 内存限制

echo -e "${CYAN}部署配置：${NC}"
echo "  后端容器数量: $BACKEND_INSTANCES"
echo "  队列容器数量: $QUEUE_INSTANCES"
echo "  Redis 内存: $REDIS_MEMORY"
echo ""

read -p "是否使用此配置？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "请编辑脚本修改配置参数"
    exit 1
fi

# ==========================================
# 1. 检查环境
# ==========================================
echo -e "${YELLOW}[1/8] 检查环境...${NC}"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: 未找到 Docker${NC}"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo -e "${RED}错误: Docker 未运行${NC}"
    exit 1
fi

# 检查 Docker Compose
if ! docker compose version &> /dev/null; then
    echo -e "${RED}错误: Docker Compose 未安装${NC}"
    exit 1
fi

# 检查系统资源
TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
CPU_CORES=$(nproc)

echo -e "${GREEN}✓ Docker 环境正常${NC}"
echo "  CPU 核心: $CPU_CORES"
echo "  总内存: ${TOTAL_MEM}GB"

if [ "$TOTAL_MEM" -lt 16 ]; then
    echo -e "${YELLOW}警告: 内存不足 16GB，建议增加内存${NC}"
fi

if [ "$CPU_CORES" -lt 8 ]; then
    echo -e "${YELLOW}警告: CPU 核心不足 8 个，建议增加 CPU${NC}"
fi
echo ""

# ==========================================
# 2. 检查 MySQL 主从
# ==========================================
echo -e "${YELLOW}[2/8] 检查 MySQL 主从集群...${NC}"

# 从 .env 读取配置
if [ -f ".env" ]; then
    source .env
else
    echo -e "${RED}错误: .env 文件不存在${NC}"
    exit 1
fi

# 询问是否跳过 MySQL 检查
read -p "是否跳过 MySQL 连接检查？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}跳过 MySQL 检查${NC}"
    echo -e "${YELLOW}提示: 请确保 MySQL 主从集群已正常运行${NC}"
else
    # 检查主库
    echo "检查主库: $DB_HOST:$DB_PORT"
    if mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1;" &> /dev/null; then
        echo -e "${GREEN}✓ 主库连接正常${NC}"
    else
        echo -e "${RED}✗ 主库连接失败${NC}"
        echo -e "${YELLOW}提示: 如果 MySQL 确实可用，可以选择跳过检查${NC}"
        exit 1
    fi
fi

echo ""

# ==========================================
# 3. 优化系统参数
# ==========================================
echo -e "${YELLOW}[3/8] 优化系统参数...${NC}"

# 检查是否需要 root 权限
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}需要 root 权限优化系统参数${NC}"
    
    # 临时优化（重启后失效）
    sudo sysctl -w net.core.somaxconn=65535 2>/dev/null || true
    sudo sysctl -w net.ipv4.tcp_max_syn_backlog=65535 2>/dev/null || true
    sudo sysctl -w fs.file-max=1000000 2>/dev/null || true
    
    echo -e "${GREEN}✓ 系统参数已临时优化${NC}"
    echo -e "${YELLOW}提示: 永久优化请参考 HIGH_CONCURRENCY_DEPLOYMENT.md${NC}"
else
    # 永久优化
    cat >> /etc/sysctl.conf << 'EOF'

# QYD 高并发优化
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 1200
net.ipv4.tcp_tw_reuse = 1
net.ipv4.ip_local_port_range = 10000 65000
fs.file-max = 1000000
fs.nr_open = 1000000
EOF
    
    sysctl -p
    echo -e "${GREEN}✓ 系统参数已永久优化${NC}"
fi
echo ""

# ==========================================
# 4. 停止旧服务
# ==========================================
echo -e "${YELLOW}[4/8] 停止旧服务...${NC}"

if docker compose ps | grep -q "Up"; then
    echo "停止现有容器..."
    docker compose down
    echo -e "${GREEN}✓ 旧服务已停止${NC}"
else
    echo "没有运行中的服务"
fi
echo ""

# ==========================================
# 5. 清理资源（可选）
# ==========================================
echo -e "${YELLOW}[5/8] 清理资源...${NC}"

read -p "是否清理旧镜像和缓存？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "清理 Docker 资源..."
    docker system prune -af --volumes
    echo -e "${GREEN}✓ 清理完成${NC}"
else
    echo "跳过清理"
fi
echo ""

# ==========================================
# 6. 构建镜像
# ==========================================
echo -e "${YELLOW}[6/8] 构建镜像...${NC}"

echo "使用国内镜像源加速构建..."
docker compose build --parallel

echo -e "${GREEN}✓ 镜像构建完成${NC}"
echo ""

# ==========================================
# 7. 初始化数据库（首次部署）
# ==========================================
echo -e "${YELLOW}[7/8] 初始化数据库...${NC}"

if [ ! -f ".initialized" ]; then
    echo "首次部署，初始化数据库..."
    
    # 启动 Redis
    docker compose up -d redis
    echo "等待 Redis 启动..."
    sleep 10
    
    # 初始化角色和管理员
    echo "初始化角色和管理员..."
    docker compose run --rm backend-api python deploy_init.py
    
    # 初始化路由
    echo "初始化路由..."
    docker compose run --rm backend-api python db/init_routes.py
    
    # 标记已初始化
    touch .initialized
    
    echo -e "${GREEN}✓ 数据库初始化完成${NC}"
else
    echo "数据库已初始化，跳过"
    echo -e "${YELLOW}提示: 如需重新初始化路由，请执行:${NC}"
    echo "  docker compose run --rm backend-api python db/init_routes.py"
fi
echo ""

# ==========================================
# 8. 启动服务（高并发模式）
# ==========================================
echo -e "${YELLOW}[8/8] 启动服务（高并发模式）...${NC}"

echo "启动 $BACKEND_INSTANCES 个后端容器和 $QUEUE_INSTANCES 个队列容器..."
docker compose up -d \
    --scale backend-api=$BACKEND_INSTANCES \
    --scale queue-worker=$QUEUE_INSTANCES \
    frontend

echo ""
echo "等待服务启动（30秒）..."
sleep 30

# 检查服务状态
echo ""
echo -e "${CYAN}服务状态：${NC}"
docker compose ps

echo ""
echo -e "${CYAN}资源使用：${NC}"
docker stats --no-stream

echo ""
echo "=========================================="
echo -e "${GREEN}部署完成！${NC}"
echo "=========================================="
echo ""

# ==========================================
# 显示部署信息
# ==========================================
echo -e "${CYAN}部署信息：${NC}"
echo "  后端容器: $BACKEND_INSTANCES 个"
echo "  队列容器: $QUEUE_INSTANCES 个"
echo "  前端容器: 1 个"
echo "  Redis 容器: 1 个"
echo ""

# 计算总连接数
TOTAL_DB_CONN=$((BACKEND_INSTANCES * 50 * 3))
TOTAL_REDIS_CONN=$((BACKEND_INSTANCES * 200))

echo -e "${CYAN}资源使用：${NC}"
echo "  数据库连接: ~$TOTAL_DB_CONN 个"
echo "  Redis 连接: ~$TOTAL_REDIS_CONN 个"
echo ""

echo -e "${CYAN}访问地址：${NC}"
echo "  前端: http://192.168.13.6"
echo "  后端: http://192.168.13.6:6080"
echo "  API 文档: http://192.168.13.6:6080/docs"
echo ""

echo -e "${CYAN}默认管理员账号：${NC}"
echo "  邮箱: zhiyu"
echo "  密码: 2201101122@qq.com"
echo ""

echo -e "${CYAN}常用命令：${NC}"
echo "  查看日志: docker compose logs -f"
echo "  查看状态: docker compose ps"
echo "  查看资源: docker stats"
echo "  重启服务: docker compose restart"
echo "  停止服务: docker compose stop"
echo ""

echo -e "${CYAN}性能测试：${NC}"
echo "  ab -n 10000 -c 100 http://192.168.13.6:6080/docs"
echo "  wrk -t12 -c1000 -d60s http://192.168.13.6:6080/docs"
echo ""

echo -e "${CYAN}监控命令：${NC}"
echo "  # 查看 MySQL 连接数"
echo "  mysql -h $DB_HOST -u $DB_USER -p -e \"SHOW PROCESSLIST;\" | wc -l"
echo ""
echo "  # 查看 Redis 连接数"
echo "  docker compose exec redis redis-cli -a $REDIS_PASSWORD CLIENT LIST | wc -l"
echo ""
echo "  # 查看队列长度"
echo "  docker compose exec redis redis-cli -a $REDIS_PASSWORD LLEN project_account_queue"
echo ""

echo -e "${YELLOW}提示：${NC}"
echo "  - 如需调整容器数量，编辑脚本顶部的配置参数"
echo "  - 详细文档请查看: HIGH_CONCURRENCY_DEPLOYMENT.md"
echo "  - 性能优化请查看: docs/performance/ULTRA_HIGH_PERFORMANCE_GUIDE.md"
echo ""

# ==========================================
# 健康检查
# ==========================================
echo -e "${YELLOW}执行健康检查...${NC}"
sleep 5

# 检查后端 API
if curl -s http://192.168.13.6:6080/docs > /dev/null; then
    echo -e "${GREEN}✓ 后端 API 正常${NC}"
else
    echo -e "${RED}✗ 后端 API 异常${NC}"
    echo "请查看日志: docker compose logs backend-api"
fi

# 检查前端
if curl -s http://192.168.13.6/ > /dev/null; then
    echo -e "${GREEN}✓ 前端服务正常${NC}"
else
    echo -e "${RED}✗ 前端服务异常${NC}"
    echo "请查看日志: docker compose logs frontend"
fi

# 检查 Redis
if docker compose exec redis redis-cli -a "$REDIS_PASSWORD" PING 2>/dev/null | grep -q "PONG"; then
    echo -e "${GREEN}✓ Redis 服务正常${NC}"
else
    echo -e "${RED}✗ Redis 服务异常${NC}"
    echo "请查看日志: docker compose logs redis"
fi

echo ""
echo -e "${GREEN}部署完成！系统已就绪。${NC}"
echo ""

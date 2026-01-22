#!/bin/bash
# MySQL环境清理脚本

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }

echo "=========================================="
echo "  MySQL环境清理脚本"
echo "=========================================="
echo ""

log_error "警告：此操作将删除所有MySQL容器和数据！"
echo ""
echo "将要执行的操作："
echo "  1. 停止所有MySQL容器"
echo "  2. 删除所有MySQL容器"
echo "  3. 删除所有MySQL数据（可选）"
echo ""

read -p "确认要继续吗？(yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "操作已取消"
    exit 0
fi

echo ""
log_info "1. 停止MySQL容器..."
docker stop mysql-master mysql-slave-1 mysql-slave-2 2>/dev/null || true

echo ""
log_info "2. 删除MySQL容器..."
docker rm mysql-master mysql-slave-1 mysql-slave-2 2>/dev/null || true

echo ""
log_info "容器已清理完成"
docker ps -a | grep mysql || echo "没有MySQL容器"

echo ""
read -p "是否删除数据目录？(yes/no): " delete_data

if [ "$delete_data" = "yes" ]; then
    log_warn "删除数据目录..."
    sudo rm -rf /opt/mysql/master/data/*
    sudo rm -rf /opt/mysql/slave-1/data/*
    sudo rm -rf /opt/mysql/slave-2/data/*
    log_info "数据目录已清理"
else
    log_info "保留数据目录"
fi

echo ""
echo "=========================================="
log_info "清理完成！"
echo "=========================================="
echo ""
echo "如需重新部署，运行："
echo "  ./deploy_mysql_final.sh"
echo ""

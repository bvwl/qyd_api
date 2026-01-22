#!/bin/bash
# MySQL容器重启脚本

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "=========================================="
echo "  MySQL容器重启脚本"
echo "=========================================="
echo ""

case "$1" in
    master|m)
        log_info "重启主库容器..."
        docker restart mysql-master
        log_info "等待30秒让MySQL启动..."
        sleep 30
        if docker exec mysql-master mysql -uroot -pzhiyu666 -e "SELECT 1" &>/dev/null; then
            log_info "主库重启成功 ✓"
        else
            log_error "主库重启失败"
            docker logs mysql-master --tail 20
        fi
        ;;
    slave1|s1|1)
        log_info "重启从库1容器..."
        docker restart mysql-slave-1
        log_info "等待30秒让MySQL启动..."
        sleep 30
        if docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SELECT 1" &>/dev/null; then
            log_info "从库1重启成功 ✓"
            log_warn "请检查复制状态："
            echo "  docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e \"SHOW REPLICA STATUS\\G\""
        else
            log_error "从库1重启失败"
            docker logs mysql-slave-1 --tail 20
        fi
        ;;
    slave2|s2|2)
        log_info "重启从库2容器..."
        docker restart mysql-slave-2
        log_info "等待30秒让MySQL启动..."
        sleep 30
        if docker exec mysql-slave-2 mysql -uroot -pzhiyu666 -e "SELECT 1" &>/dev/null; then
            log_info "从库2重启成功 ✓"
            log_warn "请检查复制状态："
            echo "  docker exec mysql-slave-2 mysql -uroot -pzhiyu666 -e \"SHOW REPLICA STATUS\\G\""
        else
            log_error "从库2重启失败"
            docker logs mysql-slave-2 --tail 20
        fi
        ;;
    all|a)
        log_info "重启所有MySQL容器..."
        docker restart mysql-master mysql-slave-1 mysql-slave-2
        log_info "等待60秒让所有MySQL启动..."
        sleep 60
        
        echo ""
        log_info "检查容器状态..."
        docker ps | grep mysql
        
        echo ""
        log_warn "从库重启后需要检查复制状态："
        echo "  ./check_mysql_status.sh"
        ;;
    *)
        echo "用法: $0 {master|slave1|slave2|all}"
        echo "简写: $0 {m|s1|s2|1|2|a}"
        echo ""
        echo "示例："
        echo "  $0 master   # 重启主库"
        echo "  $0 slave1   # 重启从库1"
        echo "  $0 all      # 重启所有容器"
        exit 1
        ;;
esac

echo ""

#!/bin/bash
# 日志管理工具脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志目录
LOG_DIR="logs"

# 显示帮助信息
show_help() {
    echo -e "${BLUE}日志管理工具${NC}"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  test        - 运行日志系统测试"
    echo "  example     - 运行使用示例"
    echo "  clean       - 清理旧日志（保留30天）"
    echo "  clean-all   - 清理所有日志"
    echo "  analyze     - 分析日志统计"
    echo "  view        - 查看实时日志"
    echo "  list        - 列出所有日志文件"
    echo "  size        - 查看日志目录大小"
    echo "  compress    - 手动压缩日志"
    echo "  help        - 显示此帮助信息"
    echo ""
}

# 运行测试
run_test() {
    echo -e "${BLUE}运行日志系统测试...${NC}"
    python test_logging_system.py
}

# 运行示例
run_example() {
    echo -e "${BLUE}运行日志使用示例...${NC}"
    python examples/log_usage_examples.py
}

# 清理日志
clean_logs() {
    echo -e "${YELLOW}清理旧日志（保留30天）...${NC}"
    python scripts/cleanup_logs.py
    echo -e "${GREEN}清理完成${NC}"
}

# 清理所有日志
clean_all_logs() {
    echo -e "${RED}警告: 将删除所有日志文件！${NC}"
    read -p "确认删除？(yes/no): " confirm
    
    if [ "$confirm" = "yes" ]; then
        echo -e "${YELLOW}删除所有日志...${NC}"
        rm -rf ${LOG_DIR}/*
        echo -e "${GREEN}所有日志已删除${NC}"
    else
        echo -e "${BLUE}操作已取消${NC}"
    fi
}

# 分析日志
analyze_logs() {
    echo -e "${BLUE}分析日志统计...${NC}"
    python scripts/analyze_logs.py
}

# 查看实时日志
view_logs() {
    if [ ! -d "$LOG_DIR" ]; then
        echo -e "${RED}日志目录不存在: $LOG_DIR${NC}"
        exit 1
    fi
    
    # 获取所有当前日志文件
    log_files=$(find $LOG_DIR -name "*.log" -type f)
    
    if [ -z "$log_files" ]; then
        echo -e "${YELLOW}没有找到日志文件${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}实时查看日志（Ctrl+C 退出）...${NC}"
    echo ""
    tail -f $log_files
}

# 列出日志文件
list_logs() {
    if [ ! -d "$LOG_DIR" ]; then
        echo -e "${RED}日志目录不存在: $LOG_DIR${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}当前日志文件:${NC}"
    ls -lh $LOG_DIR/*.log 2>/dev/null || echo "  无"
    
    echo ""
    echo -e "${BLUE}滚动日志文件:${NC}"
    ls -lh $LOG_DIR/*.log.* 2>/dev/null | grep -v ".gz$" || echo "  无"
    
    echo ""
    echo -e "${BLUE}压缩日志文件:${NC}"
    ls -lh $LOG_DIR/*.log.*.gz 2>/dev/null || echo "  无"
}

# 查看日志大小
show_size() {
    if [ ! -d "$LOG_DIR" ]; then
        echo -e "${RED}日志目录不存在: $LOG_DIR${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}日志目录大小:${NC}"
    du -sh $LOG_DIR
    
    echo ""
    echo -e "${BLUE}各类文件统计:${NC}"
    
    current_logs=$(find $LOG_DIR -name "*.log" -type f | wc -l)
    current_size=$(find $LOG_DIR -name "*.log" -type f -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1)
    echo "  当前日志: $current_logs 个, 大小: ${current_size:-0}"
    
    rotated_logs=$(find $LOG_DIR -name "*.log.*" -type f ! -name "*.gz" | wc -l)
    rotated_size=$(find $LOG_DIR -name "*.log.*" -type f ! -name "*.gz" -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1)
    echo "  滚动日志: $rotated_logs 个, 大小: ${rotated_size:-0}"
    
    compressed_logs=$(find $LOG_DIR -name "*.log.*.gz" -type f | wc -l)
    compressed_size=$(find $LOG_DIR -name "*.log.*.gz" -type f -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1)
    echo "  压缩日志: $compressed_logs 个, 大小: ${compressed_size:-0}"
}

# 手动压缩日志
compress_logs() {
    echo -e "${BLUE}手动压缩日志...${NC}"
    
    # 查找未压缩的滚动日志
    uncompressed=$(find $LOG_DIR -name "*.log.*" -type f ! -name "*.gz" 2>/dev/null)
    
    if [ -z "$uncompressed" ]; then
        echo -e "${GREEN}没有需要压缩的日志文件${NC}"
        exit 0
    fi
    
    count=0
    for file in $uncompressed; do
        echo "  压缩: $(basename $file)"
        gzip "$file"
        count=$((count + 1))
    done
    
    echo -e "${GREEN}压缩完成，共处理 $count 个文件${NC}"
}

# 主逻辑
case "${1:-help}" in
    test)
        run_test
        ;;
    example)
        run_example
        ;;
    clean)
        clean_logs
        ;;
    clean-all)
        clean_all_logs
        ;;
    analyze)
        analyze_logs
        ;;
    view)
        view_logs
        ;;
    list)
        list_logs
        ;;
    size)
        show_size
        ;;
    compress)
        compress_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}未知命令: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

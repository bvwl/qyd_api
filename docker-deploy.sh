#!/bin/bash

# QYD Docker 部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
    echo ""
}

# 检查 Docker 是否安装
check_docker() {
    print_header "检查 Docker 环境"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    print_success "Docker 版本: $(docker --version)"
    print_success "Docker Compose 版本: $(docker-compose --version)"
}

# 检查环境变量文件
check_env_file() {
    print_header "检查环境变量配置"
    
    if [ ! -f ".env" ]; then
        print_warning ".env 文件不存在"
        
        if [ -f ".env.docker" ]; then
            print_info "复制 .env.docker 到 .env"
            cp .env.docker .env
            print_warning "请编辑 .env 文件，配置数据库和 Redis 连接信息"
            read -p "是否现在编辑 .env 文件？(Y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                ${EDITOR:-vim} .env
            fi
        else
            print_error "未找到 .env.docker 模板文件"
            exit 1
        fi
    else
        print_success ".env 文件已存在"
    fi
}

# 构建镜像
build_images() {
    print_header "构建 Docker 镜像"
    
    print_info "构建后端镜像..."
    docker-compose build backend-api queue-worker
    
    print_info "构建前端镜像..."
    docker-compose build frontend
    
    print_success "镜像构建完成"
}

# 初始化数据库
init_database() {
    print_header "初始化数据库"
    
    print_warning "确保 MySQL 和 Redis 服务已启动并可访问"
    read -p "是否继续初始化数据库？(Y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "跳过数据库初始化"
        return
    fi
    
    print_info "运行数据库初始化脚本..."
    docker-compose run --rm backend-api python deploy_init.py
    
    print_success "数据库初始化完成"
}

# 启动服务
start_services() {
    print_header "启动服务"
    
    print_info "启动所有服务..."
    docker-compose up -d
    
    print_success "服务启动成功"
    
    # 显示服务状态
    echo ""
    docker-compose ps
}

# 查看日志
view_logs() {
    print_header "查看服务日志"
    
    echo "选择要查看的服务日志："
    echo "1) 后端 API"
    echo "2) 队列 Worker"
    echo "3) 前端"
    echo "4) 所有服务"
    echo "5) 跳过"
    
    read -p "请选择 (1-5): " -n 1 -r
    echo
    
    case $REPLY in
        1) docker-compose logs -f backend-api ;;
        2) docker-compose logs -f queue-worker ;;
        3) docker-compose logs -f frontend ;;
        4) docker-compose logs -f ;;
        5) return ;;
        *) print_warning "无效选择" ;;
    esac
}

# 显示访问信息
show_access_info() {
    print_header "部署完成！"
    
    echo "服务访问地址："
    echo ""
    echo "  前端应用: http://localhost"
    echo "  后端 API: http://localhost:6080"
    echo "  API 文档: http://localhost:6080/docs"
    echo ""
    echo "默认管理员账号："
    echo "  邮箱: zhiyu"
    echo "  密码: 2201101122@qq.com"
    echo ""
    print_warning "⚠️  首次登录后请立即修改密码！"
    echo ""
    echo "常用命令："
    echo "  查看服务状态: docker-compose ps"
    echo "  查看日志: docker-compose logs -f"
    echo "  停止服务: docker-compose stop"
    echo "  重启服务: docker-compose restart"
    echo "  删除服务: docker-compose down"
    echo ""
}

# 主函数
main() {
    print_header "QYD Docker 部署"
    
    # 检查 Docker
    check_docker
    
    # 检查环境变量
    check_env_file
    
    # 构建镜像
    build_images
    
    # 初始化数据库
    init_database
    
    # 启动服务
    start_services
    
    # 显示访问信息
    show_access_info
    
    # 查看日志（可选）
    view_logs
}

# 运行主函数
main

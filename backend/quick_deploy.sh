#!/bin/bash

# QYD 后端快速部署脚本
# 用于在新服务器上快速部署后端服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
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

# 打印标题
print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
    echo ""
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查 Python 版本
check_python() {
    print_header "检查 Python 环境"
    
    if ! command_exists python3; then
        print_error "未找到 Python 3，请先安装 Python 3.11+"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python 版本: $PYTHON_VERSION"
    
    # 检查版本是否 >= 3.11
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
        print_error "Python 版本过低，需要 3.11 或更高版本"
        exit 1
    fi
}

# 检查 MySQL
check_mysql() {
    print_header "检查 MySQL"
    
    if ! command_exists mysql; then
        print_warning "未找到 MySQL 客户端"
        print_info "请确保 MySQL 服务器已安装并运行"
    else
        MYSQL_VERSION=$(mysql --version | awk '{print $5}' | sed 's/,//')
        print_success "MySQL 版本: $MYSQL_VERSION"
    fi
}

# 检查 Redis
check_redis() {
    print_header "检查 Redis"
    
    if ! command_exists redis-cli; then
        print_warning "未找到 Redis 客户端"
        print_info "如果需要使用队列功能，请安装 Redis"
    else
        REDIS_VERSION=$(redis-cli --version | awk '{print $2}')
        print_success "Redis 版本: $REDIS_VERSION"
    fi
}

# 创建虚拟环境
create_venv() {
    print_header "创建虚拟环境"
    
    if [ -d "venv" ]; then
        print_warning "虚拟环境已存在，跳过创建"
    else
        print_info "创建虚拟环境..."
        python3 -m venv venv
        print_success "虚拟环境创建成功"
    fi
}

# 激活虚拟环境
activate_venv() {
    print_info "激活虚拟环境..."
    source venv/bin/activate
    print_success "虚拟环境已激活"
}

# 安装依赖
install_dependencies() {
    print_header "安装 Python 依赖"
    
    print_info "升级 pip..."
    pip install --upgrade pip -q
    
    print_info "安装依赖包（这可能需要几分钟）..."
    pip install -r requirements.txt -q
    
    print_success "依赖安装完成"
}

# 配置环境变量
configure_env() {
    print_header "配置环境变量"
    
    if [ -f ".env" ]; then
        print_warning ".env 文件已存在"
        read -p "是否覆盖现有配置？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "跳过环境变量配置"
            return
        fi
    fi
    
    print_info "复制环境变量模板..."
    cp .env.example .env
    
    print_warning "请编辑 .env 文件，配置以下必需参数："
    echo "  - DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME"
    echo "  - JWT_SECRET_KEY (至少32字符)"
    echo "  - REDIS_HOST, REDIS_PORT, REDIS_PASSWORD (如果使用 Redis)"
    echo ""
    
    read -p "是否现在编辑 .env 文件？(Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        ${EDITOR:-vim} .env
    fi
}

# 初始化 Aerich
init_aerich() {
    print_header "初始化 Aerich"
    
    if [ -d "migrations" ]; then
        print_warning "migrations 目录已存在，跳过初始化"
    else
        print_info "初始化 Aerich..."
        aerich init -t app.core.settings.TORTOISE_ORM
        print_success "Aerich 初始化完成"
    fi
}

# 初始化数据库
init_database() {
    print_header "初始化数据库"
    
    print_info "创建数据库表结构..."
    aerich init-db
    print_success "数据库表结构创建完成"
}

# 导入初始数据
import_initial_data() {
    print_header "导入初始数据"
    
    print_info "导入角色、路由和管理员用户..."
    python deploy_init.py
    
    if [ $? -eq 0 ]; then
        print_success "初始数据导入完成"
        echo ""
        print_info "默认管理员账号："
        echo "  邮箱: zhiyu"
        echo "  密码: 2201101122@qq.com"
        print_warning "⚠️  首次登录后请立即修改密码！"
    else
        print_error "初始数据导入失败"
        exit 1
    fi
}

# 测试服务启动
test_service() {
    print_header "测试服务启动"
    
    print_info "尝试启动服务（5秒后自动停止）..."
    timeout 5 python start.py || true
    
    print_success "服务启动测试完成"
}

# 显示下一步操作
show_next_steps() {
    print_header "部署完成！"
    
    echo "下一步操作："
    echo ""
    echo "1. 启动 HTTP 服务："
    echo "   python start.py"
    echo ""
    echo "2. 启动队列工作进程（可选）："
    echo "   python start_queue_worker.py"
    echo ""
    echo "3. 访问 API 文档："
    echo "   http://localhost:6080/docs"
    echo ""
    echo "4. 使用管理员账号登录："
    echo "   邮箱: zhiyu"
    echo "   密码: 2201101122@qq.com"
    echo ""
    print_warning "⚠️  首次登录后请立即修改密码！"
    echo ""
    echo "详细文档请查看: DEPLOYMENT_GUIDE.md"
    echo ""
}

# 主函数
main() {
    print_header "QYD 后端快速部署"
    
    # 检查环境
    check_python
    check_mysql
    check_redis
    
    # 创建和激活虚拟环境
    create_venv
    activate_venv
    
    # 安装依赖
    install_dependencies
    
    # 配置环境变量
    configure_env
    
    # 初始化 Aerich
    init_aerich
    
    # 初始化数据库
    init_database
    
    # 导入初始数据
    import_initial_data
    
    # 显示下一步操作
    show_next_steps
}

# 运行主函数
main

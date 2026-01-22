#!/bin/bash

# 项目清理脚本 - 删除未使用的文件
# 使用前请确保已备份项目

set -e

echo "=========================================="
echo "项目未使用文件清理脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 统计变量
DELETED_COUNT=0
FAILED_COUNT=0

# 删除函数
delete_file() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        echo -e "${YELLOW}删除:${NC} $file"
        echo "  描述: $description"
        rm -f "$file"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 成功${NC}"
            ((DELETED_COUNT++))
        else
            echo -e "${RED}✗ 失败${NC}"
            ((FAILED_COUNT++))
        fi
    else
        echo -e "${YELLOW}跳过:${NC} $file (文件不存在)"
    fi
    echo ""
}

# 删除目录函数
delete_dir() {
    local dir=$1
    local description=$2
    
    if [ -d "$dir" ] && [ -z "$(ls -A "$dir")" ]; then
        echo -e "${YELLOW}删除目录:${NC} $dir"
        echo "  描述: $description"
        rmdir "$dir"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 成功${NC}"
            ((DELETED_COUNT++))
        else
            echo -e "${RED}✗ 失败${NC}"
            ((FAILED_COUNT++))
        fi
    elif [ -d "$dir" ]; then
        echo -e "${YELLOW}跳过:${NC} $dir (目录非空)"
    else
        echo -e "${YELLOW}跳过:${NC} $dir (目录不存在)"
    fi
    echo ""
}

# 确认删除
read -p "确认删除未使用的文件? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 1
fi

echo ""
echo "=========================================="
echo "开始清理..."
echo "=========================================="
echo ""

# ========== 后端临时脚本 ==========
echo "清理后端临时脚本..."
delete_file "backend/diagnose_db.py" "数据库连接诊断脚本"
delete_file "backend/quick_test.py" "快速测试脚本"
delete_file "backend/demo_permission_setup.py" "权限设置演示脚本"
delete_file "backend/test_permission_apis.py" "权限API测试脚本"
delete_file "backend/test_rbac_apis.py" "RBAC API测试脚本"
delete_file "backend/test_read_write_split.py" "读写分离测试脚本"
delete_file "backend/fix_login_issue.sh" "登录问题修复脚本"
delete_file "backend/switch_db_mode.sh" "数据库模式切换脚本"
delete_file "backend/install_and_test.sh" "安装和测试脚本"
delete_file "backend/FIX_LOGIN_SUMMARY.md" "登录修复总结文档"

# ========== 后端未使用模块 ==========
echo "清理后端未使用模块..."
delete_file "backend/app/utils/redis_tool.py" "未使用的Redis工具模块"

# ========== 后端示例文件 ==========
echo "清理后端示例文件..."
delete_file "backend/examples/log_usage_examples.py" "日志使用示例"

# ========== 后端测试修复脚本 ==========
echo "清理后端测试修复脚本..."
delete_file "backend/tests/add_auth_to_apis.py" "批量添加认证脚本"
delete_file "backend/tests/apply_jwt_auth.py" "应用JWT认证脚本"
delete_file "backend/tests/check_exception_order.py" "检查异常顺序脚本"
delete_file "backend/tests/fix_all_apis_final.py" "修复所有API脚本"
delete_file "backend/tests/fix_all_exception_handlers.sh" "修复异常处理脚本"
delete_file "backend/tests/fix_empty_result_handling.py" "修复空结果处理脚本"
delete_file "backend/tests/fix_exception_order.py" "修复异常顺序脚本"
delete_file "backend/tests/fix_exception_order_v2.py" "修复异常顺序V2脚本"
delete_file "backend/tests/revert_empty_result_handling.py" "回滚空结果处理脚本"
delete_file "backend/tests/complete_auth_audit.sh" "完整认证审计脚本"

# ========== 前端未使用组件 ==========
echo "清理前端未使用组件..."
delete_file "frontend/src/Test.tsx" "React测试组件"
delete_file "frontend/src/examples/PermissionExample.tsx" "权限示例组件"
delete_file "frontend/src/views/User/PermissionDebug.tsx" "权限调试组件"
delete_file "frontend/src/views/User/PermissionTest.tsx" "权限测试组件"
delete_file "frontend/src/views/User/PermissionManageDebug.tsx" "权限管理调试组件"
delete_file "frontend/src/views/User/PermissionManageSimple.tsx" "权限管理简化版组件"
delete_file "frontend/src/views/User/PermissionManageV2.tsx" "权限管理V2版本组件"

# ========== 前端空目录 ==========
echo "清理前端空目录..."
delete_dir "frontend/src/components/PageContainer" "空的PageContainer目录"
delete_dir "frontend/src/components/SearchForm" "空的SearchForm目录"
delete_dir "frontend/src/styles" "空的styles目录"

# ========== 项目根目录 ==========
echo "清理项目根目录..."
delete_file "organize_project.sh" "项目组织脚本"

# ========== 总结 ==========
echo ""
echo "=========================================="
echo "清理完成"
echo "=========================================="
echo -e "${GREEN}成功删除: $DELETED_COUNT 个文件/目录${NC}"
if [ $FAILED_COUNT -gt 0 ]; then
    echo -e "${RED}删除失败: $FAILED_COUNT 个文件/目录${NC}"
fi
echo ""

# 建议后续操作
echo "建议后续操作:"
echo "1. 运行测试: npm run test (前端) 和 pytest (后端)"
echo "2. 检查构建: npm run build (前端) 和 python -m pytest (后端)"
echo "3. 提交更改: git add -A && git commit -m 'chore: 清理未使用的文件'"
echo ""


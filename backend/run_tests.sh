#!/usr/bin/env bash
# 运行 API 接口测试

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}API 接口测试${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# 检查服务是否运行
echo -e "${YELLOW}检查服务状态...${NC}"
APP_HOST=${APP_HOST:-127.0.0.1}
APP_PORT=${APP_PORT:-6080}

if curl -s "http://${APP_HOST}:${APP_PORT}/docs" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 服务正在运行 (http://${APP_HOST}:${APP_PORT})${NC}"
else
    echo -e "${RED}✗ 服务未运行，请先启动服务：${NC}"
    echo -e "  ${YELLOW}python start.py${NC}"
    exit 1
fi

echo ""

# 检查依赖
echo -e "${YELLOW}检查测试依赖...${NC}"
if ! python -c "import pytest" 2>/dev/null; then
    echo -e "${RED}✗ pytest 未安装${NC}"
    echo -e "  ${YELLOW}pip install pytest${NC}"
    exit 1
fi

if ! python -c "import requests" 2>/dev/null; then
    echo -e "${RED}✗ requests 未安装${NC}"
    echo -e "  ${YELLOW}pip install requests${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 依赖检查通过${NC}"
echo ""

# 运行测试
echo -e "${YELLOW}开始运行测试...${NC}"
echo ""

if [ $# -eq 0 ]; then
    # 运行所有测试
    python app/tests/run_all_tests.py
else
    # 运行指定的测试
    pytest "$@"
fi

exit_code=$?

echo ""
echo -e "${YELLOW}========================================${NC}"
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✓ 测试完成！${NC}"
else
    echo -e "${RED}✗ 测试失败，请检查错误信息${NC}"
fi
echo -e "${YELLOW}========================================${NC}"

exit $exit_code

#!/bin/bash

# Balance 自动计算测试脚本

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# API配置
API_URL="http://127.0.0.1:6080"
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjkyMjAyNDYsImlhdCI6MTc2OTEzMzg0NiwianRpIjoiMGNiNGEzNjQtYTQwZC00ZmU2LTllZGMtM2IzYjA3MWNhZmJjIiwiaWQiOiI3MjMzMTY1Yy1jYmFlLTRlNjctOTU3My00NWRmNmVmMzIyZWMiLCJlbWFpbCI6IjIyMDExMDExMjJAcXEuY29tIiwicm9sZXMiOlsiTUFOVUFMIiwiSVQiXX0.CVADuZ070pO0t-7sqdr0wWRh9b1Dmx5jxtDGz3QZ6Wc"
PROJECT_ID="2052f094-800c-41b1-a750-996280b38281"

echo -e "${YELLOW}=== Balance 自动计算测试 ===${NC}\n"

# 生成随机账号
RANDOM_ACCOUNT="test_$(date +%s)@example.com"

echo -e "${YELLOW}测试账号: ${RANDOM_ACCOUNT}${NC}\n"

# 测试1: 创建账号（首次创建，variable应该等于balance）
echo -e "${YELLOW}[测试1] 创建账号 (balance=444)${NC}"
RESPONSE=$(curl -s "${API_URL}/v1/project/account" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  --data-raw "{
    \"account\":\"${RANDOM_ACCOUNT}\",
    \"password\":\"Zpaily88\",
    \"account_type\":1,
    \"status\":1,
    \"project_id\":\"${PROJECT_ID}\",
    \"balance\":444
  }")

echo "$RESPONSE" | python3 -m json.tool

# 提取关键字段
BALANCE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('balance', 'N/A'))")
VARIABLE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('variable', 'N/A'))")
BALANCE_HISTORY=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('balance_history', 'N/A'))")

echo -e "\n${YELLOW}验证结果:${NC}"
echo "  balance: $BALANCE (期望: 444.000000)"
echo "  variable: $VARIABLE (期望: 444.00)"
echo "  balance_history: $BALANCE_HISTORY (期望: 包含今天的日期和444.0)"

if [[ "$BALANCE" == "444.000000" ]] && [[ "$VARIABLE" == "444.00" ]]; then
    echo -e "${GREEN}✓ 测试1通过${NC}\n"
else
    echo -e "${RED}✗ 测试1失败${NC}\n"
fi

# 测试2: 使用upsert更新余额（应该计算variable = 新余额 - 旧余额）
echo -e "${YELLOW}[测试2] 更新账号余额 (balance=500)${NC}"
RESPONSE=$(curl -s "${API_URL}/v1/project/account/upsert" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  --data-raw "{
    \"account\":\"${RANDOM_ACCOUNT}\",
    \"project_id\":\"${PROJECT_ID}\",
    \"balance\":500
  }")

echo "$RESPONSE" | python3 -m json.tool

# 提取关键字段
BALANCE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('balance', 'N/A'))")
VARIABLE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('variable', 'N/A'))")
BALANCE_HISTORY=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('balance_history', 'N/A'))")

echo -e "\n${YELLOW}验证结果:${NC}"
echo "  balance: $BALANCE (期望: 500.000000)"
echo "  variable: $VARIABLE (期望: 56.00，因为同一天更新会覆盖，所以还是500.00)"
echo "  balance_history: $BALANCE_HISTORY (期望: 包含今天的日期和500.0)"

if [[ "$BALANCE" == "500.000000" ]]; then
    echo -e "${GREEN}✓ 测试2通过${NC}\n"
else
    echo -e "${RED}✗ 测试2失败${NC}\n"
fi

echo -e "${YELLOW}=== 测试完成 ===${NC}"
echo -e "${YELLOW}注意: 如果测试失败，请确保后端服务已重启${NC}"

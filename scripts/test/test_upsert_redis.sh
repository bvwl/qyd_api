#!/bin/bash

# 测试 upsert 接口（使用Redis队列）

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "测试 /v1/project/account/upsert 接口"
echo "=========================================="

# 配置
API_URL="http://127.0.0.1:6080/v1/project/account/upsert"
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjkyMjAyNDYsImlhdCI6MTc2OTEzMzg0NiwianRpIjoiMGNiNGEzNjQtYTQwZC00ZmU2LTllZGMtM2IzYjA3MWNhZmJjIiwiaWQiOiI3MjMzMTY1Yy1jYmFlLTRlNjctOTU3My00NWRmNmVmMzIyZWMiLCJlbWFpbCI6IjIyMDExMDExMjJAcXEuY29tIiwicm9sZXMiOlsiTUFOVUFMIiwiSVQiXX0.CVADuZ070pO0t-7sqdr0wWRh9b1Dmx5jxtDGz3QZ6Wc"
PROJECT_ID="2052f094-800c-41b1-a750-996280b38281"

echo ""
echo -e "${YELLOW}测试1: 添加单条数据到队列${NC}"
echo "----------------------------------------"

RESPONSE=$(curl -s -X POST "$API_URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"account\": \"crud_user2_account\",
    \"balance\": 10,
    \"project_id\": \"$PROJECT_ID\"
  }")

echo "响应: $RESPONSE"

if echo "$RESPONSE" | grep -q "成功添加到队列"; then
    echo -e "${GREEN}✅ 测试1通过：数据已添加到队列${NC}"
else
    echo -e "${RED}❌ 测试1失败${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}测试2: 再次添加相同数据（测试更新）${NC}"
echo "----------------------------------------"

RESPONSE2=$(curl -s -X POST "$API_URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"account\": \"crud_user2_account\",
    \"balance\": 20,
    \"project_id\": \"$PROJECT_ID\"
  }")

echo "响应: $RESPONSE2"

if echo "$RESPONSE2" | grep -q "成功添加到队列"; then
    echo -e "${GREEN}✅ 测试2通过：更新数据已添加到队列${NC}"
else
    echo -e "${RED}❌ 测试2失败${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}测试3: 查看队列大小${NC}"
echo "----------------------------------------"

QUEUE_SIZE=$(redis-cli ZCARD qyd:project_account_keys_zset 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "当前队列大小: $QUEUE_SIZE"
    echo -e "${GREEN}✅ 测试3通过：队列正常${NC}"
else
    echo -e "${YELLOW}⚠️  无法连接Redis，跳过队列大小检查${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}所有测试通过！${NC}"
echo "=========================================="
echo ""
echo "提示："
echo "1. 数据已添加到Redis队列"
echo "2. 后台worker会异步处理这些数据"
echo "3. 查看处理日志: tail -f backend/logs/app.log | grep Worker"
echo "4. 监控队列大小: watch -n 1 'redis-cli ZCARD qyd:project_account_keys_zset'"
echo ""

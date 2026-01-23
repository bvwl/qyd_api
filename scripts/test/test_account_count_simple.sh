#!/bin/bash

# 简单测试账号数量

BASE_URL="http://localhost:8000"

echo "请输入用户名和密码进行测试"
read -p "用户名: " USERNAME
read -sp "密码: " PASSWORD
echo ""
echo ""

# 登录
echo "正在登录..."
LOGIN_RES=$(curl -s -X POST "${BASE_URL}/v1/user/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

TOKEN=$(echo "$LOGIN_RES" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ 登录失败"
  exit 1
fi

echo "✅ 登录成功"
echo ""

# 获取项目列表
echo "=========================================="
echo "1. 获取项目列表"
echo "=========================================="
PROJECTS=$(curl -s -X GET "${BASE_URL}/v1/project?page=1&limit=100&res_count=true" \
  -H "Authorization: Bearer $TOKEN")

echo "$PROJECTS" | python3 -m json.tool
echo ""

# 获取所有账号（不带过滤）
echo "=========================================="
echo "2. 获取所有账号（不带project_id过滤）"
echo "=========================================="
ALL_ACCOUNTS=$(curl -s -X GET "${BASE_URL}/v1/project/account?page=1&limit=100&res_count=true" \
  -H "Authorization: Bearer $TOKEN")

echo "$ALL_ACCOUNTS" | python3 -m json.tool
echo ""

# 提取项目ID并逐个查询
echo "=========================================="
echo "3. 逐个项目查询账号"
echo "=========================================="

PROJECT_IDS=$(echo "$PROJECTS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    items = data.get('items', [])
    for item in items:
        print(item['id'])
except:
    pass
" 2>/dev/null)

TOTAL=0
for PID in $PROJECT_IDS; do
  echo "项目 ID: $PID"
  ACCOUNTS=$(curl -s -X GET "${BASE_URL}/v1/project/account?project_id=$PID&page=1&limit=100&res_count=true" \
    -H "Authorization: Bearer $TOKEN")
  
  COUNT=$(echo "$ACCOUNTS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
  NUM=$(echo "$ACCOUNTS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('num', 0))" 2>/dev/null)
  
  echo "  count: $COUNT, num: $NUM"
  echo "$ACCOUNTS" | python3 -m json.tool | head -30
  echo ""
  
  TOTAL=$((TOTAL + NUM))
done

echo "=========================================="
echo "总结"
echo "=========================================="
echo "按项目累加的账号数: $TOTAL"

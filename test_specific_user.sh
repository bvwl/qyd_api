#!/bin/bash

# 测试特定用户的账号数量

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "测试用户 2201101122@qq.com 的账号数量"
echo "=========================================="
echo ""

# 登录
echo "正在登录..."
LOGIN_RES=$(curl -s -X POST "${BASE_URL}/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"2201101122@qq.com","password":"123456"}')

TOKEN=$(echo "$LOGIN_RES" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ 登录失败，尝试其他密码..."
  LOGIN_RES=$(curl -s -X POST "${BASE_URL}/v1/user/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"2201101122@qq.com","password":"admin123"}')
  
  TOKEN=$(echo "$LOGIN_RES" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)
  
  if [ -z "$TOKEN" ]; then
    echo "❌ 登录失败"
    echo "$LOGIN_RES"
    exit 1
  fi
fi

echo "✅ 登录成功"
echo ""

# 获取用户信息
echo "=========================================="
echo "1. 用户信息"
echo "=========================================="
USER_INFO=$(curl -s -X GET "${BASE_URL}/v1/user/info" \
  -H "Authorization: Bearer $TOKEN")

echo "$USER_INFO" | python3 -m json.tool
echo ""

# 获取项目列表
echo "=========================================="
echo "2. 用户的项目列表"
echo "=========================================="
PROJECTS=$(curl -s -X GET "${BASE_URL}/v1/project?page=1&limit=100&res_count=true" \
  -H "Authorization: Bearer $TOKEN")

echo "$PROJECTS" | python3 -m json.tool
echo ""

PROJECT_COUNT=$(echo "$PROJECTS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
echo "项目数量: $PROJECT_COUNT"
echo ""

# 获取所有账号
echo "=========================================="
echo "3. 获取所有账号（不带project_id过滤）"
echo "=========================================="
ALL_ACCOUNTS=$(curl -s -X GET "${BASE_URL}/v1/project/account?page=1&limit=100&res_count=true" \
  -H "Authorization: Bearer $TOKEN")

echo "$ALL_ACCOUNTS" | python3 -m json.tool
echo ""

ACCOUNT_COUNT=$(echo "$ALL_ACCOUNTS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
ACCOUNT_NUM=$(echo "$ALL_ACCOUNTS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('num', 0))" 2>/dev/null)
echo "账号数量 (count): $ACCOUNT_COUNT"
echo "账号数量 (num): $ACCOUNT_NUM"
echo ""

# 逐个项目查询
echo "=========================================="
echo "4. 逐个项目查询账号"
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
  PROJECT_NAME=$(echo "$PROJECTS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    items = data.get('items', [])
    for item in items:
        if item['id'] == '$PID':
            print(item['name'])
            break
except:
    pass
" 2>/dev/null)
  
  echo "项目: $PROJECT_NAME (ID: $PID)"
  ACCOUNTS=$(curl -s -X GET "${BASE_URL}/v1/project/account?project_id=$PID&page=1&limit=100&res_count=true" \
    -H "Authorization: Bearer $TOKEN")
  
  COUNT=$(echo "$ACCOUNTS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
  NUM=$(echo "$ACCOUNTS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('num', 0))" 2>/dev/null)
  
  echo "  count: $COUNT, num: $NUM"
  
  if [ "$NUM" -gt 0 ]; then
    echo "  账号列表:"
    echo "$ACCOUNTS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    items = data.get('items', [])
    for item in items:
        print(f\"    - {item['account']}\")
except:
    pass
" 2>/dev/null
  fi
  
  echo ""
  TOTAL=$((TOTAL + NUM))
done

echo "=========================================="
echo "总结"
echo "=========================================="
echo "用户关联的项目数: $PROJECT_COUNT"
echo "直接查询的账号数: $ACCOUNT_COUNT (count) / $ACCOUNT_NUM (num)"
echo "按项目累加的账号数: $TOTAL"
echo ""

if [ "$ACCOUNT_NUM" != "$TOTAL" ]; then
  echo "⚠️  发现不一致！"
  echo "差异: $ACCOUNT_NUM - $TOTAL = $((ACCOUNT_NUM - TOTAL))"
else
  echo "✅ 数据一致"
fi

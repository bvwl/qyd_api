#!/bin/bash

# 调试账号数量问题

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "调试账号数量问题"
echo "=========================================="
echo ""

# 1. 登录获取Token
echo "步骤 1: 登录用户"
echo "----------------------------------------"

read -p "请输入用户名: " USERNAME
read -sp "请输入密码: " PASSWORD
echo ""

LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/v1/user/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME\",
    \"password\": \"$PASSWORD\"
  }")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ 登录失败"
  echo "响应: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ 登录成功"
echo ""

# 2. 获取用户信息
echo "步骤 2: 获取用户信息"
echo "----------------------------------------"

USER_INFO=$(curl -s -X GET "${BASE_URL}/v1/user/info" \
  -H "Authorization: Bearer $TOKEN")

echo "用户信息:"
echo "$USER_INFO" | python3 -m json.tool 2>/dev/null || echo "$USER_INFO"
echo ""

# 3. 获取用户的项目列表
echo "步骤 3: 获取用户的项目列表"
echo "----------------------------------------"

PROJECTS=$(curl -s -X GET "${BASE_URL}/v1/project?page=1&limit=100&res_count=true" \
  -H "Authorization: Bearer $TOKEN")

echo "项目列表:"
echo "$PROJECTS" | python3 -m json.tool 2>/dev/null || echo "$PROJECTS"
echo ""

PROJECT_COUNT=$(echo $PROJECTS | grep -o '"count":[0-9]*' | head -1 | cut -d':' -f2)
echo "项目总数: $PROJECT_COUNT"
echo ""

# 4. 获取所有账号（不带project_id过滤）
echo "步骤 4: 获取所有账号（不带project_id过滤）"
echo "----------------------------------------"

ALL_ACCOUNTS=$(curl -s -X GET "${BASE_URL}/v1/project/account?page=1&limit=100&res_count=true" \
  -H "Authorization: Bearer $TOKEN")

echo "所有账号:"
echo "$ALL_ACCOUNTS" | python3 -m json.tool 2>/dev/null || echo "$ALL_ACCOUNTS"
echo ""

TOTAL_ACCOUNT_COUNT=$(echo $ALL_ACCOUNTS | grep -o '"count":[0-9]*' | head -1 | cut -d':' -f2)
ACTUAL_ACCOUNT_COUNT=$(echo $ALL_ACCOUNTS | grep -o '"num":[0-9]*' | cut -d':' -f2)
echo "账号总数 (count): $TOTAL_ACCOUNT_COUNT"
echo "实际返回数量 (num): $ACTUAL_ACCOUNT_COUNT"
echo ""

# 5. 逐个项目查询账号数量
echo "步骤 5: 逐个项目查询账号数量"
echo "----------------------------------------"

# 提取项目ID列表
PROJECT_IDS=$(echo "$PROJECTS" | grep -o '"id":"[^"]*' | cut -d'"' -f4)

TOTAL_BY_PROJECT=0
for PROJECT_ID in $PROJECT_IDS; do
  echo "查询项目 $PROJECT_ID 的账号..."
  
  PROJECT_ACCOUNTS=$(curl -s -X GET "${BASE_URL}/v1/project/account?project_id=$PROJECT_ID&page=1&limit=100&res_count=true" \
    -H "Authorization: Bearer $TOKEN")
  
  COUNT=$(echo $PROJECT_ACCOUNTS | grep -o '"count":[0-9]*' | head -1 | cut -d':' -f2)
  NUM=$(echo $PROJECT_ACCOUNTS | grep -o '"num":[0-9]*' | cut -d':' -f2)
  
  echo "  - count: $COUNT, num: $NUM"
  
  if [ -n "$NUM" ]; then
    TOTAL_BY_PROJECT=$((TOTAL_BY_PROJECT + NUM))
  fi
done

echo ""
echo "按项目累加的账号总数: $TOTAL_BY_PROJECT"
echo ""

# 6. 总结
echo "=========================================="
echo "总结"
echo "=========================================="
echo "项目数量: $PROJECT_COUNT"
echo "直接查询的账号总数: $TOTAL_ACCOUNT_COUNT (count) / $ACTUAL_ACCOUNT_COUNT (num)"
echo "按项目累加的账号数: $TOTAL_BY_PROJECT"
echo ""

if [ "$ACTUAL_ACCOUNT_COUNT" != "$TOTAL_BY_PROJECT" ]; then
  echo "⚠️  发现不一致！"
  echo "可能的原因："
  echo "  1. 有账号没有关联项目"
  echo "  2. 数据权限过滤逻辑有问题"
  echo "  3. 有重复计数"
else
  echo "✅ 数据一致"
fi

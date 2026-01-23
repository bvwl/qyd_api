#!/bin/bash

# 测试权限管理API
# 需要先登录获取token

BASE_URL="http://127.0.0.1:6080"
TOKEN=""

echo "=========================================="
echo "测试权限管理API"
echo "=========================================="

# 1. 登录获取token
echo -e "\n1. 登录获取token..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/v1/user/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhiyu",
    "password": "2201101122@qq.com"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ 登录失败"
  echo "响应: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ 登录成功"
echo "Token: ${TOKEN:0:50}..."

# 2. 获取角色列表
echo -e "\n2. 获取角色列表..."
ROLES_RESPONSE=$(curl -s -X GET "${BASE_URL}/v1/user/role?page=1&limit=100" \
  -H "Authorization: Bearer $TOKEN")

echo "$ROLES_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$ROLES_RESPONSE"

# 提取第一个角色ID
ROLE_ID=$(echo $ROLES_RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -z "$ROLE_ID" ]; then
  echo "❌ 未找到角色"
  exit 1
fi

echo -e "\n测试角色ID: $ROLE_ID"

# 3. 获取路由树
echo -e "\n3. 获取路由树..."
TREE_RESPONSE=$(curl -s -X GET "${BASE_URL}/v1/user/route/tree?status=1" \
  -H "Authorization: Bearer $TOKEN")

echo "$TREE_RESPONSE" | python3 -m json.tool 2>/dev/null | head -50 || echo "$TREE_RESPONSE" | head -50

# 提取前3个路由ID
ROUTE_IDS=$(echo $TREE_RESPONSE | grep -o '"id":"[^"]*"' | head -3 | cut -d'"' -f4 | tr '\n' ',' | sed 's/,$//')

echo -e "\n测试路由IDs: $ROUTE_IDS"

# 4. 获取角色的路由权限
echo -e "\n4. 获取角色的路由权限..."
ROLE_ROUTES_RESPONSE=$(curl -s -X GET "${BASE_URL}/v1/user/role/${ROLE_ID}/routes" \
  -H "Authorization: Bearer $TOKEN")

echo "$ROLE_ROUTES_RESPONSE" | python3 -m json.tool 2>/dev/null | head -50 || echo "$ROLE_ROUTES_RESPONSE" | head -50

# 5. 设置角色的路由权限
echo -e "\n5. 设置角色的路由权限..."

# 构建路由ID数组
IFS=',' read -ra ROUTE_ID_ARRAY <<< "$ROUTE_IDS"
ROUTE_JSON="["
for id in "${ROUTE_ID_ARRAY[@]}"; do
  ROUTE_JSON="${ROUTE_JSON}\"${id}\","
done
ROUTE_JSON="${ROUTE_JSON%,}]"

echo "设置的路由IDs: $ROUTE_JSON"

SET_ROUTES_RESPONSE=$(curl -s -X POST "${BASE_URL}/v1/user/role/${ROLE_ID}/routes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$ROUTE_JSON")

echo "$SET_ROUTES_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$SET_ROUTES_RESPONSE"

# 6. 再次获取角色的路由权限验证
echo -e "\n6. 验证设置结果..."
VERIFY_RESPONSE=$(curl -s -X GET "${BASE_URL}/v1/user/role/${ROLE_ID}/routes" \
  -H "Authorization: Bearer $TOKEN")

echo "$VERIFY_RESPONSE" | python3 -m json.tool 2>/dev/null | head -30 || echo "$VERIFY_RESPONSE" | head -30

echo -e "\n=========================================="
echo "✅ 测试完成"
echo "=========================================="

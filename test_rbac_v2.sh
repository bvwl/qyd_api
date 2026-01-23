#!/bin/bash

# RBAC v2 API 测试脚本

BASE_URL="http://localhost:6080/v1"
TOKEN=""

echo "=========================================="
echo "RBAC v2 API 测试"
echo "=========================================="
echo ""

# 1. 登录获取 Token
echo "1. 登录获取 Token..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhiyu",
    "password": "2201101122@qq.com"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ 登录失败"
  echo "$LOGIN_RESPONSE"
  exit 1
fi

echo "✓ 登录成功"
echo "Token: ${TOKEN:0:50}..."
echo ""

# 2. 获取当前用户的菜单
echo "2. 获取当前用户的菜单..."
MENUS_RESPONSE=$(curl -s -X GET "${BASE_URL}/rbac/user/menus" \
  -H "Authorization: Bearer $TOKEN")

echo "$MENUS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$MENUS_RESPONSE"
echo ""

# 3. 获取当前用户的权限
echo "3. 获取当前用户的权限..."
PERMISSIONS_RESPONSE=$(curl -s -X GET "${BASE_URL}/rbac/user/permissions" \
  -H "Authorization: Bearer $TOKEN")

echo "$PERMISSIONS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$PERMISSIONS_RESPONSE"
echo ""

# 4. 检查是否有指定权限
echo "4. 检查是否有 'user:create' 权限..."
HAS_PERM_RESPONSE=$(curl -s -X GET "${BASE_URL}/rbac/user/has-permission?code=user:create" \
  -H "Authorization: Bearer $TOKEN")

echo "$HAS_PERM_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HAS_PERM_RESPONSE"
echo ""

# 5. 获取菜单树
echo "5. 获取完整菜单树..."
MENU_TREE_RESPONSE=$(curl -s -X GET "${BASE_URL}/rbac/menu/tree" \
  -H "Authorization: Bearer $TOKEN")

echo "$MENU_TREE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$MENU_TREE_RESPONSE"
echo ""

# 6. 获取菜单列表（分页）
echo "6. 获取菜单列表（第1页，每页10条）..."
MENU_LIST_RESPONSE=$(curl -s -X GET "${BASE_URL}/rbac/menu?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN")

echo "$MENU_LIST_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$MENU_LIST_RESPONSE"
echo ""

echo "=========================================="
echo "✓ 测试完成"
echo "=========================================="

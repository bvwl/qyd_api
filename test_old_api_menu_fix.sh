#!/bin/bash

# 测试旧 API 的菜单设置（修复父级菜单丢失问题）

BASE_URL="http://localhost:6080/v1"
TOKEN=""

echo "=========================================="
echo "测试旧 API 角色路由设置"
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
  exit 1
fi

echo "✓ 登录成功"
echo ""

# 2. 获取 GM 角色
echo "2. 获取 GM 角色..."
ROLES_RESPONSE=$(curl -s -X GET "${BASE_URL}/user/role?code=GM" \
  -H "Authorization: Bearer $TOKEN")

GM_ROLE_ID=$(echo $ROLES_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['items'][0]['id'])" 2>/dev/null)

if [ -z "$GM_ROLE_ID" ]; then
  echo "❌ 获取 GM 角色失败"
  exit 1
fi

echo "✓ GM 角色 ID: $GM_ROLE_ID"
echo ""

# 3. 获取所有路由
echo "3. 获取所有路由..."
ROUTES_RESPONSE=$(curl -s -X GET "${BASE_URL}/user/route/tree" \
  -H "Authorization: Bearer $TOKEN")

echo "路由树结构："
echo "$ROUTES_RESPONSE" | python3 -m json.tool 2>/dev/null | head -80
echo ""

# 4. 获取当前角色的路由
echo "4. 获取 GM 角色当前的路由..."
CURRENT_ROUTES=$(curl -s -X GET "${BASE_URL}/user/role/${GM_ROLE_ID}/routes" \
  -H "Authorization: Bearer $TOKEN")

CURRENT_COUNT=$(echo $CURRENT_ROUTES | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data))" 2>/dev/null)
echo "当前路由数量: $CURRENT_COUNT"
echo ""

# 5. 提取一个二级菜单的ID（用于测试）
echo "5. 提取测试用的菜单ID..."

# 获取"用户列表"的ID
USER_LIST_ID=$(echo $ROUTES_RESPONSE | python3 -c "
import sys, json
data = json.load(sys.stdin)
def find_route(routes, name):
    for route in routes:
        if route.get('name') == name:
            return route['id']
        if 'children' in route:
            result = find_route(route['children'], name)
            if result:
                return result
    return None
print(find_route(data, 'UserList'))
" 2>/dev/null)

if [ -z "$USER_LIST_ID" ]; then
  echo "❌ 获取用户列表路由ID失败"
  exit 1
fi

echo "用户列表路由 ID: $USER_LIST_ID"
echo ""

# 6. 设置角色路由（只传递一个二级菜单）
echo "6. 设置角色路由（只选择用户列表）..."
echo "   模拟场景：只选择'用户列表'，不选择'角色管理'"
echo ""

SET_ROUTES_RESPONSE=$(curl -s -X POST "${BASE_URL}/user/role/${GM_ROLE_ID}/routes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "[\"$USER_LIST_ID\"]")

echo "设置响应："
echo "$SET_ROUTES_RESPONSE" | python3 -m json.tool 2>/dev/null
echo ""

# 7. 验证：获取设置后的路由
echo "7. 验证：获取设置后的路由..."
UPDATED_ROUTES=$(curl -s -X GET "${BASE_URL}/user/role/${GM_ROLE_ID}/routes" \
  -H "Authorization: Bearer $TOKEN")

UPDATED_COUNT=$(echo $UPDATED_ROUTES | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data))" 2>/dev/null)

echo "更新后的路由树："
echo "$UPDATED_ROUTES" | python3 -m json.tool 2>/dev/null | head -50
echo ""

# 8. 检查父级菜单是否存在
echo "=========================================="
echo "测试结果："
echo "  - 前端传递: 1 个节点（用户列表）"
echo "  - 保存后: $UPDATED_COUNT 个节点"
echo ""

if [ "$UPDATED_COUNT" -ge 2 ]; then
  echo "✓ 测试通过！"
  echo "  父级菜单（用户管理）已自动补全"
else
  echo "❌ 测试失败！"
  echo "  父级菜单可能丢失"
fi
echo "=========================================="

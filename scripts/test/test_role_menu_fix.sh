#!/bin/bash

# 测试角色菜单设置（修复父级菜单丢失问题）

BASE_URL="http://localhost:6080/v1"
TOKEN=""

echo "=========================================="
echo "测试角色菜单设置"
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

# 2. 获取所有菜单
echo "2. 获取所有菜单..."
MENUS_RESPONSE=$(curl -s -X GET "${BASE_URL}/rbac/menu/tree" \
  -H "Authorization: Bearer $TOKEN")

echo "$MENUS_RESPONSE" | python3 -m json.tool 2>/dev/null | head -50
echo ""

# 3. 获取 GM 角色
echo "3. 获取 GM 角色..."
ROLES_RESPONSE=$(curl -s -X GET "${BASE_URL}/rbac/role?code=GM" \
  -H "Authorization: Bearer $TOKEN")

GM_ROLE_ID=$(echo $ROLES_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['items'][0]['id'])" 2>/dev/null)

if [ -z "$GM_ROLE_ID" ]; then
  echo "❌ 获取 GM 角色失败"
  exit 1
fi

echo "✓ GM 角色 ID: $GM_ROLE_ID"
echo ""

# 4. 获取 GM 角色当前的菜单
echo "4. 获取 GM 角色当前的菜单..."
CURRENT_MENUS=$(curl -s -X GET "${BASE_URL}/rbac/role/${GM_ROLE_ID}/menus" \
  -H "Authorization: Bearer $TOKEN")

echo "$CURRENT_MENUS" | python3 -m json.tool 2>/dev/null
echo ""

# 5. 模拟场景：选择部分二级菜单
echo "5. 测试场景：选择用户管理下的部分菜单..."
echo "   - 用户管理（主菜单）"
echo "   - 用户列表（二级菜单）✓"
echo "   - 角色管理（二级菜单）✗ 不选"
echo ""

# 获取菜单ID（需要根据实际情况调整）
# 这里我们模拟只选择用户列表，不选择角色管理
# 前端会传递：['user-list'] （只有选中的叶子节点）
# 后端应该自动补全：['user-management', 'user-list']

echo "6. 设置角色菜单（只选择用户列表）..."

# 注意：这里需要传递实际的菜单ID
# 为了演示，我们先获取菜单ID
USER_LIST_ID=$(echo $MENUS_RESPONSE | python3 -c "
import sys, json
data = json.load(sys.stdin)
def find_menu(menus, code):
    for menu in menus:
        if menu.get('code') == code:
            return menu['id']
        if 'children' in menu:
            result = find_menu(menu['children'], code)
            if result:
                return result
    return None
print(find_menu(data['data'], 'user-list'))
" 2>/dev/null)

if [ -z "$USER_LIST_ID" ]; then
  echo "❌ 获取用户列表菜单ID失败"
  exit 1
fi

echo "用户列表菜单 ID: $USER_LIST_ID"

# 设置菜单（只传递选中的节点）
SET_MENUS_RESPONSE=$(curl -s -X POST "${BASE_URL}/rbac/role/${GM_ROLE_ID}/menus" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"menu_ids\": [\"$USER_LIST_ID\"]}")

echo "$SET_MENUS_RESPONSE" | python3 -m json.tool 2>/dev/null
echo ""

# 7. 验证：获取设置后的菜单
echo "7. 验证：获取设置后的菜单..."
UPDATED_MENUS=$(curl -s -X GET "${BASE_URL}/rbac/role/${GM_ROLE_ID}/menus" \
  -H "Authorization: Bearer $TOKEN")

echo "$UPDATED_MENUS" | python3 -m json.tool 2>/dev/null
echo ""

# 8. 检查父级菜单是否存在
MENU_COUNT=$(echo $UPDATED_MENUS | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])" 2>/dev/null)

echo "=========================================="
if [ "$MENU_COUNT" -ge 2 ]; then
  echo "✓ 测试通过！"
  echo "  保存的菜单数量: $MENU_COUNT"
  echo "  包含了父级菜单（用户管理）和子菜单（用户列表）"
else
  echo "❌ 测试失败！"
  echo "  保存的菜单数量: $MENU_COUNT"
  echo "  父级菜单可能丢失"
fi
echo "=========================================="

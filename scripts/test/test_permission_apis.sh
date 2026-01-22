#!/bin/bash

# 测试权限管理相关API

echo "=========================================="
echo "测试权限管理API"
echo "=========================================="
echo ""

# 1. 登录获取token
echo "1. 登录获取token..."
LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:6080/v1/user/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"zhiyu","password":"2201101122@qq.com"}')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ 登录失败"
    echo $LOGIN_RESPONSE | python3 -m json.tool
    exit 1
fi

echo "✅ 登录成功"
echo ""

# 2. 测试获取路由树
echo "2. 测试获取路由树 (GET /v1/user/route/tree)..."
TREE_RESPONSE=$(curl -s "http://127.0.0.1:6080/v1/user/route/tree?status=1" \
  -H "Authorization: Bearer $TOKEN")

if echo $TREE_RESPONSE | grep -q '"id"'; then
    echo "✅ 路由树获取成功"
    echo "   路由数量: $(echo $TREE_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")"
else
    echo "❌ 路由树获取失败"
    echo $TREE_RESPONSE | python3 -m json.tool
fi
echo ""

# 3. 测试获取角色列表
echo "3. 测试获取角色列表 (GET /v1/user/role)..."
ROLE_RESPONSE=$(curl -s "http://127.0.0.1:6080/v1/user/role?page=1&limit=100" \
  -H "Authorization: Bearer $TOKEN")

if echo $ROLE_RESPONSE | grep -q '"items"'; then
    echo "✅ 角色列表获取成功"
    echo "   角色数量: $(echo $ROLE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['num'])")"
else
    echo "❌ 角色列表获取失败"
    echo $ROLE_RESPONSE | python3 -m json.tool
fi
echo ""

# 4. 获取ADMIN角色ID
ADMIN_ROLE_ID=$(echo $ROLE_RESPONSE | python3 -c "import sys, json; data = json.load(sys.stdin); print([r['id'] for r in data['items'] if r['code'] == 'ADMIN'][0])")

# 5. 测试获取角色的路由权限
echo "4. 测试获取角色的路由权限 (GET /v1/user/role/{id}/routes)..."
ROLE_ROUTES_RESPONSE=$(curl -s "http://127.0.0.1:6080/v1/user/role/$ADMIN_ROLE_ID/routes" \
  -H "Authorization: Bearer $TOKEN")

if echo $ROLE_ROUTES_RESPONSE | grep -q '"id"'; then
    echo "✅ 角色路由权限获取成功"
    echo "   ADMIN角色路由数量: $(echo $ROLE_ROUTES_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")"
else
    echo "❌ 角色路由权限获取失败"
    echo $ROLE_ROUTES_RESPONSE | python3 -m json.tool
fi
echo ""

# 6. 测试获取当前用户的路由权限
echo "5. 测试获取当前用户的路由权限 (GET /v1/user/route/user-routes)..."
USER_ROUTES_RESPONSE=$(curl -s "http://127.0.0.1:6080/v1/user/route/user-routes" \
  -H "Authorization: Bearer $TOKEN")

if echo $USER_ROUTES_RESPONSE | grep -q '"id"'; then
    echo "✅ 用户路由权限获取成功"
    echo "   当前用户路由数量: $(echo $USER_ROUTES_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")"
else
    echo "❌ 用户路由权限获取失败"
    echo $USER_ROUTES_RESPONSE | python3 -m json.tool
fi
echo ""

# 7. 测试路由列表API
echo "6. 测试路由列表API (GET /v1/user/route)..."
ROUTE_LIST_RESPONSE=$(curl -s "http://127.0.0.1:6080/v1/user/route?page=1&limit=5&res_count=true" \
  -H "Authorization: Bearer $TOKEN")

if echo $ROUTE_LIST_RESPONSE | grep -q '"items"'; then
    echo "✅ 路由列表获取成功"
    echo "   总数: $(echo $ROUTE_LIST_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])")"
    echo "   当前页数量: $(echo $ROUTE_LIST_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['num'])")"
else
    echo "❌ 路由列表获取失败"
    echo $ROUTE_LIST_RESPONSE | python3 -m json.tool
fi
echo ""

echo "=========================================="
echo "测试完成！"
echo "=========================================="
echo ""
echo "前端权限管理页面地址: http://localhost:3000/user/permission"
echo "请使用以下账号登录测试:"
echo "  邮箱: zhiyu"
echo "  密码: 2201101122@qq.com"

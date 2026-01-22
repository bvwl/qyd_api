#!/bin/bash

echo "测试权限管理API端点"
echo "================================"
echo ""

# 测试角色列表（不需要认证）
echo "1. 测试角色列表 API"
echo "GET http://127.0.0.1:6080/v1/user/role?page=1&limit=10"
curl -s "http://127.0.0.1:6080/v1/user/role?page=1&limit=10" | python3 -m json.tool
echo ""
echo ""

# 测试路由树（需要认证）
echo "2. 测试路由树 API（需要认证）"
echo "GET http://127.0.0.1:6080/v1/user/route/tree?status=1"
echo "注意：此API需要JWT token"
echo ""

# 获取token（需要先登录）
echo "3. 获取登录token"
echo "POST http://127.0.0.1:6080/v1/user/auth/login"
TOKEN=$(curl -s -X POST "http://127.0.0.1:6080/v1/user/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"zhiyu","password":"zhiyu666"}' | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")

if [ -n "$TOKEN" ]; then
  echo "✓ 登录成功，获取到token"
  echo ""
  
  # 使用token测试路由树
  echo "4. 使用token测试路由树 API"
  curl -s "http://127.0.0.1:6080/v1/user/route/tree?status=1" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -50
  echo ""
  echo ""
  
  # 测试角色路由
  echo "5. 测试角色路由 API"
  ROLE_ID=$(curl -s "http://127.0.0.1:6080/v1/user/role?page=1&limit=1" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['items'][0]['id'] if data.get('items') else '')")
  
  if [ -n "$ROLE_ID" ]; then
    echo "角色ID: $ROLE_ID"
    curl -s "http://127.0.0.1:6080/v1/user/role/$ROLE_ID/routes" \
      -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -30
  fi
else
  echo "✗ 登录失败，无法获取token"
fi

echo ""
echo "================================"
echo "测试完成"

#!/bin/bash

# 测试服务器密码 AES 加密和 Proxy URL 功能

echo "=========================================="
echo "测试服务器密码 AES 加密和 Proxy URL 功能"
echo "=========================================="
echo ""

# 管理员 Token
ADMIN_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjkzNDg1NTEsImlhdCI6MTc2OTI2MjE1MSwianRpIjoiYjEzNTA5N2YtYmQ2MC00ZTAwLTg0MTQtYzNhYTIxYjVhZWNmIiwiaWQiOiI3OTE0Y2JhYy04ZmY5LTRiMTAtOTg1NC04MGZjMTY2N2EzMzkiLCJlbWFpbCI6InpoaXl1Iiwicm9sZXMiOlsiQURNSU4iXX0.sCbtJeAwr-zIDPyAbfvkTLuaQYg35WzY46Zqy7I-Hh4"

# 普通用户 Token
USER_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjkzNDU2NTAsImlhdCI6MTc2OTI1OTI1MCwianRpIjoiYTUxY2E0ZDktZDRlOS00NTIzLTg4OTEtMGM2NjczZTk2MjY5IiwiaWQiOiI3MjMzMTY1Yy1jYmFlLTRlNjctOTU3My00NWRmNmVmMzIyZWMiLCJlbWFpbCI6IjIyMDExMDExMjJAcXEuY29tIiwicm9sZXMiOlsiTUFOVUFMIiwiSVQiXX0.Isc5uatd1bCpgWMSGrZARjPouU6s4d2FGkK9PYNiQzs"

BASE_URL="http://127.0.0.1:6080"

echo "1. 测试创建服务器（密码应该被加密）"
echo "----------------------------------------"
CREATE_RESPONSE=$(curl -s -X POST "${BASE_URL}/v1/server/info" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "test.server.com",
    "ssh_port": 22,
    "password": "MyPlainPassword123",
    "domain": "test.domain.com",
    "port": 30001,
    "group_id": "9e9250f0-e9df-4efb-924c-243e1130085e",
    "status": 1,
    "is_sale": 1
  }')

echo "$CREATE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$CREATE_RESPONSE"
SERVER_ID=$(echo "$CREATE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
echo ""
echo "创建的服务器ID: $SERVER_ID"
echo ""

if [ -z "$SERVER_ID" ]; then
  echo "❌ 创建服务器失败"
  exit 1
fi

echo "2. 测试管理员查询服务器（应该返回解密后的密码）"
echo "----------------------------------------"
ADMIN_GET_RESPONSE=$(curl -s -X GET "${BASE_URL}/v1/server/info/${SERVER_ID}" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}")

echo "$ADMIN_GET_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$ADMIN_GET_RESPONSE"
ADMIN_PASSWORD=$(echo "$ADMIN_GET_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('password', ''))" 2>/dev/null)
echo ""
echo "管理员看到的密码: $ADMIN_PASSWORD"
echo ""

if [ "$ADMIN_PASSWORD" = "MyPlainPassword123" ]; then
  echo "✅ 管理员可以看到解密后的密码"
else
  echo "❌ 管理员密码解密失败"
fi
echo ""

echo "3. 测试普通用户查询服务器（应该返回加密后的密码）"
echo "----------------------------------------"
USER_GET_RESPONSE=$(curl -s -X GET "${BASE_URL}/v1/server/info/${SERVER_ID}" \
  -H "Authorization: Bearer ${USER_TOKEN}")

echo "$USER_GET_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$USER_GET_RESPONSE"
USER_PASSWORD=$(echo "$USER_GET_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('password', ''))" 2>/dev/null)
echo ""
echo "普通用户看到的密码: $USER_PASSWORD"
echo ""

if [ "$USER_PASSWORD" != "MyPlainPassword123" ] && [ -n "$USER_PASSWORD" ]; then
  echo "✅ 普通用户看到的是加密后的密码"
else
  echo "❌ 普通用户密码加密失败"
fi
echo ""

echo "4. 测试 Proxy URL（应该包含用户自己的服务器账号）"
echo "----------------------------------------"
ADMIN_PROXY_URL=$(echo "$ADMIN_GET_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('proxy_url', ''))" 2>/dev/null)
USER_PROXY_URL=$(echo "$USER_GET_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('proxy_url', ''))" 2>/dev/null)

echo "管理员的 Proxy URL: $ADMIN_PROXY_URL"
echo "普通用户的 Proxy URL: $USER_PROXY_URL"
echo ""

if [[ "$ADMIN_PROXY_URL" == socks5://* ]]; then
  echo "✅ Proxy URL 格式正确"
else
  echo "❌ Proxy URL 格式错误"
fi
echo ""

echo "5. 测试更新服务器密码（应该重新加密）"
echo "----------------------------------------"
UPDATE_RESPONSE=$(curl -s -X PUT "${BASE_URL}/v1/server/info/${SERVER_ID}" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "NewPassword456"
  }')

echo "$UPDATE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$UPDATE_RESPONSE"
UPDATED_PASSWORD=$(echo "$UPDATE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('password', ''))" 2>/dev/null)
echo ""
echo "更新后管理员看到的密码: $UPDATED_PASSWORD"
echo ""

if [ "$UPDATED_PASSWORD" = "NewPassword456" ]; then
  echo "✅ 密码更新成功，管理员可以看到新密码"
else
  echo "❌ 密码更新失败"
fi
echo ""

echo "6. 测试查询服务器列表（管理员）"
echo "----------------------------------------"
LIST_RESPONSE=$(curl -s -X GET "${BASE_URL}/v1/server/info?host=test.server.com" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}")

echo "$LIST_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LIST_RESPONSE"
echo ""

echo "7. 清理测试数据"
echo "----------------------------------------"
DELETE_RESPONSE=$(curl -s -X DELETE "${BASE_URL}/v1/server/info/${SERVER_ID}" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}")

echo "$DELETE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$DELETE_RESPONSE"
echo ""

echo "=========================================="
echo "测试完成"
echo "=========================================="

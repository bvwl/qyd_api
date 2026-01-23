#!/bin/bash

# 测试项目账号API的JWT认证
# 使用标准的 Authorization: Bearer token 方式

BASE_URL="http://localhost:6080"

echo "=========================================="
echo "测试项目账号API - JWT认证"
echo "=========================================="
echo ""

# 1. 登录获取JWT Token
echo "1. 登录获取JWT Token..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/v1/user/login" \
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
echo ""

# 2. 测试项目钱包列表（使用JWT）
echo "2. 测试项目钱包列表（JWT认证）..."
WALLET_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/v1/project/wallet?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN")

echo "响应: $WALLET_RESPONSE" | head -c 200
echo ""
echo ""

# 3. 测试项目账号列表（使用JWT）
echo "3. 测试项目账号列表（JWT认证）..."
ACCOUNT_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/v1/project/account?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN")

echo "响应: $ACCOUNT_RESPONSE" | head -c 200
echo ""
echo ""

# 4. 测试项目余额列表（使用JWT）
echo "4. 测试项目余额列表（JWT认证）..."
BALANCE_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/v1/project/balance?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN")

echo "响应: $BALANCE_RESPONSE" | head -c 200
echo ""
echo ""

# 5. 测试项目信息列表（使用JWT）
echo "5. 测试项目信息列表（JWT认证）..."
PROJECT_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/v1/project/info?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN")

echo "响应: $PROJECT_RESPONSE" | head -c 200
echo ""
echo ""

# 6. 测试无Token访问（应该返回401）
echo "6. 测试无Token访问（应该返回401）..."
NO_AUTH_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X GET "${BASE_URL}/api/v1/project/wallet?page=1&limit=10")

HTTP_CODE=$(echo "$NO_AUTH_RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)
if [ "$HTTP_CODE" = "401" ]; then
  echo "✅ 正确返回401未授权"
else
  echo "❌ 应该返回401，实际返回: $HTTP_CODE"
fi
echo ""

echo "=========================================="
echo "测试完成"
echo "=========================================="

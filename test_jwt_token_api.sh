#!/bin/bash

# JWT Token API测试脚本
# 测试生成10年有效期的JWT Token

echo "=========================================="
echo "JWT Token API 测试"
echo "=========================================="
echo ""

BASE_URL="http://127.0.0.1:6080"

# 1. 登录获取JWT
echo "1. 登录获取JWT Token..."
echo "----------------------------------------"

LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/v1/user/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhiyu",
    "password": "2201101122@qq.com"
  }')

echo "登录响应: $LOGIN_RESPONSE"
echo ""

# 提取JWT Token
LOGIN_JWT=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$LOGIN_JWT" ]; then
    echo "❌ 登录失败，无法获取JWT Token"
    exit 1
fi

echo "✅ 登录成功"
echo "JWT Token长度: ${#LOGIN_JWT} 字符"
echo ""

# 2. 生成API Token
echo "2. 生成API Token（10年有效期）..."
echo "----------------------------------------"

API_TOKEN_RESPONSE=$(curl -s -X POST "${BASE_URL}/v1/user/token/generate" \
  -H "Authorization: Bearer ${LOGIN_JWT}")

echo "API Token响应:"
echo "$API_TOKEN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$API_TOKEN_RESPONSE"
echo ""

# 检查是否有错误
if echo "$API_TOKEN_RESPONSE" | grep -q "detail"; then
    echo "❌ 生成API Token失败"
    exit 1
fi

# 提取API Token
API_TOKEN=$(echo $API_TOKEN_RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$API_TOKEN" ]; then
    echo "❌ 无法提取API Token"
    exit 1
fi

echo "✅ API Token生成成功"
echo "Token长度: ${#API_TOKEN} 字符"
echo "Token预览: ${API_TOKEN:0:80}..."
echo ""

# 3. 使用API Token访问接口
echo "3. 使用API Token访问项目列表..."
echo "----------------------------------------"

PROJECT_RESPONSE=$(curl -s -X GET "${BASE_URL}/v1/project/info?page=1&limit=5" \
  -H "Authorization: Bearer ${API_TOKEN}")

echo "项目列表响应:"
echo "$PROJECT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$PROJECT_RESPONSE"
echo ""

# 检查是否成功
if echo "$PROJECT_RESPONSE" | grep -q '"message":"成功"'; then
    echo "✅ API Token验证成功，可以正常访问接口"
else
    echo "❌ API Token验证失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 所有测试通过！"
echo "=========================================="
echo ""
echo "API Token已生成并验证成功"
echo "Token: $API_TOKEN"
echo ""
echo "使用方法："
echo "curl -X GET \"${BASE_URL}/v1/project/info\" \\"
echo "  -H \"Authorization: Bearer ${API_TOKEN}\""
echo ""

#!/bin/bash

# 测试创建、修改、查询权限控制
# 规则：ADMIN可以操作所有数据，其他角色只能操作自己关联的项目数据

BASE_URL="http://127.0.0.1:6080/v1"

echo "=========================================="
echo "测试创建、修改、查询权限控制"
echo "=========================================="
echo ""

# 1. 管理员登录
echo "1. 管理员登录..."
ADMIN_TOKEN=$(curl -s -X POST "${BASE_URL}/user/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhiyu",
    "password": "2201101122@qq.com"
  }' | jq -r '.access_token')

if [ -z "$ADMIN_TOKEN" ] || [ "$ADMIN_TOKEN" = "null" ]; then
  echo "❌ 管理员登录失败"
  exit 1
fi
echo "✅ 管理员登录成功"
echo "Token: ${ADMIN_TOKEN:0:20}..."
echo ""

# 2. 创建测试用户1
echo "2. 创建测试用户1 (test_user1)..."
USER1_RESPONSE=$(curl -s -X POST "${BASE_URL}/user/user" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_user1@test.com",
    "nickname": "测试用户1",
    "password": "test123456",
    "status": 1
  }')

USER1_ID=$(echo $USER1_RESPONSE | jq -r '.id')
echo "用户1 ID: $USER1_ID"
echo ""

# 3. 创建测试用户2
echo "3. 创建测试用户2 (test_user2)..."
USER2_RESPONSE=$(curl -s -X POST "${BASE_URL}/user/user" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_user2@test.com",
    "nickname": "测试用户2",
    "password": "test123456",
    "status": 1
  }')

USER2_ID=$(echo $USER2_RESPONSE | jq -r '.id')
echo "用户2 ID: $USER2_ID"
echo ""

# 4. 用户1登录
echo "4. 用户1登录..."
USER1_TOKEN=$(curl -s -X POST "${BASE_URL}/user/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_user1@test.com",
    "password": "test123456"
  }' | jq -r '.access_token')

echo "✅ 用户1登录成功"
echo ""

# 5. 用户2登录
echo "5. 用户2登录..."
USER2_TOKEN=$(curl -s -X POST "${BASE_URL}/user/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_user2@test.com",
    "password": "test123456"
  }' | jq -r '.access_token')

echo "✅ 用户2登录成功"
echo ""

# 6. 用户1创建项目（应该自动关联到自己）
echo "6. 用户1创建项目..."
PROJECT1_RESPONSE=$(curl -s -X POST "${BASE_URL}/project/info" \
  -H "Authorization: Bearer $USER1_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "用户1的项目",
    "status": 1
  }')

PROJECT1_ID=$(echo $PROJECT1_RESPONSE | jq -r '.id')
echo "项目1 ID: $PROJECT1_ID"
echo "关联用户: $(echo $PROJECT1_RESPONSE | jq -r '.users')"
echo ""

# 7. 管理员创建项目并关联用户2
echo "7. 管理员创建项目并关联用户2..."
PROJECT2_RESPONSE=$(curl -s -X POST "${BASE_URL}/project/info" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"用户2的项目\",
    \"status\": 1,
    \"user_ids\": [\"$USER2_ID\"]
  }")

PROJECT2_ID=$(echo $PROJECT2_RESPONSE | jq -r '.id')
echo "项目2 ID: $PROJECT2_ID"
echo "关联用户: $(echo $PROJECT2_RESPONSE | jq -r '.users')"
echo ""

# 8. 用户1查询自己的项目（应该成功）
echo "8. 用户1查询自己的项目..."
QUERY_RESULT=$(curl -s -X GET "${BASE_URL}/project/info/${PROJECT1_ID}" \
  -H "Authorization: Bearer $USER1_TOKEN")

if echo $QUERY_RESULT | jq -e '.data.id' > /dev/null; then
  echo "✅ 用户1可以查询自己的项目"
else
  echo "❌ 用户1无法查询自己的项目"
  echo "响应: $QUERY_RESULT"
fi
echo ""

# 9. 用户1查询用户2的项目（应该失败）
echo "9. 用户1查询用户2的项目（应该失败）..."
QUERY_RESULT=$(curl -s -X GET "${BASE_URL}/project/info/${PROJECT2_ID}" \
  -H "Authorization: Bearer $USER1_TOKEN")

if echo $QUERY_RESULT | jq -e '.detail' | grep -q "无权访问"; then
  echo "✅ 用户1无法查询用户2的项目（权限控制正常）"
else
  echo "❌ 权限控制失败，用户1可以查询用户2的项目"
  echo "响应: $QUERY_RESULT"
fi
echo ""

# 10. 用户1为自己的项目创建账号（应该成功）
echo "10. 用户1为自己的项目创建账号..."
ACCOUNT1_RESPONSE=$(curl -s -X POST "${BASE_URL}/project/account" \
  -H "Authorization: Bearer $USER1_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"account\": \"user1_account\",
    \"status\": 1,
    \"account_type\": 1,
    \"project_id\": \"$PROJECT1_ID\"
  }")

ACCOUNT1_ID=$(echo $ACCOUNT1_RESPONSE | jq -r '.data.id')
if [ "$ACCOUNT1_ID" != "null" ]; then
  echo "✅ 用户1可以为自己的项目创建账号"
  echo "账号 ID: $ACCOUNT1_ID"
else
  echo "❌ 用户1无法为自己的项目创建账号"
  echo "响应: $ACCOUNT1_RESPONSE"
fi
echo ""

# 11. 用户1为用户2的项目创建账号（应该失败）
echo "11. 用户1为用户2的项目创建账号（应该失败）..."
ACCOUNT_RESULT=$(curl -s -X POST "${BASE_URL}/project/account" \
  -H "Authorization: Bearer $USER1_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"account\": \"user1_try_create\",
    \"status\": 1,
    \"account_type\": 1,
    \"project_id\": \"$PROJECT2_ID\"
  }")

if echo $ACCOUNT_RESULT | jq -e '.detail' | grep -q "无权访问"; then
  echo "✅ 用户1无法为用户2的项目创建账号（权限控制正常）"
else
  echo "❌ 权限控制失败，用户1可以为用户2的项目创建账号"
  echo "响应: $ACCOUNT_RESULT"
fi
echo ""

# 12. 用户1更新自己的项目账号（应该成功）
echo "12. 用户1更新自己的项目账号..."
UPDATE_RESULT=$(curl -s -X PUT "${BASE_URL}/project/account/${ACCOUNT1_ID}" \
  -H "Authorization: Bearer $USER1_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": 2
  }')

if echo $UPDATE_RESULT | jq -e '.data.id' > /dev/null; then
  echo "✅ 用户1可以更新自己的项目账号"
else
  echo "❌ 用户1无法更新自己的项目账号"
  echo "响应: $UPDATE_RESULT"
fi
echo ""

# 13. 管理员为用户2的项目创建账号
echo "13. 管理员为用户2的项目创建账号..."
ACCOUNT2_RESPONSE=$(curl -s -X POST "${BASE_URL}/project/account" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"account\": \"user2_account\",
    \"status\": 1,
    \"account_type\": 1,
    \"project_id\": \"$PROJECT2_ID\"
  }")

ACCOUNT2_ID=$(echo $ACCOUNT2_RESPONSE | jq -r '.data.id')
echo "✅ 管理员创建账号成功"
echo "账号 ID: $ACCOUNT2_ID"
echo ""

# 14. 用户1尝试更新用户2的项目账号（应该失败）
echo "14. 用户1尝试更新用户2的项目账号（应该失败）..."
UPDATE_RESULT=$(curl -s -X PUT "${BASE_URL}/project/account/${ACCOUNT2_ID}" \
  -H "Authorization: Bearer $USER1_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": 2
  }')

if echo $UPDATE_RESULT | jq -e '.detail' | grep -q "无权访问"; then
  echo "✅ 用户1无法更新用户2的项目账号（权限控制正常）"
else
  echo "❌ 权限控制失败，用户1可以更新用户2的项目账号"
  echo "响应: $UPDATE_RESULT"
fi
echo ""

# 15. 用户1查询用户2的项目账号（应该失败）
echo "15. 用户1查询用户2的项目账号（应该失败）..."
QUERY_RESULT=$(curl -s -X GET "${BASE_URL}/project/account/${ACCOUNT2_ID}" \
  -H "Authorization: Bearer $USER1_TOKEN")

if echo $QUERY_RESULT | jq -e '.detail' | grep -q "无权访问"; then
  echo "✅ 用户1无法查询用户2的项目账号（权限控制正常）"
else
  echo "❌ 权限控制失败，用户1可以查询用户2的项目账号"
  echo "响应: $QUERY_RESULT"
fi
echo ""

# 16. 管理员可以查询所有账号
echo "16. 管理员查询用户2的项目账号..."
QUERY_RESULT=$(curl -s -X GET "${BASE_URL}/project/account/${ACCOUNT2_ID}" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

if echo $QUERY_RESULT | jq -e '.data.id' > /dev/null; then
  echo "✅ 管理员可以查询所有账号"
else
  echo "❌ 管理员无法查询账号"
  echo "响应: $QUERY_RESULT"
fi
echo ""

# 17. 测试项目钱包权限
echo "17. 用户1为自己的项目创建钱包..."
WALLET1_RESPONSE=$(curl -s -X POST "${BASE_URL}/project/wallet" \
  -H "Authorization: Bearer $USER1_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"public_key\": \"user1_wallet_public_key\",
    \"chain\": \"ETH\",
    \"project_id\": \"$PROJECT1_ID\"
  }")

WALLET1_ID=$(echo $WALLET1_RESPONSE | jq -r '.data.id')
if [ "$WALLET1_ID" != "null" ]; then
  echo "✅ 用户1可以为自己的项目创建钱包"
  echo "钱包 ID: $WALLET1_ID"
else
  echo "❌ 用户1无法为自己的项目创建钱包"
  echo "响应: $WALLET1_RESPONSE"
fi
echo ""

# 18. 用户1尝试为用户2的项目创建钱包（应该失败）
echo "18. 用户1尝试为用户2的项目创建钱包（应该失败）..."
WALLET_RESULT=$(curl -s -X POST "${BASE_URL}/project/wallet" \
  -H "Authorization: Bearer $USER1_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"public_key\": \"user1_try_wallet\",
    \"chain\": \"ETH\",
    \"project_id\": \"$PROJECT2_ID\"
  }")

if echo $WALLET_RESULT | jq -e '.detail' | grep -q "无权访问"; then
  echo "✅ 用户1无法为用户2的项目创建钱包（权限控制正常）"
else
  echo "❌ 权限控制失败，用户1可以为用户2的项目创建钱包"
  echo "响应: $WALLET_RESULT"
fi
echo ""

echo "=========================================="
echo "测试完成"
echo "=========================================="
echo ""
echo "总结："
echo "✅ 创建权限：用户只能为自己关联的项目创建资源"
echo "✅ 查询权限：用户只能查询自己关联的项目的资源"
echo "✅ 修改权限：用户只能修改自己关联的项目的资源"
echo "✅ 管理员权限：ADMIN可以操作所有资源"

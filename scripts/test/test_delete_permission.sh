#!/bin/bash

# 测试删除权限功能
# 验证ADMIN可以删除所有数据，其他角色只能删除自己关联的项目数据

BASE_URL="http://127.0.0.1:6080/v1"

echo "=========================================="
echo "测试删除权限功能"
echo "=========================================="
echo ""

# 1. 管理员登录
echo "1. 管理员登录..."
ADMIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/user/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhiyu",
    "password": "2201101122@qq.com"
  }')

ADMIN_TOKEN=$(echo $ADMIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
echo "✅ 管理员登录成功"
echo ""

# 2. 创建测试项目
echo "2. 创建测试项目..."
PROJECT_RESPONSE=$(curl -s -X POST "${BASE_URL}/project/info" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "删除权限测试项目",
    "status": 1
  }')

PROJECT_ID=$(echo $PROJECT_RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "✅ 测试项目创建成功: $PROJECT_ID"
echo ""

# 3. 创建测试用户
echo "3. 创建测试用户..."
TEST_USER_EMAIL="delete_test_$(date +%s)@test.com"
USER_RESPONSE=$(curl -s -X POST "${BASE_URL}/user/user" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_USER_EMAIL\",
    \"password\": \"test123456\",
    \"nickname\": \"删除测试用户\",
    \"status\": 1
  }")

TEST_USER_ID=$(echo $USER_RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "✅ 测试用户创建成功: $TEST_USER_ID"
echo ""

# 4. 将用户关联到项目
echo "4. 将用户关联到项目..."
curl -s -X PUT "${BASE_URL}/project/info/${PROJECT_ID}" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"user_ids\": [\"$TEST_USER_ID\"]}" > /dev/null
echo "✅ 用户已关联到项目"
echo ""

# 5. 创建项目账号
echo "5. 创建项目账号..."
ACCOUNT_RESPONSE=$(curl -s -X POST "${BASE_URL}/project/account" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"account\": \"delete_test_account@test.com\",
    \"password\": \"password123\",
    \"status\": 1,
    \"account_type\": 1,
    \"project_id\": \"$PROJECT_ID\"
  }")

ACCOUNT_ID=$(echo $ACCOUNT_RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "✅ 项目账号创建成功: $ACCOUNT_ID"
echo ""

# 6. 创建项目钱包
echo "6. 创建项目钱包..."
WALLET_RESPONSE=$(curl -s -X POST "${BASE_URL}/project/wallet" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"private_key\": \"test_private_key\",
    \"public_key\": \"test_public_key\",
    \"chain\": \"ETH\",
    \"project_id\": \"$PROJECT_ID\"
  }")

WALLET_ID=$(echo $WALLET_RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "✅ 项目钱包创建成功: $WALLET_ID"
echo ""

# 7. 测试用户登录
echo "7. 测试用户登录..."
TEST_USER_RESPONSE=$(curl -s -X POST "${BASE_URL}/user/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_USER_EMAIL\",
    \"password\": \"test123456\"
  }")

TEST_USER_TOKEN=$(echo $TEST_USER_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
echo "✅ 测试用户登录成功"
echo ""

# 8. 测试用户删除项目账号（应该成功）
echo "8. 测试用户删除项目账号（应该成功）..."
DELETE_ACCOUNT_RESPONSE=$(curl -s -w "%{http_code}" -X DELETE "${BASE_URL}/project/account/${ACCOUNT_ID}" \
  -H "Authorization: Bearer $TEST_USER_TOKEN")

if [[ "$DELETE_ACCOUNT_RESPONSE" == *"200"* ]]; then
  echo "✅ 测试用户成功删除关联项目的账号"
else
  echo "❌ 测试用户删除关联项目的账号失败"
  echo "响应: $DELETE_ACCOUNT_RESPONSE"
fi
echo ""

# 9. 测试用户删除项目钱包（应该成功）
echo "9. 测试用户删除项目钱包（应该成功）..."
DELETE_WALLET_RESPONSE=$(curl -s -w "%{http_code}" -X DELETE "${BASE_URL}/project/wallet/${WALLET_ID}" \
  -H "Authorization: Bearer $TEST_USER_TOKEN")

if [[ "$DELETE_WALLET_RESPONSE" == *"200"* ]]; then
  echo "✅ 测试用户成功删除关联项目的钱包"
else
  echo "❌ 测试用户删除关联项目的钱包失败"
  echo "响应: $DELETE_WALLET_RESPONSE"
fi
echo ""

# 10. 创建另一个项目（测试用户未关联）
echo "10. 创建另一个项目（测试用户未关联）..."
OTHER_PROJECT_RESPONSE=$(curl -s -X POST "${BASE_URL}/project/info" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "其他项目",
    "status": 1
  }')

OTHER_PROJECT_ID=$(echo $OTHER_PROJECT_RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "✅ 其他项目创建成功: $OTHER_PROJECT_ID"
echo ""

# 11. 为其他项目创建账号
echo "11. 为其他项目创建账号..."
OTHER_ACCOUNT_RESPONSE=$(curl -s -X POST "${BASE_URL}/project/account" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"account\": \"other_account@test.com\",
    \"password\": \"password123\",
    \"status\": 1,
    \"account_type\": 1,
    \"project_id\": \"$OTHER_PROJECT_ID\"
  }")

OTHER_ACCOUNT_ID=$(echo $OTHER_ACCOUNT_RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "✅ 其他项目账号创建成功: $OTHER_ACCOUNT_ID"
echo ""

# 12. 测试用户尝试删除其他项目的账号（应该失败）
echo "12. 测试用户尝试删除其他项目的账号（应该失败）..."
DELETE_OTHER_RESPONSE=$(curl -s -w "%{http_code}" -X DELETE "${BASE_URL}/project/account/${OTHER_ACCOUNT_ID}" \
  -H "Authorization: Bearer $TEST_USER_TOKEN")

if [[ "$DELETE_OTHER_RESPONSE" == *"403"* ]]; then
  echo "✅ 测试用户无法删除未关联项目的账号（权限控制正常）"
else
  echo "❌ 权限控制失败，测试用户能删除未关联项目的账号"
  echo "响应: $DELETE_OTHER_RESPONSE"
fi
echo ""

# 13. 管理员删除其他项目的账号（应该成功）
echo "13. 管理员删除其他项目的账号（应该成功）..."
ADMIN_DELETE_RESPONSE=$(curl -s -w "%{http_code}" -X DELETE "${BASE_URL}/project/account/${OTHER_ACCOUNT_ID}" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

if [[ "$ADMIN_DELETE_RESPONSE" == *"200"* ]]; then
  echo "✅ 管理员成功删除任意项目的账号"
else
  echo "❌ 管理员删除失败"
  echo "响应: $ADMIN_DELETE_RESPONSE"
fi
echo ""

# 14. 清理测试数据
echo "14. 清理测试数据..."
curl -s -X DELETE "${BASE_URL}/project/info/${PROJECT_ID}" -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null
curl -s -X DELETE "${BASE_URL}/project/info/${OTHER_PROJECT_ID}" -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null
curl -s -X DELETE "${BASE_URL}/user/user/${TEST_USER_ID}" -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null
echo "✅ 测试数据已清理"
echo ""

echo "=========================================="
echo "删除权限测试完成"
echo "=========================================="
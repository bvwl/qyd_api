#!/bin/bash

# 完整的数据权限测试
# 包括：创建项目、创建账号、关联用户、验证权限

BASE_URL="http://127.0.0.1:6080/v1"

echo "=========================================="
echo "完整数据权限测试"
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

# 2. 创建测试项目A
echo "2. 创建测试项目A..."
PROJECT_A_NAME="测试项目A_$(date +%s)"
PROJECT_A_RESPONSE=$(curl -s -X POST "${BASE_URL}/project/info" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"$PROJECT_A_NAME\",
    \"status\": 1
  }")

PROJECT_A_ID=$(echo $PROJECT_A_RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "✅ 项目A创建成功: $PROJECT_A_ID"
echo ""

# 3. 创建测试项目B
echo "3. 创建测试项目B..."
PROJECT_B_NAME="测试项目B_$(date +%s)"
PROJECT_B_RESPONSE=$(curl -s -X POST "${BASE_URL}/project/info" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"$PROJECT_B_NAME\",
    \"status\": 1
  }")

PROJECT_B_ID=$(echo $PROJECT_B_RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "✅ 项目B创建成功: $PROJECT_B_ID"
echo ""

# 4. 为项目A创建账号
echo "4. 为项目A创建账号..."
ACCOUNT_A_RESPONSE=$(curl -s -X POST "${BASE_URL}/project/account" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"account\": \"account_a_$(date +%s)@test.com\",
    \"password\": \"password123\",
    \"status\": 1,
    \"account_type\": 1,
    \"project_id\": \"$PROJECT_A_ID\"
  }")

ACCOUNT_A_ID=$(echo $ACCOUNT_A_RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "✅ 项目A账号创建成功: $ACCOUNT_A_ID"
echo ""

# 5. 为项目B创建账号
echo "5. 为项目B创建账号..."
ACCOUNT_B_RESPONSE=$(curl -s -X POST "${BASE_URL}/project/account" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"account\": \"account_b_$(date +%s)@test.com\",
    \"password\": \"password123\",
    \"status\": 1,
    \"account_type\": 1,
    \"project_id\": \"$PROJECT_B_ID\"
  }")

ACCOUNT_B_ID=$(echo $ACCOUNT_B_RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "✅ 项目B账号创建成功: $ACCOUNT_B_ID"
echo ""

# 6. 创建测试用户
echo "6. 创建测试用户..."
TEST_USER_EMAIL="test_user_$(date +%s)@test.com"
CREATE_USER_RESPONSE=$(curl -s -X POST "${BASE_URL}/user/user" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_USER_EMAIL\",
    \"password\": \"test123456\",
    \"nickname\": \"测试用户\",
    \"status\": 1
  }")

TEST_USER_ID=$(echo $CREATE_USER_RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "✅ 测试用户创建成功: $TEST_USER_ID"
echo ""

# 7. 将测试用户关联到项目A（只关联项目A，不关联项目B）
echo "7. 将测试用户关联到项目A..."
UPDATE_PROJECT_A=$(curl -s -X PUT "${BASE_URL}/project/info/${PROJECT_A_ID}" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_ids\": [\"$TEST_USER_ID\"]
  }")
echo "✅ 用户已关联到项目A"
echo ""

# 8. 测试用户登录
echo "8. 测试用户登录..."
TEST_USER_RESPONSE=$(curl -s -X POST "${BASE_URL}/user/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_USER_EMAIL\",
    \"password\": \"test123456\"
  }")

TEST_USER_TOKEN=$(echo $TEST_USER_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
echo "✅ 测试用户登录成功"
echo ""

# 9. 管理员查询所有项目
echo "9. 管理员查询所有项目..."
ADMIN_PROJECTS=$(curl -s -X GET "${BASE_URL}/project/info?page=1&limit=100" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
ADMIN_PROJECT_COUNT=$(echo $ADMIN_PROJECTS | grep -o '"num":[0-9]*' | cut -d':' -f2)
echo "✅ 管理员可以看到 $ADMIN_PROJECT_COUNT 个项目"
echo ""

# 10. 测试用户查询项目（应该只能看到项目A）
echo "10. 测试用户查询项目..."
TEST_USER_PROJECTS=$(curl -s -X GET "${BASE_URL}/project/info?page=1&limit=100" \
  -H "Authorization: Bearer $TEST_USER_TOKEN")
TEST_USER_PROJECT_COUNT=$(echo $TEST_USER_PROJECTS | grep -o '"num":[0-9]*' | cut -d':' -f2)
echo "✅ 测试用户可以看到 $TEST_USER_PROJECT_COUNT 个项目（应该只有项目A）"

# 检查是否包含项目A
if echo "$TEST_USER_PROJECTS" | grep -q "$PROJECT_A_ID"; then
  echo "   ✅ 包含项目A（正确）"
else
  echo "   ❌ 不包含项目A（错误）"
fi

# 检查是否包含项目B
if echo "$TEST_USER_PROJECTS" | grep -q "$PROJECT_B_ID"; then
  echo "   ❌ 包含项目B（错误，不应该看到）"
else
  echo "   ✅ 不包含项目B（正确）"
fi
echo ""

# 11. 管理员查询所有项目账号
echo "11. 管理员查询所有项目账号..."
ADMIN_ACCOUNTS=$(curl -s -X GET "${BASE_URL}/project/account?page=1&limit=100" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
ADMIN_ACCOUNT_COUNT=$(echo $ADMIN_ACCOUNTS | grep -o '"num":[0-9]*' | cut -d':' -f2)
echo "✅ 管理员可以看到 $ADMIN_ACCOUNT_COUNT 个项目账号"
echo ""

# 12. 测试用户查询项目账号（应该只能看到项目A的账号）
echo "12. 测试用户查询项目账号..."
TEST_USER_ACCOUNTS=$(curl -s -X GET "${BASE_URL}/project/account?page=1&limit=100" \
  -H "Authorization: Bearer $TEST_USER_TOKEN")
TEST_USER_ACCOUNT_COUNT=$(echo $TEST_USER_ACCOUNTS | grep -o '"num":[0-9]*' | cut -d':' -f2)
echo "✅ 测试用户可以看到 $TEST_USER_ACCOUNT_COUNT 个项目账号（应该只有项目A的账号）"

# 检查是否包含账号A
if echo "$TEST_USER_ACCOUNTS" | grep -q "$ACCOUNT_A_ID"; then
  echo "   ✅ 包含项目A的账号（正确）"
else
  echo "   ❌ 不包含项目A的账号（错误）"
fi

# 检查是否包含账号B
if echo "$TEST_USER_ACCOUNTS" | grep -q "$ACCOUNT_B_ID"; then
  echo "   ❌ 包含项目B的账号（错误，不应该看到）"
else
  echo "   ✅ 不包含项目B的账号（正确）"
fi
echo ""

# 13. 测试结果总结
echo "=========================================="
echo "测试结果总结"
echo "=========================================="
echo "管理员可见项目数: $ADMIN_PROJECT_COUNT"
echo "测试用户可见项目数: $TEST_USER_PROJECT_COUNT (应该为1)"
echo ""
echo "管理员可见账号数: $ADMIN_ACCOUNT_COUNT"
echo "测试用户可见账号数: $TEST_USER_ACCOUNT_COUNT (应该为1)"
echo ""

if [ "$TEST_USER_PROJECT_COUNT" = "1" ] && [ "$TEST_USER_ACCOUNT_COUNT" = "1" ]; then
  echo "✅✅✅ 数据权限测试完全通过！"
  echo "   - 管理员可以看到所有数据"
  echo "   - 普通用户只能看到关联项目的数据"
  echo "   - 普通用户看不到未关联项目的数据"
else
  echo "⚠️  数据权限测试存在问题"
fi
echo ""

# 14. 清理测试数据
echo "14. 清理测试数据..."
curl -s -X DELETE "${BASE_URL}/project/account/${ACCOUNT_A_ID}" -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null
curl -s -X DELETE "${BASE_URL}/project/account/${ACCOUNT_B_ID}" -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null
curl -s -X DELETE "${BASE_URL}/project/info/${PROJECT_A_ID}" -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null
curl -s -X DELETE "${BASE_URL}/project/info/${PROJECT_B_ID}" -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null
curl -s -X DELETE "${BASE_URL}/user/user/${TEST_USER_ID}" -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null
echo "✅ 测试数据已清理"
echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="

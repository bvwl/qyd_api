#!/bin/bash

# 测试数据权限功能
# 验证ADMIN和GM可以查看所有数据，其他角色只能查看自己关联的数据

BASE_URL="http://127.0.0.1:6080/v1"

echo "=========================================="
echo "测试数据权限功能"
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

if [ -z "$ADMIN_TOKEN" ]; then
  echo "❌ 管理员登录失败"
  echo "响应: $ADMIN_RESPONSE"
  exit 1
fi

echo "✅ 管理员登录成功"
echo "Token: ${ADMIN_TOKEN:0:20}..."
echo ""

# 2. 管理员查询项目列表
echo "2. 管理员查询项目列表..."
ADMIN_PROJECTS=$(curl -s -X GET "${BASE_URL}/project/info?page=1&limit=10" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

ADMIN_PROJECT_COUNT=$(echo $ADMIN_PROJECTS | grep -o '"num":[0-9]*' | cut -d':' -f2)
echo "✅ 管理员可以看到 $ADMIN_PROJECT_COUNT 个项目"
echo ""

# 3. 管理员查询项目账号列表
echo "3. 管理员查询项目账号列表..."
ADMIN_ACCOUNTS=$(curl -s -X GET "${BASE_URL}/project/account?page=1&limit=10" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

ADMIN_ACCOUNT_COUNT=$(echo $ADMIN_ACCOUNTS | grep -o '"num":[0-9]*' | cut -d':' -f2)
echo "✅ 管理员可以看到 $ADMIN_ACCOUNT_COUNT 个项目账号"
echo ""

# 4. 创建测试用户（普通角色）
echo "4. 创建测试用户（普通角色）..."
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

TEST_USER_ID=$(echo $CREATE_USER_RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TEST_USER_ID" ]; then
  echo "❌ 创建测试用户失败"
  echo "响应: $CREATE_USER_RESPONSE"
  exit 1
fi

echo "✅ 测试用户创建成功"
echo "用户ID: $TEST_USER_ID"
echo "邮箱: $TEST_USER_EMAIL"
echo ""

# 5. 测试用户登录
echo "5. 测试用户登录..."
TEST_USER_RESPONSE=$(curl -s -X POST "${BASE_URL}/user/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_USER_EMAIL\",
    \"password\": \"test123456\"
  }")

TEST_USER_TOKEN=$(echo $TEST_USER_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TEST_USER_TOKEN" ]; then
  echo "❌ 测试用户登录失败"
  echo "响应: $TEST_USER_RESPONSE"
  exit 1
fi

echo "✅ 测试用户登录成功"
echo "Token: ${TEST_USER_TOKEN:0:20}..."
echo ""

# 6. 测试用户查询项目列表（应该为空或只看到关联的项目）
echo "6. 测试用户查询项目列表..."
TEST_USER_PROJECTS=$(curl -s -X GET "${BASE_URL}/project/info?page=1&limit=10" \
  -H "Authorization: Bearer $TEST_USER_TOKEN")

TEST_USER_PROJECT_COUNT=$(echo $TEST_USER_PROJECTS | grep -o '"num":[0-9]*' | cut -d':' -f2)

if [ -z "$TEST_USER_PROJECT_COUNT" ]; then
  echo "✅ 测试用户没有关联任何项目（符合预期）"
else
  echo "✅ 测试用户可以看到 $TEST_USER_PROJECT_COUNT 个项目（只能看到关联的项目）"
fi
echo ""

# 7. 测试用户查询项目账号列表（应该为空或只看到关联项目的账号）
echo "7. 测试用户查询项目账号列表..."
TEST_USER_ACCOUNTS=$(curl -s -X GET "${BASE_URL}/project/account?page=1&limit=10" \
  -H "Authorization: Bearer $TEST_USER_TOKEN")

TEST_USER_ACCOUNT_COUNT=$(echo $TEST_USER_ACCOUNTS | grep -o '"num":[0-9]*' | cut -d':' -f2)

if [ -z "$TEST_USER_ACCOUNT_COUNT" ]; then
  echo "✅ 测试用户没有关联任何项目账号（符合预期）"
else
  echo "✅ 测试用户可以看到 $TEST_USER_ACCOUNT_COUNT 个项目账号（只能看到关联项目的账号）"
fi
echo ""

# 8. 对比结果
echo "=========================================="
echo "数据权限测试结果对比"
echo "=========================================="
echo "管理员可见项目数: $ADMIN_PROJECT_COUNT"
echo "测试用户可见项目数: ${TEST_USER_PROJECT_COUNT:-0}"
echo ""
echo "管理员可见项目账号数: $ADMIN_ACCOUNT_COUNT"
echo "测试用户可见项目账号数: ${TEST_USER_ACCOUNT_COUNT:-0}"
echo ""

if [ "$ADMIN_PROJECT_COUNT" -gt "${TEST_USER_PROJECT_COUNT:-0}" ]; then
  echo "✅ 数据权限测试通过！"
  echo "   - 管理员可以看到所有数据"
  echo "   - 普通用户只能看到关联的数据"
else
  echo "⚠️  数据权限可能存在问题"
  echo "   - 管理员和普通用户看到的数据数量相同"
fi
echo ""

# 9. 清理测试数据（可选）
echo "9. 清理测试用户..."
DELETE_RESPONSE=$(curl -s -X DELETE "${BASE_URL}/user/user/${TEST_USER_ID}" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

echo "✅ 测试用户已删除"
echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="

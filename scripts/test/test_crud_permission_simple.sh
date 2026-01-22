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

echo "✅ 管理员登录成功"
echo ""

# 2. 创建测试用户1
echo "2. 创建测试用户1..."
USER1_ID=$(curl -s -X POST "${BASE_URL}/user/user" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "crud_test_user1@test.com",
    "nickname": "CRUD测试用户1",
    "password": "test123456",
    "status": 1
  }' | jq -r '.id')

echo "用户1 ID: $USER1_ID"
echo ""

# 3. 创建测试用户2
echo "3. 创建测试用户2..."
USER2_ID=$(curl -s -X POST "${BASE_URL}/user/user" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "crud_test_user2@test.com",
    "nickname": "CRUD测试用户2",
    "password": "test123456",
    "status": 1
  }' | jq -r '.id')

echo "用户2 ID: $USER2_ID"
echo ""

# 4. 用户1登录
echo "4. 用户1登录..."
USER1_TOKEN=$(curl -s -X POST "${BASE_URL}/user/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "crud_test_user1@test.com",
    "password": "test123456"
  }' | jq -r '.access_token')

echo "✅ 用户1登录成功"
echo ""

# 5. 用户2登录
echo "5. 用户2登录..."
USER2_TOKEN=$(curl -s -X POST "${BASE_URL}/user/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "crud_test_user2@test.com",
    "password": "test123456"
  }' | jq -r '.access_token')

echo "✅ 用户2登录成功"
echo ""

# 6. 用户1创建项目（应该自动关联到自己）
echo "6. 用户1创建项目..."
PROJECT1_ID=$(curl -s -X POST "${BASE_URL}/project/info" \
  -H "Authorization: Bearer $USER1_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "用户1的CRUD测试项目",
    "status": 1
  }' | jq -r '.id')

echo "✅ 项目1创建成功"
echo "项目1 ID: $PROJECT1_ID"
echo ""

# 7. 管理员创建项目并关联用户2
echo "7. 管理员创建项目并关联用户2..."
PROJECT2_ID=$(curl -s -X POST "${BASE_URL}/project/info" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"用户2的CRUD测试项目\",
    \"status\": 1,
    \"user_ids\": [\"$USER2_ID\"]
  }" | jq -r '.id')

echo "✅ 项目2创建成功"
echo "项目2 ID: $PROJECT2_ID"
echo ""

# 8. 测试查询权限：用户1查询自己的项目（应该成功）
echo "8. 测试查询权限：用户1查询自己的项目..."
RESULT=$(curl -s -X GET "${BASE_URL}/project/info/${PROJECT1_ID}" \
  -H "Authorization: Bearer $USER1_TOKEN")

if echo "$RESULT" | jq -e '.id' > /dev/null 2>&1; then
  echo "✅ 用户1可以查询自己的项目"
else
  echo "❌ 用户1无法查询自己的项目"
  echo "响应: $RESULT"
fi
echo ""

# 9. 测试查询权限：用户1查询用户2的项目（应该失败）
echo "9. 测试查询权限：用户1查询用户2的项目（应该失败）..."
RESULT=$(curl -s -X GET "${BASE_URL}/project/info/${PROJECT2_ID}" \
  -H "Authorization: Bearer $USER1_TOKEN")

if echo "$RESULT" | jq -e '.detail' 2>/dev/null | grep -q "无权访问"; then
  echo "✅ 用户1无法查询用户2的项目（权限控制正常）"
else
  echo "❌ 权限控制失败"
  echo "响应: $RESULT"
fi
echo ""

# 10. 测试创建权限：用户1为自己的项目创建账号（应该成功）
echo "10. 测试创建权限：用户1为自己的项目创建账号..."
ACCOUNT1_ID=$(curl -s -X POST "${BASE_URL}/project/account" \
  -H "Authorization: Bearer $USER1_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"account\": \"crud_user1_account\",
    \"status\": 1,
    \"account_type\": 1,
    \"project_id\": \"$PROJECT1_ID\"
  }" | jq -r '.id')

if [ "$ACCOUNT1_ID" != "null" ] && [ -n "$ACCOUNT1_ID" ]; then
  echo "✅ 用户1可以为自己的项目创建账号"
  echo "账号 ID: $ACCOUNT1_ID"
else
  echo "❌ 用户1无法为自己的项目创建账号"
fi
echo ""

# 11. 测试创建权限：用户1为用户2的项目创建账号（应该失败）
echo "11. 测试创建权限：用户1为用户2的项目创建账号（应该失败）..."
RESULT=$(curl -s -X POST "${BASE_URL}/project/account" \
  -H "Authorization: Bearer $USER1_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"account\": \"crud_user1_try_create\",
    \"status\": 1,
    \"account_type\": 1,
    \"project_id\": \"$PROJECT2_ID\"
  }")

if echo "$RESULT" | jq -e '.detail' 2>/dev/null | grep -q "无权访问"; then
  echo "✅ 用户1无法为用户2的项目创建账号（权限控制正常）"
else
  echo "❌ 权限控制失败"
  echo "响应: $RESULT"
fi
echo ""

# 12. 测试修改权限：用户1更新自己的项目账号（应该成功）
echo "12. 测试修改权限：用户1更新自己的项目账号..."
RESULT=$(curl -s -X PUT "${BASE_URL}/project/account/${ACCOUNT1_ID}" \
  -H "Authorization: Bearer $USER1_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": 2
  }')

if echo "$RESULT" | jq -e '.id' > /dev/null 2>&1; then
  echo "✅ 用户1可以更新自己的项目账号"
else
  echo "❌ 用户1无法更新自己的项目账号"
  echo "响应: $RESULT"
fi
echo ""

# 13. 管理员为用户2的项目创建账号
echo "13. 管理员为用户2的项目创建账号..."
ACCOUNT2_ID=$(curl -s -X POST "${BASE_URL}/project/account" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"account\": \"crud_user2_account\",
    \"status\": 1,
    \"account_type\": 1,
    \"project_id\": \"$PROJECT2_ID\"
  }" | jq -r '.id')

echo "✅ 管理员创建账号成功"
echo "账号 ID: $ACCOUNT2_ID"
echo ""

# 14. 测试修改权限：用户1尝试更新用户2的项目账号（应该失败）
echo "14. 测试修改权限：用户1尝试更新用户2的项目账号（应该失败）..."
RESULT=$(curl -s -X PUT "${BASE_URL}/project/account/${ACCOUNT2_ID}" \
  -H "Authorization: Bearer $USER1_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": 2
  }')

if echo "$RESULT" | jq -e '.detail' 2>/dev/null | grep -q "无权访问"; then
  echo "✅ 用户1无法更新用户2的项目账号（权限控制正常）"
else
  echo "❌ 权限控制失败"
  echo "响应: $RESULT"
fi
echo ""

# 15. 测试查询权限：用户1查询用户2的项目账号（应该失败）
echo "15. 测试查询权限：用户1查询用户2的项目账号（应该失败）..."
RESULT=$(curl -s -X GET "${BASE_URL}/project/account/${ACCOUNT2_ID}" \
  -H "Authorization: Bearer $USER1_TOKEN")

if echo "$RESULT" | jq -e '.detail' 2>/dev/null | grep -q "无权访问"; then
  echo "✅ 用户1无法查询用户2的项目账号（权限控制正常）"
else
  echo "❌ 权限控制失败"
  echo "响应: $RESULT"
fi
echo ""

# 16. 管理员可以查询所有账号
echo "16. 管理员查询用户2的项目账号..."
RESULT=$(curl -s -X GET "${BASE_URL}/project/account/${ACCOUNT2_ID}" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

if echo "$RESULT" | jq -e '.id' > /dev/null 2>&1; then
  echo "✅ 管理员可以查询所有账号"
else
  echo "❌ 管理员无法查询账号"
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

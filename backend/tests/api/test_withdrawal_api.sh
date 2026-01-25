#!/bin/bash

# 项目提现API测试脚本

BASE_URL="http://localhost:6080"
API_PREFIX="/v1/project/withdrawal"

echo "============================================================"
echo "项目提现API测试"
echo "============================================================"
echo ""

# 1. 登录获取Token
echo "1. 登录获取Token..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/v1/user/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhiyu",
    "password": "2201101122@qq.com"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "✗ 登录失败"
  echo "响应: $LOGIN_RESPONSE"
  exit 1
fi

echo "✓ 登录成功"
echo "Token: ${TOKEN:0:50}..."
echo ""

# 2. 创建测试项目
echo "2. 创建测试项目..."
PROJECT_RESPONSE=$(curl -s -X POST "${BASE_URL}/v1/project/info" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "提现测试项目_'$(date +%s)'",
    "status": 1
  }')

PROJECT_ID=$(echo $PROJECT_RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$PROJECT_ID" ]; then
  echo "✗ 创建项目失败"
  echo "响应: $PROJECT_RESPONSE"
  exit 1
fi

echo "✓ 创建成功"
echo "项目ID: $PROJECT_ID"
echo ""

# 3. 创建提现记录（只传入平台币）
echo "3. 创建提现记录（只传入平台币）..."
CREATE_RESPONSE=$(curl -s -X POST "${BASE_URL}${API_PREFIX}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "'$PROJECT_ID'",
    "platform_coin": "123.456789012345678901"
  }')

echo "响应: $CREATE_RESPONSE"
echo ""

# 4. 查询提现记录
echo "4. 查询提现记录..."
GET_RESPONSE=$(curl -s -X GET "${BASE_URL}${API_PREFIX}/project/${PROJECT_ID}" \
  -H "Authorization: Bearer $TOKEN")

echo "响应: $GET_RESPONSE"
echo ""

# 5. 更新记录（添加稳定币）
echo "5. 更新记录（添加稳定币）..."
UPDATE_RESPONSE=$(curl -s -X POST "${BASE_URL}${API_PREFIX}/upsert" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "'$PROJECT_ID'",
    "stable_coin": "999.888777666555444333"
  }')

echo "响应: $UPDATE_RESPONSE"
echo ""

# 6. 再次更新（修改平台币和添加人民币）
echo "6. 再次更新（修改平台币和添加人民币）..."
UPDATE2_RESPONSE=$(curl -s -X POST "${BASE_URL}${API_PREFIX}/upsert" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "'$PROJECT_ID'",
    "platform_coin": "200.123456789012345678",
    "rmb": "1000.50",
    "remark": "测试更新"
  }')

echo "响应: $UPDATE2_RESPONSE"
echo ""

# 7. 查询列表
echo "7. 查询提现记录列表..."
LIST_RESPONSE=$(curl -s -X GET "${BASE_URL}${API_PREFIX}?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN")

echo "响应: $LIST_RESPONSE"
echo ""

# 8. 测试精度（极小值）
echo "8. 测试精度（极小值）..."
PRECISION_RESPONSE=$(curl -s -X POST "${BASE_URL}${API_PREFIX}/upsert" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "'$PROJECT_ID'",
    "platform_coin": "0.000000000000000001"
  }')

echo "响应: $PRECISION_RESPONSE"
echo ""

# 9. 最终查询
echo "9. 最终查询..."
FINAL_RESPONSE=$(curl -s -X GET "${BASE_URL}${API_PREFIX}/project/${PROJECT_ID}" \
  -H "Authorization: Bearer $TOKEN")

echo "响应: $FINAL_RESPONSE"
echo ""

# 10. 删除测试项目
echo "10. 清理测试数据..."
DELETE_RESPONSE=$(curl -s -X DELETE "${BASE_URL}/v1/project/info/${PROJECT_ID}" \
  -H "Authorization: Bearer $TOKEN")

echo "✓ 清理完成"
echo ""

echo "============================================================"
echo "✓ 测试完成！"
echo "============================================================"

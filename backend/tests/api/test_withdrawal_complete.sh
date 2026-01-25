#!/bin/bash

# 项目提现功能完整测试

BASE_URL="http://localhost:6080"

echo "============================================================"
echo "项目提现功能完整测试"
echo "============================================================"
echo ""

# 1. 登录
echo "1. 登录..."
TOKEN=$(curl -s -X POST "${BASE_URL}/v1/user/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"zhiyu","password":"2201101122@qq.com"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "✗ 登录失败"
  exit 1
fi
echo "✓ 登录成功"
echo ""

# 2. 创建测试项目
echo "2. 创建测试项目..."
PROJECT_ID=$(curl -s -X POST "${BASE_URL}/v1/project/info" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"提现完整测试_'$(date +%s)'","status":1}' | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

echo "✓ 项目ID: $PROJECT_ID"
echo ""

# 3. 创建提现记录（只传入平台币）
echo "3. 创建提现记录（平台币: 100.123456789012345678）..."
curl -s -X POST "${BASE_URL}/v1/project/withdrawal" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "'$PROJECT_ID'",
    "platform_coin": "100.123456789012345678"
  }' | python -m json.tool | grep -E "(platform_coin|stable_coin|rmb)" | head -10
echo ""

# 4. 查询记录
echo "4. 查询提现记录..."
WITHDRAWAL_ID=$(curl -s -X GET "${BASE_URL}/v1/project/withdrawal/project/${PROJECT_ID}" \
  -H "Authorization: Bearer $TOKEN" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "✓ 提现记录ID: $WITHDRAWAL_ID"
echo ""

# 5. 更新记录（添加稳定币）
echo "5. 更新记录（添加稳定币: 200.987654321098765432）..."
curl -s -X PUT "${BASE_URL}/v1/project/withdrawal/${WITHDRAWAL_ID}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "stable_coin": "200.987654321098765432"
  }' | python -m json.tool | grep -E "(stable_coin)" | head -5
echo ""

# 6. 再次更新（修改平台币和添加人民币）
echo "6. 再次更新（平台币: 250.555555555555555555, 人民币: 1000.50）..."
curl -s -X PUT "${BASE_URL}/v1/project/withdrawal/${WITHDRAWAL_ID}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform_coin": "250.555555555555555555",
    "rmb": "1000.50",
    "remark": "测试更新"
  }' | python -m json.tool | grep -E "(platform_coin|rmb|remark)" | head -10
echo ""

# 7. 查询最终结果
echo "7. 查询最终结果（应该有完整的历史记录）..."
curl -s -X GET "${BASE_URL}/v1/project/withdrawal/project/${PROJECT_ID}" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
echo ""

# 8. 测试精度（极小值）
echo "8. 测试精度（极小值: 0.000000000000000001）..."
curl -s -X PUT "${BASE_URL}/v1/project/withdrawal/${WITHDRAWAL_ID}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform_coin": "0.000000000000000001"
  }' | python -m json.tool | grep -E "(platform_coin)" | head -5
echo ""

# 9. 查询列表
echo "9. 查询提现记录列表..."
curl -s -X GET "${BASE_URL}/v1/project/withdrawal?page=1&limit=10&res_count=true" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool | head -20
echo ""

# 10. 清理测试数据
echo "10. 清理测试数据..."
curl -s -X DELETE "${BASE_URL}/v1/project/info/${PROJECT_ID}" \
  -H "Authorization: Bearer $TOKEN" > /dev/null
echo "✓ 清理完成"
echo ""

echo "============================================================"
echo "✓ 测试完成！"
echo "============================================================"

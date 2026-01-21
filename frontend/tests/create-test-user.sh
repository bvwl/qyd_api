#!/bin/bash

echo "创建测试用户..."
echo ""

# 创建用户
response=$(curl -s -X POST "http://127.0.0.1:6080/v1/user/user" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "nickname": "管理员",
    "password": "admin123",
    "status": 1
  }')

echo "响应："
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
echo ""

if echo "$response" | grep -q "id"; then
  echo "✅ 用户创建成功！"
  echo ""
  echo "登录信息："
  echo "  邮箱：admin@example.com"
  echo "  密码：admin123"
else
  echo "❌ 用户创建失败"
  echo ""
  echo "可能的原因："
  echo "  1. 用户已存在"
  echo "  2. 后端服务未启动"
  echo "  3. 数据库连接失败"
fi

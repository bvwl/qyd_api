#!/bin/bash

# 测试项目统计API

echo "=========================================="
echo "测试项目统计API"
echo "=========================================="
echo ""

# 设置API地址和Token
API_BASE="http://127.0.0.1:6080"
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjkzNDg1NTEsImlhdCI6MTc2OTI2MjE1MSwianRpIjoiYjEzNTA5N2YtYmQ2MC00ZTAwLTg0MTQtYzNhYTIxYjVhZWNmIiwiaWQiOiI3OTE0Y2JhYy04ZmY5LTRiMTAtOTg1NC04MGZjMTY2N2EzMzkiLCJlbWFpbCI6InpoaXl1Iiwicm9sZXMiOlsiQURNSU4iXX0.sCbtJeAwr-zIDPyAbfvkTLuaQYg35WzY46Zqy7I-Hh4"

# 测试1: 获取仪表盘统计数据（最近7天）
echo "测试1: 获取仪表盘统计数据（最近7天）"
echo "URL: ${API_BASE}/v1/project/stats/dashboard?days=7"
curl -s -X GET "${API_BASE}/v1/project/stats/dashboard?days=7" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json" | python3 -m json.tool
echo ""
echo ""

# 测试2: 获取仪表盘统计数据（最近30天）
echo "测试2: 获取仪表盘统计数据（最近30天）"
echo "URL: ${API_BASE}/v1/project/stats/dashboard?days=30"
curl -s -X GET "${API_BASE}/v1/project/stats/dashboard?days=30" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json" | python3 -m json.tool 2>&1 | head -50
echo ""
echo ""

# 测试3: 获取指定项目今天的更新数量
echo "测试3: 获取指定项目今天的更新数量"
echo "请先获取一个项目ID，然后替换下面的PROJECT_ID"
echo ""
# 先获取项目列表
echo "获取项目列表..."
PROJECT_ID=$(curl -s -X GET "${API_BASE}/v1/project/info?page=1&limit=1" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['items'][0]['id'] if data.get('items') else '')" 2>/dev/null)

if [ -n "$PROJECT_ID" ]; then
    echo "项目ID: $PROJECT_ID"
    echo "URL: ${API_BASE}/v1/project/stats/project/${PROJECT_ID}/today"
    curl -s -X GET "${API_BASE}/v1/project/stats/project/${PROJECT_ID}/today" \
      -H "Authorization: Bearer ${TOKEN}" \
      -H "Accept: application/json" | python3 -m json.tool
else
    echo "未找到项目，跳过此测试"
fi
echo ""
echo ""

# 测试4: 清除统计缓存（仅管理员）
echo "测试4: 清除统计缓存"
echo "URL: ${API_BASE}/v1/project/stats/cache/clear"
curl -s -X POST "${API_BASE}/v1/project/stats/cache/clear" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json" | python3 -m json.tool
echo ""
echo ""

# 测试5: 再次获取统计数据（验证缓存已清除）
echo "测试5: 再次获取统计数据（验证缓存已清除）"
echo "URL: ${API_BASE}/v1/project/stats/dashboard?days=7"
curl -s -X GET "${API_BASE}/v1/project/stats/dashboard?days=7" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json" | python3 -m json.tool 2>&1 | head -30
echo ""
echo ""

echo "=========================================="
echo "测试完成！"
echo "=========================================="

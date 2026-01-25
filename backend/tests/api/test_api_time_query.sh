#!/bin/bash

# 测试时间参数查询是否修复成功

echo "=========================================="
echo "测试时间参数查询修复"
echo "=========================================="
echo ""

# 设置API地址和Token
API_BASE="http://127.0.0.1:6080"
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjkzNDg1NTEsImlhdCI6MTc2OTI2MjE1MSwianRpIjoiYjEzNTA5N2YtYmQ2MC00ZTAwLTg0MTQtYzNhYTIxYjVhZWNmIiwiaWQiOiI3OTE0Y2JhYy04ZmY5LTRiMTAtOTg1NC04MGZjMTY2N2EzMzkiLCJlbWFpbCI6InpoaXl1Iiwicm9sZXMiOlsiQURNSU4iXX0.sCbtJeAwr-zIDPyAbfvkTLuaQYg35WzY46Zqy7I-Hh4"

# 测试1: 日期格式
echo "测试1: 日期格式 (YYYY-MM-DD)"
echo "URL: ${API_BASE}/v1/project/account?update_time_start=2026-01-25&update_time_end=2026-01-25&page=1&limit=10"
curl -s -X GET "${API_BASE}/v1/project/account?update_time_start=2026-01-25&update_time_end=2026-01-25&page=1&limit=10" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json" | python3 -m json.tool 2>&1 | head -20
echo ""
echo ""

# 测试2: 日期时间格式
echo "测试2: 日期时间格式 (YYYY-MM-DD HH:mm:ss)"
echo "URL: ${API_BASE}/v1/project/account?update_time_start=2026-01-25%2000:00:00&update_time_end=2026-01-25%2023:59:59&page=1&limit=10"
curl -s -X GET "${API_BASE}/v1/project/account?update_time_start=2026-01-25%2000:00:00&update_time_end=2026-01-25%2023:59:59&page=1&limit=10" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json" | python3 -m json.tool 2>&1 | head -20
echo ""
echo ""

# 测试3: 时间戳格式
echo "测试3: 时间戳格式 (13位毫秒)"
echo "URL: ${API_BASE}/v1/project/account?update_time_start=1737792000000&update_time_end=1737878399000&page=1&limit=10"
curl -s -X GET "${API_BASE}/v1/project/account?update_time_start=1737792000000&update_time_end=1737878399000&page=1&limit=10" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json" | python3 -m json.tool 2>&1 | head -20
echo ""
echo ""

# 测试4: 其他接口 - 用户列表
echo "测试4: 用户列表时间查询"
echo "URL: ${API_BASE}/v1/user/user?create_time_start=2026-01-01&create_time_end=2026-01-31&page=1&limit=10"
curl -s -X GET "${API_BASE}/v1/user/user?create_time_start=2026-01-01&create_time_end=2026-01-31&page=1&limit=10" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json" | python3 -m json.tool 2>&1 | head -20
echo ""
echo ""

# 测试5: 项目列表
echo "测试5: 项目列表时间查询"
echo "URL: ${API_BASE}/v1/project/info?update_time_start=2026-01-25&page=1&limit=10"
curl -s -X GET "${API_BASE}/v1/project/info?update_time_start=2026-01-25&page=1&limit=10" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json" | python3 -m json.tool 2>&1 | head -20
echo ""
echo ""

echo "=========================================="
echo "测试完成！"
echo "如果看到正常的JSON响应（而不是错误信息），说明修复成功。"
echo "=========================================="

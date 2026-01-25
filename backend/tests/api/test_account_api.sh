#!/bin/bash

# 测试服务器账号API是否返回 is_all_inbound_added 字段

echo "测试服务器账号列表 API"
echo "======================================"

# 获取 Token（使用管理员账号）
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njk0MTk0MzMsImlhdCI6MTc2OTMzMzAzMywianRpIjoiMGI1ODc2NzYtMDFmYy00NmI3LTljYWUtYjBlMzI3NTdiNTA4IiwiaWQiOiI3OTE0Y2JhYy04ZmY5LTRiMTAtOTg1NC04MGZjMTY2N2EzMzkiLCJlbWFpbCI6InpoaXl1Iiwicm9sZXMiOlsiQURNSU4iXX0.pTJtPSFEiCUm6Sa1lTUJS6d6WNcq6R5gmat8XxjNvpQ"

# 调用 API
echo ""
echo "请求: GET /v1/server/account?page=1&limit=10&res_count=true"
echo ""

curl -s "http://127.0.0.1:6080/v1/server/account?page=1&limit=10&res_count=true" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" | jq '.'

echo ""
echo "======================================"
echo "检查返回数据中是否包含 is_all_inbound_added 字段"

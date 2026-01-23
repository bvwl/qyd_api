#!/bin/bash

# 测试树形选择修复
# 验证：选择部分子菜单时，父菜单不会丢失，未选择的子菜单也不会被自动选中

BASE_URL="http://127.0.0.1:6080"
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjkyMzgxNzIsImlhdCI6MTc2OTE1MTc3MiwianRpIjoiZmZhYTE4Y2QtNTM3OC00ZjI0LWI0MzctOWNkMjc4ZjUwMmQ3IiwiaWQiOiI3OTE0Y2JhYy04ZmY5LTRiMTAtOTg1NC04MGZjMTY2N2EzMzkiLCJlbWFpbCI6InpoaXl1Iiwicm9sZXMiOlsiQURNSU4iXX0.3CIqqtKqpHZLoAMDZun4ZdiJEBHxu0gjxDz0c1uUlW8"
ROLE_ID="ae3904c1-a360-451e-8b87-9ddf8973fe95"

echo "=========================================="
echo "测试树形选择修复"
echo "=========================================="
echo ""

echo "步骤 1: 获取所有路由（用于查看结构）"
echo "----------------------------------------"
curl -s "${BASE_URL}/v1/user/route/tree?status=1" \
  -H "Authorization: Bearer ${TOKEN}" | jq -r '.[] | "\(.id) - \(.title) (parent: \(.parent_id // "null"))"' | head -20
echo ""

echo "步骤 2: 设置角色权限（选择部分子菜单）"
echo "----------------------------------------"
echo "选择的节点："
echo "  - 05d6f4e6-0760-4512-834d-d3097f48f850"
echo "  - 2962dda0-b238-48cd-a30f-f71f94adac0f"
echo "  - 9678e888-4d83-4105-864b-df785034b862"
echo "  - ceb4c2d8-af80-4900-bd2f-ece4ae672600"
echo "  - effe9b56-1706-475b-bdc7-4672f7ca34ca"
echo "  - bfd60855-8a34-48ab-a4d8-5533cefd8717"
echo "  - 5826bf49-f043-4a6d-9658-f712f95f4c6c"
echo "  - d92745cd-e1a6-4e87-a7e5-46ed297da9a5"
echo "  - 280d869a-5d9f-4666-9c2a-0f7da40e23f5"
echo "  - 73992a93-7b5b-4d44-83a9-388ff4da2bf5"
echo "  - 5c8f51ae-4b4d-4b8f-b236-43564c9164c1"
echo "  - 9951c958-841c-452a-a3ab-cb39e3ad672b"
echo "  - bf7ec69c-294e-4568-9d06-17bf40aa31ee"
echo "  - 55460b38-2a8f-4825-887c-2bcdd429010b"
echo "  - 2a49b0c1-6654-4573-b17f-019b483e107b"
echo "  - 85c8699c-9ade-4949-bb1b-d7ca03a80057"
echo "  - 4a8c60a3-cc60-46ba-8f0f-d882db120e3f"
echo "  - 0f613960-02dc-41da-b6cc-0a7089c097ed"
echo ""

curl -s -X POST "${BASE_URL}/v1/user/role/${ROLE_ID}/routes" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '["05d6f4e6-0760-4512-834d-d3097f48f850","2962dda0-b238-48cd-a30f-f71f94adac0f","9678e888-4d83-4105-864b-df785034b862","ceb4c2d8-af80-4900-bd2f-ece4ae672600","effe9b56-1706-475b-bdc7-4672f7ca34ca","bfd60855-8a34-48ab-a4d8-5533cefd8717","5826bf49-f043-4a6d-9658-f712f95f4c6c","d92745cd-e1a6-4e87-a7e5-46ed297da9a5","280d869a-5d9f-4666-9c2a-0f7da40e23f5","73992a93-7b5b-4d44-83a9-388ff4da2bf5","5c8f51ae-4b4d-4b8f-b236-43564c9164c1","9951c958-841c-452a-a3ab-cb39e3ad672b","bf7ec69c-294e-4568-9d06-17bf40aa31ee","55460b38-2a8f-4825-887c-2bcdd429010b","2a49b0c1-6654-4573-b17f-019b483e107b","85c8699c-9ade-4949-bb1b-d7ca03a80057","4a8c60a3-cc60-46ba-8f0f-d882db120e3f","0f613960-02dc-41da-b6cc-0a7089c097ed"]' | jq '.'
echo ""

echo "步骤 3: 查询角色权限（新格式）"
echo "----------------------------------------"
RESPONSE=$(curl -s "${BASE_URL}/v1/user/role/${ROLE_ID}/routes" \
  -H "Authorization: Bearer ${TOKEN}")

echo "返回的数据结构："
echo "$RESPONSE" | jq 'keys'
echo ""

echo "checked_keys（应该只包含叶子节点）："
echo "$RESPONSE" | jq -r '.checked_keys | length'
echo "$RESPONSE" | jq -r '.checked_keys[]' | head -10
echo ""

echo "tree（完整的树结构）："
echo "$RESPONSE" | jq -r '.tree | length'
echo "$RESPONSE" | jq -r '.tree[] | "\(.id) - \(.title)"' | head -10
echo ""

echo "=========================================="
echo "测试完成"
echo "=========================================="
echo ""
echo "预期结果："
echo "  1. checked_keys 只包含叶子节点（没有子节点的节点）"
echo "  2. tree 包含完整的树结构（包括父节点）"
echo "  3. 前端使用 checked_keys 设置 Tree 的 checkedKeys"
echo "  4. Tree 组件会自动计算父节点的半选状态"
echo ""

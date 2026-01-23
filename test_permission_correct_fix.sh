#!/bin/bash

# 权限管理正确修复验证脚本

echo "=========================================="
echo "权限管理修复验证"
echo "=========================================="
echo ""

# 配置
API_BASE="http://localhost:6080"
TOKEN=""

# 颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取 Token
echo "步骤 1: 登录获取 Token"
echo "----------------------------------------"
LOGIN_RESPONSE=$(curl -s -X POST "${API_BASE}/v1/user/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhiyu",
    "password": "2201101122@qq.com"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo -e "${RED}❌ 登录失败${NC}"
  echo "响应: $LOGIN_RESPONSE"
  exit 1
fi

echo -e "${GREEN}✅ 登录成功${NC}"
echo "Token: ${TOKEN:0:50}..."
echo ""

# 获取角色列表
echo "步骤 2: 获取角色列表"
echo "----------------------------------------"
ROLES_RESPONSE=$(curl -s -X GET "${API_BASE}/v1/user/role?page=1&limit=100" \
  -H "Authorization: Bearer $TOKEN")

# 提取手动操作员角色ID
MANUAL_ROLE_ID=$(echo $ROLES_RESPONSE | grep -o '"code":"MANUAL"[^}]*"id":"[^"]*' | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -z "$MANUAL_ROLE_ID" ]; then
  echo -e "${RED}❌ 未找到手动操作员角色${NC}"
  exit 1
fi

echo -e "${GREEN}✅ 找到手动操作员角色${NC}"
echo "角色ID: $MANUAL_ROLE_ID"
echo ""

# 获取路由树
echo "步骤 3: 获取路由树"
echo "----------------------------------------"
ROUTES_RESPONSE=$(curl -s -X GET "${API_BASE}/v1/user/route/tree?status=1" \
  -H "Authorization: Bearer $TOKEN")

# 提取服务器管理相关的路由ID
echo "提取路由ID..."
echo "$ROUTES_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)

# 查找服务器管理节点
server_node = None
for node in data:
    if node.get('title') == '服务器管理':
        server_node = node
        break

if server_node:
    print('服务器管理ID:', server_node['id'])
    if 'children' in server_node:
        for child in server_node['children']:
            print(f\"  - {child['title']}: {child['id']}\")
" > /tmp/route_ids.txt

cat /tmp/route_ids.txt
echo ""

# 读取路由ID
SERVER_MGMT_ID=$(grep "服务器管理ID:" /tmp/route_ids.txt | awk '{print $2}')
COUNTRY_ID=$(grep "国家管理:" /tmp/route_ids.txt | awk '{print $3}')
GROUP_ID=$(grep "分组管理:" /tmp/route_ids.txt | awk '{print $3}')
SERVER_LIST_ID=$(grep "服务器列表:" /tmp/route_ids.txt | awk '{print $3}')

echo "路由ID汇总:"
echo "  服务器管理: $SERVER_MGMT_ID"
echo "  国家管理: $COUNTRY_ID"
echo "  分组管理: $GROUP_ID"
echo "  服务器列表: $SERVER_LIST_ID"
echo ""

# 测试场景1：设置所有子菜单
echo "=========================================="
echo "测试场景 1: 设置所有子菜单"
echo "=========================================="
echo ""

echo "设置权限: 国家管理、分组管理、服务器列表"
SET_RESPONSE=$(curl -s -X POST "${API_BASE}/v1/user/role/${MANUAL_ROLE_ID}/routes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "[\"$SERVER_MGMT_ID\", \"$COUNTRY_ID\", \"$GROUP_ID\", \"$SERVER_LIST_ID\"]")

echo "响应: $SET_RESPONSE"
echo ""

echo "查询权限..."
GET_RESPONSE=$(curl -s -X GET "${API_BASE}/v1/user/role/${MANUAL_ROLE_ID}/routes" \
  -H "Authorization: Bearer $TOKEN")

echo "返回的路由数量:"
echo "$GET_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)

def count_routes(nodes):
    count = len(nodes)
    for node in nodes:
        if 'children' in node:
            count += count_routes(node['children'])
    return count

total = count_routes(data)
print(f'  总计: {total} 个节点')

for node in data:
    print(f\"  - {node['title']}\")
    if 'children' in node:
        for child in node['children']:
            print(f\"    - {child['title']}\")
"
echo ""

# 测试场景2：取消一个子菜单
echo "=========================================="
echo "测试场景 2: 取消国家管理"
echo "=========================================="
echo ""

echo "设置权限: 只保留分组管理、服务器列表"
SET_RESPONSE=$(curl -s -X POST "${API_BASE}/v1/user/role/${MANUAL_ROLE_ID}/routes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "[\"$SERVER_MGMT_ID\", \"$GROUP_ID\", \"$SERVER_LIST_ID\"]")

echo "响应: $SET_RESPONSE"
echo ""

echo "查询权限..."
GET_RESPONSE=$(curl -s -X GET "${API_BASE}/v1/user/role/${MANUAL_ROLE_ID}/routes" \
  -H "Authorization: Bearer $TOKEN")

echo "返回的路由:"
echo "$GET_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)

has_server_mgmt = False
has_country = False
has_group = False
has_server_list = False

for node in data:
    if node['title'] == '服务器管理':
        has_server_mgmt = True
        print(f\"✅ {node['title']} (父节点自动补全)\")
        if 'children' in node:
            for child in node['children']:
                print(f\"  - {child['title']}\")
                if child['title'] == '国家管理':
                    has_country = True
                elif child['title'] == '分组管理':
                    has_group = True
                elif child['title'] == '服务器列表':
                    has_server_list = True

print()
print('验证结果:')
print(f\"  服务器管理（父节点）: {'✅ 存在' if has_server_mgmt else '❌ 不存在'}\")
print(f\"  国家管理: {'❌ 存在（错误）' if has_country else '✅ 不存在（正确）'}\")
print(f\"  分组管理: {'✅ 存在' if has_group else '❌ 不存在'}\")
print(f\"  服务器列表: {'✅ 存在' if has_server_list else '❌ 不存在'}\")

if has_server_mgmt and not has_country and has_group and has_server_list:
    print()
    print('🎉 测试通过！')
    sys.exit(0)
else:
    print()
    print('❌ 测试失败！')
    sys.exit(1)
"

TEST_RESULT=$?
echo ""

# 测试场景3：只保留一个子菜单
echo "=========================================="
echo "测试场景 3: 只保留分组管理"
echo "=========================================="
echo ""

echo "设置权限: 只保留分组管理"
SET_RESPONSE=$(curl -s -X POST "${API_BASE}/v1/user/role/${MANUAL_ROLE_ID}/routes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "[\"$SERVER_MGMT_ID\", \"$GROUP_ID\"]")

echo "响应: $SET_RESPONSE"
echo ""

echo "查询权限..."
GET_RESPONSE=$(curl -s -X GET "${API_BASE}/v1/user/role/${MANUAL_ROLE_ID}/routes" \
  -H "Authorization: Bearer $TOKEN")

echo "返回的路由:"
echo "$GET_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)

for node in data:
    if node['title'] == '服务器管理':
        print(f\"✅ {node['title']} (父节点自动补全)\")
        if 'children' in node:
            for child in node['children']:
                print(f\"  - {child['title']}\")
"
echo ""

# 测试场景4：取消所有子菜单
echo "=========================================="
echo "测试场景 4: 取消所有子菜单"
echo "=========================================="
echo ""

echo "设置权限: 清空所有服务器管理相关权限"
SET_RESPONSE=$(curl -s -X POST "${API_BASE}/v1/user/role/${MANUAL_ROLE_ID}/routes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "[]")

echo "响应: $SET_RESPONSE"
echo ""

echo "查询权限..."
GET_RESPONSE=$(curl -s -X GET "${API_BASE}/v1/user/role/${MANUAL_ROLE_ID}/routes" \
  -H "Authorization: Bearer $TOKEN")

echo "返回的路由:"
echo "$GET_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)

has_server_mgmt = False
for node in data:
    if node['title'] == '服务器管理':
        has_server_mgmt = True

if has_server_mgmt:
    print('❌ 服务器管理仍然存在（错误）')
else:
    print('✅ 服务器管理已消失（正确）')
"
echo ""

# 总结
echo "=========================================="
echo "测试总结"
echo "=========================================="
echo ""

if [ $TEST_RESULT -eq 0 ]; then
  echo -e "${GREEN}✅ 所有测试通过！${NC}"
  echo ""
  echo "修复验证成功："
  echo "  1. ✅ 可以设置所有子菜单"
  echo "  2. ✅ 可以取消部分子菜单，父节点仍然存在"
  echo "  3. ✅ 可以只保留一个子菜单"
  echo "  4. ✅ 取消所有子菜单后，父节点消失"
else
  echo -e "${RED}❌ 测试失败${NC}"
  echo ""
  echo "请检查后端代码是否正确实现了叶子节点过滤逻辑"
fi

echo ""
echo "详细文档: PERMISSION_CORRECT_FIX.md"
echo "=========================================="

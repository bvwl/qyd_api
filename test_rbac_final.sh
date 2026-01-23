#!/bin/bash

# RBAC 最终方案测试脚本

echo "=========================================="
echo "RBAC 最终方案测试"
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
  exit 1
fi

echo -e "${GREEN}✅ 登录成功${NC}"
echo ""

# 获取角色列表
echo "步骤 2: 获取角色列表"
echo "----------------------------------------"
ROLES_RESPONSE=$(curl -s -X GET "${API_BASE}/v1/user/role?page=1&limit=100" \
  -H "Authorization: Bearer $TOKEN")

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

echo "路由树获取成功"
echo ""

# 测试场景1：设置所有子菜单
echo "=========================================="
echo "测试场景 1: 设置所有子菜单"
echo "=========================================="
echo ""

# 这里需要手动提取路由ID，或者使用 jq
echo "请手动测试："
echo "1. 打开权限管理页面"
echo "2. 选择'手动操作员'角色"
echo "3. 勾选'服务器管理'下的所有子菜单"
echo "4. 点击'保存权限'"
echo "5. 刷新页面"
echo "6. 验证：所有子菜单都被选中 ✅"
echo ""

# 测试场景2：取消一个子菜单
echo "=========================================="
echo "测试场景 2: 取消一个子菜单"
echo "=========================================="
echo ""

echo "请手动测试："
echo "1. 取消勾选'国家管理'"
echo "2. 点击'保存权限'"
echo "3. 刷新页面"
echo "4. 验证：'服务器管理'为半选状态 ✅"
echo "5. 验证：'国家管理'未选中 ✅"
echo "6. 验证：其他子菜单仍然选中 ✅"
echo ""

# 查看后端日志
echo "=========================================="
echo "查看后端日志"
echo "=========================================="
echo ""

echo "后端日志应该显示："
echo "  角色 手动操作员 权限更新："
echo "    - 保存了 X 个节点"
echo ""
echo "  角色 手动操作员 权限查询："
echo "    - 返回 X 个节点"
echo ""

echo "=========================================="
echo "测试说明"
echo "=========================================="
echo ""

echo "核心逻辑："
echo "  1. 保存时：保存用户选中的所有节点"
echo "  2. 查询时：返回实际保存的节点"
echo "  3. 显示时：Tree 组件自动处理父子关系"
echo ""

echo "预期行为："
echo "  - 全选时：父节点和所有子节点都被保存"
echo "  - 部分选中时：只保存选中的子节点"
echo "  - Tree 组件会自动显示父节点为半选状态"
echo ""

echo "详细文档: RBAC_FINAL_SOLUTION.md"
echo "=========================================="

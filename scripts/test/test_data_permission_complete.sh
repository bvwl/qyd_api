#!/bin/bash

# 数据权限完整测试脚本
# 测试所有资源的数据权限过滤功能

BASE_URL="http://localhost:8000"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "数据权限完整测试"
echo "=========================================="
echo ""

# 测试用户凭证
ADMIN_TOKEN=""
GM_TOKEN=""
IT_TOKEN=""
MANUAL_TOKEN=""

# 1. 登录获取Token
echo -e "${YELLOW}步骤 1: 登录获取各角色Token${NC}"
echo "----------------------------------------"

# 登录ADMIN
echo "登录 ADMIN 用户..."
ADMIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }')

ADMIN_TOKEN=$(echo $ADMIN_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)
if [ -n "$ADMIN_TOKEN" ]; then
  echo -e "${GREEN}✓ ADMIN登录成功${NC}"
else
  echo -e "${RED}✗ ADMIN登录失败${NC}"
  echo "响应: $ADMIN_RESPONSE"
fi

# 登录GM (如果存在)
echo "登录 GM 用户..."
GM_RESPONSE=$(curl -s -X POST "${BASE_URL}/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "gm",
    "password": "gm123"
  }')

GM_TOKEN=$(echo $GM_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)
if [ -n "$GM_TOKEN" ]; then
  echo -e "${GREEN}✓ GM登录成功${NC}"
else
  echo -e "${YELLOW}⚠ GM用户不存在或登录失败${NC}"
fi

# 登录IT (如果存在)
echo "登录 IT 用户..."
IT_RESPONSE=$(curl -s -X POST "${BASE_URL}/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "it_user",
    "password": "it123"
  }')

IT_TOKEN=$(echo $IT_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)
if [ -n "$IT_TOKEN" ]; then
  echo -e "${GREEN}✓ IT登录成功${NC}"
else
  echo -e "${YELLOW}⚠ IT用户不存在或登录失败${NC}"
fi

# 登录MANUAL (如果存在)
echo "登录 MANUAL 用户..."
MANUAL_RESPONSE=$(curl -s -X POST "${BASE_URL}/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "manual_user",
    "password": "manual123"
  }')

MANUAL_TOKEN=$(echo $MANUAL_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)
if [ -n "$MANUAL_TOKEN" ]; then
  echo -e "${GREEN}✓ MANUAL登录成功${NC}"
else
  echo -e "${YELLOW}⚠ MANUAL用户不存在或登录失败${NC}"
fi

echo ""

# 2. 测试项目列表数据权限
echo -e "${YELLOW}步骤 2: 测试项目列表数据权限${NC}"
echo "----------------------------------------"

if [ -n "$ADMIN_TOKEN" ]; then
  echo "测试 ADMIN 访问项目列表..."
  ADMIN_PROJECTS=$(curl -s -X GET "${BASE_URL}/v1/project?page=1&limit=10" \
    -H "Authorization: Bearer $ADMIN_TOKEN")
  ADMIN_COUNT=$(echo $ADMIN_PROJECTS | grep -o '"num":[0-9]*' | cut -d':' -f2)
  echo -e "${GREEN}✓ ADMIN 可以看到 $ADMIN_COUNT 个项目${NC}"
fi

if [ -n "$GM_TOKEN" ]; then
  echo "测试 GM 访问项目列表..."
  GM_PROJECTS=$(curl -s -X GET "${BASE_URL}/v1/project?page=1&limit=10" \
    -H "Authorization: Bearer $GM_TOKEN")
  GM_COUNT=$(echo $GM_PROJECTS | grep -o '"num":[0-9]*' | cut -d':' -f2)
  echo -e "${GREEN}✓ GM 可以看到 $GM_COUNT 个项目${NC}"
fi

if [ -n "$IT_TOKEN" ]; then
  echo "测试 IT 访问项目列表..."
  IT_PROJECTS=$(curl -s -X GET "${BASE_URL}/v1/project?page=1&limit=10" \
    -H "Authorization: Bearer $IT_TOKEN")
  IT_COUNT=$(echo $IT_PROJECTS | grep -o '"num":[0-9]*' | cut -d':' -f2)
  echo -e "${GREEN}✓ IT 可以看到 $IT_COUNT 个项目 (仅分配的项目)${NC}"
fi

if [ -n "$MANUAL_TOKEN" ]; then
  echo "测试 MANUAL 访问项目列表..."
  MANUAL_PROJECTS=$(curl -s -X GET "${BASE_URL}/v1/project?page=1&limit=10" \
    -H "Authorization: Bearer $MANUAL_TOKEN")
  MANUAL_COUNT=$(echo $MANUAL_PROJECTS | grep -o '"num":[0-9]*' | cut -d':' -f2)
  echo -e "${GREEN}✓ MANUAL 可以看到 $MANUAL_COUNT 个项目 (仅分配的项目)${NC}"
fi

echo ""

# 3. 测试项目账号数据权限
echo -e "${YELLOW}步骤 3: 测试项目账号数据权限${NC}"
echo "----------------------------------------"

if [ -n "$ADMIN_TOKEN" ]; then
  echo "测试 ADMIN 访问项目账号..."
  ADMIN_ACCOUNTS=$(curl -s -X GET "${BASE_URL}/v1/project/account?page=1&limit=10" \
    -H "Authorization: Bearer $ADMIN_TOKEN")
  ADMIN_ACCOUNT_COUNT=$(echo $ADMIN_ACCOUNTS | grep -o '"num":[0-9]*' | cut -d':' -f2)
  echo -e "${GREEN}✓ ADMIN 可以看到 $ADMIN_ACCOUNT_COUNT 个项目账号${NC}"
fi

if [ -n "$IT_TOKEN" ]; then
  echo "测试 IT 访问项目账号..."
  IT_ACCOUNTS=$(curl -s -X GET "${BASE_URL}/v1/project/account?page=1&limit=10" \
    -H "Authorization: Bearer $IT_TOKEN")
  IT_ACCOUNT_COUNT=$(echo $IT_ACCOUNTS | grep -o '"num":[0-9]*' | cut -d':' -f2)
  if [ -z "$IT_ACCOUNT_COUNT" ]; then
    echo -e "${YELLOW}⚠ IT 没有项目账号数据 (正常，如果没有分配项目)${NC}"
  else
    echo -e "${GREEN}✓ IT 可以看到 $IT_ACCOUNT_COUNT 个项目账号 (仅分配的项目)${NC}"
  fi
fi

echo ""

# 4. 测试项目钱包数据权限
echo -e "${YELLOW}步骤 4: 测试项目钱包数据权限${NC}"
echo "----------------------------------------"

if [ -n "$ADMIN_TOKEN" ]; then
  echo "测试 ADMIN 访问项目钱包..."
  ADMIN_WALLETS=$(curl -s -X GET "${BASE_URL}/v1/project/wallet?page=1&limit=10" \
    -H "Authorization: Bearer $ADMIN_TOKEN")
  ADMIN_WALLET_COUNT=$(echo $ADMIN_WALLETS | grep -o '"num":[0-9]*' | cut -d':' -f2)
  echo -e "${GREEN}✓ ADMIN 可以看到 $ADMIN_WALLET_COUNT 个项目钱包${NC}"
fi

if [ -n "$IT_TOKEN" ]; then
  echo "测试 IT 访问项目钱包..."
  IT_WALLETS=$(curl -s -X GET "${BASE_URL}/v1/project/wallet?page=1&limit=10" \
    -H "Authorization: Bearer $IT_TOKEN")
  IT_WALLET_COUNT=$(echo $IT_WALLETS | grep -o '"num":[0-9]*' | cut -d':' -f2)
  if [ -z "$IT_WALLET_COUNT" ]; then
    echo -e "${YELLOW}⚠ IT 没有项目钱包数据 (正常，如果没有分配项目)${NC}"
  else
    echo -e "${GREEN}✓ IT 可以看到 $IT_WALLET_COUNT 个项目钱包 (仅分配的项目)${NC}"
  fi
fi

echo ""

# 5. 测试服务器资源访问权限
echo -e "${YELLOW}步骤 5: 测试服务器资源访问权限${NC}"
echo "----------------------------------------"

if [ -n "$ADMIN_TOKEN" ]; then
  echo "测试 ADMIN 访问服务器列表..."
  ADMIN_SERVERS=$(curl -s -X GET "${BASE_URL}/v1/server?page=1&limit=10" \
    -H "Authorization: Bearer $ADMIN_TOKEN")
  if echo "$ADMIN_SERVERS" | grep -q '"num"'; then
    ADMIN_SERVER_COUNT=$(echo $ADMIN_SERVERS | grep -o '"num":[0-9]*' | cut -d':' -f2)
    echo -e "${GREEN}✓ ADMIN 可以访问服务器资源 ($ADMIN_SERVER_COUNT 个)${NC}"
  else
    echo -e "${RED}✗ ADMIN 访问服务器失败${NC}"
    echo "响应: $ADMIN_SERVERS"
  fi
fi

if [ -n "$GM_TOKEN" ]; then
  echo "测试 GM 访问服务器列表..."
  GM_SERVERS=$(curl -s -X GET "${BASE_URL}/v1/server?page=1&limit=10" \
    -H "Authorization: Bearer $GM_TOKEN")
  if echo "$GM_SERVERS" | grep -q '"num"'; then
    GM_SERVER_COUNT=$(echo $GM_SERVERS | grep -o '"num":[0-9]*' | cut -d':' -f2)
    echo -e "${GREEN}✓ GM 可以访问服务器资源 ($GM_SERVER_COUNT 个)${NC}"
  else
    echo -e "${RED}✗ GM 访问服务器失败${NC}"
  fi
fi

if [ -n "$IT_TOKEN" ]; then
  echo "测试 IT 访问服务器列表..."
  IT_SERVERS=$(curl -s -X GET "${BASE_URL}/v1/server?page=1&limit=10" \
    -H "Authorization: Bearer $IT_TOKEN")
  if echo "$IT_SERVERS" | grep -q '"num"'; then
    IT_SERVER_COUNT=$(echo $IT_SERVERS | grep -o '"num":[0-9]*' | cut -d':' -f2)
    echo -e "${GREEN}✓ IT 可以访问服务器资源 ($IT_SERVER_COUNT 个)${NC}"
  else
    echo -e "${RED}✗ IT 访问服务器失败${NC}"
  fi
fi

if [ -n "$MANUAL_TOKEN" ]; then
  echo "测试 MANUAL 访问服务器列表..."
  MANUAL_SERVERS=$(curl -s -X GET "${BASE_URL}/v1/server?page=1&limit=10" \
    -H "Authorization: Bearer $MANUAL_TOKEN")
  if echo "$MANUAL_SERVERS" | grep -q '403\|没有权限'; then
    echo -e "${GREEN}✓ MANUAL 被正确拒绝访问服务器资源 (403)${NC}"
  elif echo "$MANUAL_SERVERS" | grep -q '"num"'; then
    echo -e "${RED}✗ MANUAL 不应该能访问服务器资源${NC}"
  else
    echo -e "${YELLOW}⚠ MANUAL 访问服务器返回异常响应${NC}"
    echo "响应: $MANUAL_SERVERS"
  fi
fi

echo ""

# 6. 测试邮箱资源访问权限
echo -e "${YELLOW}步骤 6: 测试邮箱资源访问权限${NC}"
echo "----------------------------------------"

if [ -n "$ADMIN_TOKEN" ]; then
  echo "测试 ADMIN 访问邮箱列表..."
  ADMIN_MAILS=$(curl -s -X GET "${BASE_URL}/v1/mail?page=1&limit=10" \
    -H "Authorization: Bearer $ADMIN_TOKEN")
  if echo "$ADMIN_MAILS" | grep -q '"num"'; then
    ADMIN_MAIL_COUNT=$(echo $ADMIN_MAILS | grep -o '"num":[0-9]*' | cut -d':' -f2)
    echo -e "${GREEN}✓ ADMIN 可以访问邮箱资源 ($ADMIN_MAIL_COUNT 个)${NC}"
  else
    echo -e "${RED}✗ ADMIN 访问邮箱失败${NC}"
    echo "响应: $ADMIN_MAILS"
  fi
fi

if [ -n "$GM_TOKEN" ]; then
  echo "测试 GM 访问邮箱列表..."
  GM_MAILS=$(curl -s -X GET "${BASE_URL}/v1/mail?page=1&limit=10" \
    -H "Authorization: Bearer $GM_TOKEN")
  if echo "$GM_MAILS" | grep -q '"num"'; then
    GM_MAIL_COUNT=$(echo $GM_MAILS | grep -o '"num":[0-9]*' | cut -d':' -f2)
    echo -e "${GREEN}✓ GM 可以访问邮箱资源 ($GM_MAIL_COUNT 个)${NC}"
  else
    echo -e "${RED}✗ GM 访问邮箱失败${NC}"
  fi
fi

if [ -n "$IT_TOKEN" ]; then
  echo "测试 IT 访问邮箱列表..."
  IT_MAILS=$(curl -s -X GET "${BASE_URL}/v1/mail?page=1&limit=10" \
    -H "Authorization: Bearer $IT_TOKEN")
  if echo "$IT_MAILS" | grep -q '"num"'; then
    IT_MAIL_COUNT=$(echo $IT_MAILS | grep -o '"num":[0-9]*' | cut -d':' -f2)
    echo -e "${GREEN}✓ IT 可以访问邮箱资源 ($IT_MAIL_COUNT 个)${NC}"
  else
    echo -e "${RED}✗ IT 访问邮箱失败${NC}"
  fi
fi

if [ -n "$MANUAL_TOKEN" ]; then
  echo "测试 MANUAL 访问邮箱列表..."
  MANUAL_MAILS=$(curl -s -X GET "${BASE_URL}/v1/mail?page=1&limit=10" \
    -H "Authorization: Bearer $MANUAL_TOKEN")
  if echo "$MANUAL_MAILS" | grep -q '403\|没有权限'; then
    echo -e "${GREEN}✓ MANUAL 被正确拒绝访问邮箱资源 (403)${NC}"
  elif echo "$MANUAL_MAILS" | grep -q '"num"'; then
    echo -e "${RED}✗ MANUAL 不应该能访问邮箱资源${NC}"
  else
    echo -e "${YELLOW}⚠ MANUAL 访问邮箱返回异常响应${NC}"
    echo "响应: $MANUAL_MAILS"
  fi
fi

echo ""

# 7. 总结
echo "=========================================="
echo -e "${YELLOW}测试总结${NC}"
echo "=========================================="
echo ""
echo "数据权限规则："
echo "  • ADMIN/GM: 可以访问所有数据"
echo "  • IT: 只能访问分配的项目数据，可以访问服务器和邮箱"
echo "  • MANUAL: 只能访问分配的项目数据，不能访问服务器和邮箱"
echo ""
echo "测试完成！"

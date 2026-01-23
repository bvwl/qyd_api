#!/bin/bash

BASE_URL="http://localhost:6080"

echo "=========================================="
echo "测试API数据权限过滤（重启后）"
echo "=========================================="
echo ""

# 测试admin用户
echo "1. 测试 ADMIN 用户"
echo "----------------------------------------"
ADMIN_LOGIN=$(curl -s -X POST "${BASE_URL}/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"zhiyu","password":"admin123"}')

ADMIN_TOKEN=$(echo "$ADMIN_LOGIN" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)

if [ -n "$ADMIN_TOKEN" ]; then
  echo "✅ ADMIN 登录成功"
  
  # 获取所有账号
  ADMIN_ACCOUNTS=$(curl -s -X GET "${BASE_URL}/v1/project/account?page=1&limit=100&res_count=true" \
    -H "Authorization: Bearer $ADMIN_TOKEN")
  
  ADMIN_COUNT=$(echo "$ADMIN_ACCOUNTS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
  ADMIN_NUM=$(echo "$ADMIN_ACCOUNTS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('num', 0))" 2>/dev/null)
  
  echo "ADMIN 看到的账号数: count=$ADMIN_COUNT, num=$ADMIN_NUM"
  echo "账号列表:"
  echo "$ADMIN_ACCOUNTS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    items = data.get('items', [])
    for item in items:
        project_name = item.get('project', {}).get('name', '无项目')
        print(f\"  - {item['account']} (项目: {project_name})\")
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null
else
  echo "❌ ADMIN 登录失败"
fi

echo ""
echo "2. 测试 IT/MANUAL 用户 (2201101122@qq.com)"
echo "----------------------------------------"

# 尝试不同的密码
for PASSWORD in "123456" "admin123" "password" "2201101122"; do
  USER_LOGIN=$(curl -s -X POST "${BASE_URL}/v1/user/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"2201101122@qq.com\",\"password\":\"$PASSWORD\"}")
  
  USER_TOKEN=$(echo "$USER_LOGIN" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)
  
  if [ -n "$USER_TOKEN" ]; then
    echo "✅ 用户登录成功 (密码: $PASSWORD)"
    
    # 获取用户的项目
    USER_PROJECTS=$(curl -s -X GET "${BASE_URL}/v1/project?page=1&limit=100&res_count=true" \
      -H "Authorization: Bearer $USER_TOKEN")
    
    PROJECT_COUNT=$(echo "$USER_PROJECTS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
    echo "用户关联的项目数: $PROJECT_COUNT"
    echo "项目列表:"
    echo "$USER_PROJECTS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    items = data.get('items', [])
    for item in items:
        print(f\"  - {item['name']} (ID: {item['id']})\")
except:
    pass
" 2>/dev/null
    
    # 获取所有账号
    USER_ACCOUNTS=$(curl -s -X GET "${BASE_URL}/v1/project/account?page=1&limit=100&res_count=true" \
      -H "Authorization: Bearer $USER_TOKEN")
    
    USER_COUNT=$(echo "$USER_ACCOUNTS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
    USER_NUM=$(echo "$USER_ACCOUNTS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('num', 0))" 2>/dev/null)
    
    echo ""
    echo "用户看到的账号数: count=$USER_COUNT, num=$USER_NUM"
    echo "账号列表:"
    echo "$USER_ACCOUNTS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    items = data.get('items', [])
    for item in items:
        project_name = item.get('project', {}).get('name', '无项目')
        print(f\"  - {item['account']} (项目: {project_name})\")
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null
    
    echo ""
    echo "预期: 用户应该只看到 3 个账号（2个项目：1个账号+2个账号）"
    if [ "$USER_NUM" -eq 3 ]; then
      echo "✅ 数据权限过滤正确"
    else
      echo "❌ 数据权限过滤有问题，实际看到 $USER_NUM 个账号"
    fi
    
    break
  fi
done

if [ -z "$USER_TOKEN" ]; then
  echo "❌ 用户登录失败，尝试了多个密码都不对"
  echo "请手动提供正确的密码"
fi

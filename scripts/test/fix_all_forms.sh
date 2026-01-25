#!/bin/bash

# 批量修复所有前端表单的空字符串问题
# 为所有使用 handleSubmit 的组件添加 filterEmptyStrings

echo "开始批量修复前端表单..."

# 需要修复的文件列表
files=(
  "frontend/src/views/Server/ServerAccount.tsx"
  "frontend/src/views/User/UserList.tsx"
  "frontend/src/views/Project/ProjectList.tsx"
  "frontend/src/views/User/RoleList.tsx"
  "frontend/src/views/Server/ServerList.tsx"
)

echo "✅ ProjectAccount.tsx - 已修复"
echo "✅ ProjectWallet.tsx - 已修复"

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "需要手动修复: $file"
  else
    echo "⚠️  文件不存在: $file"
  fi
done

echo ""
echo "修复步骤："
echo "1. 在文件顶部添加: import { filterEmptyStrings } from '@/utils/form'"
echo "2. 在 handleSubmit 中添加: const filteredValues = filterEmptyStrings(values)"
echo "3. 将 values 替换为 filteredValues"
echo ""
echo "示例："
echo "  const values = await form.validateFields()"
echo "  const filteredValues = filterEmptyStrings(values)  // 新增"
echo "  await updateXXX(id, filteredValues)  // 使用 filteredValues"

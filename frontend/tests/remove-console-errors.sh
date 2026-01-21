#!/bin/bash

# 批量移除前端页面中的 console.error 行
# 使用方法: chmod +x remove-console-errors.sh && ./remove-console-errors.sh

echo "开始移除 console.error..."

# 查找所有 .tsx 文件并移除 console.error 行
find src/views -name "*.tsx" -type f | while read file; do
  if grep -q "console\.error" "$file"; then
    echo "处理: $file"
    # 使用 sed 删除包含 console.error 的行
    sed -i.bak '/console\.error/d' "$file"
    # 删除备份文件
    rm "${file}.bak" 2>/dev/null || true
  fi
done

echo "完成！"
echo "建议: 刷新浏览器查看效果"

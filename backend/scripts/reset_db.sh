#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${BACKEND_DIR}"

# 加载环境变量
if [ -f ".env" ]; then
  set -a
  . ".env"
  set +a
fi

echo "⚠️  警告: 这将删除所有数据库表和迁移记录！"
read -p "确定要继续吗? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "已取消"
  exit 0
fi

echo "正在删除迁移文件夹..."
rm -rf migrations

echo "正在重新初始化迁移..."
aerich init -t app.core.settings.TORTOISE_ORM

echo "正在创建初始迁移..."
aerich init-db

echo "✅ 数据库重置完成！"

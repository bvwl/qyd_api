#!/bin/bash

# 项目文件整理脚本
# 将根目录的文档文件移动到对应的分类文件夹

echo "开始整理项目文件..."

# 创建文档分类文件夹
mkdir -p docs/features/wallet
mkdir -p docs/features/project
mkdir -p docs/features/xui
mkdir -p docs/features/server
mkdir -p docs/features/security
mkdir -p docs/features/api-token
mkdir -p docs/features/frontend
mkdir -p docs/features/redis
mkdir -p docs/features/proxy
mkdir -p docs/infrastructure
mkdir -p scripts/test

# 移动钱包相关文档
echo "整理钱包相关文档..."
mv 批量创建钱包*.md docs/features/wallet/ 2>/dev/null
mv WALLET_*.md docs/features/wallet/ 2>/dev/null
mv INSTALL_WALLET_BATCH_CREATE.md docs/features/wallet/ 2>/dev/null

# 移动项目管理相关文档
echo "整理项目管理相关文档..."
mv PROJECT_*.md docs/features/project/ 2>/dev/null
mv 项目统计*.md docs/features/project/ 2>/dev/null
mv ORGANIZATION_COMPLETE.md docs/features/project/ 2>/dev/null

# 移动XUI相关文档
echo "整理XUI相关文档..."
mv XUI_*.md docs/features/xui/ 2>/dev/null

# 移动服务器管理相关文档
echo "整理服务器管理相关文档..."
mv SERVER_*.md docs/features/server/ 2>/dev/null

# 移动安全日志相关文档
echo "整理安全日志相关文档..."
mv SECURITY_*.md docs/features/security/ 2>/dev/null

# 移动API Token相关文档
echo "整理API Token相关文档..."
mv API_TOKEN_*.md docs/features/api-token/ 2>/dev/null
mv TOKEN_*.md docs/features/api-token/ 2>/dev/null

# 移动前端相关文档
echo "整理前端相关文档..."
mv FRONTEND_*.md docs/features/frontend/ 2>/dev/null
mv 仪表盘*.md docs/features/frontend/ 2>/dev/null

# 移动Redis相关文档
echo "整理Redis相关文档..."
mv REDIS_*.md docs/features/redis/ 2>/dev/null

# 移动代理相关文档
echo "整理代理相关文档..."
mv PROXY_*.md docs/features/proxy/ 2>/dev/null

# 移动基础设施相关文档
echo "整理基础设施相关文档..."
mv 读写分离*.md docs/infrastructure/ 2>/dev/null
mv 时间参数*.md docs/infrastructure/ 2>/dev/null
mv TIME_PARAMETER_FIX.md docs/infrastructure/ 2>/dev/null

# 移动测试脚本
echo "整理测试脚本..."
mv test_*.sh scripts/test/ 2>/dev/null
mv fix_all_forms.sh scripts/test/ 2>/dev/null

# 移动队列处理脚本
echo "整理队列处理脚本..."
mv start_queue_processing.sh scripts/ 2>/dev/null

# 保留在根目录的文件
# - README.md
# - QUICK_START_GUIDE.md
# - .gitignore
# - .DS_Store

echo "文件整理完成！"
echo ""
echo "文件夹结构："
echo "docs/features/wallet/        - 钱包功能文档"
echo "docs/features/project/       - 项目管理文档"
echo "docs/features/xui/           - XUI集成文档"
echo "docs/features/server/        - 服务器管理文档"
echo "docs/features/security/      - 安全日志文档"
echo "docs/features/api-token/     - API Token文档"
echo "docs/features/frontend/      - 前端功能文档"
echo "docs/features/redis/         - Redis相关文档"
echo "docs/features/proxy/         - 代理功能文档"
echo "docs/infrastructure/         - 基础设施文档"
echo "scripts/test/                - 测试脚本"

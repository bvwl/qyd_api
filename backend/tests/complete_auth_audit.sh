#!/bin/bash

# 完成 API 认证审计和文档整理
# 使用方法: chmod +x complete_auth_audit.sh && ./complete_auth_audit.sh

echo "========================================="
echo "API 认证审计和文档整理"
echo "========================================="
echo ""

# 1. 备份当前 README
echo "1. 备份当前 README..."
cp README.md README.md.backup
echo "✅ 已备份到 README.md.backup"
echo ""

# 2. 替换 README
echo "2. 更新 README..."
cp README_NEW.md README.md
echo "✅ README 已更新"
echo ""

# 3. 删除多余的文档
echo "3. 删除多余的文档..."
rm -f JWT_IMPLEMENTATION_GUIDE.md
rm -f API_TOKEN_IMPLEMENTATION.md
rm -f JWT_SUMMARY.md
rm -f QUICK_JWT_REFERENCE.md
rm -f QUICK_PASSWORD_REFERENCE.md
rm -f PASSWORD_ENCRYPTION_SUMMARY.md
rm -f USER_ROLE_MANAGEMENT_SUMMARY.md
rm -f CLEANUP_SUMMARY.md
rm -f FILE_ORGANIZATION.md
rm -f FIX_ROLE_IDS_ISSUE.md
rm -f JWT_COMPLETION_REPORT.md
echo "✅ 已删除多余文档"
echo ""

# 4. 保留的文档列表
echo "4. 保留的文档："
echo "   - README.md (主文档)"
echo "   - API_AUTHENTICATION_AUDIT.md (认证审计报告)"
echo "   - db/README.md (数据库说明)"
echo "   - db/INITIALIZATION_SUMMARY.md (初始化总结)"
echo "   - app/tests/README.md (测试说明)"
echo "   - app/logs/README.md (日志说明)"
echo "   - app/logs/USAGE.md (日志使用)"
echo ""

# 5. 提示手动任务
echo "========================================="
echo "需要手动完成的任务："
echo "========================================="
echo ""
echo "1. 为以下 10 个文件添加认证："
echo "   - app/apis/v1/mail/outlook.py"
echo "   - app/apis/v1/project/account.py"
echo "   - app/apis/v1/project/balance.py"
echo "   - app/apis/v1/server/country.py"
echo "   - app/apis/v1/server/group.py"
echo "   - app/apis/v1/server/info.py"
echo "   - app/apis/v1/user/log.py"
echo "   - app/apis/v1/user/role.py"
echo "   - app/apis/v1/user/route.py"
echo "   - app/apis/v1/user/token.py"
echo ""
echo "2. 在每个文件中："
echo "   a. 添加导入："
echo "      from fastapi import Depends"
echo "      from app.apis.deps import get_current_user"
echo ""
echo "   b. 为每个端点函数添加参数："
echo "      current_user: dict = Depends(get_current_user)"
echo ""
echo "3. 测试所有 API 端点"
echo ""
echo "4. 验证认证是否生效："
echo "   - 未认证请求应返回 401"
echo "   - JWT Token 认证应正常工作"
echo "   - API Token 认证应正常工作"
echo ""
echo "========================================="
echo "参考文档："
echo "========================================="
echo "- API_AUTHENTICATION_AUDIT.md - 详细的审计报告"
echo "- README.md - 更新后的主文档"
echo ""
echo "完成！"

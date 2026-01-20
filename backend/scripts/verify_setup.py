#!/usr/bin/env python
"""
项目完整性验证脚本

运行此脚本以验证所有模块、CRUD、API 是否正确配置
"""
import sys
from pathlib import Path

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

def verify_models():
    """验证所有模型"""
    print("🔍 验证模型...")
    try:
        from app.models.user import UserInfo, UserRole, UserToken, UserLog, FrontendRoute
        from app.models.project import ProjectInfo, ProjectAccount, ProjectWallet, ProjectBalance
        from app.models.server import ServerCountry, ServerGroup, ServerInfo, ServerAccount
        from app.models.mail import EmailInfo
        print("  ✅ 用户模块：UserInfo, UserRole, UserToken, UserLog, FrontendRoute")
        print("  ✅ 项目模块：ProjectInfo, ProjectAccount, ProjectWallet, ProjectBalance")
        print("  ✅ 服务器模块：ServerCountry, ServerGroup, ServerInfo, ServerAccount")
        print("  ✅ 邮箱模块：EmailInfo")
        return True
    except Exception as e:
        print(f"  ❌ 模型导入失败: {e}")
        return False

def verify_crud():
    """验证所有 CRUD"""
    print("\n🔍 验证 CRUD...")
    try:
        from app.crud.user.user import user_crud
        from app.crud.user.role import role_crud
        from app.crud.user.route import route_crud
        from app.crud.user.token import token_crud
        from app.crud.user.log import log_crud
        from app.crud.project.info import project_info_crud
        from app.crud.project.account import project_account_crud
        from app.crud.project.wallet import project_wallet_crud
        from app.crud.project.balance import project_balance_crud
        from app.crud.server.country import server_country_crud
        from app.crud.server.group import server_group_crud
        from app.crud.server.info import server_info_crud
        from app.crud.server.account import server_account_crud
        from app.crud.mail.info import email_info_crud
        print("  ✅ 用户模块：user_crud, role_crud, route_crud, token_crud, log_crud")
        print("  ✅ 项目模块：project_info_crud, project_account_crud, project_wallet_crud, project_balance_crud")
        print("  ✅ 服务器模块：server_country_crud, server_group_crud, server_info_crud, server_account_crud")
        print("  ✅ 邮箱模块：email_info_crud")
        return True
    except Exception as e:
        print(f"  ❌ CRUD 导入失败: {e}")
        return False

def verify_apis():
    """验证所有 API"""
    print("\n🔍 验证 API...")
    try:
        from app.apis.v1.user.auth import app as auth_app
        from app.apis.v1.user.user import app as user_app
        from app.apis.v1.user.role import app as role_app
        from app.apis.v1.user.route import app as route_app
        from app.apis.v1.user.token import app as token_app
        from app.apis.v1.user.log import app as log_app
        from app.apis.v1.project.info import app as project_info_app
        from app.apis.v1.project.account import app as project_account_app
        from app.apis.v1.project.wallet import app as project_wallet_app
        from app.apis.v1.project.balance import app as project_balance_app
        from app.apis.v1.server.country import app as server_country_app
        from app.apis.v1.server.group import app as server_group_app
        from app.apis.v1.server.info import app as server_info_app
        from app.apis.v1.server.account import app as server_account_app
        from app.apis.v1.mail.info import app as mail_info_app
        from app.apis.v1.mail.outlook import app as mail_outlook_app
        print("  ✅ 用户模块：auth, user, role, route, token, log")
        print("  ✅ 项目模块：info, account, wallet, balance")
        print("  ✅ 服务器模块：country, group, info, account")
        print("  ✅ 邮箱模块：info, outlook")
        return True
    except Exception as e:
        print(f"  ❌ API 导入失败: {e}")
        return False

def verify_app():
    """验证应用主入口"""
    print("\n🔍 验证应用主入口...")
    try:
        from app.main import app
        print("  ✅ FastAPI 应用导入成功")
        return True
    except Exception as e:
        print(f"  ❌ 应用导入失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("QYD API 后端服务 - 完整性验证")
    print("=" * 60)
    
    results = []
    results.append(("模型", verify_models()))
    results.append(("CRUD", verify_crud()))
    results.append(("API", verify_apis()))
    results.append(("应用", verify_app()))
    
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name:10s}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 所有验证通过！项目配置正确。")
        print("\n下一步：")
        print("  1. 配置 .env 文件（数据库连接信息）")
        print("  2. 运行 bash scripts/init_db.sh 初始化数据库")
        print("  3. 运行 python start.py 启动服务")
        return 0
    else:
        print("\n⚠️  部分验证失败，请检查错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())

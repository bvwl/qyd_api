#!/usr/bin/env python3
"""
检查账号数量问题
直接查询数据库，对比实际数据
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到路径
backend_dir = Path(__file__).parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

# 加载.env文件
env_path = backend_dir / '.env'
load_dotenv(env_path)
print(f"✓ 已加载环境变量: {env_path}")
print()

from tortoise import Tortoise
from app.core.settings import TORTOISE_ORM
from app.models.project import ProjectInfo, ProjectAccount
from app.models.user import UserInfo


async def main():
    # 初始化数据库
    await Tortoise.init(config=TORTOISE_ORM)
    
    print("=" * 60)
    print("检查账号数量问题")
    print("=" * 60)
    print()
    
    # 1. 获取所有项目
    print("1. 所有项目:")
    print("-" * 60)
    projects = await ProjectInfo.all()
    for project in projects:
        print(f"  - {project.name} (ID: {project.id})")
    print(f"\n总共 {len(projects)} 个项目\n")
    
    # 2. 获取所有账号
    print("2. 所有账号:")
    print("-" * 60)
    accounts = await ProjectAccount.all().prefetch_related('project')
    for account in accounts:
        project_name = account.project.name if account.project else "无项目"
        print(f"  - {account.account} (项目: {project_name}, ID: {account.id})")
    print(f"\n总共 {len(accounts)} 个账号\n")
    
    # 3. 按项目统计账号数量
    print("3. 按项目统计账号数量:")
    print("-" * 60)
    total_by_project = 0
    for project in projects:
        project_accounts = await ProjectAccount.filter(project_id=project.id).count()
        print(f"  - {project.name}: {project_accounts} 个账号")
        total_by_project += project_accounts
    print(f"\n按项目累加: {total_by_project} 个账号\n")
    
    # 4. 检查是否有账号没有关联项目
    print("4. 检查没有关联项目的账号:")
    print("-" * 60)
    orphan_accounts = await ProjectAccount.filter(project_id__isnull=True)
    if orphan_accounts:
        print(f"  发现 {len(orphan_accounts)} 个没有关联项目的账号:")
        for account in orphan_accounts:
            print(f"    - {account.account} (ID: {account.id})")
    else:
        print("  ✅ 没有孤立账号")
    print()
    
    # 5. 获取用户信息
    print("5. 用户及其关联的项目:")
    print("-" * 60)
    users = await UserInfo.all().prefetch_related('projects', 'roles')
    for user in users:
        roles = [role.code for role in user.roles]
        user_projects = [p.name for p in user.projects]
        # 使用email而不是username
        print(f"  - {user.email} (角色: {', '.join(roles)})")
        if user_projects:
            print(f"    关联项目: {', '.join(user_projects)}")
        else:
            print(f"    关联项目: 无")
    print()
    
    # 6. 模拟数据权限过滤
    print("6. 模拟数据权限过滤:")
    print("-" * 60)
    
    # 获取一个非管理员用户
    test_user = None
    for user in users:
        roles = [role.code for role in user.roles]
        if 'ADMIN' not in roles and 'GM' not in roles:
            test_user = user
            break
    
    if test_user:
        print(f"测试用户: {test_user.username}")
        user_project_ids = [str(p.id) for p in test_user.projects]
        print(f"用户关联的项目ID: {user_project_ids}")
        
        if user_project_ids:
            # 查询该用户能看到的账号
            filtered_accounts = await ProjectAccount.filter(
                project_id__in=user_project_ids
            ).prefetch_related('project')
            
            print(f"\n该用户能看到的账号 ({len(filtered_accounts)} 个):")
            for account in filtered_accounts:
                project_name = account.project.name if account.project else "无项目"
                print(f"  - {account.account} (项目: {project_name})")
        else:
            print("该用户没有关联任何项目，应该看不到任何账号")
    else:
        print("没有找到非管理员用户进行测试")
    print()
    
    # 7. 总结
    print("=" * 60)
    print("总结:")
    print("=" * 60)
    print(f"项目总数: {len(projects)}")
    print(f"账号总数: {len(accounts)}")
    print(f"按项目累加: {total_by_project}")
    print(f"孤立账号: {len(orphan_accounts)}")
    
    if len(accounts) != total_by_project:
        print("\n⚠️  发现不一致！")
        print(f"差异: {len(accounts)} - {total_by_project} = {len(accounts) - total_by_project}")
    else:
        print("\n✅ 数据一致")

if __name__ == '__main__':
    asyncio.run(main())
    # 关闭数据库连接
    asyncio.run(Tortoise.close_connections())

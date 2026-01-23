#!/usr/bin/env python3
"""
测试 filter_by_user_projects 函数
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到路径
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

# 加载.env文件
env_path = backend_dir / '.env'
load_dotenv(env_path)

from tortoise import Tortoise
from app.core.settings import TORTOISE_ORM
from app.models.user import UserInfo
from app.utils.data_permission import filter_by_user_projects, get_user_data_scope


async def main():
    # 初始化数据库
    await Tortoise.init(config=TORTOISE_ORM)
    
    print("=" * 60)
    print("测试 filter_by_user_projects 函数")
    print("=" * 60)
    print()
    
    # 获取所有用户
    users = await UserInfo.all().prefetch_related('projects', 'roles')
    
    for user in users:
        print(f"用户: {user.email}")
        print(f"  ID: {user.id}")
        
        roles = [role.code for role in user.roles]
        print(f"  角色: {', '.join(roles) if roles else '无'}")
        
        projects = [p.name for p in user.projects]
        print(f"  关联项目: {', '.join(projects) if projects else '无'}")
        
        # 测试 get_user_data_scope
        scope = await get_user_data_scope(str(user.id))
        print(f"  数据范围:")
        print(f"    - has_global_access: {scope['has_global_access']}")
        print(f"    - project_ids: {scope['project_ids']}")
        print(f"    - roles: {scope['roles']}")
        
        # 测试 filter_by_user_projects
        filtered_ids = await filter_by_user_projects(str(user.id))
        print(f"  过滤结果:")
        if filtered_ids is None:
            print(f"    - None (全局访问，不过滤)")
        elif len(filtered_ids) == 0:
            print(f"    - [] (无项目)")
        else:
            print(f"    - {len(filtered_ids)} 个项目ID")
            for pid in filtered_ids:
                print(f"      * {pid}")
        
        print()
    
    await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(main())

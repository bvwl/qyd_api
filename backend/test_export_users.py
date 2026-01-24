#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试导出功能中的用户列显示

运行方式：
python test_export_users.py
"""

import asyncio
from app.models.project import ProjectInfo


async def test_user_display():
    """测试用户显示逻辑"""
    print("=" * 60)
    print("测试导出功能中的用户列显示")
    print("=" * 60)
    
    try:
        # 获取所有项目（预加载用户）
        projects = await ProjectInfo.all().prefetch_related('users')
        
        print(f"\n找到 {len(projects)} 个项目\n")
        
        for i, project in enumerate(projects, 1):
            print(f"{i}. 项目: {project.name}")
            print(f"   ID: {project.id}")
            
            # 获取用户昵称
            user_nicknames = []
            if project.users:
                for user in project.users:
                    if user.nickname:
                        user_nicknames.append(user.nickname)
                    else:
                        user_nicknames.append(user.email)
            
            users_str = ", ".join(user_nicknames) if user_nicknames else "未分配"
            print(f"   所属用户: {users_str}")
            print(f"   用户数量: {len(project.users) if project.users else 0}")
            print()
        
        print("=" * 60)
        print("测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 初始化数据库连接
    from tortoise import Tortoise
    from app.core.settings import TORTOISE_ORM
    
    async def main():
        await Tortoise.init(config=TORTOISE_ORM)
        await test_user_display()
        await Tortoise.close_connections()
    
    asyncio.run(main())

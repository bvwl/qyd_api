#!/usr/bin/env python3
"""
更新GM角色描述
将"游戏管理员"改为"项目管理员"
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载.env文件
from dotenv import load_dotenv
env_path = project_root / '.env'
load_dotenv(env_path)

# 导入必要的模块
from tortoise import Tortoise
from app.core import settings


async def update_gm_role():
    """更新GM角色描述"""
    print("=" * 60)
    print("更新GM角色描述")
    print("=" * 60)
    
    try:
        # 初始化数据库连接
        await Tortoise.init(config=settings.TORTOISE_ORM)
        print("✓ 数据库连接成功")
        print()
        
        from app.models.user import UserRole
        
        # 查找GM角色
        gm_role = await UserRole.get_or_none(code="GM")
        
        if not gm_role:
            print("✗ 未找到GM角色")
            return False
        
        print(f"当前GM角色信息:")
        print(f"  名称: {gm_role.name}")
        print(f"  描述: {gm_role.description}")
        print()
        
        # 更新角色信息
        gm_role.name = "项目管理员"
        gm_role.description = "项目管理员，负责项目运营和管理"
        await gm_role.save()
        
        print("✓ GM角色已更新:")
        print(f"  新名称: {gm_role.name}")
        print(f"  新描述: {gm_role.description}")
        print()
        
        # 验证更新
        updated_role = await UserRole.get(code="GM")
        print("验证更新结果:")
        print(f"  名称: {updated_role.name}")
        print(f"  描述: {updated_role.description}")
        print()
        
        print("=" * 60)
        print("✅ 更新完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"✗ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await Tortoise.close_connections()
        print("✓ 数据库连接已关闭")


async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("GM角色描述更新脚本")
    print("将'游戏管理员'改为'项目管理员'")
    print("=" * 60)
    print()
    
    success = await update_gm_role()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

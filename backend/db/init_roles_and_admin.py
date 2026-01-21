#!/usr/bin/env python3
"""
数据库初始化脚本
- 初始化角色：ADMIN, GM, IT, MANUAL
- 创建管理员账户：zhiyu (2201101122@qq.com)
"""
import asyncio
import sys
import os 
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
from app.core.tools import hashing


# 角色配置
ROLES = [
    {
        "name": "管理员",
        "code": "ADMIN",
        "description": "系统管理员，拥有所有权限"
    },
    {
        "name": "项目管理员",
        "code": "GM",
        "description": "项目管理员，负责项目运营和管理"
    },
    {
        "name": "技术人员",
        "code": "IT",
        "description": "技术人员，负责系统维护和技术支持"
    },
    {
        "name": "手动操作员",
        "code": "MANUAL",
        "description": "手动操作员，负责日常手动操作"
    }
]

# 管理员账户配置
ADMIN_USER = {
    "email": "zhiyu",
    "password": "2201101122@qq.com",
    "nickname": "至宇",
    "avatar": None,
    "status": 1  # 正常状态
}


async def init_database():
    """初始化数据库连接"""
    print("=" * 60)
    print("初始化数据库连接")
    print("=" * 60)
    
    try:
        await Tortoise.init(config=settings.TORTOISE_ORM)
        print(f"✓ 数据库连接成功")
        print(f"  主机: {settings.DB_HOST}:{settings.DB_PORT}")
        print(f"  数据库: {settings.DB_NAME}")
        print(f"  用户: {settings.DB_USER}")
        print()
        return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False


async def init_roles():
    """初始化角色"""
    print("=" * 60)
    print("初始化角色")
    print("=" * 60)
    
    from app.models.user import UserRole
    
    created_roles = []
    updated_roles = []
    
    for role_data in ROLES:
        try:
            # 检查角色是否已存在
            role = await UserRole.get_or_none(code=role_data["code"])
            
            if role:
                # 更新现有角色
                role.name = role_data["name"]
                role.description = role_data["description"]
                await role.save()
                updated_roles.append(role_data["code"])
                print(f"✓ 更新角色: {role_data['code']} - {role_data['name']}")
            else:
                # 创建新角色
                role = await UserRole.create(**role_data)
                created_roles.append(role_data["code"])
                print(f"✓ 创建角色: {role_data['code']} - {role_data['name']}")
                
        except Exception as e:
            print(f"✗ 处理角色 {role_data['code']} 失败: {e}")
            return False
    
    print()
    print(f"角色初始化完成:")
    print(f"  新建: {len(created_roles)} 个")
    print(f"  更新: {len(updated_roles)} 个")
    print()
    return True


async def init_admin_user():
    """初始化管理员账户"""
    print("=" * 60)
    print("初始化管理员账户")
    print("=" * 60)
    
    from app.models.user import UserInfo, UserRole
    
    try:
        # 检查用户是否已存在
        user = await UserInfo.get_or_none(email=ADMIN_USER["email"]).prefetch_related("roles")
        
        # 加密密码
        password_hash = hashing.hash(ADMIN_USER["password"])
        
        if user:
            # 更新现有用户
            user.password = password_hash
            user.nickname = ADMIN_USER["nickname"]
            user.status = ADMIN_USER["status"]
            if ADMIN_USER["avatar"]:
                user.avatar = ADMIN_USER["avatar"]
            await user.save()
            print(f"✓ 更新用户: {ADMIN_USER['email']}")
            action = "更新"
        else:
            # 创建新用户
            user = await UserInfo.create(
                email=ADMIN_USER["email"],
                password=password_hash,
                nickname=ADMIN_USER["nickname"],
                avatar=ADMIN_USER["avatar"],
                status=ADMIN_USER["status"]
            )
            print(f"✓ 创建用户: {ADMIN_USER['email']}")
            action = "创建"
        
        # 分配ADMIN角色
        admin_role = await UserRole.get(code="ADMIN")
        
        # 清除现有角色关联
        await user.roles.clear()
        
        # 添加ADMIN角色
        await user.roles.add(admin_role)
        
        print(f"✓ 分配角色: ADMIN")
        print()
        print(f"管理员账户{action}成功:")
        print(f"  邮箱: {ADMIN_USER['email']}")
        print(f"  昵称: {ADMIN_USER['nickname']}")
        print(f"  密码: {ADMIN_USER['password']}")
        print(f"  角色: ADMIN")
        print()
        return True
        
    except Exception as e:
        print(f"✗ 初始化管理员账户失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def verify_initialization():
    """验证初始化结果"""
    print("=" * 60)
    print("验证初始化结果")
    print("=" * 60)
    
    from app.models.user import UserRole, UserInfo
    
    try:
        # 验证角色
        roles = await UserRole.all()
        print(f"✓ 角色总数: {len(roles)}")
        for role in roles:
            print(f"  - {role.code}: {role.name}")
        
        print()
        
        # 验证管理员
        admin = await UserInfo.get(email=ADMIN_USER["email"]).prefetch_related("roles")
        print(f"✓ 管理员账户: {admin.email}")
        print(f"  昵称: {admin.nickname}")
        print(f"  状态: {admin.status}")
        print(f"  角色: {', '.join([role.code for role in admin.roles])}")
        
        # 验证密码
        is_valid = hashing.verify(ADMIN_USER["password"], admin.password)
        print(f"  密码验证: {'✓ 通过' if is_valid else '✗ 失败'}")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ 验证失败: {e}")
        return False


async def close_database():
    """关闭数据库连接"""
    await Tortoise.close_connections()
    print("✓ 数据库连接已关闭")


async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("数据库初始化脚本")
    print("=" * 60)
    print()
    
    # 初始化数据库连接
    if not await init_database():
        return 1
    
    try:
        # 初始化角色
        if not await init_roles():
            return 1
        
        # 初始化管理员账户
        if not await init_admin_user():
            return 1
        
        # 验证初始化结果
        if not await verify_initialization():
            return 1
        
        print("=" * 60)
        print("✅ 初始化完成！")
        print("=" * 60)
        print()
        print("📝 登录信息:")
        print(f"  邮箱: {ADMIN_USER['email']}")
        print(f"  密码: {ADMIN_USER['password']}")
        print()
        print("🔐 安全提示:")
        print("  请在首次登录后立即修改密码！")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n✗ 初始化过程出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        await close_database()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

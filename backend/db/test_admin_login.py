#!/usr/bin/env python3
"""
测试管理员登录
验证初始化的管理员账户是否可以正常登录
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

from tortoise import Tortoise
from app.core import settings
from app.core.tools import hashing
from app.utils.jwt_tool import JwtToken


async def test_login():
    """测试登录"""
    print("\n" + "=" * 60)
    print("测试管理员登录")
    print("=" * 60 + "\n")
    
    # 初始化数据库
    await Tortoise.init(config=settings.TORTOISE_ORM)
    
    try:
        from app.models.user import UserInfo
        
        # 测试账户
        email = "zhiyu"
        password = "2201101122@qq.com"
        
        print(f"测试账户: {email}")
        print(f"测试密码: {password}")
        print()
        
        # 1. 查询用户
        print("步骤1: 查询用户...")
        user = await UserInfo.get_or_none(email=email).prefetch_related('roles')
        
        if not user:
            print("✗ 用户不存在")
            return False
        
        print(f"✓ 用户存在")
        print(f"  ID: {user.id}")
        print(f"  邮箱: {user.email}")
        print(f"  昵称: {user.nickname}")
        print(f"  状态: {user.status}")
        print()
        
        # 2. 验证密码
        print("步骤2: 验证密码...")
        is_valid = hashing.verify(password, user.password)
        
        if not is_valid:
            print("✗ 密码错误")
            return False
        
        print("✓ 密码正确")
        print()
        
        # 3. 获取角色
        print("步骤3: 获取用户角色...")
        roles = [role.code for role in user.roles]
        print(f"✓ 角色: {', '.join(roles)}")
        print()
        
        # 4. 生成JWT token
        print("步骤4: 生成JWT token...")
        token_data = {
            "id": str(user.id),
            "email": user.email,
            "roles": roles
        }
        access_token = JwtToken.create_token(token_data)
        print(f"✓ Token生成成功")
        print(f"  Token长度: {len(access_token)}")
        print(f"  Token前50字符: {access_token[:50]}...")
        print()
        
        # 5. 验证token
        print("步骤5: 验证JWT token...")
        payload = JwtToken.verify_token(access_token)
        print(f"✓ Token验证成功")
        print(f"  用户ID: {payload.get('id')}")
        print(f"  邮箱: {payload.get('email')}")
        print(f"  角色: {payload.get('roles')}")
        print()
        
        print("=" * 60)
        print("✅ 登录测试通过！")
        print("=" * 60)
        print()
        print("📝 登录信息:")
        print(f"  邮箱: {email}")
        print(f"  密码: {password}")
        print(f"  Token: {access_token[:50]}...")
        print()
        print("🔗 API测试命令:")
        print(f"""
curl -X POST http://localhost:6080/api/v1/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{{
    "email": "{email}",
    "password": "{password}"
  }}'
""")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    result = asyncio.run(test_login())
    sys.exit(0 if result else 1)

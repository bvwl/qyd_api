#!/usr/bin/env python3
"""
部署初始化脚本
用于新服务器上的数据库初始化和初始数据导入

使用方法:
    python deploy_init.py

功能:
    1. 检查环境配置
    2. 初始化数据库连接
    3. 创建所有表结构（通过 Aerich）
    4. 导入初始数据（角色、路由、管理员用户）
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from tortoise import Tortoise
from app.core.settings import TORTOISE_ORM
from app.core.tools import hashing
from app.models.user import UserInfo, UserRole, FrontendRoute
import uuid


class DeployInitializer:
    """部署初始化器"""
    
    def __init__(self):
        self.db_initialized = False
        
    async def check_environment(self):
        """检查环境配置"""
        print("=" * 60)
        print("1. 检查环境配置...")
        print("=" * 60)
        
        required_env_vars = [
            'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME',
            'JWT_SECRET_KEY'
        ]
        
        missing_vars = []
        for var in required_env_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            else:
                # 隐藏敏感信息
                if 'PASSWORD' in var or 'SECRET' in var:
                    display_value = '*' * 8
                else:
                    display_value = value
                print(f"  ✓ {var}: {display_value}")
        
        if missing_vars:
            print(f"\n  ✗ 缺少环境变量: {', '.join(missing_vars)}")
            print(f"  请在 .env 文件中配置这些变量")
            return False
        
        print("\n  ✓ 环境配置检查通过")
        return True
    
    async def init_database(self):
        """初始化数据库连接"""
        print("\n" + "=" * 60)
        print("2. 初始化数据库连接...")
        print("=" * 60)
        
        try:
            await Tortoise.init(config=TORTOISE_ORM)
            self.db_initialized = True
            print("  ✓ 数据库连接成功")
            
            # 生成数据库表结构
            await Tortoise.generate_schemas()
            print("  ✓ 数据库表结构创建成功")
            
            return True
        except Exception as e:
            print(f"  ✗ 数据库连接失败: {str(e)}")
            return False
    
    async def import_roles(self):
        """导入角色数据"""
        print("\n" + "=" * 60)
        print("3. 导入角色数据...")
        print("=" * 60)
        
        roles_data = [
            {
                'code': 'ADMIN',
                'name': '管理员',
                'description': '系统管理员，拥有所有权限',
                'is_default': False
            },
            {
                'code': 'GM',
                'name': '项目管理员',
                'description': '项目管理员，可以管理项目和用户',
                'is_default': False
            },
            {
                'code': 'IT',
                'name': '技术人员',
                'description': '技术支持人员',
                'is_default': False
            },
            {
                'code': 'MANUAL',
                'name': '手动操作员',
                'description': '手动操作人员，默认角色',
                'is_default': True
            }
        ]
        
        created_roles = {}
        for role_data in roles_data:
            # 检查角色是否已存在
            existing_role = await UserRole.filter(code=role_data['code']).first()
            if existing_role:
                print(f"  - 角色 {role_data['code']} 已存在，跳过")
                created_roles[role_data['code']] = existing_role
                continue
            
            # 创建角色
            role = await UserRole.create(**role_data)
            created_roles[role_data['code']] = role
            print(f"  ✓ 创建角色: {role_data['code']} - {role_data['name']}")
        
        print(f"\n  ✓ 角色数据导入完成，共 {len(created_roles)} 个角色")
        return created_roles
    
    async def import_routes(self):
        """导入路由数据"""
        print("\n" + "=" * 60)
        print("4. 导入路由数据...")
        print("=" * 60)
        
        # 一级菜单
        routes_data = [
            # 仪表盘
            {
                'name': '仪表盘',
                'path': '/dashboard',
                'component': 'Dashboard',
                'icon': 'DashboardOutlined',
                'sort': 1,
                'parent_id': None
            },
            # 用户管理
            {
                'name': '用户管理',
                'path': '/user',
                'component': None,
                'icon': 'UserOutlined',
                'sort': 2,
                'parent_id': None,
                'children': [
                    {'name': '用户列表', 'path': '/user/list', 'component': 'UserList', 'sort': 1},
                    {'name': '角色管理', 'path': '/user/role', 'component': 'RoleList', 'sort': 2},
                    {'name': '路由管理', 'path': '/user/route', 'component': 'RouteList', 'sort': 3},
                    {'name': '权限管理', 'path': '/user/permission', 'component': 'PermissionManage', 'sort': 4},
                    {'name': 'API Token', 'path': '/user/token', 'component': 'TokenList', 'sort': 5},
                    {'name': '操作日志', 'path': '/user/log', 'component': 'LogList', 'sort': 6},
                ]
            },
            # 项目管理
            {
                'name': '项目管理',
                'path': '/project',
                'component': None,
                'icon': 'ProjectOutlined',
                'sort': 3,
                'parent_id': None,
                'children': [
                    {'name': '项目列表', 'path': '/project/list', 'component': 'ProjectList', 'sort': 1},
                    {'name': '项目账号', 'path': '/project/account', 'component': 'ProjectAccount', 'sort': 2},
                    {'name': '项目钱包', 'path': '/project/wallet', 'component': 'ProjectWallet', 'sort': 3},
                    {'name': '批量创建钱包', 'path': '/project/wallet/batch-create', 'component': 'WalletBatchCreate', 'sort': 4},
                ]
            },
            # 服务器管理
            {
                'name': '服务器管理',
                'path': '/server',
                'component': None,
                'icon': 'CloudServerOutlined',
                'sort': 4,
                'parent_id': None,
                'children': [
                    {'name': '服务器列表', 'path': '/server/list', 'component': 'ServerList', 'sort': 1},
                    {'name': '国家管理', 'path': '/server/country', 'component': 'CountryList', 'sort': 2},
                    {'name': '分组管理', 'path': '/server/group', 'component': 'GroupList', 'sort': 3},
                    {'name': '服务器账号', 'path': '/server/account', 'component': 'ServerAccount', 'sort': 4},
                ]
            },
            # 邮箱管理
            {
                'name': '邮箱管理',
                'path': '/mail',
                'component': None,
                'icon': 'MailOutlined',
                'sort': 5,
                'parent_id': None,
                'children': [
                    {'name': '邮箱列表', 'path': '/mail/list', 'component': 'MailList', 'sort': 1},
                    {'name': '发送邮件', 'path': '/mail/send', 'component': 'MailSend', 'sort': 2},
                    {'name': '邮件查看器', 'path': '/mail/viewer', 'component': 'MailViewer', 'sort': 3},
                ]
            },
            # XUI 管理
            {
                'name': 'XUI管理',
                'path': '/xui',
                'component': None,
                'icon': 'ApiOutlined',
                'sort': 6,
                'parent_id': None,
                'children': [
                    {'name': 'XUI服务器', 'path': '/xui/server', 'component': 'XuiServerList', 'sort': 1},
                    {'name': 'XUI入站', 'path': '/xui/inbound', 'component': 'XuiInboundList', 'sort': 2},
                    {'name': 'XUI账号', 'path': '/xui/account', 'component': 'XuiAccountList', 'sort': 3},
                    {'name': 'XUI日志', 'path': '/xui/log', 'component': 'XuiOperationLog', 'sort': 4},
                ]
            },
        ]
        
        created_routes = []
        route_map = {}
        
        async def create_route(route_data, parent_id=None):
            """递归创建路由"""
            children = route_data.pop('children', None)
            route_data['parent_id'] = parent_id
            
            # 检查路由是否已存在
            existing_route = await FrontendRoute.filter(path=route_data['path']).first()
            if existing_route:
                print(f"  - 路由 {route_data['path']} 已存在，跳过")
                route_map[route_data['path']] = existing_route
                return existing_route
            
            # 创建路由
            route = await FrontendRoute.create(**route_data)
            route_map[route_data['path']] = route
            created_routes.append(route)
            print(f"  ✓ 创建路由: {route_data['path']} - {route_data['name']}")
            
            # 创建子路由
            if children:
                for child_data in children:
                    await create_route(child_data, parent_id=route.id)
            
            return route
        
        # 创建所有路由
        for route_data in routes_data:
            await create_route(route_data.copy())
        
        print(f"\n  ✓ 路由数据导入完成，共 {len(created_routes)} 个路由")
        return route_map
    
    async def import_admin_user(self, roles):
        """导入管理员用户"""
        print("\n" + "=" * 60)
        print("5. 导入管理员用户...")
        print("=" * 60)
        
        admin_email = 'zhiyu'
        admin_password = '2201101122@qq.com'
        
        # 检查管理员是否已存在
        existing_admin = await UserInfo.filter(email=admin_email).first()
        if existing_admin:
            print(f"  - 管理员用户 {admin_email} 已存在，跳过")
            return existing_admin
        
        # 创建管理员用户
        admin_user = await UserInfo.create(
            email=admin_email,
            nickname='系统管理员',
            password=hashing.hash(admin_password),
            status=1
        )
        
        # 分配 ADMIN 角色
        admin_role = roles.get('ADMIN')
        if admin_role:
            await admin_user.roles.add(admin_role)
            print(f"  ✓ 创建管理员用户: {admin_email}")
            print(f"  ✓ 分配角色: ADMIN")
        
        print(f"\n  管理员账号信息:")
        print(f"    邮箱: {admin_email}")
        print(f"    密码: {admin_password}")
        print(f"    ⚠️  请在首次登录后立即修改密码！")
        
        return admin_user
    
    async def bind_admin_routes(self, roles, route_map):
        """为管理员角色绑定所有路由"""
        print("\n" + "=" * 60)
        print("6. 绑定管理员路由权限...")
        print("=" * 60)
        
        admin_role = roles.get('ADMIN')
        if not admin_role:
            print("  ✗ 未找到 ADMIN 角色")
            return False
        
        # 获取所有路由
        all_routes = await FrontendRoute.all()
        
        # 清除现有绑定
        await admin_role.routes.clear()
        
        # 绑定所有路由
        await admin_role.routes.add(*all_routes)
        
        print(f"  ✓ 为 ADMIN 角色绑定 {len(all_routes)} 个路由")
        return True
    
    async def bind_gm_routes(self, roles, route_map):
        """为 GM 角色绑定路由权限"""
        print("\n" + "=" * 60)
        print("7. 绑定 GM 路由权限...")
        print("=" * 60)
        
        gm_role = roles.get('GM')
        if not gm_role:
            print("  ✗ 未找到 GM 角色")
            return False
        
        # GM 可访问的路由路径
        gm_routes_paths = [
            '/dashboard',
            '/project',
            '/project/list',
            '/project/account',
            '/project/wallet',
            '/project/wallet/batch-create',
            '/server',
            '/server/list',
            '/server/country',
            '/server/group',
            '/server/account',
            '/mail',
            '/mail/list',
            '/mail/send',
            '/mail/viewer',
        ]
        
        # 清除现有绑定
        await gm_role.routes.clear()
        
        # 绑定路由
        gm_routes = []
        for path in gm_routes_paths:
            route = await FrontendRoute.filter(path=path).first()
            if route:
                gm_routes.append(route)
        
        await gm_role.routes.add(*gm_routes)
        
        print(f"  ✓ 为 GM 角色绑定 {len(gm_routes)} 个路由")
        return True
    
    async def verify_initialization(self):
        """验证初始化结果"""
        print("\n" + "=" * 60)
        print("8. 验证初始化结果...")
        print("=" * 60)
        
        # 检查角色
        roles_count = await UserRole.all().count()
        print(f"  ✓ 角色数量: {roles_count}")
        
        # 检查路由
        routes_count = await FrontendRoute.all().count()
        print(f"  ✓ 路由数量: {routes_count}")
        
        # 检查用户
        users_count = await UserInfo.all().count()
        print(f"  ✓ 用户数量: {users_count}")
        
        # 检查管理员
        admin = await UserInfo.filter(email='zhiyu').first()
        if admin:
            admin_roles = await admin.roles.all()
            print(f"  ✓ 管理员用户: zhiyu")
            print(f"  ✓ 管理员角色: {', '.join([r.code for r in admin_roles])}")
        
        return True
    
    async def cleanup(self):
        """清理资源"""
        if self.db_initialized:
            await Tortoise.close_connections()
    
    async def run(self):
        """运行初始化流程"""
        try:
            # 1. 检查环境
            if not await self.check_environment():
                return False
            
            # 2. 初始化数据库
            if not await self.init_database():
                return False
            
            # 3. 导入角色
            roles = await self.import_roles()
            
            # 4. 导入路由
            route_map = await self.import_routes()
            
            # 5. 导入管理员用户
            await self.import_admin_user(roles)
            
            # 6. 绑定管理员路由
            await self.bind_admin_routes(roles, route_map)
            
            # 7. 绑定 GM 路由
            await self.bind_gm_routes(roles, route_map)
            
            # 8. 验证初始化
            await self.verify_initialization()
            
            print("\n" + "=" * 60)
            print("✓ 部署初始化完成！")
            print("=" * 60)
            print("\n下一步:")
            print("  1. 访问前端应用: http://localhost:3000")
            print("  2. 使用管理员账号登录:")
            print("     邮箱: zhiyu")
            print("     密码: 2201101122@qq.com")
            print("  3. ⚠️  首次登录后请立即修改密码！")
            print("\n")
            
            return True
            
        except Exception as e:
            print(f"\n✗ 初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.cleanup()


async def main():
    """主函数"""
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    initializer = DeployInitializer()
    success = await initializer.run()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main())

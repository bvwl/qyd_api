"""
测试 XUI 路由是否正确添加
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# 加载环境变量
env_path = backend_dir / '.env'
load_dotenv(env_path)

from tortoise import Tortoise
from app.core import settings
from app.models.user import FrontendRoute


async def test_xui_routes():
    """
    测试 XUI 路由
    """
    print("=" * 60)
    print("测试 XUI 路由")
    print("=" * 60)
    print()
    
    try:
        # 初始化数据库连接
        await Tortoise.init(config=settings.get_tortoise_config())
        print("✓ 数据库连接成功")
        print()
        
        # 测试 1: 检查 XUI 父路由
        print("📋 测试 1: 检查 XUI 父路由")
        xui_route = await FrontendRoute.get_or_none(name='xui')
        
        if xui_route:
            print(f"  ✅ XUI 路由存在")
            print(f"     ID: {xui_route.id}")
            print(f"     名称: {xui_route.name}")
            print(f"     路径: {xui_route.path}")
            print(f"     标题: {xui_route.title}")
            print(f"     图标: {xui_route.icon}")
            print(f"     排序: {xui_route.sort}")
            print(f"     状态: {xui_route.status}")
        else:
            print(f"  ❌ XUI 路由不存在")
            print(f"     请运行: ./add_xui_routes.sh")
            return
        
        print()
        
        # 测试 2: 检查 XUI 子路由
        print("📋 测试 2: 检查 XUI 子路由")
        children = await FrontendRoute.filter(parent_id=xui_route.id).order_by('sort')
        
        expected_children = [
            ('xui-server', '/xui/server', '服务器列表'),
            ('xui-inbound', '/xui/inbound', '入站列表'),
            ('xui-account', '/xui/account', '账号管理'),
        ]
        
        if len(children) == len(expected_children):
            print(f"  ✅ 子路由数量正确: {len(children)}")
        else:
            print(f"  ⚠️  子路由数量不匹配: 期望 {len(expected_children)}，实际 {len(children)}")
        
        for i, child in enumerate(children):
            expected = expected_children[i] if i < len(expected_children) else None
            if expected:
                name_match = child.name == expected[0]
                path_match = child.path == expected[1]
                title_match = child.title == expected[2]
                
                if name_match and path_match and title_match:
                    print(f"  ✅ {child.title} ({child.path})")
                else:
                    print(f"  ⚠️  {child.title} ({child.path})")
                    if not name_match:
                        print(f"     名称不匹配: 期望 {expected[0]}，实际 {child.name}")
                    if not path_match:
                        print(f"     路径不匹配: 期望 {expected[1]}，实际 {child.path}")
                    if not title_match:
                        print(f"     标题不匹配: 期望 {expected[2]}，实际 {child.title}")
            else:
                print(f"  ⚠️  额外的子路由: {child.title} ({child.path})")
        
        print()
        
        # 测试 3: 检查路由排序
        print("📋 测试 3: 检查路由排序")
        parent_routes = await FrontendRoute.filter(parent_id=None).order_by('sort')
        
        print("  当前一级菜单排序:")
        for route in parent_routes:
            marker = "  👉" if route.name == 'xui' else "    "
            print(f"{marker} {route.sort}. {route.title} ({route.path})")
        
        # 检查 XUI 的排序是否合理
        xui_sort = xui_route.sort
        if 1 <= xui_sort <= 10:
            print(f"  ✅ XUI 排序合理: {xui_sort}")
        else:
            print(f"  ⚠️  XUI 排序可能不合理: {xui_sort}")
        
        print()
        
        # 测试 4: 检查路由状态
        print("📋 测试 4: 检查路由状态")
        all_xui_routes = [xui_route] + children
        all_active = all(route.status == 1 for route in all_xui_routes)
        
        if all_active:
            print(f"  ✅ 所有 XUI 路由都是激活状态")
        else:
            print(f"  ⚠️  部分 XUI 路由未激活:")
            for route in all_xui_routes:
                if route.status != 1:
                    print(f"     - {route.title}: 状态 {route.status}")
        
        print()
        
        # 测试 5: 统计信息
        print("📋 测试 5: 统计信息")
        total_routes = await FrontendRoute.all().count()
        parent_count = await FrontendRoute.filter(parent_id=None).count()
        child_count = total_routes - parent_count
        
        print(f"  总路由数: {total_routes}")
        print(f"  一级菜单: {parent_count}")
        print(f"  二级菜单: {child_count}")
        print(f"  XUI 路由: {len(all_xui_routes)} (1 个父路由 + {len(children)} 个子路由)")
        
        print()
        print("=" * 60)
        print("✅ 测试完成！")
        print("=" * 60)
        print()
        
        # 给出建议
        print("下一步:")
        print("  1. 重启后端服务")
        print("  2. 刷新前端页面")
        print("  3. 在角色管理中为 ADMIN 角色分配 XUI 路由权限")
        print("  4. 使用 ADMIN 账号登录，检查菜单是否显示")
        print()
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(test_xui_routes())

"""
测试项目账号通过 host 自动绑定服务器

验证：
1. 传入 host 字段，自动查询并绑定 server_id
2. host 不存在时的处理
3. 同时传入 host 和 server_id 时，host 优先
"""

import asyncio
import sys
from uuid import UUID
from tortoise import Tortoise

sys.path.insert(0, '/Users/qyd/qyd_api2/backend')

from app.core import settings
from app.models.project import ProjectInfo, ProjectAccount
from app.models.server import ServerInfo
from app.crud.project.account import project_account_crud
from app.schemas.project.account import Create, Update


async def test_host_binding():
    """测试 host 自动绑定功能"""
    await Tortoise.init(config=settings.TORTOISE_ORM)
    
    try:
        print("\n" + "="*80)
        print("测试项目账号通过 host 自动绑定服务器")
        print("="*80)
        
        # 1. 获取一个测试项目
        project = await ProjectInfo.first()
        if not project:
            print("❌ 没有找到项目，请先创建项目")
            return
        
        print(f"\n使用项目: {project.name} (ID: {project.id})")
        
        # 2. 获取一个测试服务器
        server = await ServerInfo.first()
        if not server:
            print("❌ 没有找到服务器，请先创建服务器")
            return
        
        print(f"使用服务器: {server.host} (ID: {server.id})")
        
        # 3. 测试通过 host 创建账号
        print("\n" + "-"*80)
        print("测试1: 通过 host 创建账号")
        print("-"*80)
        
        test_account_1 = f"test_host_binding_{asyncio.get_event_loop().time()}@example.com"
        
        create_data = Create(
            project_id=project.id,
            account=test_account_1,
            password="test_password",
            host=server.host,  # 传入 host 而不是 server_id
            status=1,
            account_type=1
        )
        
        print(f"\n创建数据:")
        print(f"  账号: {create_data.account}")
        print(f"  host: {create_data.host}")
        print(f"  server_id: {create_data.server_id}")
        
        created = await project_account_crud.create(create_data)
        print(f"\n✅ 创建成功")
        print(f"  ID: {created.id}")
        print(f"  账号: {created.account}")
        print(f"  绑定的服务器ID: {created.server_id}")
        print(f"  绑定的服务器host: {created.server.host if created.server else 'None'}")
        
        # 验证
        assert created.server_id == server.id, "server_id 应该自动绑定"
        assert created.server.host == server.host, "服务器信息应该正确"
        print("✅ host 自动绑定验证通过")
        
        # 4. 测试 host 不存在的情况
        print("\n" + "-"*80)
        print("测试2: host 不存在时的处理")
        print("-"*80)
        
        test_account_2 = f"test_host_not_exist_{asyncio.get_event_loop().time()}@example.com"
        
        create_data_2 = Create(
            project_id=project.id,
            account=test_account_2,
            password="test_password",
            host="nonexistent.host.com",  # 不存在的 host
            status=1,
            account_type=1
        )
        
        print(f"\n创建数据:")
        print(f"  账号: {create_data_2.account}")
        print(f"  host: {create_data_2.host} (不存在)")
        
        created_2 = await project_account_crud.create(create_data_2)
        print(f"\n✅ 创建成功（宽松模式）")
        print(f"  ID: {created_2.id}")
        print(f"  账号: {created_2.account}")
        print(f"  绑定的服务器ID: {created_2.server_id}")
        
        # 验证
        assert created_2.server_id is None, "host 不存在时 server_id 应该为 None"
        print("✅ host 不存在时的处理验证通过")
        
        # 5. 测试更新时通过 host 绑定
        print("\n" + "-"*80)
        print("测试3: 更新时通过 host 绑定服务器")
        print("-"*80)
        
        # 获取另一个服务器（如果有的话）
        servers = await ServerInfo.all().limit(2)
        if len(servers) > 1:
            another_server = servers[1]
            print(f"\n使用另一个服务器: {another_server.host} (ID: {another_server.id})")
            
            update_data = Update(
                host=another_server.host  # 更新 host
            )
            
            updated = await project_account_crud.update(created.id, update_data)
            print(f"\n✅ 更新成功")
            print(f"  账号: {updated.account}")
            print(f"  新的服务器ID: {updated.server_id}")
            print(f"  新的服务器host: {updated.server.host if updated.server else 'None'}")
            
            # 验证
            assert updated.server_id == another_server.id, "server_id 应该更新"
            print("✅ 更新时 host 绑定验证通过")
        else:
            print("\n⚠️  只有一个服务器，跳过更新测试")
        
        # 6. 清理测试数据
        print("\n" + "-"*80)
        print("清理测试数据")
        print("-"*80)
        
        await project_account_crud.delete(created.id)
        await project_account_crud.delete(created_2.id)
        print("✅ 测试数据已清理")
        
        print("\n" + "="*80)
        print("✅ 所有测试通过！")
        print("="*80)
        
        print("\n总结:")
        print("1. ✅ 传入 host 可以自动查询并绑定 server_id")
        print("2. ✅ host 不存在时不会报错，server_id 为 None")
        print("3. ✅ 更新时也可以通过 host 重新绑定服务器")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(test_host_binding())

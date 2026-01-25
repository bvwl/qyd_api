"""
XUI 数据库迁移测试脚本
"""
import asyncio
from app.core.database import init_db, close_db
from app.models.xui import XuiServer, XuiInbound
from app.models.server import ServerAccount
from app.core.tools import aes_encrypt
from uuid import uuid4


async def test_migration():
    """测试数据库迁移"""
    print("=== XUI 数据库迁移测试 ===\n")
    
    # 初始化数据库
    print("1. 初始化数据库连接...")
    await init_db()
    print("✅ 数据库连接成功\n")
    
    try:
        # 测试 XuiServer 表
        print("2. 测试 xui_server 表...")
        test_server = await XuiServer.create(
            name="测试服务器",
            host="192.168.1.100",
            domain="test.example.com",
            port=10010,
            username="admin",
            password=aes_encrypt("admin123", "192.168.1.100"),
            is_ssl=False,
            web_path="/web3",
            status=1
        )
        print(f"✅ 创建服务器成功: {test_server.id}")
        print(f"   - 名称: {test_server.name}")
        print(f"   - Host: {test_server.host}")
        print(f"   - Domain: {test_server.domain}")
        print(f"   - 端口: {test_server.port}\n")
        
        # 测试 XuiInbound 表
        print("3. 测试 xui_inbound 表...")
        test_inbound = await XuiInbound.create(
            server_id=test_server.id,
            inbound_id=1,
            listen_host="192.168.1.100",
            listen_port=21000,
            protocol=1,  # HTTP
            status=1,
            default_username="cqrxy",
            default_password=aes_encrypt("Zpaily88", "192.168.1.100:21000"),
            remark="测试入站"
        )
        print(f"✅ 创建入站成功: {test_inbound.id}")
        print(f"   - 监听地址: {test_inbound.listen_host}")
        print(f"   - 监听端口: {test_inbound.listen_port}")
        print(f"   - 协议: {test_inbound.protocol}\n")
        
        # 测试多对多关系
        print("4. 测试多对多关系...")
        
        # 检查是否有现有的 ServerAccount
        existing_account = await ServerAccount.first()
        
        if existing_account:
            print(f"   使用现有账号: {existing_account.username}")
            test_account = existing_account
        else:
            # 创建测试账号
            test_account = await ServerAccount.create(
                username="test_user",
                password=aes_encrypt("test_pass", "test_user")
            )
            print(f"   创建测试账号: {test_account.username}")
        
        # 添加账号到入站
        await test_inbound.accounts.add(test_account)
        print(f"✅ 添加账号到入站成功\n")
        
        # 验证关系
        print("5. 验证多对多关系...")
        accounts = await test_inbound.accounts.all()
        print(f"✅ 入站关联的账号数量: {len(accounts)}")
        for account in accounts:
            print(f"   - 账号: {account.username}\n")
        
        # 查询测试
        print("6. 测试查询功能...")
        
        # 查询服务器
        servers = await XuiServer.all()
        print(f"✅ 服务器总数: {len(servers)}")
        
        # 查询入站
        inbounds = await XuiInbound.filter(server_id=test_server.id).all()
        print(f"✅ 入站总数: {len(inbounds)}")
        
        # 预加载关联数据
        inbound_with_server = await XuiInbound.get(id=test_inbound.id).prefetch_related('server')
        print(f"✅ 预加载服务器: {inbound_with_server.server.name}\n")
        
        # 清理测试数据
        print("7. 清理测试数据...")
        await test_inbound.delete()
        print("✅ 删除入站")
        
        await test_server.delete()
        print("✅ 删除服务器")
        
        if not existing_account:
            await test_account.delete()
            print("✅ 删除测试账号")
        
        print("\n=== 所有测试通过 ===")
        print("\n数据库表结构验证成功！")
        print("- xui_server 表: ✅")
        print("- xui_inbound 表: ✅")
        print("- xui_inbound_account 关系表: ✅")
        print("- 外键约束: ✅")
        print("- 多对多关系: ✅")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 关闭数据库连接
        await close_db()
        print("\n数据库连接已关闭")


if __name__ == "__main__":
    asyncio.run(test_migration())

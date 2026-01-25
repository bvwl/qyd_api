"""
测试 XUI 账号入站状态自动更新功能
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
load_dotenv()

from tortoise import Tortoise
from app.core.settings import get_tortoise_config
from app.models.server import ServerAccount
from app.models.xui import XuiInbound
from app.crud.xui.user import xui_inbound_account_crud


async def init_db():
    """初始化数据库"""
    await Tortoise.init(config=get_tortoise_config())


async def close_db():
    """关闭数据库"""
    await Tortoise.close_connections()


async def test_status_update():
    """测试状态更新"""
    await init_db()
    
    try:
        # 1. 获取一个测试账号
        account = await ServerAccount.first()
        if not account:
            print("❌ 没有找到测试账号")
            return
        
        print(f"\n📋 测试账号: {account.username}")
        print(f"   账号ID: {account.id}")
        print(f"   当前状态: {'已全部添加' if account.is_all_inbound_added else '未全部添加'}")
        
        # 2. 获取所有入站
        inbounds = await XuiInbound.all()
        print(f"\n📊 系统中共有 {len(inbounds)} 个入站")
        
        if not inbounds:
            print("❌ 没有入站，无法测试")
            return
        
        # 3. 检查账号已添加到多少个入站
        added_count = 0
        for inbound in inbounds:
            exists = await inbound.accounts.filter(id=account.id).exists()
            if exists:
                added_count += 1
                print(f"   ✅ 已添加到: {inbound.listen_host}:{inbound.listen_port}")
            else:
                print(f"   ❌ 未添加到: {inbound.listen_host}:{inbound.listen_port}")
        
        print(f"\n📈 已添加到 {added_count}/{len(inbounds)} 个入站")
        
        # 4. 手动调用状态更新方法
        print(f"\n🔄 调用 _update_account_inbound_status() 方法...")
        await xui_inbound_account_crud._update_account_inbound_status(account.id)
        
        # 5. 重新获取账号，检查状态是否更新
        account = await ServerAccount.get(id=account.id)
        expected_status = (added_count == len(inbounds))
        
        print(f"\n✅ 状态更新完成:")
        print(f"   预期状态: {'已全部添加' if expected_status else '未全部添加'}")
        print(f"   实际状态: {'已全部添加' if account.is_all_inbound_added else '未全部添加'}")
        
        if account.is_all_inbound_added == expected_status:
            print(f"\n✅ 测试通过！状态更新正确")
        else:
            print(f"\n❌ 测试失败！状态不匹配")
        
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(test_status_update())

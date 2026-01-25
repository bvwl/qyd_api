"""
修复所有账号的入站状态
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


async def fix_all_account_status():
    """修复所有账号的入站状态"""
    await init_db()
    
    try:
        # 获取所有账号
        accounts = await ServerAccount.all()
        total_inbounds = await XuiInbound.all().count()
        
        print(f"\n📊 系统统计:")
        print(f"   总账号数: {len(accounts)}")
        print(f"   总入站数: {total_inbounds}")
        print(f"\n{'='*60}")
        
        fixed_count = 0
        unchanged_count = 0
        
        for account in accounts:
            # 获取账号已添加的入站数量
            added_count = await XuiInbound.filter(accounts__id=account.id).count()
            expected_status = (added_count == total_inbounds)
            
            # 检查状态是否需要更新
            if account.is_all_inbound_added != expected_status:
                print(f"\n🔧 修复账号: {account.username}")
                print(f"   当前状态: {'已全部添加' if account.is_all_inbound_added else '未全部添加'}")
                print(f"   实际情况: 已添加 {added_count}/{total_inbounds} 个入站")
                print(f"   应该状态: {'已全部添加' if expected_status else '未全部添加'}")
                
                # 调用更新方法
                await xui_inbound_account_crud._update_account_inbound_status(account.id)
                fixed_count += 1
                print(f"   ✅ 已修复")
            else:
                unchanged_count += 1
        
        print(f"\n{'='*60}")
        print(f"\n📈 修复完成:")
        print(f"   修复数量: {fixed_count}")
        print(f"   无需修复: {unchanged_count}")
        print(f"   总计: {len(accounts)}")
        
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(fix_all_account_status())

"""
清理重复的项目账号记录
保留最新的记录，删除旧的重复记录
"""
import asyncio
from collections import defaultdict
from tortoise import Tortoise
from app.core.settings import get_tortoise_config
from app.models.project import ProjectAccount


async def cleanup_duplicates():
    """清理重复记录"""
    # 初始化数据库
    await Tortoise.init(config=get_tortoise_config())
    
    # 查询所有记录
    all_accounts = await ProjectAccount.all()
    
    # 按 (account, project_id) 分组
    groups = defaultdict(list)
    for account in all_accounts:
        key = (account.account, str(account.project_id))
        groups[key].append(account)
    
    # 找出重复的记录
    duplicates_found = 0
    records_deleted = 0
    
    for key, accounts in groups.items():
        if len(accounts) > 1:
            duplicates_found += 1
            # 按更新时间排序，保留最新的
            accounts.sort(key=lambda x: x.update_time, reverse=True)
            keep = accounts[0]
            delete = accounts[1:]
            
            print(f"\n发现重复记录: account={key[0]}, project_id={key[1]}")
            print(f"  保留: id={keep.id}, balance={keep.balance}, update_time={keep.update_time}")
            
            for acc in delete:
                print(f"  删除: id={acc.id}, balance={acc.balance}, update_time={acc.update_time}")
                await acc.delete()
                records_deleted += 1
    
    print(f"\n清理完成:")
    print(f"  发现重复组: {duplicates_found}")
    print(f"  删除记录数: {records_deleted}")
    
    # 关闭数据库连接
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(cleanup_duplicates())

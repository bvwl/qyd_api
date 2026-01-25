"""
测试db_read函数
"""
import asyncio
from tortoise import Tortoise
from app.core.settings import get_tortoise_config, get_read_db, DB_READ_WRITE_SPLIT
from app.models.stats import ProjectDailyStats
from app.core.database import db_read

async def test():
    # 初始化数据库
    await Tortoise.init(config=get_tortoise_config())
    
    print(f"DB_READ_WRITE_SPLIT: {DB_READ_WRITE_SPLIT}")
    print(f"get_read_db(): {get_read_db()}")
    print(f"Type: {type(get_read_db())}")
    
    # 测试db_read
    print("\n测试 db_read(ProjectDailyStats):")
    query = db_read(ProjectDailyStats)
    print(f"Type: {type(query)}")
    print(f"Query: {query}")
    
    # 测试查询
    try:
        stats_list = await query.all()
        print(f"✅ 查询成功，返回 {len(stats_list)} 条记录")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    # 关闭连接
    await Tortoise.close_connections()

if __name__ == '__main__':
    asyncio.run(test())

"""
数据库读写分离工具模块
"""
from typing import Type, TypeVar
from tortoise.models import Model
from tortoise.queryset import QuerySet
from app.core.settings import get_read_db, get_write_db, DB_READ_WRITE_SPLIT

T = TypeVar('T', bound=Model)


class ReadWriteRouter:
    """读写分离路由器"""
    
    @staticmethod
    def read(model: Type[T]) -> QuerySet[T]:
        """
        获取用于读操作的QuerySet
        
        Args:
            model: Tortoise模型类
            
        Returns:
            QuerySet: 连接到从库的QuerySet
            
        Example:
            # 从从库读取用户列表
            users = await ReadWriteRouter.read(User).all()
            
            # 从从库查询单个用户
            user = await ReadWriteRouter.read(User).get(id=1)
        """
        if DB_READ_WRITE_SPLIT:
            from tortoise import Tortoise
            db_name = get_read_db()
            # 获取实际的数据库连接对象
            db_conn = Tortoise.get_connection(db_name)
            # 使用 filter() 创建 QuerySet，然后指定数据库连接
            return model.filter().using_db(db_conn)
        # 不启用读写分离时，返回一个空的QuerySet（不是all()）
        return model.filter()
    
    @staticmethod
    def write(model: Type[T]) -> QuerySet[T]:
        """
        获取用于写操作的QuerySet
        
        Args:
            model: Tortoise模型类
            
        Returns:
            QuerySet: 连接到主库的QuerySet
            
        Example:
            # 创建新用户（写入主库）
            user = await ReadWriteRouter.write(User).create(
                username="test",
                email="test@example.com"
            )
            
            # 更新用户（写入主库）
            await ReadWriteRouter.write(User).filter(id=1).update(username="new_name")
            
            # 删除用户（写入主库）
            await ReadWriteRouter.write(User).filter(id=1).delete()
        """
        if DB_READ_WRITE_SPLIT:
            from tortoise import Tortoise
            db_name = get_write_db()
            # 获取实际的数据库连接对象
            db_conn = Tortoise.get_connection(db_name)
            return model.filter().using_db(db_conn)
        return model.filter()


# 便捷别名
db_read = ReadWriteRouter.read
db_write = ReadWriteRouter.write


def get_db_info() -> dict:
    """
    获取数据库配置信息
    
    Returns:
        dict: 数据库配置信息
    """
    from app.core.settings import (
        DB_HOST, DB_PORT, DB_NAME,
        DB_SLAVE1_HOST, DB_SLAVE1_PORT,
        DB_SLAVE2_HOST, DB_SLAVE2_PORT,
        DB_READ_WRITE_SPLIT
    )
    
    info = {
        "read_write_split": DB_READ_WRITE_SPLIT,
        "master": {
            "host": DB_HOST,
            "port": DB_PORT,
            "database": DB_NAME,
        }
    }
    
    if DB_READ_WRITE_SPLIT:
        info["slaves"] = [
            {
                "name": "slave1",
                "host": DB_SLAVE1_HOST,
                "port": DB_SLAVE1_PORT,
                "database": DB_NAME,
            },
            {
                "name": "slave2",
                "host": DB_SLAVE2_HOST,
                "port": DB_SLAVE2_PORT,
                "database": DB_NAME,
            }
        ]
    
    return info

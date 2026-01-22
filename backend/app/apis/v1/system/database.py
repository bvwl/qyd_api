"""
数据库信息和读写分离测试API
"""
from fastapi import APIRouter, Depends
from tortoise import Tortoise
from app.core.database import get_db_info
from app.core.settings import DB_READ_WRITE_SPLIT, get_read_db, get_write_db
from app.core.verify import get_current_user

router = APIRouter()


@router.get("/info")
async def get_database_info():
    """
    获取数据库配置信息
    
    Returns:
        dict: 数据库配置信息，包括主从配置
    """
    return get_db_info()


@router.get("/connections")
async def get_database_connections():
    """
    获取当前数据库连接状态
    
    Returns:
        dict: 所有数据库连接的状态信息
    """
    connections = {}
    
    for conn_name in Tortoise._connections.keys():
        try:
            conn = Tortoise.get_connection(conn_name)
            # 执行简单查询测试连接
            result = await conn.execute_query("SELECT 1 as test, DATABASE() as db_name, @@hostname as host")
            connections[conn_name] = {
                "status": "connected",
                "database": result[0]["db_name"] if result else None,
                "host": result[0]["host"] if result else None,
            }
        except Exception as e:
            connections[conn_name] = {
                "status": "error",
                "error": str(e)
            }
    
    return {
        "read_write_split_enabled": DB_READ_WRITE_SPLIT,
        "connections": connections
    }


@router.get("/test-routing")
async def test_database_routing():
    """
    测试数据库路由
    
    Returns:
        dict: 读写操作的路由信息
    """
    read_dbs = []
    for _ in range(10):
        read_dbs.append(get_read_db())
    
    from collections import Counter
    read_distribution = Counter(read_dbs)
    
    return {
        "read_write_split_enabled": DB_READ_WRITE_SPLIT,
        "write_db": get_write_db(),
        "read_db_distribution": dict(read_distribution),
        "total_read_samples": len(read_dbs)
    }


@router.get("/test-query")
async def test_database_query():
    """
    测试数据库查询
    
    执行简单查询测试所有数据库连接
    
    Returns:
        dict: 各数据库的查询结果
    """
    results = {}
    
    for conn_name in Tortoise._connections.keys():
        try:
            conn = Tortoise.get_connection(conn_name)
            result = await conn.execute_query("""
                SELECT 
                    DATABASE() as current_db,
                    @@hostname as hostname,
                    @@port as port,
                    @@server_id as server_id,
                    NOW() as current_time
            """)
            results[conn_name] = {
                "status": "success",
                "data": result[0] if result else None
            }
        except Exception as e:
            results[conn_name] = {
                "status": "error",
                "error": str(e)
            }
    
    return results

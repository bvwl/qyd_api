"""
数据库管理API
"""
from fastapi import APIRouter, Depends, HTTPException
from app.apis.deps import get_admin_user
from app.core.settings import (
    _slave_health_cache,
    check_slave_health,
    DB_READ_WRITE_SPLIT,
    DB_HOST,
    DB_PORT,
    DB_SLAVE1_HOST,
    DB_SLAVE1_PORT,
    DB_SLAVE2_HOST,
    DB_SLAVE2_PORT,
)

app = APIRouter()


@app.get("/health", description="获取数据库健康状态", summary="获取数据库健康状态")
async def get_database_health(
    admin_user: dict = Depends(get_admin_user)
):
    """
    获取数据库健康状态（仅管理员可用）
    
    返回：
    - 主库状态
    - 从库状态
    - 读写分离是否启用
    """
    try:
        result = {
            "read_write_split": DB_READ_WRITE_SPLIT,
            "master": {
                "host": DB_HOST,
                "port": DB_PORT,
                "status": "healthy"  # 主库默认健康
            }
        }
        
        if DB_READ_WRITE_SPLIT:
            # 检查从库健康状态
            slave1_healthy = check_slave_health("slave1")
            slave2_healthy = check_slave_health("slave2")
            
            result["slaves"] = [
                {
                    "name": "slave1",
                    "host": DB_SLAVE1_HOST,
                    "port": DB_SLAVE1_PORT,
                    "status": "healthy" if slave1_healthy else "unhealthy"
                },
                {
                    "name": "slave2",
                    "host": DB_SLAVE2_HOST,
                    "port": DB_SLAVE2_PORT,
                    "status": "healthy" if slave2_healthy else "unhealthy"
                }
            ]
        
        return {
            "code": 1,
            "message": "成功",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据库健康状态失败: {str(e)}")


@app.post("/health/clear-cache", description="清除健康检查缓存", summary="清除健康检查缓存")
async def clear_health_cache(
    admin_user: dict = Depends(get_admin_user)
):
    """
    清除健康检查缓存（仅管理员可用）
    
    用途：
    - 强制重新检查从库健康状态
    - 从库恢复后，立即生效
    """
    try:
        global _slave_health_cache
        _slave_health_cache.clear()
        
        return {
            "code": 1,
            "message": "健康检查缓存已清除"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除缓存失败: {str(e)}")


@app.get("/stats", description="获取数据库统计信息", summary="获取数据库统计信息")
async def get_database_stats(
    admin_user: dict = Depends(get_admin_user)
):
    """
    获取数据库统计信息（仅管理员可用）
    
    返回：
    - 连接池状态
    - 查询统计
    """
    try:
        from tortoise import Tortoise
        
        result = {
            "connections": {}
        }
        
        # 获取所有连接的状态
        for conn_name in ["default", "slave1", "slave2"]:
            try:
                conn = Tortoise.get_connection(conn_name)
                if conn:
                    result["connections"][conn_name] = {
                        "status": "connected",
                        "pool_size": getattr(conn._pool, 'size', 'unknown') if hasattr(conn, '_pool') else 'unknown'
                    }
                else:
                    result["connections"][conn_name] = {
                        "status": "not_configured"
                    }
            except Exception as e:
                result["connections"][conn_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "code": 1,
            "message": "成功",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据库统计信息失败: {str(e)}")

"""
Simple test to verify database connection cleanup works properly
"""
import sys
from pathlib import Path

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import asyncio
from tortoise import Tortoise
from app.core.settings import TORTOISE_ORM


async def test_connection():
    """Test database connection and cleanup"""
    print("Initializing database connection...")
    await Tortoise.init(config=TORTOISE_ORM)
    
    print("Testing connection...")
    conn = Tortoise.get_connection("default")
    result = await conn.execute_query("SELECT 1")
    print(f"Query result: {result}")
    
    print("Closing connections...")
    await Tortoise.close_connections()
    print("✅ Connections closed successfully!")


if __name__ == "__main__":
    asyncio.run(test_connection())

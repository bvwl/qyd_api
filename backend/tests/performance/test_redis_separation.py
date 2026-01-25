#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Redis数据库分离
验证项目账号和项目提现使用不同的Redis数据库
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载.env文件
from dotenv import load_dotenv
env_path = project_root / '.env'
load_dotenv(env_path)

from app.utils.project_account_queue import project_account_queue
from app.utils.project_withdrawal_queue import project_withdrawal_queue


async def test_redis_separation():
    """测试Redis数据库分离"""
    print("=" * 60)
    print("测试Redis数据库分离")
    print("=" * 60)
    print()
    
    # 初始化队列
    await project_account_queue.init_redis()
    await project_withdrawal_queue.init_redis()
    
    print("项目账号队列配置:")
    print(f"  队列名称: {project_account_queue.queue_name}")
    print(f"  队列DB: {project_account_queue.queue_db}")
    print(f"  缓存DB: {project_account_queue.cache_db}")
    print()
    
    print("项目提现队列配置:")
    print(f"  队列名称: {project_withdrawal_queue.queue_name}")
    print(f"  队列DB: {project_withdrawal_queue.queue_db}")
    print(f"  缓存DB: {project_withdrawal_queue.cache_db}")
    print()
    
    # 验证使用不同的数据库
    if project_account_queue.queue_db == project_withdrawal_queue.queue_db:
        print("✗ 错误：两个队列使用相同的队列数据库！")
        return False
    
    if project_account_queue.cache_db == project_withdrawal_queue.cache_db:
        print("✗ 错误：两个队列使用相同的缓存数据库！")
        return False
    
    print("✓ 验证通过：两个队列使用不同的Redis数据库")
    print()
    
    # 测试连接
    try:
        account_redis = await project_account_queue.get_redis()
        withdrawal_redis = await project_withdrawal_queue.get_redis()
        
        # 测试写入
        await account_redis.set("test_account", "account_value")
        await withdrawal_redis.set("test_withdrawal", "withdrawal_value")
        
        # 验证隔离
        account_value = await account_redis.get("test_withdrawal")
        withdrawal_value = await withdrawal_redis.get("test_account")
        
        if account_value is None and withdrawal_value is None:
            print("✓ 数据隔离验证通过：两个队列的数据互不影响")
        else:
            print("✗ 数据隔离验证失败：数据泄露到其他数据库")
            return False
        
        # 清理测试数据
        await account_redis.delete("test_account")
        await withdrawal_redis.delete("test_withdrawal")
        
    except Exception as e:
        print(f"✗ 连接测试失败: {e}")
        return False
    
    print()
    print("=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    result = asyncio.run(test_redis_separation())
    sys.exit(0 if result else 1)

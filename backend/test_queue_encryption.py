#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 Redis 队列的加密功能
"""

import asyncio
import json
from uuid import uuid4


async def test_queue_encryption():
    """测试队列加密功能"""
    print("=" * 60)
    print("测试 Redis 队列加密功能")
    print("=" * 60)
    
    from app.utils.project_account_queue import project_account_queue
    from app.models.project import ProjectInfo
    from tortoise import Tortoise
    from app.core.settings import get_db_url
    
    # 初始化数据库连接
    await Tortoise.init(
        db_url=get_db_url(),
        modules={'models': ['app.models.user', 'app.models.project', 'app.models.server', 'app.models.mail']}
    )
    
    try:
        # 1. 创建测试项目（如果不存在）
        test_project_name = "测试加密项目"
        project = await ProjectInfo.get_or_none(name=test_project_name)
        
        if not project:
            project = await ProjectInfo.create(
                name=test_project_name,
                status=1
            )
            print(f"\n✓ 创建测试项目: {project.name} (ID: {project.id})")
        else:
            print(f"\n✓ 使用现有项目: {project.name} (ID: {project.id})")
        
        # 2. 准备测试数据（包含敏感字段）
        test_data = {
            "account": f"test_queue_{uuid4().hex[:8]}@example.com",
            "project_id": str(project.id),
            "account_type": 2,  # 钱包类型
            "status": 1,
            "balance": 100.5,
            "data": {
                "address": "0x1234567890abcdef",
                "private_key": "0xabcdef1234567890abcdef1234567890",  # 敏感字段
                "mnemonic": "word1 word2 word3 word4 word5 word6",  # 敏感字段
                "balance": 100.5,
                "nested": {
                    "private_key": "nested_private_key_value",  # 嵌套的敏感字段
                    "other_field": "other_value"
                }
            }
        }
        
        print(f"\n原始数据:")
        print(f"  账号: {test_data['account']}")
        print(f"  private_key: {test_data['data']['private_key']}")
        print(f"  mnemonic: {test_data['data']['mnemonic']}")
        print(f"  nested.private_key: {test_data['data']['nested']['private_key']}")
        
        # 3. 添加到队列（应该自动加密）
        print(f"\n添加数据到队列...")
        success = await project_account_queue.add_to_queue(test_data)
        
        if success:
            print(f"✓ 数据已添加到队列")
            
            # 4. 检查队列大小
            queue_size = await project_account_queue.get_queue_size()
            print(f"✓ 当前队列大小: {queue_size}")
            
            # 5. 检查 Redis 中的数据是否已加密
            redis = await project_account_queue.get_redis()
            task_key = project_account_queue._generate_task_key(test_data)
            
            redis_data_str = await redis.get(task_key)
            if redis_data_str:
                redis_data = json.loads(redis_data_str)
                print(f"\nRedis 中存储的数据:")
                print(f"  账号: {redis_data['account']}")
                
                if 'data' in redis_data and redis_data['data']:
                    print(f"  private_key: {redis_data['data'].get('private_key', 'N/A')[:50]}...")
                    print(f"  mnemonic: {redis_data['data'].get('mnemonic', 'N/A')[:50]}...")
                    
                    # 验证是否已加密（加密后的数据应该与原始数据不同）
                    is_encrypted = (
                        redis_data['data'].get('private_key') != test_data['data']['private_key']
                    )
                    
                    if is_encrypted:
                        print(f"\n✓ 敏感字段已加密存储在 Redis 中")
                    else:
                        print(f"\n✗ 警告：敏感字段未加密！")
                else:
                    print(f"  data 字段为空")
            else:
                print(f"\n✗ 无法从 Redis 获取数据")
        else:
            print(f"✗ 添加到队列失败")
        
        print(f"\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)
        print("\n注意：")
        print("1. 数据已加密存储在 Redis 队列中")
        print("2. 队列处理器会将加密数据写入数据库")
        print("3. 查询时根据权限自动解密")
        print("4. 请手动启动队列处理器来处理数据：")
        print("   cd backend && python start_queue_worker.py")
        
    finally:
        await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(test_queue_encryption())

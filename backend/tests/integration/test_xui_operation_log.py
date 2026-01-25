#!/usr/bin/env python3
"""
测试 XUI 操作日志功能
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tortoise import Tortoise
from app.core.settings import TORTOISE_ORM
from app.models.user import XuiOperationLog, XuiOperationType, XuiOperationStatus
from uuid import uuid4


async def test_operation_log():
    """测试操作日志"""
    # 初始化数据库
    await Tortoise.init(config=TORTOISE_ORM)
    
    print("=" * 80)
    print("测试 XUI 操作日志功能")
    print("=" * 80)
    
    # 1. 创建测试日志
    print("\n1. 创建失败日志...")
    log = await XuiOperationLog.create(
        operation_type=XuiOperationType.ADD_ACCOUNT,
        status=XuiOperationStatus.FAILED,
        inbound_id=uuid4(),
        account_id=uuid4(),
        inbound_info="192.168.1.1:8080",
        account_username="test_user",
        error_message="测试错误: 解密密码失败"
    )
    print(f"✅ 创建日志成功: {log.id}")
    print(f"   操作类型: {log.operation_type}")
    print(f"   状态: {log.status}")
    print(f"   入站信息: {log.inbound_info}")
    print(f"   账号用户名: {log.account_username}")
    print(f"   错误信息: {log.error_message}")
    
    # 2. 查询失败日志
    print("\n2. 查询失败日志...")
    failed_logs = await XuiOperationLog.filter(status=XuiOperationStatus.FAILED).all()
    print(f"✅ 找到 {len(failed_logs)} 条失败日志")
    for log in failed_logs[:5]:  # 只显示前5条
        print(f"   - {log.account_username}: {log.error_message}")
    
    # 3. 更新日志状态(模拟重试)
    print("\n3. 模拟重试...")
    log.status = XuiOperationStatus.RETRYING
    log.retry_count += 1
    await log.save()
    print(f"✅ 更新状态为重试中,重试次数: {log.retry_count}")
    
    # 4. 模拟重试成功
    print("\n4. 模拟重试成功...")
    log.status = XuiOperationStatus.SUCCESS
    log.error_message = None
    await log.save()
    print(f"✅ 更新状态为成功")
    
    # 5. 统计
    print("\n5. 统计信息...")
    total = await XuiOperationLog.all().count()
    success = await XuiOperationLog.filter(status=XuiOperationStatus.SUCCESS).count()
    failed = await XuiOperationLog.filter(status=XuiOperationStatus.FAILED).count()
    print(f"✅ 总计: {total} 条")
    print(f"   成功: {success} 条")
    print(f"   失败: {failed} 条")
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)
    
    await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(test_operation_log())

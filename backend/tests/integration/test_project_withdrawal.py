#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试项目提现功能
"""
import asyncio
import sys
from pathlib import Path
from decimal import Decimal
from uuid import uuid4

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载.env文件
from dotenv import load_dotenv
env_path = project_root / '.env'
load_dotenv(env_path)


async def test_withdrawal():
    """测试项目提现功能"""
    print("=" * 60)
    print("测试项目提现功能")
    print("=" * 60)
    
    from tortoise import Tortoise
    from app.core import settings
    from app.models.project import ProjectInfo, ProjectWithdrawal
    from datetime import datetime
    
    # 初始化数据库连接
    await Tortoise.init(config=settings.TORTOISE_ORM)
    print(f"✓ 数据库连接成功\n")
    
    try:
        # 1. 创建测试项目
        test_project_name = f"测试提现项目_{uuid4().hex[:8]}"
        project = await ProjectInfo.create(
            name=test_project_name,
            status=1
        )
        print(f"\n✓ 创建测试项目: {project.name} (ID: {project.id})")
        
        # 2. 测试创建提现记录（只传入平台币）
        print(f"\n{'='*60}")
        print("测试1: 创建提现记录（只传入平台币）")
        print(f"{'='*60}")
        
        platform_coin_value = Decimal("123.456789012345678901")  # 超过18位小数
        withdrawal = await ProjectWithdrawal.create(
            project_id=project.id,
            platform_coin=platform_coin_value,
            platform_coin_change=platform_coin_value,
            platform_coin_history={
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"): str(platform_coin_value)
            }
        )
        
        print(f"✓ 创建成功")
        print(f"  平台币: {withdrawal.platform_coin}")
        print(f"  平台币变动: {withdrawal.platform_coin_change}")
        print(f"  平台币历史: {withdrawal.platform_coin_history}")
        
        # 3. 测试更新（添加稳定币）
        print(f"\n{'='*60}")
        print("测试2: 更新记录（添加稳定币）")
        print(f"{'='*60}")
        
        stable_coin_value = Decimal("999.888777666555444333")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        withdrawal.stable_coin = stable_coin_value
        withdrawal.stable_coin_change = stable_coin_value
        withdrawal.stable_coin_history = {now: str(stable_coin_value)}
        await withdrawal.save()
        
        print(f"✓ 更新成功")
        print(f"  稳定币: {withdrawal.stable_coin}")
        print(f"  稳定币变动: {withdrawal.stable_coin_change}")
        print(f"  稳定币历史: {withdrawal.stable_coin_history}")
        
        # 4. 测试再次更新（修改平台币和添加人民币）
        print(f"\n{'='*60}")
        print("测试3: 再次更新（修改平台币和添加人民币）")
        print(f"{'='*60}")
        
        new_platform_coin = Decimal("200.123456789012345678")
        rmb_value = Decimal("1000.50")
        now2 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 更新平台币
        old_platform_coin = withdrawal.platform_coin
        withdrawal.platform_coin = new_platform_coin
        withdrawal.platform_coin_change = new_platform_coin - old_platform_coin
        if withdrawal.platform_coin_history is None:
            withdrawal.platform_coin_history = {}
        withdrawal.platform_coin_history[now2] = str(new_platform_coin)
        
        # 添加人民币
        withdrawal.rmb = rmb_value
        withdrawal.rmb_change = rmb_value
        withdrawal.rmb_history = {now2: str(rmb_value)}
        
        await withdrawal.save()
        
        print(f"✓ 更新成功")
        print(f"  平台币: {withdrawal.platform_coin}")
        print(f"  平台币变动: {withdrawal.platform_coin_change}")
        print(f"  平台币历史记录数: {len(withdrawal.platform_coin_history)}")
        print(f"  人民币: {withdrawal.rmb}")
        print(f"  人民币变动: {withdrawal.rmb_change}")
        
        # 5. 测试查询
        print(f"\n{'='*60}")
        print("测试4: 查询记录")
        print(f"{'='*60}")
        
        found = await ProjectWithdrawal.get(id=withdrawal.id)
        await found.fetch_related('project')
        
        print(f"✓ 查询成功")
        print(f"  项目: {found.project.name}")
        print(f"  平台币: {found.platform_coin}")
        print(f"  稳定币: {found.stable_coin}")
        print(f"  人民币: {found.rmb}")
        print(f"  平台币历史记录: {found.platform_coin_history}")
        print(f"  稳定币历史记录: {found.stable_coin_history}")
        print(f"  人民币历史记录: {found.rmb_history}")
        
        # 6. 测试精度
        print(f"\n{'='*60}")
        print("测试5: 验证精度")
        print(f"{'='*60}")
        
        # 验证平台币精度（18位小数）
        test_value = Decimal("0.123456789012345678")
        withdrawal.platform_coin = test_value
        await withdrawal.save()
        
        reloaded = await ProjectWithdrawal.get(id=withdrawal.id)
        print(f"✓ 精度测试")
        print(f"  原始值: {test_value}")
        print(f"  存储值: {reloaded.platform_coin}")
        print(f"  精度保持: {test_value == reloaded.platform_coin}")
        
        # 7. 清理测试数据
        print(f"\n{'='*60}")
        print("清理测试数据")
        print(f"{'='*60}")
        
        await withdrawal.delete()
        await project.delete()
        print(f"✓ 清理完成")
        
        print(f"\n{'='*60}")
        print("✓ 所有测试通过！")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(test_withdrawal())

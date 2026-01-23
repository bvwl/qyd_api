#!/usr/bin/env python3
"""
Redis队列性能测试脚本
测试项目账号批量处理的性能
"""
import asyncio
import time
import sys
from uuid import uuid4
from decimal import Decimal

# 添加项目路径
sys.path.insert(0, '.')

from app.utils.project_account_queue import project_account_queue
from app.core.settings import REDIS_QUEUE_NUM_WORKERS, REDIS_QUEUE_BATCH_SIZE


async def test_add_performance(num_items=2000):
    """测试添加性能"""
    print(f"\n{'='*60}")
    print(f"测试1: 添加 {num_items} 条数据到队列")
    print(f"{'='*60}")
    
    await project_account_queue.init_redis()
    
    start_time = time.time()
    success = 0
    fail = 0
    
    # 生成测试数据
    test_project_id = str(uuid4())
    
    for i in range(num_items):
        data = {
            "account": f"test{i}@example.com",
            "project_id": test_project_id,
            "password": f"password{i}",
            "status": 1,
            "account_type": 1,
            "balance": float(Decimal("100.00") + Decimal(str(i))),
            "data": {"test": f"data{i}"}
        }
        
        if await project_account_queue.add_to_queue(data):
            success += 1
        else:
            fail += 1
        
        # 每100条显示进度
        if (i + 1) % 100 == 0:
            print(f"进度: {i + 1}/{num_items} ({(i+1)/num_items*100:.1f}%)")
    
    elapsed = time.time() - start_time
    
    print(f"\n添加结果:")
    print(f"  成功: {success} 条")
    print(f"  失败: {fail} 条")
    print(f"  耗时: {elapsed:.2f} 秒")
    print(f"  速度: {success/elapsed:.2f} 条/秒")
    
    # 获取队列大小
    queue_size = await project_account_queue.get_queue_size()
    print(f"  队列大小: {queue_size} 条")
    
    return queue_size


async def test_process_performance():
    """测试处理性能"""
    print(f"\n{'='*60}")
    print(f"测试2: 监控处理性能")
    print(f"{'='*60}")
    
    print(f"\n配置信息:")
    print(f"  Worker数量: {REDIS_QUEUE_NUM_WORKERS}")
    print(f"  批处理大小: {REDIS_QUEUE_BATCH_SIZE}")
    
    # 启动队列处理
    print(f"\n启动队列处理...")
    await project_account_queue.start()
    
    # 监控处理进度
    print(f"\n开始监控...")
    start_time = time.time()
    start_size = await project_account_queue.get_queue_size()
    last_size = start_size
    
    print(f"初始队列大小: {start_size} 条\n")
    
    monitor_interval = 2  # 每2秒监控一次
    
    while True:
        await asyncio.sleep(monitor_interval)
        
        current_size = await project_account_queue.get_queue_size()
        elapsed = time.time() - start_time
        
        # 计算处理速度
        processed = start_size - current_size
        if elapsed > 0:
            avg_rate = processed / elapsed
        else:
            avg_rate = 0
        
        # 计算瞬时速度
        instant_processed = last_size - current_size
        if monitor_interval > 0:
            instant_rate = instant_processed / monitor_interval
        else:
            instant_rate = 0
        
        print(f"[{elapsed:6.1f}s] 剩余: {current_size:5d} | "
              f"已处理: {processed:5d} | "
              f"平均: {avg_rate:6.1f}条/秒 | "
              f"瞬时: {instant_rate:6.1f}条/秒")
        
        last_size = current_size
        
        # 队列为空，处理完成
        if current_size == 0:
            break
    
    total_time = time.time() - start_time
    
    print(f"\n处理完成:")
    print(f"  总数据量: {start_size} 条")
    print(f"  总耗时: {total_time:.2f} 秒")
    print(f"  平均速度: {start_size/total_time:.2f} 条/秒")
    
    # 停止队列处理
    await project_account_queue.stop()
    
    return start_size / total_time


async def test_sustained_performance(duration=60):
    """测试持续性能（持续添加和处理）"""
    print(f"\n{'='*60}")
    print(f"测试3: 持续性能测试（{duration}秒）")
    print(f"{'='*60}")
    
    await project_account_queue.init_redis()
    await project_account_queue.start()
    
    test_project_id = str(uuid4())
    
    start_time = time.time()
    total_added = 0
    
    print(f"\n开始持续添加数据...")
    
    async def add_data():
        """持续添加数据"""
        nonlocal total_added
        counter = 0
        while time.time() - start_time < duration:
            data = {
                "account": f"sustained{counter}@example.com",
                "project_id": test_project_id,
                "balance": 100.00 + counter
            }
            if await project_account_queue.add_to_queue(data):
                total_added += 1
                counter += 1
            await asyncio.sleep(0.001)  # 控制添加速度
    
    async def monitor():
        """监控处理进度"""
        last_time = start_time
        last_size = 0
        
        while time.time() - start_time < duration:
            await asyncio.sleep(5)
            
            current_time = time.time()
            current_size = await project_account_queue.get_queue_size()
            elapsed = current_time - start_time
            
            print(f"[{elapsed:5.1f}s] 已添加: {total_added:5d} | "
                  f"队列大小: {current_size:5d} | "
                  f"添加速度: {total_added/elapsed:.1f}条/秒")
            
            last_time = current_time
            last_size = current_size
    
    # 并发执行添加和监控
    await asyncio.gather(add_data(), monitor())
    
    # 等待队列处理完成
    print(f"\n等待队列处理完成...")
    while True:
        size = await project_account_queue.get_queue_size()
        if size == 0:
            break
        print(f"剩余: {size} 条")
        await asyncio.sleep(2)
    
    total_time = time.time() - start_time
    
    print(f"\n持续性能测试结果:")
    print(f"  测试时长: {duration} 秒")
    print(f"  总添加: {total_added} 条")
    print(f"  总耗时: {total_time:.2f} 秒")
    print(f"  平均速度: {total_added/total_time:.2f} 条/秒")
    
    await project_account_queue.stop()


async def main():
    """主测试函数"""
    print(f"\n{'#'*60}")
    print(f"# Redis队列性能测试")
    print(f"{'#'*60}")
    
    try:
        # 测试1: 添加性能
        queue_size = await test_add_performance(2000)
        
        if queue_size > 0:
            # 测试2: 处理性能
            process_rate = await test_process_performance()
            
            print(f"\n{'='*60}")
            print(f"性能总结")
            print(f"{'='*60}")
            print(f"处理速度: {process_rate:.2f} 条/秒")
            
            if process_rate >= 2000:
                print(f"✅ 达到目标性能（2000条/秒）")
            else:
                print(f"❌ 未达到目标性能（2000条/秒）")
                print(f"差距: {2000 - process_rate:.2f} 条/秒")
                print(f"\n优化建议:")
                print(f"  1. 增加Worker数量: REDIS_QUEUE_NUM_WORKERS")
                print(f"  2. 增加批处理大小: REDIS_QUEUE_BATCH_SIZE")
                print(f"  3. 增加数据库连接池: DB_MAXSIZE")
                print(f"  4. 增加Redis连接池: REDIS_MAX_CONNECTIONS")
        
        # 可选：测试3 - 持续性能测试
        # await test_sustained_performance(60)
        
    except KeyboardInterrupt:
        print(f"\n\n测试被中断")
        await project_account_queue.stop()
    except Exception as e:
        print(f"\n\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        await project_account_queue.stop()


if __name__ == "__main__":
    asyncio.run(main())

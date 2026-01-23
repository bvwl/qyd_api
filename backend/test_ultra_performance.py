"""
超高性能测试脚本
测试10000+条/秒的处理能力
"""
import asyncio
import time
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parent))

# 加载环境变量
from start import load_env_from_file
load_env_from_file()

from tortoise import Tortoise
from app.core.settings import get_tortoise_config, REDIS_ENABLED
from app.utils.logs import getLogger

logger = getLogger('app')


async def test_ultra_performance():
    """测试超高性能配置"""
    print("="*70)
    print("超高性能测试 - 目标: 10000+条/秒")
    print("="*70)
    
    if not REDIS_ENABLED:
        print("❌ Redis未启用，无法进行测试")
        return
    
    # 初始化数据库
    try:
        await Tortoise.init(config=get_tortoise_config())
        print("✅ 数据库连接已建立")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return
    
    try:
        from app.utils.project_account_queue import project_account_queue
        
        # 测试配置
        test_count = 50000  # 5万条数据
        batch_size = int(os.getenv("REDIS_QUEUE_BATCH_SIZE", "500"))
        num_workers = int(os.getenv("REDIS_QUEUE_NUM_WORKERS", "12"))
        
        print(f"\n测试配置：")
        print(f"  数据量: {test_count:,} 条")
        print(f"  批处理大小: {batch_size}")
        print(f"  Worker数量: {num_workers}")
        print(f"  预期性能: {num_workers * batch_size / 1.5:.0f} 条/秒")
        
        # 生成测试数据
        print(f"\n{'='*70}")
        print(f"阶段1: 生成测试数据")
        print(f"{'='*70}")
        
        test_data = []
        for i in range(test_count):
            test_data.append({
                'project_id': f'perf_test_project_{i % 100}',
                'account': f'perf_test_account_{i}',
                'password': f'password_{i}',
                'balance': 1000.0 + (i % 1000),
                'status': 1,
                'remark': f'Performance test data {i}'
            })
        
        print(f"✅ 已生成 {test_count:,} 条测试数据")
        
        # 添加到队列
        print(f"\n{'='*70}")
        print(f"阶段2: 添加数据到Redis队列")
        print(f"{'='*70}")
        
        add_start = time.time()
        success_count = 0
        fail_count = 0
        
        for i, data in enumerate(test_data):
            if await project_account_queue.add_to_queue(data):
                success_count += 1
            else:
                fail_count += 1
            
            # 每1000条显示进度
            if (i + 1) % 1000 == 0:
                elapsed = time.time() - add_start
                speed = (i + 1) / elapsed
                print(f"  进度: {i+1:,}/{test_count:,} ({(i+1)/test_count*100:.1f}%) - "
                      f"速度: {speed:.0f}条/秒")
        
        add_time = time.time() - add_start
        
        print(f"\n✅ 添加完成")
        print(f"  成功: {success_count:,} 条")
        print(f"  失败: {fail_count:,} 条")
        print(f"  耗时: {add_time:.2f}秒")
        print(f"  速度: {success_count/add_time:.0f}条/秒")
        
        # 等待处理完成
        print(f"\n{'='*70}")
        print(f"阶段3: 等待队列处理完成")
        print(f"{'='*70}")
        
        process_start = time.time()
        last_size = await project_account_queue.get_queue_size()
        check_count = 0
        
        print(f"  初始队列大小: {last_size:,} 条")
        
        while True:
            await asyncio.sleep(2)
            
            current_size = await project_account_queue.get_queue_size()
            elapsed = time.time() - process_start
            
            if current_size > 0:
                processed = last_size - current_size
                if processed > 0:
                    speed = processed / 2  # 2秒间隔
                    eta = current_size / speed if speed > 0 else 0
                    print(f"  剩余: {current_size:,} 条 | "
                          f"处理速度: {speed:.0f}条/秒 | "
                          f"已用时: {elapsed:.0f}秒 | "
                          f"预计剩余: {eta:.0f}秒")
                last_size = current_size
            else:
                # 队列为空，再等待5秒确认
                check_count += 1
                if check_count >= 3:
                    break
                print(f"  队列为空，确认中... ({check_count}/3)")
        
        process_time = time.time() - process_start
        total_time = time.time() - add_start
        
        # 显示结果
        print(f"\n{'='*70}")
        print(f"测试完成！")
        print(f"{'='*70}")
        
        print(f"\n📊 性能统计：")
        print(f"  数据量: {test_count:,} 条")
        print(f"  添加耗时: {add_time:.2f}秒")
        print(f"  处理耗时: {process_time:.2f}秒")
        print(f"  总耗时: {total_time:.2f}秒")
        print(f"  添加速度: {success_count/add_time:.0f}条/秒")
        print(f"  处理速度: {test_count/process_time:.0f}条/秒")
        
        # 性能评估
        processing_speed = test_count / process_time
        
        print(f"\n🎯 性能评估：")
        if processing_speed >= 15000:
            print(f"  ⭐⭐⭐ 优秀！处理速度: {processing_speed:.0f}条/秒 (>= 15000)")
        elif processing_speed >= 10000:
            print(f"  ✅ 达标！处理速度: {processing_speed:.0f}条/秒 (>= 10000)")
        elif processing_speed >= 5000:
            print(f"  ⚠️  接近达标，处理速度: {processing_speed:.0f}条/秒 (>= 5000)")
        else:
            print(f"  ❌ 未达标，处理速度: {processing_speed:.0f}条/秒 (< 5000)")
        
        # 优化建议
        if processing_speed < 10000:
            print(f"\n💡 优化建议：")
            if processing_speed < 5000:
                print(f"  1. 增加队列进程数（当前可能只有1个）")
                print(f"  2. 增加批处理大小: REDIS_QUEUE_BATCH_SIZE=800")
                print(f"  3. 检查数据库性能和索引")
            elif processing_speed < 8000:
                print(f"  1. 增加批处理大小: REDIS_QUEUE_BATCH_SIZE=800")
                print(f"  2. 增加worker数量: REDIS_QUEUE_NUM_WORKERS=16")
            else:
                print(f"  1. 微调批处理大小: REDIS_QUEUE_BATCH_SIZE=600")
                print(f"  2. 启动多个队列进程（2-3个）")
        
        print(f"\n{'='*70}")
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        print(f"\n❌ 测试失败: {e}")
    finally:
        # 关闭数据库连接
        await Tortoise.close_connections()
        print("\n✅ 数据库连接已关闭")


async def cleanup_test_data():
    """清理测试数据"""
    print("\n清理测试数据...")
    
    try:
        await Tortoise.init(config=get_tortoise_config())
        
        from app.models.project import ProjectAccount
        
        # 删除测试数据
        deleted = await ProjectAccount.filter(
            project_id__startswith='perf_test_project_'
        ).delete()
        
        print(f"✅ 已删除 {deleted} 条测试数据")
        
    except Exception as e:
        print(f"❌ 清理失败: {e}")
    finally:
        await Tortoise.close_connections()


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='超高性能测试')
    parser.add_argument('--cleanup', action='store_true', help='清理测试数据')
    args = parser.parse_args()
    
    if args.cleanup:
        await cleanup_test_data()
    else:
        await test_ultra_performance()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n测试已中断")
        sys.exit(0)

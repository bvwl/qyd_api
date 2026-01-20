#!/usr/bin/env python3
"""
日志系统测试脚本
验证日志系统的各项功能
"""

import os
import sys
import time
import glob
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.logs import getLogger, log_api_call, compress_old_logs, delete_old_compressed_logs


def test_basic_logging():
    """测试基础日志功能"""
    print("\n=== 测试 1: 基础日志功能 ===")
    
    logger = getLogger('test')
    logger.debug("这是 DEBUG 日志")
    logger.info("这是 INFO 日志")
    logger.warning("这是 WARNING 日志")
    logger.error("这是 ERROR 日志")
    
    print("✓ 基础日志测试完成")


def test_multiple_modules():
    """测试多模块独立日志"""
    print("\n=== 测试 2: 多模块独立日志 ===")
    
    modules = ['user', 'project', 'server', 'mail', 'api']
    
    for module in modules:
        logger = getLogger(module)
        logger.info(f"{module} 模块日志测试")
    
    # 检查日志文件是否创建
    log_dir = "logs"
    for module in modules:
        log_file = os.path.join(log_dir, f"{module}.log")
        if os.path.exists(log_file):
            print(f"✓ {module}.log 创建成功")
        else:
            print(f"✗ {module}.log 创建失败")


def test_api_logging():
    """测试 API 日志功能"""
    print("\n=== 测试 3: API 日志功能 ===")
    
    logger = getLogger('api_test')
    
    # 测试成功请求
    log_api_call(
        logger=logger,
        user_id="test_user_123",
        endpoint="/api/v1/test",
        method="GET",
        params={"id": 1, "name": "test"},
        response_status=200,
        client_ip="127.0.0.1"
    )
    
    # 测试失败请求
    log_api_call(
        logger=logger,
        user_id="test_user_456",
        endpoint="/api/v1/login",
        method="POST",
        params={"username": "test", "password": "should_be_filtered"},
        response_status=401,
        client_ip="192.168.1.100"
    )
    
    print("✓ API 日志测试完成")


def test_logger_singleton():
    """测试 Logger 单例模式"""
    print("\n=== 测试 4: Logger 单例模式 ===")
    
    logger1 = getLogger('singleton_test')
    logger2 = getLogger('singleton_test')
    
    if id(logger1) == id(logger2):
        print("✓ Logger 单例模式正常")
    else:
        print("✗ Logger 单例模式失败")


def test_log_compression():
    """测试日志压缩功能"""
    print("\n=== 测试 5: 日志压缩功能 ===")
    
    log_dir = "logs"
    test_logger_name = "compression_test"
    
    # 创建测试日志
    logger = getLogger(test_logger_name)
    for i in range(100):
        logger.info(f"测试日志压缩 - 消息 {i}")
    
    # 创建一个模拟的旧日志文件
    test_old_log = os.path.join(log_dir, f"{test_logger_name}.log.2026-01-20_00")
    if not os.path.exists(test_old_log):
        with open(test_old_log, 'w') as f:
            f.write("这是一个测试的旧日志文件\n" * 100)
        print(f"✓ 创建测试旧日志文件: {test_old_log}")
    
    # 执行压缩
    compress_old_logs(log_dir=log_dir, name=test_logger_name)
    
    # 检查是否生成了压缩文件
    compressed_file = test_old_log + '.gz'
    if os.path.exists(compressed_file):
        print(f"✓ 日志压缩成功: {compressed_file}")
        
        # 比较文件大小
        if os.path.exists(test_old_log):
            original_size = os.path.getsize(test_old_log)
        else:
            original_size = 0
        compressed_size = os.path.getsize(compressed_file)
        
        if original_size > 0:
            ratio = (1 - compressed_size / original_size) * 100
            print(f"  压缩率: {ratio:.1f}%")
    else:
        print("✗ 日志压缩失败")


def test_log_cleanup():
    """测试日志清理功能"""
    print("\n=== 测试 6: 日志清理功能 ===")
    
    log_dir = "logs"
    
    # 统计清理前的文件数量
    before_count = len(glob.glob(os.path.join(log_dir, "*.gz")))
    print(f"清理前压缩日志文件数量: {before_count}")
    
    # 执行清理（保留 30 天）
    delete_old_compressed_logs(log_dir=log_dir, days=30)
    
    # 统计清理后的文件数量
    after_count = len(glob.glob(os.path.join(log_dir, "*.gz")))
    print(f"清理后压缩日志文件数量: {after_count}")
    
    print("✓ 日志清理测试完成")


def test_performance():
    """测试日志性能"""
    print("\n=== 测试 7: 日志性能测试 ===")
    
    logger = getLogger('performance_test')
    
    # 测试写入 1000 条日志的时间
    start_time = time.time()
    for i in range(1000):
        logger.info(f"性能测试消息 {i}")
    elapsed = time.time() - start_time
    
    print(f"写入 1000 条日志耗时: {elapsed:.3f} 秒")
    print(f"平均每条日志耗时: {elapsed/1000*1000:.3f} 毫秒")
    
    if elapsed < 1.0:
        print("✓ 日志性能良好")
    else:
        print("⚠ 日志性能可能需要优化")


def test_log_file_structure():
    """测试日志文件结构"""
    print("\n=== 测试 8: 日志文件结构 ===")
    
    log_dir = "logs"
    
    if not os.path.exists(log_dir):
        print(f"✗ 日志目录不存在: {log_dir}")
        return
    
    print(f"日志目录: {log_dir}")
    
    # 统计各类文件
    log_files = glob.glob(os.path.join(log_dir, "*.log"))
    rotated_files = glob.glob(os.path.join(log_dir, "*.log.*"))
    compressed_files = glob.glob(os.path.join(log_dir, "*.log.*.gz"))
    uncompressed_rotated = [f for f in rotated_files if not f.endswith('.gz')]
    
    print(f"  当前日志文件: {len(log_files)} 个")
    print(f"  滚动日志文件: {len(rotated_files)} 个")
    print(f"  压缩日志文件: {len(compressed_files)} 个")
    print(f"  未压缩滚动日志: {len(uncompressed_rotated)} 个")
    
    # 计算总大小
    total_size = 0
    for pattern in ["*.log", "*.log.*"]:
        for file in glob.glob(os.path.join(log_dir, pattern)):
            total_size += os.path.getsize(file)
    
    print(f"  总大小: {total_size / 1024:.2f} KB")
    
    print("✓ 日志文件结构检查完成")


def display_summary():
    """显示测试摘要"""
    print("\n" + "="*60)
    print("日志系统测试摘要")
    print("="*60)
    
    log_dir = "logs"
    
    if os.path.exists(log_dir):
        # 列出所有日志文件
        log_files = sorted(glob.glob(os.path.join(log_dir, "*.log")))
        
        print("\n当前日志文件:")
        for log_file in log_files:
            size = os.path.getsize(log_file)
            print(f"  - {os.path.basename(log_file)} ({size} bytes)")
        
        # 列出压缩文件
        compressed_files = sorted(glob.glob(os.path.join(log_dir, "*.log.*.gz")))
        if compressed_files:
            print(f"\n压缩日志文件: {len(compressed_files)} 个")
    
    print("\n测试完成！请查看 logs/ 目录下的日志文件。")
    print("="*60)


def main():
    """运行所有测试"""
    print("="*60)
    print("日志系统测试")
    print("="*60)
    
    try:
        test_basic_logging()
        test_multiple_modules()
        test_api_logging()
        test_logger_singleton()
        test_log_compression()
        test_log_cleanup()
        test_performance()
        test_log_file_structure()
        
        display_summary()
        
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

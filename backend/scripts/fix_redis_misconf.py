#!/usr/bin/env python3
"""
Redis MISCONF 错误快速修复脚本
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from redis.asyncio import Redis
from app.core.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD


async def check_redis_connection():
    """检查 Redis 连接"""
    try:
        redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
        if REDIS_PASSWORD:
            redis_url = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"
        
        redis = Redis.from_url(redis_url, decode_responses=True)
        await redis.ping()
        print("✅ Redis 连接正常")
        return redis
    except Exception as e:
        print(f"❌ 无法连接到 Redis: {e}")
        return None


async def check_disk_space():
    """检查磁盘空间"""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        
        used_percent = (used / total) * 100
        
        print(f"\n磁盘空间:")
        print(f"  总计: {total // (2**30)} GB")
        print(f"  已用: {used // (2**30)} GB ({used_percent:.1f}%)")
        print(f"  可用: {free // (2**30)} GB")
        
        if used_percent > 90:
            print(f"⚠️  警告: 磁盘使用率 {used_percent:.1f}%，建议清理磁盘空间")
            print("\n可以运行以下命令清理日志:")
            print("  python backend/scripts/cleanup_logs.py")
        else:
            print(f"✅ 磁盘空间充足")
        
        return used_percent
    except Exception as e:
        print(f"⚠️  无法检查磁盘空间: {e}")
        return None


async def check_redis_memory(redis):
    """检查 Redis 内存使用"""
    try:
        info = await redis.info("memory")
        used_memory = info.get("used_memory_human", "N/A")
        maxmemory = info.get("maxmemory_human", "N/A")
        
        print(f"\nRedis 内存使用:")
        print(f"  已用内存: {used_memory}")
        print(f"  最大内存: {maxmemory}")
        
        return info
    except Exception as e:
        print(f"⚠️  无法获取 Redis 内存信息: {e}")
        return None


async def check_redis_config(redis):
    """检查 Redis 配置"""
    try:
        config = await redis.config_get("stop-writes-on-bgsave-error")
        current_value = config.get("stop-writes-on-bgsave-error", "unknown")
        
        print(f"\n当前 Redis 持久化配置:")
        print(f"  stop-writes-on-bgsave-error: {current_value}")
        
        return current_value
    except Exception as e:
        print(f"⚠️  无法获取 Redis 配置: {e}")
        return None


async def fix_redis_config(redis):
    """修复 Redis 配置"""
    try:
        await redis.config_set("stop-writes-on-bgsave-error", "no")
        print("\n✅ 配置已更新: stop-writes-on-bgsave-error = no")
        
        # 验证配置
        config = await redis.config_get("stop-writes-on-bgsave-error")
        new_value = config.get("stop-writes-on-bgsave-error", "unknown")
        print(f"验证配置: stop-writes-on-bgsave-error = {new_value}")
        
        print("\n⚠️  注意: 此配置在 Redis 重启后会失效")
        print("如需永久生效，请修改 redis.conf 文件:")
        print("  stop-writes-on-bgsave-error no")
        
        return True
    except Exception as e:
        print(f"❌ 配置更新失败: {e}")
        return False


async def test_redis_write(redis):
    """测试 Redis 写入"""
    try:
        import time
        test_key = f"test_fix_{int(time.time())}"
        
        await redis.set(test_key, "test_value", ex=10)
        print("\n✅ Redis 写入测试成功")
        
        await redis.delete(test_key)
        return True
    except Exception as e:
        print(f"\n❌ Redis 写入测试失败: {e}")
        print("\n建议:")
        print("1. 检查磁盘空间是否充足")
        print("2. 检查 Redis 日志")
        print("3. 查看详细修复指南: cat REDIS_MISCONF_FIX.md")
        return False


async def main():
    """主函数"""
    print("=" * 50)
    print("Redis MISCONF 错误快速修复")
    print("=" * 50)
    
    print(f"\nRedis 配置:")
    print(f"  主机: {REDIS_HOST}")
    print(f"  端口: {REDIS_PORT}")
    
    # 1. 检查 Redis 连接
    print("\n1. 检查 Redis 连接...")
    redis = await check_redis_connection()
    if not redis:
        return
    
    # 2. 检查磁盘空间
    print("\n2. 检查磁盘空间...")
    disk_usage = await check_disk_space()
    
    # 3. 检查 Redis 内存
    print("\n3. 检查 Redis 内存使用...")
    await check_redis_memory(redis)
    
    # 4. 检查当前配置
    print("\n4. 检查当前配置...")
    current_config = await check_redis_config(redis)
    
    # 5. 询问是否修复
    print("\n" + "=" * 50)
    print("修复选项:")
    print("=" * 50)
    print("1. 禁用持久化错误检查 (推荐，立即生效)")
    print("2. 仅测试写入，不修改配置")
    print("3. 退出")
    
    try:
        choice = input("\n请选择 (1/2/3): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\n已取消")
        await redis.close()
        return
    
    if choice == "1":
        print("\n正在禁用持久化错误检查...")
        success = await fix_redis_config(redis)
        
        if success:
            print("\n测试 Redis 写入...")
            await test_redis_write(redis)
    elif choice == "2":
        print("\n测试 Redis 写入...")
        await test_redis_write(redis)
    elif choice == "3":
        print("\n已退出，未做任何修改")
    else:
        print("\n无效选择")
    
    # 关闭连接
    await redis.close()
    
    print("\n完成！")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

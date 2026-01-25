#!/usr/bin/env python3
"""
测试时间参数修复是否成功
"""

import asyncio
import sys
from datetime import datetime
from app.utils.time_tool import parse_time


async def test_parse_time():
    """测试parse_time函数"""
    print("=" * 60)
    print("测试 parse_time() 函数")
    print("=" * 60)
    
    # 测试1: 字符串日期
    test_cases = [
        ("2026-01-25", False),
        ("2026-01-25", True),
        ("2026-01-25 10:30:00", False),
        (1737792000000, False),  # 13位时间戳
        (1737792000, False),     # 10位时间戳
    ]
    
    for val, is_end in test_cases:
        try:
            result = parse_time(val, is_end)
            print(f"✅ parse_time({val!r}, is_end={is_end}) = {result}")
        except Exception as e:
            print(f"❌ parse_time({val!r}, is_end={is_end}) 失败: {e}")
    
    # 测试2: 传入datetime对象（这应该会失败，因为parse_time不支持）
    print("\n" + "=" * 60)
    print("测试传入 datetime 对象（预期失败）")
    print("=" * 60)
    
    dt = datetime.now()
    try:
        result = parse_time(dt)
        print(f"❌ 意外成功: parse_time(datetime对象) = {result}")
    except Exception as e:
        print(f"✅ 预期失败: parse_time(datetime对象) 失败: {e}")
    
    print("\n" + "=" * 60)
    print("结论：")
    print("- parse_time() 只能处理字符串和整数")
    print("- API层不应该调用parse_time()，应该直接传递原始参数给CRUD层")
    print("- CRUD层统一调用parse_time()进行解析")
    print("=" * 60)


if __name__ == '__main__':
    asyncio.run(test_parse_time())

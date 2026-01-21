#!/usr/bin/env python3
"""
测试 gen_api_token 函数
"""
from app.core.tools import gen_api_token
import hashlib
import time

def test_gen_api_token():
    """测试API Token生成函数"""
    
    print("="*60)
    print("  测试 gen_api_token 函数")
    print("="*60)
    
    # 测试用例
    test_cases = [
        {
            "username": "test@example.com",
            "timestamp": 1737446400000,  # 固定时间戳
            "expected": hashlib.md5(b"test@example.com17374464000009527").hexdigest()
        },
        {
            "username": "zhiyu",
            "timestamp": 1234567890123,
            "expected": hashlib.md5(b"zhiyu12345678901239527").hexdigest()
        },
        {
            "username": "admin@test.com",
            "timestamp": int(time.time() * 1000),
            "expected": None  # 动态计算
        }
    ]
    
    all_passed = True
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"  用户名: {case['username']}")
        print(f"  时间戳: {case['timestamp']}")
        
        # 生成token
        result = gen_api_token(case['username'], case['timestamp'])
        
        # 计算预期值
        if case['expected'] is None:
            raw_string = f"{case['username']}{case['timestamp']}9527"
            expected = hashlib.md5(raw_string.encode('utf-8')).hexdigest()
        else:
            expected = case['expected']
        
        print(f"  生成规则: MD5({case['username']} + {case['timestamp']} + 9527)")
        print(f"  生成结果: {result}")
        print(f"  预期结果: {expected}")
        
        if result == expected:
            print(f"  ✅ 通过")
        else:
            print(f"  ❌ 失败")
            all_passed = False
    
    # 测试token长度
    print(f"\n测试Token长度:")
    token = gen_api_token("test", 1234567890123)
    print(f"  Token: {token}")
    print(f"  长度: {len(token)}")
    if len(token) == 32:
        print(f"  ✅ 长度正确 (MD5固定32位)")
    else:
        print(f"  ❌ 长度错误 (应为32位)")
        all_passed = False
    
    # 测试token格式
    print(f"\n测试Token格式:")
    if all(c in '0123456789abcdef' for c in token):
        print(f"  ✅ 格式正确 (MD5十六进制)")
    else:
        print(f"  ❌ 格式错误 (应为十六进制)")
        all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("  ✅ 所有测试通过")
    else:
        print("  ❌ 部分测试失败")
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    import sys
    success = test_gen_api_token()
    sys.exit(0 if success else 1)
